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
