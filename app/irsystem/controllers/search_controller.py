from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from flask import current_app
import json

project_name = "Parallel Pigskins: Football Player Similarity Engine"
net_id = "Neil Madhavani nmm85, Cal Lombardo cal362, Alex Lin ajl346, Eric Whitehead ew424, David Fleurantin djf252"

@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	
	# Right now this is a list, (one of ['p'], ['t'], ['p', 't'], []) - cannot be empty or be both checked
	checks = request.args.getlist('cbox')

	#with app.open_resource('static/NFL_team_rosters.json') as t:
		#teams = json.load(t)
	f = current_app.open_resource('static/inverted_index.json')
	inverted_index = json.load(f)
	
	# inverted_index: {key -> [player, count] list}
	
	if query:
		results = {}
		q_traits = query.split(",")
		for word in q_traits:
			wl = word.lower()
			if wl in inverted_index:
				
				for player, score in inverted_index[wl]:
					results[player] = results.get(player, 0) + score 

		scores = [(player, score) for player, score in results.items()]
		scores.sort(reverse=True, key=lambda x: x[1])
		data = [player for player, _ in scores]
		data = data[:5]
		print(data)	
	
	
	if not query or len(checks) == 0:
		data = []
		output_message = ''
	elif len(checks) == 2:
		data = ['']
		output_message = "Error: two boxes checked. Only check one box."
	else:
		output_message = "Your search: " + query
		# data = range(5)
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)
