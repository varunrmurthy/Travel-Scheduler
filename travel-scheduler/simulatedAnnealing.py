import random
from Place import Place
import requests

def simulatedAnnealing(data, hotel, maxIterations = 10):
    finalBestOrdering = {}
    finalBestTime = 0
    hotelObj = Place(None, None, None, None, None)
    hotelObj.pos = hotel
    foodLists = {}
    entertainLists = {}

    #get all food places out
    #edited this block
    for key in data:
        foodLists[key], entertainLists[key] = [], []
        for attraction in data[key]:
            if attraction.category == 'FOOD_BEVERAGE':
                foodLists[key].append(attraction)
            else:
                entertainLists[key].append(attraction)

    for key in data:
        if len(data[key]) == 0:
            finalBestOrdering[key] = data[key]
            continue

        elif len(data[key]) == 1:
            finalBestOrdering[key] = data[key]
            finalBestTime += getTime(hotelObj, data[key][0]) + getTime(data[key][0], hotelObj)
            continue

        ##edited these 2 lines
        curr = [hotelObj] + getInitialOrdering(foodLists[key], entertainLists[key]) + [hotelObj]
        foodIndeces, entertainIndeces = getIndeces(curr)

        bestOrdering = curr
        bestTime = getTime(curr)

        for i in range(maxIterations):
            curr = randomizeOrdering(curr, foodIndeces, entertainIndeces)
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
    PARAMS = {'from':start.pos, 'to':end.pos, 'key':}
    r = requests.get(url = URL, params = PARAMS)
    data = r.json()
    return data.get('route').get('time')

def temperature(iteration):
    return 1 / (iteration + 1)

#edited this function
def randomizeOrdering(data, foodIndeces, entertainIndeces):
    rand1 = random.randint(1, len(data) - 2)
    if data[rand1].category == 'FOOD_BEVERAGE':
        rand2 = foodIndeces[random.randint(0, len(foodIndeces) - 1)]
        while rand1 == rand2:
            rand2 = foodIndeces[random.randint(0, len(foodIndeces) - 1)]
    else:
        rand2 = entertainIndeces[random.randint(0, len(entertainIndeces) - 1)]
        while rand1 == rand2:
            rand2 = entertainIndeces[random.randint(0, len(entertainIndeces) - 1)]
    data[rand1], data[rand2] = data[rand2], data[rand1]
    return data

#wrote these last 2 functions
def getInitialOrdering(foodLists, entertainLists, count=0, ordering=[]):
    if not foodLists:
        return ordering + entertainLists
    if not entertainLists:
        return ordering + foodLists
    if not count:
        return getInitialOrdering(foodLists[1:], entertainLists, 2, ordering + [foodLists[0]])
    else:
        return getInitialOrdering(foodLists, entertainLists[1:], count - 1, ordering + [entertainLists[0]])

def getIndeces(data):
    foodIndeces, entertainIndeces = [], []
    count = 0
    for attraction in data:
        if attraction.category == 'FOOD_BEVERAGE':
            foodIndeces.append(count)
        elif attraction.category:
            entertainIndeces.append(count)
        count += 1
    return foodIndeces, entertainIndeces
