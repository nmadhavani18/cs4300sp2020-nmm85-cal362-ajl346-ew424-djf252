from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from flask import current_app
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
# DEVELOPER_KEY = "AIzaSyBv8cM9jRZfZ2QmVcnSqMunqzIFr4PwZxg"
DEVELOPER_KEY = "AIzaSyAORCs5Nvrxu1rsufxjcvcLB4zw32AcdBc"

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = DEVELOPER_KEY)


@irsystem.route('/', methods=['GET'])
def search():
    query = request.args.get('search')
    clear = request.args.get('results')
    print("clear is: ", clear)
    print("query is: ", query)

    # Right now this is a list, (one of ['p'], ['t'], ['p', 't'], []) - cannot be empty or be both checked
    checks = request.args.getlist('cbox')

    # inverted_index: {key -> [player, count] list}

    if query:
        results = {}
        q_split = query.split(",")
        term_player_index = {}
        player_term_index = {}

        # original inverted indexes
        f1 = current_app.open_resource('static/inverted_index.json')
        term_player_index = json.load(f1)

        f2 = current_app.open_resource('static/inverted_index2.json')
        player_term_index = json.load(f2)

        # player/term to numeric index
        term_inverse_index = {term : idx for idx, term in enumerate(term_player_index)}
        player_inverse_index = {player : idx for idx, player in enumerate(player_term_index)}

        tp_matrix = np.zeros((len(player_inverse_index), len(term_inverse_index)))

        # create player-term frequency matrix
        for player in player_term_index:
            player_idx = player_inverse_index[player]
            for entry in player_term_index[player]:
                term = entry[0]
                num = entry[1]
                term_idx = term_inverse_index[term]
                tp_matrix[player_idx, term_idx] = num
        
        if checks == ['t']:
            for word in q_split:
                wl = word.lower()
                if wl in term_inverse_index:
                    term_idx = term_inverse_index[wl]
                    for pair in term_player_index[wl]:
                        player = pair[0]
                        player_idx = player_inverse_index[player]
                        num = tp_matrix[player_idx, term_idx]
                        norm = np.linalg.norm(tp_matrix[player_idx])

                        results[player] = num / norm
        else:
            for word in q_split:
                wl = word.lower()
                if wl in player_inverse_index:
                    player_idx = player_inverse_index[wl]
                    for player in player_inverse_index:
                        if player_inverse_index[player] != player_idx:
                            # cosine similarity
                            p_idx2 = player_inverse_index[player]
                            temp = np.multiply(tp_matrix[player_idx], tp_matrix[p_idx2])
                            CS_num = np.sum(temp)

                            norm1 = np.linalg.norm(tp_matrix[player_idx])
                            norm2 = np.linalg.norm(tp_matrix[p_idx2])

                            results[player] = CS_num / (norm1 * norm2)

        # for word in q_split:
        #     wl = word.lower()
        #     if wl in term_player_index:

        #         for entry in term_player_index[wl]:
        #             player = entry[0]
        #             num = entry[1]

        #             normal_sum = 0
        #             for lst in player_term_index[player]:
        #                 normal_sum += lst[1]^2
                    
        #             entry[1] = num / math.sqrt(normal_sum)

        #         for k, val in term_player_index[wl]:
        #             results[k] = results.get(k, 0) + val

        scores = [(player, score) for player, score in results.items()]
        scores.sort(reverse=True, key=lambda x: x[1])
        data = [player for player, _ in scores]
        data = data[:5]  # limit to top 5
        
        for i in range(len(data)):
            thumb, link, title = ytHighlights(data[i])
            # thumb, link, title = "blank", "blank", "blank"
            updateTitle(title)
            data[i] = [data[i], thumb, link, updateTitle(title)]

            print(data)

    if not query or len(checks) == 0:
        data = []
        output_message = ''
    elif len(checks) == 2:
        data = ['']
        output_message = "Error: two boxes checked. Only check one box."
    else:
        output_message = "Your search: " + query
        if data == []:
            data = ["Error: no results found. Change input and retry."]
        return render_template('results.html', name=project_name, netid=net_id, output_message=output_message, data=data)
        # data = range(5)
    return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)


def ytHighlights(player_name):
    # print("Highlights check")
    request = youtube.search().list(
        part="snippet",
        q= player_name + " highlights"
    )

    response = request.execute()
    responseJson = json.dumps(response)
    output1 = (response["items"][0]["snippet"]["thumbnails"]["high"]["url"],
            "https://www.youtube.com/watch?v=" + response["items"][0]["id"]["videoId"], 
            response["items"][0]["snippet"]["title"])
    return output1

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
