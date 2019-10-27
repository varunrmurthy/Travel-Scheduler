import requests
MAPQUEST_API_KEY = 'sUwBhlO1aKJsW4vEJ0lj8x11CA4uudDX'
MAPQUEST_URL = "http://www.mapquestapi.com/directions/v2/route?"

class Place:

    def __init__(self, name, latitude, longitude, data, checkins = 50, rating = 5, category = 'FOOD_BEVERAGE', price = 10):

        self.name = name
        self.lat = latitude
        self.lon = longitude
        self.pos = str(latitude) + ", " + str(longitude)
        self.data = data
        self.category = category
        self.price = price
        self.checkins = checkins
        self.rating = rating

    def calc_dist_from_center(self, center):
        MAPQUEST_PARAMS = {'key': MAPQUEST_API_KEY, 'from': center, 'to': str(self.lat) + ", " + str(self.lon)}
        res = requests.get(url= MAPQUEST_URL, params = MAPQUEST_PARAMS)
        distance = res.json()['route']['distance']
        return distance

    def calculate_value(self, checkins, rating, w_checkins=0.1, w_rating=4):
        self.value = int(checkins*w_checkins + rating*w_rating)
        return self.value

    def calculate_weight(self, center, estimated_time_spent=150, w_travel_time = 1.0, w_est_time = 1.0):
        travel_time = self.calc_dist_from_center(center)
        self.weight = int(w_travel_time*travel_time + w_est_time*estimated_time_spent)
        return self.weight
