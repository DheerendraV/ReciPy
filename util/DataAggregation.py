from pymongo import MongoClient
import json 

def fetchData(outputFilename,port=27017):
    cluster = MongoClient('localhost',port)

    db = cluster.get_database("recipes-master")

    data = []
    for collection in ["food-recipes","allrecipes-recipes","foodnetwork-recipes","recipetineats-recipes","simplyrecipes-recipes"]:
        coll = db.get_collection(collection)
        cursor = coll.find()
        data.extend(list(cursor))

    for i in range(len(data)):
        data[i]['_id'] = str(data[i]['_id'])

    with open(outputFilename, 'w') as jsonFile:
        json.dump(data, jsonFile)

if __name__ == "__main__":
    fetchData("final-recipes.json")
