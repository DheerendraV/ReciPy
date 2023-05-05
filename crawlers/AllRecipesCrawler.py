import urllib
import urllib.request
from bs4 import BeautifulSoup
from pymongo import MongoClient

class Crawler:
    def __init__(self, url, db,collection):
        cluster = MongoClient("mongodb://localhost:27017/")
        self.db = cluster[db]
        self.collection = self.db[collection]

        self.url = url
        self.links = []
        self.visited = []
        self.queue = []
        self.queue.append(self.url)
        self.visited.append(self.url)
        self.crawl()

    def crawl(self):
        while self.queue:
            url = self.queue.pop(0)
            try:
                with urllib.request.urlopen(url) as response:
                    htmltext = response.read()
            except:
                print("Error: " + url)
                break
            soup = BeautifulSoup(htmltext,features="html.parser")

            # for AllRecipes.com, parse soup for Title
            title = soup.find("h1",id="article-heading_2-0").text.strip()
            
            # for AllRecipes.com, parse soup for Cooking time, prep time, total time and servings

           
            statBucket = soup.find("div",id="recipe-details_1-0")
            
            # need to discuss with team on how to handle this, for now lets hardcode the keys
            statKeys = statBucket.find_all("div",class_="mntl-recipe-details__label")
            
       
            
            statValue = statBucket.find_all("div",class_="mntl-recipe-details__value")

            stats = {}
            for i in range(len(statKeys)):
                # Need to discius with team on how to handle this, for now just ignore the additional time field
                unCleanStat = statKeys[i].text.strip()
                cleanStat = unCleanStat.replace(":","")
                if cleanStat in ["Total Time","Servings"]:  
                    if cleanStat == "Total Time":
                        cleanStat = "totalTime"
                    else:
                        cleanStat = "servings"
                    stats[cleanStat] = statValue[i].text.strip()
                

            
            # for AllRecipes.com, parse soup for Nutrition
            nutrBucket = soup.find_all("tr",class_="mntl-nutrition-facts-summary__table-row")
            nutrition = {}
            for ele in nutrBucket:
                tD = ele.find_all("td")
                nutrition[tD[1].text.strip().lower()] = tD[0].text.strip()
            stats["nutrition"] = nutrition
            
            # for AllRecipes.com, parse soup for Ingredients
            ingredientList = []
            ingredients = soup.find("ul",class_="mntl-structured-ingredients__list")
            
            for ingredient in ingredients.find_all("p"):
                spanBucket = ingredient.find_all("span")
                ingrStrBuilder = ""
                for i,span in enumerate(spanBucket):
                    if i == 0:
                        ingrStrBuilder+=span.text.strip()
                    else:
                        ingrStrBuilder+=" "+span.text.strip()
                ingredientList.append(ingrStrBuilder.strip())



            # for AllRecipes.com, parse soup for Directions

            directionsList = []
            directions = soup.find("ol",id="mntl-sc-block_2-0")
            for direction in directions.find_all("li"):
                directionsList.append(direction.text.strip())

            tempDict = {}
            tempDict["url"] = url
            tempDict["title"] = title
            tempDict["stats"] = stats
            tempDict["dataSource"] = "allrecipes"
            tempDict["ingredients"] = ingredientList
            tempDict["directions"] = directionsList
            # print(tempDict)
            try:
                self.collection.insert_one(tempDict)
                print("Inserted: " + title)
            except:
                print("Error inserting: " + title)
            # DFS to visit all relevant links on the recipe page
            for tag in soup.findAll('a', href=True):
                if "https://www.allrecipes.com/recipe/" in tag['href'] and tag['href'] not in self.visited:
                    self.visited.append(tag['href'])
                    self.queue.append(tag['href'])
                    self.links.append(tag['href'])

                    

    def get_links(self):
        return self.links

    def get_visited(self):
        return self.visited

    def get_queue(self):
        return self.queue


if __name__ == "__main__":
    crawler = Crawler("https://www.allrecipes.com/recipe/8513735/lemon-chicken-romano/","recipes-master","allrecipes-recipes")
    crawler.crawl()
    # print(crawler.get_links())
    print(len(crawler.get_visited()))
    # print(crawler.get_queue())
