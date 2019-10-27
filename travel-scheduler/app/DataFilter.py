from Place import Place
from KMeans import KMeans
import requests
import sa
import random

class DataFilter:

    def query_potential_locations(self, center_lat, center_lon, interests = ["FOOD_BEVERAGE"], dist=500, num_locations=50, categories = ['ARTS_ENTERTAINMENT','SHOPPING_RETAIL']):
        '''
            Queries num_locations near the center (lat, lon) using Facebook Places API_KEY
        '''

        center = center_lat + ", " + center_lon
        API_KEY = "MyhhJX525dvRwSUWpKHNOTKDjJaK59WX"
        access_token = "2210087485905915|vSCL_c4XqrU_ABMFWOdzbyhh_jk"
        FB_URL = "https://graph.facebook.com/search?type=place"
        cat = 'FOOD_BEVERAGE'
        FB_PARAMS = {'categories' : str([cat]), \
            'fields': ['name,checkins,overall_star_rating,location, category_list, price_range'], \
            'center': center, \
            'distance': 2000, \
            'access_token': access_token}
        res = requests.get(url = FB_URL, params = FB_PARAMS)
        all_locations = res.json()['data']
        all_locations.sort(key = lambda place: -place['checkins'])
        attractions_with_rating = [a for a in all_locations if 'overall_star_rating' in a]
        places = []
        attractions = []
        price_mapping = {"$": 10, "$$": 20, "$$$": 40, "$$$$": 200, "Unspecified": 15}
        for category in categories:
            FB_PARAMS = {'categories' : str([category]), \
            'fields': ['name,checkins,overall_star_rating,location, price_range'], \
            'center': center, \
            'distance': 2000, \
            'access_token': access_token}
            res = requests.get(url = FB_URL, params = FB_PARAMS)
            all_locations = res.json()['data']
            all_locations.sort(key = lambda place: -place['checkins'])
            attractions_with_rating = [a for a in all_locations if 'overall_star_rating' in a]
            for attraction in attractions_with_rating:
                if 'price_range' in attraction.keys():
                    price = price_mapping[str(attraction['price_range'])]
                else:
                    price = 10
                loc_data = attraction["location"]

                if set(['street', 'city', 'state', 'zip']) <=set(loc_data.keys()):
                    address = loc_data['street'] + "," + loc_data['city'] + "," + loc_data['state'] + " " + loc_data['zip']
                else:
                    continue
                place = \
                        Place(attraction["name"], \
                              attraction["location"]["latitude"], \
                              attraction["location"]["longitude"], \
                              attraction, address, attraction["checkins"], \
                              attraction["overall_star_rating"], category, price)
                places.append(place)

        filtered_places = self.filter_user_interests(interests, places) #need to get user input
        return filtered_places[:num_locations]

    def gen_specified_locations(self, user_locs):
        """
            Generate data for a list of user specified locations of interests, which will be combined
            with the generic list of attractions. Will be passed into k-means.
        """
        API_KEY = "AIzaSyC2Sixwd61MWgbL6qxCrX1JTAEotj5RWDs"
        URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?" #change output and parameters
        fields = 'name,rating,geometry,formatted_address'
        places = []
        for l in user_locs:
            r = requests.get(URL + 'input=' + l + \
                                '&inputtype=textquery' + '&fields=' + fields + \
                                '&key=' + API_KEY)
            attraction = r.json()['candidates'][0]
            place = \
                Place(attraction["name"], \
                    attraction["geometry"]["location"]["lat"], \
                    attraction["geometry"]["location"]["lng"], \
                      attraction, attraction['formatted_address'])
            places.append(place)
        return places

    def filter_user_interests(self, interests, places, num_non_interests=0):
        """
            Filters attraction by user interests by matching categories.
            num_non_interests is an optional parameter. It represents the number of attractions
            not listed in user interests to include in the final list of attractions.
        """
        res = []
        for place in places:
            if place.category in interests: #is category a correct field?
                res.append(place)
            elif num_non_interests > 0: #allow to add a number of places of "non-interest"
                res.append(place)
                num_non_interests -= 1
        return res


    def filter_by_popularity(self, center, attractions):
        '''
            Filters attractions using knapsack.
            weights = a weighted average of estimated time spent at location and distance from center
            values = a weighted average of num checkins and overall star rating
        '''
        weights, values, prices = [], [], []
        for place in attractions:
            val = place.calculate_value(place.checkins, place.rating)
            weight = place.calculate_weight(center)
            prices.append(place.price)
            values.append(val)
            weights.append(weight)
        return self.knapsack(1000000, weights, values, len(attractions), attractions)

    def cluster_attractions(self, data, days):

        '''
            Clusters attractions into the # days clusters.
        '''
        return self.k_means(data, days)

    ################## HELPER FUNCTIONS #######################
    # Performs knapsack on list of weights/values
    # def knapsack(self, W, wt, val, P, prices, n, attractions):
    #     K = [[[0 for x in range(P + 1)] for x in range(W+1)] for x in range(n+1)]

    #     # Build table K[][] in bottom up manner
    #     for i in range(n+1):
    #         for w in range(W+1):
    #             for p in range(P + 1):
    #                 if i==0 or w==0 or p==0:
    #                     K[i][w][p] = 0
    #                 elif wt[i-1] <= w and prices[i-1] <= p:
    #                     K[i][w][p] = max(val[i-1] + K[i-1][w-wt[i-1]][p-prices[i-1]],  K[i-1][w][p])
    #                 else:
    #                     K[i][w][p] = K[i-1][w][p]
    #     print("table built")
    #    # stores the result of Knapsack
    #     res = K[n][W][P]
    #     visited_list = []
    #     w = W
    #     for i in range(n, 0, -1):
    #         if res <= 0:
    #             break
    #         if res == K[i - 1][w][P]:
    #             continue
    #         else:
    #             visited_list.append(attractions[i-1])
    #             # print(attractions[i - 1].name)
    #             print(attractions[i - 1])
    #             res = res - val[i - 1]
    #             w = w - wt[i - 1]
    #     return visited_list
    def knapsack(self, W, wt, val, n, attractions):
        K = [[0 for x in range(W+1)] for x in range(n+1)]

        # Build table K[][] in bottom up manner
        for i in range(n+1):
            for w in range(W+1):
                if i==0 or w==0:
                    K[i][w] = 0
                elif wt[i-1] <= w:
                    K[i][w] = max(val[i-1] + K[i-1][w-wt[i-1]],  K[i-1][w])
                else:
                    K[i][w] = K[i-1][w]

       # stores the result of Knapsack
        res = K[n][W]
        visited_list = []
        w = W
        for i in range(n, 0, -1):
            if res <= 0:
                break
            if res == K[i - 1][w]:
                continue
            else:
                visited_list.append(attractions[i-1])
                print(attractions[i - 1].name)
                res = res - val[i - 1]
                w = w - wt[i - 1]
        return visited_list

    def k_means(self, data, k=3):
        ''' Runs k means algorithm on data, and returns the clustered data '''
        kmeans = KMeans(k)
        kmeans.fit(data)
        return kmeans.classification_names

def printNicelyxD(clustered_attractions):
    finString = ""
    dayToName = {}
    dayToLoc = {}
    for cluster in clustered_attractions:
        #print('Day ' + str(cluster + 1) + ': ', end = '')
        finString += 'Day ' + str(cluster + 1) + ': \n'
        locs = []
        names = []
        numAttractions = len(clustered_attractions[cluster])
        for x in range(numAttractions):
            if clustered_attractions[cluster][x].name:
                if x  < numAttractions - 1:
                    #print(clustered_attractions[cluster][x].name + ', ', end = '')
                    finString += clustered_attractions[cluster][x].name + ', '

                else:
                    print(clustered_attractions[cluster][x].name)
                    finString += clustered_attractions[cluster][x].name
                locs.append(clustered_attractions[cluster][x].address)
                names.append(clustered_attractions[cluster][x].name)

        dayToName[cluster] = names
        dayToLoc[cluster] = locs
        finString += "\n"
    return finString, dayToName, dayToLoc

def getTimeTraveled(clustered_attractions):
    time = 0
    for cluster in clustered_attractions:
        currLocation = center
        for location in cluster_attractions[cluster]:
            time += simulatedAnnealing.getMapQuestTime(currLocation, location)
            currLocation = location
        time += simulatedAnnealing.getMapQuestTime(currLocation, center)
    return time

def append_food(hotel_lat, hotel_lon, attractions, df):
    hours_map = {"ARTS_ENTERTAINMENT" : 2, "EDUCATION" : 1, "FITNESS_RECREATION" : 1.5, "FOOD_BEVERAGE": 1.5,  "SHOPPING_RETAIL": 2}
    hours_before_food = 0
    fin_itinerary = []
    restaurant = df.query_potential_locations(hotel_lat, hotel_lon, ["FOOD_BEVERAGE"], 150, 20, ["FOOD_BEVERAGE"])
    random.shuffle(restaurant)
    fin_itinerary.append(restaurant[0])
    for attraction in attractions:
        hours_before_food += hours_map[attraction.category]
        if (hours_before_food > 6):
            lat = str(float(fin_itinerary[-1].lat) + float(attraction.lat))
            lon = str(float(fin_itinerary[-1].lon) + float(attraction.lon))
            center = lat + "," + lon
            restaurant = df.query_potential_locations(lat, lon, ["FOOD_BEVERAGE"], 150, 20, ["FOOD_BEVERAGE"])
            random.shuffle(restaurant)
            fin_itinerary.append(restaurant[0])
            fin_itinerary.append(attraction)
            hours_before_food = 0
        elif (hours_before_food > 4):
            restaurant = df.query_potential_locations(str(attraction.lat), str(attraction.lon), ["FOOD_BEVERAGE"], 150, 20, ["FOOD_BEVERAGE"])
            random.shuffle(restaurant)
            fin_itinerary.append(attraction)
            fin_itinerary.append(restaurant[0])
            hours_before_food = 0
    return fin_itinerary



def user_input_to_output(center, user_locs, interests, days, radius):
    dataFilter = DataFilter()
    place = dataFilter.gen_specified_locations([center.split(",")[0]])[0]
    print(place.lat, place.lon)
    lat, lon = str(place.lat), str(place.lon)
    attractions = dataFilter.query_potential_locations(lat, lon, interests, radius)
    filtered_attractions = dataFilter.filter_by_popularity(center, attractions)
    filtered_attractions += dataFilter.gen_specified_locations(user_locs) #extend the attractions to cover user specified places
    clustered_attractions = dataFilter.cluster_attractions(filtered_attractions, days)
    print("Starting SA")
    SAOrder, SATime = sa.simulatedAnnealing(clustered_attractions, center, 1)
    fin_itinerary = {}
    for cluster in SAOrder:
         fin_itinerary[cluster] = append_food(lat, lon, SAOrder[cluster], dataFilter)
    print('Attractions ordered after Simulated Annealing:')
    finString, dayToName, dayToLoc = printNicelyxD(fin_itinerary)
    return finString, dayToName, dayToLoc


user_locs = ["Central Park"]
interests = ['ARTS_ENTERTAINMENT','SHOPPING_RETAIL']
categories = ['ARTS_ENTERTAINMENT','SHOPPING_RETAIL']
days = 3
radius = 600
center = "Palace Hotel, a Luxury Collection Hotel, San Francisco, New Montgomery Street, San Francisco, CA, USA"
# user_input_to_output(center, user_locs, interests, days, radius)
