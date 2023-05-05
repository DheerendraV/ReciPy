import urllib
import urllib.request
from bs4 import BeautifulSoup
from pymongo import MongoClient
#import json

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
        #self.count = 0
        self.crawl()

    def crawl(self):
        #outfile = open("error.json", "a") 
        while self.queue:
            url = self.queue.pop(0)
            try:
                with urllib.request.urlopen(url) as response:
                    htmltext = response.read()
            except:
                print("Error: " + url)
                break

            soup = BeautifulSoup(htmltext,features="html.parser")
            recipe = soup.find("main",id="recipe")
            
            if recipe is not None:
            
                tempDict = self.parse(url,soup)
                
                #Save to json [For Testing]
                # try:
                #     json.dump(tempDict, outfile)
                # except:
                #     print("Failed json dump:",url)

                try:
                    self.collection.insert_one(tempDict)
                    print("Inserted: " + tempDict["title"])
                except:
                    print("Error inserting: " + tempDict["title"])

            #DFS to visit all relevant links on the recipe page
            for tag in soup.findAll('a', href=True):
                if "https://www.food.com/" in tag['href'] and tag['href'] not in self.visited:
                    self.visited.append(tag['href'])
                    self.queue.append(tag['href'])
                    self.links.append(tag['href'])  

    def parse(self, url, soup):
        title = soup.find("div","title").h1.string.strip()
               
        stats = {}

        #try:
            #stats["rating"] = soup.find("div","rating").a["title"][13:17]
        #except:
            #stats["rating"] = 0.00
            #stats["imageLink"] = soup.find("div","primary-image").img["src"]

        factsLabel = soup.find_all("dt","facts__label")
        facts = soup.find_all("dd","facts__value")
        for i in range(len(factsLabel)):
            if factsLabel[i].string.strip() == "Ready In:":
                stats["totalTime"] = facts[i].string.strip() if facts[i].string else None
            #elif factsLabel[i].string.strip() == "Ingredients:":
                #stats["numIngredients"] = facts[i].string.strip() if facts[i].string else None
            elif factsLabel[i].string.strip() == "Serves:":
                stats["servings"] = facts[i].string.strip() if facts[i].string else None
        
        stats['nutrition'] = {}
        stats['nutrition']['carbs'] ="---"
        stats['nutrition']['calories'] ="---"
        stats['nutrition']['fat'] ="---"
        stats['nutrition']['protein'] ="---"

        ing_soup = soup.find("section","ingredients").ul.find_all("li")
        ingredientsList = []
        for item in ing_soup:
            if item.h4:
                continue
            try:
                quant = item.span.get_text().strip()
                ing_text = item.find("span","ingredient-text")
                ingredient = " ".join(ing_text.get_text().strip().split())
                list_item = quant + " " + ingredient if len(quant) > 0 else "--- "+ ingredient
            except:
                print("Error during certain item:",title,item)
                continue
            ingredientsList.append(list_item)
        directionsList = []
        try:
            dirtyDirectionsList = soup.find("ul","direction-list").find_all("li","direction")
            directionsList = list(map(lambda x: x.string.strip(),dirtyDirectionsList))
        except:
            print("Error during directions:",title)

        tempDict = {}
        #self.count+=1
        #tempDict["id"] = self.count        
        tempDict["url"] = url
        tempDict["dataSource"] = "www.food.com"
        tempDict["title"] = title
        tempDict["stats"] = stats
        tempDict["ingredients"] = ingredientsList
        tempDict["directions"] = directionsList
        
        return tempDict

    
    def get_links(self):
        return self.links

    def get_visited(self):
        return self.visited

    def get_queue(self):
        return self.queue


if __name__ == "__main__":
    crawler = Crawler("https://www.food.com/html-sitemap","recipes-master","food-recipes")
    crawler.crawl()
    # print(len(crawler.visited))
    # print(crawler.get_links())
    # print(crawler.get_visited())
    # print(crawler.get_queue())