from flask import Flask, render_template, request, session, jsonify
from DataFilter import user_input_to_output

app = Flask(__name__)
app.config['input'] = {}


@app.route('/')
def location():
    return render_template('location_input.html')

@app.route('/submit_location', methods=['POST'])
def submit_location():
    app.config['input']['location'] = request.form['pac-input']


@app.route('/logistics')
def logistics():
    return render_template('logistics_input.html')

@app.route('/submit_logistics', methods=["POST"])
def submit_logistics():
    input = app.config['input']
    input['days'] = request.form['days']
    input['miles'] = request.form['miles']
    input['budget'] = request.form['budget']

@app.route('/interests')
def interests():
    return render_template('interests_input.html')

@app.route('/change', methods=['POST'])
def change():
    input = app.config['input']
    if not 'interests' in input:
        input['interests'] = []

    selected = input['interests']

    current = request.form.lists()[0][1][0]
    if not current in selected:
        selected.append(current)
        return jsonify(result='t'+current)
    else:
        selected.remove(current)
        return jsonify(result='f'+current)

@app.route('/places')
def places():
    if 'places' in app.config['input']:
        places_list = app.config['input']['places']
    else:
        places_list = []
        app.config['input']['places'] = places_list
    return render_template('places_input.html', places=places_list)

@app.route('/submit_place', methods=['POST'])
def submit_place():
    addr = request.form.get('place', '', type=str)
    app.config['input']['places'].append(addr)

@app.route('/itinerary')
def itinerary():

    hotel = "Empire State Building"
    center = "40.7484, -73.9857"
    user_locs = ["Central Park"]
    interests = ['ARTS_ENTERTAINMENT','SHOPPING_RETAIL']
    categories = ['ARTS_ENTERTAINMENT','SHOPPING_RETAIL']
    days = 3
    # result, waypoints, names = user_input_to_output (input['location'], input['places'], input['interests'], input['days'])
    # result, waypoints, names = user_input_to_output (input['location'], input['places'], input['interests'], input['days'])
    input = app.config['input']
    results, names, waypoints = user_input_to_output(input['location'], input['places'], ['ARTS_ENTERTAINMENT','SHOPPING_RETAIL'], int(input['days']), int(input['miles']) * 1609)

    # waypoints = {0: ['228 W 39th St,New York,NY 10018', '340 W 50th St,New York,NY 10019', '228 W 52nd St,New York,NY 10019', '235 West 50th St.,New York,NY 10019', 'Times Square: 147 West 43rd Street - Upper East Side: 1081 Third Ave,New York,NY 10036', '220 W 48th St,New York,NY 10036', '228 W 39th St,New York,NY 10018', 'Brooks Atkinson Theatre, 256 West 47th St,New York,NY 10036', '9 W 53rd St,New York,NY 10019'], 1: ['11 Madison Ave,New York,NY 10010', '124 W 43rd St,New York,NY 10036', '42 E 20th St,New York,NY 10003'], 2: ['228 W 39th St,New York,NY 10018', '200 W 40th St,New York,NY 10018-1709', 'Times Square: 147 West 43rd Street - Upper East Side: 1081 Third Ave,New York,NY 10036', '247 W 44th St,New York,NY 10036', '1 E 55th St,New York,NY 10022']}
    # names = {0: ["Carragher's Pub & Restaurant", 'Puffs', "Gallagher's Steakhouse", 'Once On This Island Broadway', "Tony's DiNapoli", 'A Bronx Tale The Musical', "Carragher's Pub & Restaurant", 'Waitress the Musical', 'The Modern'], 1: ['Eleven Madison Park', 'Beautiful - The Carole King Musical', 'Gramercy Tavern'], 2: ["Carragher's Pub & Restaurant", 'Midtown Comics Times Square', "Tony's DiNapoli", 'The Phantom Of The Opera - Broadway', 'The Polo Bar, New York City']}

    return render_template('itinerary.html', center = input['location'], waypoints = waypoints, names = names)
