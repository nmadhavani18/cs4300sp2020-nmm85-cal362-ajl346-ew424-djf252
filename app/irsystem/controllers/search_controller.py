from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from flask import current_app, session
import json
import math
import numpy as np
import io
import os
import sys
import pprint
import googleapiclient.discovery

project_name = "Parallel Pigskins: Football Player Similarity Engine"
net_id = "Neil Madhavani nmm85, Cal Lombardo cal362, Alex Lin ajl346, Eric Whitehead ew424, David Fleurantin djf252"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "AIzaSyBv8cM9jRZfZ2QmVcnSqMunqzIFr4PwZxg"
# DEVELOPER_KEY = "AIzaSyAORCs5Nvrxu1rsufxjcvcLB4zw32AcdBc"
# DEVELOPER_KEY = "AIzaSyBXF84YPcwV38EB0E3im_CHi951OHUYKGs"
# DEVELOPER_KEY = "AIzaSyAc9eFivfJBHtDY7Rs7dn4a3gJcXBNQCWU"
# DEVELOPER_KEY = "AIzaSyDxMRllRdEV0ei9OC1T_bbnjKJ5j1Na0oo"

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = DEVELOPER_KEY)


term_player_index = {}
player_term_index = {}



@irsystem.route('/', methods=['GET'])
def search():
    query = request.args.get('search')
    clear = request.args.get('results')
    # print("clear is: ", clear)
    # print("query is: ", query)

    # Right now this is a list, (one of ['p'], ['t'], ['p', 't'], []) - cannot be empty or be both checked
    checks = request.args.getlist('cbox')

    session['query'] = query
    session['checks'] = checks

    # inverted_index: {key -> [player, count] list}
    print("query is: ", query)

    if query:
        results = {}
        q_split = query.split(",")
        term_player_index = {}
        player_term_index = {}

        # original inverted indexes
        if term_player_index == {}:
            print("File opened")
            f1 = current_app.open_resource('static/inverted_index.json')
            term_player_index = json.load(f1)

        if player_term_index == {}:
            print("File opened")
            f2 = current_app.open_resource('static/inverted_index2.json')
            player_term_index = json.load(f2)

        # player/term to numeric index
        term_inverse_index = {term : idx for idx, term in enumerate(term_player_index)}
        player_inverse_index = {player : idx for idx, player in enumerate(player_term_index)}

        with open('app/static/relevant.json', 'r') as json_file:
            rdict = json.load(json_file)

        with open('app/static/irrelevant.json', 'r') as json_file:
            idict = json.load(json_file)

        tp_matrix = np.load('app/static/tp_matrix.npy')

        np.save('app/static/tp_matrix', tp_matrix)

        if checks == ['t']:
            for i in range(len(q_split)):
                word = q_split[i]
                wl = word.lower()
                wl = wl.strip()

                if wl in term_inverse_index:
                    print("in term_inv_index, wl is: ", wl)
                    term_idx = term_inverse_index[wl]
                    for pair in term_player_index[wl]:
                        player = pair[0]
                        player_idx = player_inverse_index[player]
                        num = tp_matrix[player_idx, term_idx]
                        norm = np.linalg.norm(tp_matrix[player_idx])

                        # idf = np.count_nonzero(tp_matrix[:, term_idx])
                        # idf = idf / len(player_inverse_index)

                        # multiply (num / norm) by math.log(idf)
                        # add them for each query trait
                        if player not in results:
                            results[player] = 0
                        results[player] += (num / norm)

        else:
            player_vector = np.zeros(len(tp_matrix[0]))
            relevant_vector = np.zeros(len(tp_matrix[0]))
            irrelevant_vector = np.zeros(len(tp_matrix[0]))
            relevant_size = 0
            irrelevant_size = 0
            count = 0
            query_players = set()

            for word in q_split:
                wl = word.lower()
                wl = wl.strip()
                query_players.add(wl)

                if wl in player_inverse_index:

                    player_idx = player_inverse_index[wl]
                    # print(wl, " First traits: ", tp_matrix[player_idx][:10])

                    # pseudo rocchio update
                    for player in player_inverse_index:
                        if wl in idict and player in idict[wl]:
                            pidx = player_inverse_index[player]
                            irrelevant_vector += tp_matrix[pidx]
                        if wl in rdict and player in rdict[wl]:
                            pidx = player_inverse_index[player]
                            relevant_vector += tp_matrix[pidx]

                    if wl in idict and wl in rdict:
                        relevant_size += len(rdict[wl])
                        irrelevant_size += len(idict[wl])

                        relevant = relevant_vector / relevant_size
                        irrelevant = irrelevant_vector / irrelevant_size

                        player_vector += 0.9*tp_matrix[player_idx] + 0.1*relevant - 0.15*irrelevant
                    else:
                        player_vector += tp_matrix[player_idx]
                    count += 1

            player_vector /= count

            for player in player_inverse_index:
                if player not in query_players:
                    # cosine similarity
                    p_idx2 = player_inverse_index[player]
                    temp = np.multiply(player_vector, tp_matrix[p_idx2])
                    CS_num = np.sum(temp)

                    norm1 = np.linalg.norm(player_vector)
                    norm2 = np.linalg.norm(tp_matrix[p_idx2])

                    results[player] = CS_num / (norm1 * norm2)

        scores = [(player, score) for player, score in results.items()]
        scores.sort(reverse=True, key=lambda x: x[1])
        data = [player for player, _ in scores]
        data = data[:5]  # limit to top 5

        # initially add all players to relevant (player comp only)
        if checks == ['p']:
            for q in query_players:
                if q not in rdict:
                    rdict[q] = []
                    for player in data:
                        rdict[q].append(player)
                else:
                    for player in data:
                        if player not in rdict[q]:
                            rdict[q].append(player)

            with open('app/static/relevant.json', 'w') as fp:
                json.dump(rdict, fp, indent=4)

        file_r_yt = open('app/static/youtube_cache.json', 'r')
        yt_dict = json.load(file_r_yt)
        file_r_yt.close()

        positions_file = open('app/static/player_to_position.json', 'r')
        player_pos_dict = json.load(positions_file)

        for i in range(len(data)):
            thumb, link, title = ytHighlights(data[i], yt_dict)
            # thumb, link, title = "blank", "blank", "blank"
            # updateTitle(title)
            data[i] = [data[i], thumb, link, updateTitle(title), player_pos_dict[data[i]]]
            print(data[i])

        positions_file.close()
        file_w_yt = open('app/static/youtube_cache.json', 'w')

        json.dump(yt_dict, file_w_yt, indent = 4)
        file_w_yt.close()



    if not query or len(checks) == 0:
        data = []
        output_message = ''
    elif len(checks) == 2:
        data = ['']
        output_message = "Error: two boxes checked. Only check one box."
    else:
        print("query is: ", query)
        output_message = "Your search: " + query
        if data == []:
            data = ["Error: no results found. Change input and retry."]
        return render_template('results.html', name=project_name, netid=net_id, output_message=output_message, data=data)

    return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)


def ytHighlights(player_name, yt_dict):
    try:
        if player_name not in yt_dict:
            print(player_name)
            print("Api call made")
            request = youtube.search().list(
                part="snippet",
                q= player_name + " highlights"
            )

            response = request.execute()
            responseJson = json.dumps(response)
            thumb = response["items"][0]["snippet"]["thumbnails"]["high"]["url"]
            url = "https://www.youtube.com/watch?v=" + response["items"][0]["id"]["videoId"]
            title = response["items"][0]["snippet"]["title"]
            title = updateTitle(title)

            yt_dict[player_name] = {"thumbnail": thumb, "url": url, "title": title}
    except:
        return ("", "", "ERROR: API CALLS MAXED OUT")

    return (yt_dict[player_name]["thumbnail"],
                yt_dict[player_name]["url"],
                yt_dict[player_name]["title"])

# Some youtube titles have "&quot;" instead of " and #39 instead of ', so this eliminates them
def updateTitle(title):
    title = title.split("&quot;")
    new_t = ""
    for t in title:
        new_t += t + " "

    new_t = new_t.split("&#39;")
    title = ""
    for t in new_t:
        title += t + " "
    return title

@irsystem.route('/results')
def results():
    term_player_index = {}
    player_term_index = {}

    f1 = current_app.open_resource('static/inverted_index.json')
    term_player_index = json.load(f1)

    f2 = current_app.open_resource('static/inverted_index2.json')
    player_term_index = json.load(f2)

    term_inverse_index = {term : idx for idx, term in enumerate(term_player_index)}
    player_inverse_index = {player : idx for idx, player in enumerate(player_term_index)}

    disagreed = request.args.getlist('newcbox')
    query = session.get('query').lower()
    query = query.split(', ')

    checks = session.get('checks')

    print("Disagreed is: ", disagreed)

    tp_matrix = np.load('app/static/tp_matrix.npy')
    output_message = ''
    data = []

    # print("update")

    # get associated result which is agreed/disagreed with

    if checks == ['t']:
        print("checked")
        for trait in query:
            if trait in term_inverse_index:
                term_index = term_inverse_index[trait]

                for player in disagreed:
                    player_index = player_inverse_index[player]
                    tp_matrix[player_index, term_index] = 0

        np.save('app/static/tp_matrix', tp_matrix)

    else:
        print("not checked")
        with open('app/static/irrelevant.json', 'r') as json_file:
            idict = json.load(json_file)

        with open('app/static/relevant.json', 'r') as json_file:
            rdict = json.load(json_file)

        query_players = set()
        for word in query:
            word = word.strip()
            query_players.add(word)

        for plyr in query_players:
            if plyr in idict:
                for player in disagreed:
                    if player not in idict[plyr]:
                        idict[plyr].append(player)

            if plyr not in idict:
                idict[plyr] = []
                for player in disagreed:
                    idict[plyr].append(player)

            if plyr in rdict:
                for player in disagreed:
                    if player in rdict[plyr]:
                        rdict[plyr].remove(player)

        with open('app/static/irrelevant.json', 'w') as fp:
            json.dump(idict, fp, indent=4)

        with open('app/static/relevant.json', 'w') as fp:
            json.dump(rdict, fp, indent=4)

        np.save('app/static/tp_matrix', tp_matrix)

    return redirect(url_for('irsystem.search'))

    # return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)
