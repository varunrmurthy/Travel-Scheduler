import random
from Place import Place
import requests

def simulatedAnnealing(data, hotel, maxIterations = 10):
	finalBestOrdering = {}
	finalBestTime = 0
	hotelObj = Place(None, None, None, None)
	hotelObj.pos = hotel

	for key in data:
		if len(data[key]) == 0:
			finalBestOrdering[key] = data[key]
			continue

		elif len(data[key]) == 1:
			finalBestOrdering[key] = data[key]
			finalBestTime += getTime([hotelObj] + [data[key][0]]) + getTime([data[key][0]] +  [hotelObj])
			continue

		curr = [hotelObj] + data[key] + [hotelObj]

		bestOrdering = curr
		bestTime = getTime(curr)

		for i in range(maxIterations):
			curr = randomizeOrdering(curr)
			val = getTime(curr)
			if val < bestTime:
				bestTime = val
				bestOrdering = curr
			else:
				rand = random.random()
				if rand < temperature(i):
					bestTime = val
					bestOrdering = curr

		finalBestOrdering[key] =  bestOrdering[1:-1]
		finalBestTime += bestTime
	return finalBestOrdering, finalBestTime

def getTime(data):
	totalTime = 0
	for i in range(len(data) - 1):
		totalTime += getMapQuestTime(data[i], data[i + 1])
	return totalTime

def getMapQuestTime(start, end):
	URL = "https://www.mapquestapi.com/directions/v2/route?"
	PARAMS = {'from':start.pos, 'to':end.pos, 'key':"MyhhJX525dvRwSUWpKHNOTKDjJaK59WX"}
	r = requests.get(url = URL, params = PARAMS)
	data = r.json()
	return data.get('route').get('time')

def temperature(iteration):
	return 1 / (iteration + 1)

def randomizeOrdering(data):
	rand1 = random.randint(1, len(data) - 2)
	rand2 = random.randint(1, len(data) - 2)
	while rand1 == rand2:
		rand2 = random.randint(1, len(data) - 2)
	data[rand1], data[rand2] = data[rand2], data[rand1]
	return data
