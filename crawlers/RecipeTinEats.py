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
            fullSoup = BeautifulSoup(htmltext,features="html.parser")

            soup = fullSoup.find("div", class_="wprm-recipe-container")
            if soup is not None:
                # for recipetineats.com, parse soup for Title
                title = self.getSoupText(soup.find("h2", {"class":"wprm-recipe-name wprm-block-text-bold"}))

                # for recipetineats.com, parse soup for Cooking time, prep time, total time and servings
                # Prep Time:
                prepSoup = soup.find("div", {"class":"wprm-recipe-prep-time-container"})
                prepTime = "---"
                
                if prepSoup is not None:
                    prepTime = self.getSoupText(prepSoup.find("span", {"class": "wprm-recipe-time wprm-block-text-normal"}))
                
                # Cook Time:
                cookSoup = soup.find("div", {"class":"wprm-recipe-cook-time-container"})
                cookTime = "---"
                
                if cookSoup is not None:
                    cookTime = self.getSoupText(cookSoup.find("span", {"class": "wprm-recipe-time"}))
                
                
                # Total Time:
                totalTimeSoup = soup.find("div", class_="wprm-recipe-total-time-container")
                
                totalTimeText = "---"
                
                if totalTimeSoup is not None:
                    totalTimeText = self.getSoupText(totalTimeSoup.find("span", class_="wprm-block-text-normal"))

                totalTime = "---"
                
                if totalTimeText != "---":
                    totalTime = totalTimeText
                elif cookTime == "---" and prepTime != "---":
                    totalTime = prepTime
                elif cookTime != "---" and prepTime != "---":
                    totalTime = str(int(''.join(filter(str.isdigit, prepTime))) + int(''.join(filter(str.isdigit, cookTime)))) + " mins"
                
                # Servings:  
                servings = self.getSoupText(soup.find("div", {"class":"wprm-entry-servings"})).replace("Servings", "").split("\n")[0]
                
                # Nutrition Details:
                nutritionDetailSoup = soup.find_all("span", {"class":"wprm-nutrition-label-text-nutrition-container"})
                nutrition = {'calories': '---', 'carbs': '---', 'protein': '---', 'fat': '---'}
                
                if nutritionDetailSoup is not None:
                    for span in nutritionDetailSoup:
                        nutritionLabel = span.find("span", class_="wprm-nutrition-label-text-nutrition-label")
                        nutritionValue = span.find("span", class_="wprm-nutrition-label-text-nutrition-value")
                        nutritionUnit = span.find("span", class_="wprm-nutrition-label-text-nutrition-unit")
                        nutritionDaily = span.find("span", class_="wprm-nutrition-label-text-nutrition-daily")
        
                        nutritionName = self.getSoupText(nutritionLabel).lower().replace(":","")

                        if nutritionName in ["calories", "carbohydrates", "fat", "protein"]:
                            if nutritionName == "carbohydrates":
                                nutritionName = "carbs"
                                
                            nutrition[nutritionName] = self.getSoupText(nutritionValue) + \
                                self.getSoupText(nutritionUnit).replace("---","") + \
                                self.getSoupText(nutritionDaily).replace("---","")
                
                stats = {"nutrition":nutrition, 'totalTime': totalTime, 'servings': servings}
                
                # for recipetineats.com, parse soup for Ingredients
                ingredientList = []
                ingredients = soup.find_all("ul",class_="wprm-recipe-ingredients")
                for ingredientGroup in ingredients:
                    for ingredient in ingredientGroup.find_all("li"):
                        # Ingredient Amount
                        amount = ingredient.find("span", class_="wprm-recipe-ingredient-amount")
                    
                        if amount is not None:
                            amount = amount.text.strip()
                        else:
                            amount = ""
                            
                        # Ingredient Unit
                        unit = ingredient.find("span", class_="wprm-recipe-ingredient-unit")
                        
                        if unit is not None:
                            unit = unit.text.strip()
                        else:
                            unit = ""
                            
                        # Ingredient Name
                        name = ingredient.find("span", class_="wprm-recipe-ingredient-name")

                        if name is not None:
                            name = name.text.strip()

                        fullIngredient = (amount + " " + unit + " " + name).replace("  ", " ")
                        
                        ingredientList.append(fullIngredient)

                # for recipetineats.com, parse soup for Directions
                directionsList = []
                directions = soup.find_all("ul", class_="wprm-recipe-instructions")

                for directionGroup in directions:
                    for direction in directionGroup:
                        directionsList.append(direction.text.strip())

                tempDict = {}
                tempDict["title"] = title
                tempDict["url"] = url
                tempDict["ingredients"] = ingredientList
                tempDict["directions"] = directionsList
                tempDict["dataSource"] = "www.recipetineats.com"
                tempDict["stats"] = stats

            # print(tempDict)


            try:
                self.collection.insert_one(tempDict)
                print("Inserted: " + tempDict["title"])
            except:
                print("Error inserting: " + tempDict["title"])
                
            # DFS to visit all relevant links on the recipe page
            tagSoup = fullSoup.find('a', {"rel":"prev"})
               
            if tagSoup != None:
                tag = tagSoup['href']
                if tag == "https://www.recipetineats.com/chef-wanted-to-cook-with-me/":
                    tag = "https://www.recipetineats.com/thai-black-sticky-rice-pudding/"
                if url == "https://www.recipetineats.com/hot-cross-buns-recipe/" and tag == "https://www.recipetineats.com/my-shout-fundraiser-meals-frontline-workers-covid-19-coronavirus-sydney/":
                    tag = "https://www.recipetineats.com/chocolate-cake/"
                    
                if "https://www.recipetineats.com/" in tag and tag not in self.visited:
                    self.visited.append(tag)
                    self.queue.append(tag)
                    self.links.append(tag)

    # To reduce the errors thrown, safe way to grab the text
    def getSoupText(self, souped):
        return souped.text.strip() if souped is not None else "---"
        
    def get_links(self):
        return self.links

    def get_visited(self):
        return self.visited

    def get_queue(self):
        return self.queue


if __name__ == "__main__":
    crawler = Crawler("https://www.recipetineats.com/truly-crispy-oven-baked-buffalo-wings-my-wings-cookbook/","recipes-master","recipetineats-recipes")
    crawler.crawl()
