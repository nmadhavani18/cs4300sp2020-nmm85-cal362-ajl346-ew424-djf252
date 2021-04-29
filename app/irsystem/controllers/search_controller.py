from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from flask import current_app
import json
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
		inverted_index = {}
		
		if checks == ['t']:
			f1 = current_app.open_resource('static/inverted_index.json')
			inverted_index = json.load(f1)
		else:
			f2 = current_app.open_resource('static/inverted_index2.json')
			inverted_index = json.load(f2)
			
		for word in q_split:
			wl = word.lower()
			if wl in inverted_index:
				
				for k, val in inverted_index[wl]:
					results[k] = results.get(k, 0) + val
			
		scores = [(player, score) for player, score in results.items()]
		scores.sort(reverse=True, key=lambda x: x[1])
		data = [player for player, _ in scores]
		data = data[:5] # limit to top 5
		
		if checks == ['t']:
			"""
			# I ran into an error with exceeding daily limit on API calls...
			for i in range(len(data)):
				thumb, link, title = ytHighlights(data[i])
				updateTitle(title)
				data[i] = [data[i], thumb, link, updateTitle(title)]
			# print(data)
			"""
			# hardcoded for front end testing
			data = [
				['tom brady', 'https://i.ytimg.com/vi/O7Di8ZpJnm8/hqdefault.jpg', 'https://www.youtube.com/watch?v=O7Di8ZpJnm8', 'Tom Brady Full Season Highlights | NFL 2020'], 
				['larry johnson', 'https://i.ytimg.com/vi/V2Z-UexN24c/hqdefault.jpg', 'https://www.youtube.com/watch?v=V2Z-UexN24c', 'Larry Johnson ULTIMATE Hornets Mixtape!'], 
				['drew brees', 'https://i.ytimg.com/vi/W6o1eXZd7EE/hqdefault.jpg', 'https://www.youtube.com/watch?v=W6o1eXZd7EE', 'Drew Brees&#39; &quot;Big Easy Savior&quot; Career Highlights! | NFL Legends'], 
				['denzelle good', 'https://i.ytimg.com/vi/IZwX2NoCfSc/hqdefault.jpg', 'https://www.youtube.com/watch?v=IZwX2NoCfSc', 'Raiders guard Denzelle Good on pivoting from Tackle: “Guard is kind of what I am naturally now”'], 
				['willie parker', 'https://i.ytimg.com/vi/berzoi2bQeM/hqdefault.jpg', 'https://www.youtube.com/watch?v=berzoi2bQeM', '&quot;Fast&quot; Willie Parker!!! {Career Highlights}']
			]


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
	print(title)