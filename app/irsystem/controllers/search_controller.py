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
	

	# This is a test to see if we can load static json files into our logic - check console to see that it prints
	# We can store our data (ranking system) as JSONs and then access them upon a query
	f = current_app.open_resource('static/NFL_team_rosters.json')
	teams = json.load(f)
	print("# of teams is: ", len(teams))
	


	if not query or len(checks) == 0:
		data = []
		output_message = ''
	elif len(checks) == 2:
		data = ['']
		output_message = "Error: two boxes checked. Only check one box."
	else:
		output_message = "Your search: " + query
		data = range(5)
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)
