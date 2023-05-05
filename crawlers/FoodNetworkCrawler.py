# Library imports
import urllib                 # URL handling module
import urllib.request         # opening and reading URLs
from bs4 import BeautifulSoup  # web scraper - HTML/XML
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

    # Accessor method to get the link
    def get_links(self):
        return self.links

    # Accessor method to get the visited page
    def get_visited(self):
        return self.visited

    # Accessor method to get the queue
    def get_queue(self):
        return self.queue

    def parsePage(self, url, soup):
        # Strip title from soup parse
        # print(url)

        # -------------------
        # >>> Title <<<
        # -------------------
        title = soup.find(
            class_="o-AssetTitle__a-HeadlineText").text.strip()
        if not title:
            print("Title error")
            return

        # -------------------
        # >>> Ingredients <<<
        # -------------------
        ingredientList = []
        ingredients = soup.find_all(class_="o-Ingredients__a-Ingredient")
        if ingredients:
            ingredientList = [ingredient.get_text()
                              for ingredient in ingredients]
            # Removes first "ingredient" being polluted with 'Deselect All'
            # and replaces string \xa0 with whitespace to not pollute the scraping process
            strippedIngredients = [ingredientList[i].strip() for i in range(len(ingredientList))]
            for i in range(len(strippedIngredients)):
                strippedIngredients[i] = strippedIngredients[i].replace("\xa0", " ")
                strippedIngredients[i] = strippedIngredients[i].replace("\u202f", " ")
            if "Deselect All" in strippedIngredients:
                strippedIngredients.remove("Deselect All")
            # print(strippedIngredients)
        else:
            print("No ingredients found")
            strippedIngredients = "---"
        
        # ------------------
        # >>> Directions <<<
        # ------------------
        directionsList = []
        directions = soup.find_all(class_="o-Method__m-Step")
        if directions:
            directionsList = [direction.get_text()
                              for direction in directions]
            strippedDirections = [directionsList[i].strip() for i in range(len(directionsList))]
            for i in range(len(strippedDirections)):
                strippedDirections[i] = strippedDirections[i].replace("\xa0", " ")
                strippedDirections[i] = strippedDirections[i].replace("\u202f", " ")
            if "Deselect All" in strippedDirections:
                strippedDirections.remove("Deselect All")
        else:
            print("No directions found")
            strippedDirections = "---"


        # ------------
        # >>> Time <<<
        # ------------

        # find the specific tag (span) with the time value
        # if you don't do this, you won't be able to get string
        times = soup.find("span", class_="o-RecipeInfo__a-Description m-RecipeInfo__a-Description--Total")
        if times:
            strippedTimes = times.text.strip()
        else:
            strippedTimes = "---"

        # --------------------
        # >>> Serving Size <<<
        # --------------------
        strippedServings = "---"
        serving_soup = soup.find("ul", class_="o-RecipeInfo__m-Yield")
        if serving_soup:
            serving_key = serving_soup.find_all("span", class_="o-RecipeInfo__a-Headline")
            serving_val = serving_soup.find_all("span", class_="o-RecipeInfo__a-Description")
            if serving_key and serving_val:
                for i in range(len(serving_key)):
                    if serving_key[i].text.strip() == "Yield:":
                        strippedServings = str(serving_val[i].text.strip())
                        break
                # print(strippedServings)

        # -----------------
        # >>> Nutrition <<<
        # -----------------
        cal = 0
        fat = 0
        carb = 0
        prot = 0
        nutrition = {}
        nutrition_soup = soup.find("dl", class_="m-NutritionTable__a-Content")
        if nutrition_soup:
            nutri_key = nutrition_soup.find_all("dt", class_="m-NutritionTable__a-Headline")
            nutri_val = nutrition_soup.find_all("dd", class_="m-NutritionTable__a-Description")
            if nutri_key and nutri_val:
                for i in range(len(nutri_key)):
                    curr_key = nutri_key[i].string
                    if curr_key == "Calories":
                        nutrition["calories"] = nutri_val[i].string
                        cal = 1
                    elif curr_key == "Total Fat":
                        nutrition["fat"] = nutri_val[i].string
                        fat = 1
                    elif curr_key == "Carbohydrates":
                        nutrition["carbs"] = nutri_val[i].string
                        carb = 1
                    elif curr_key == "Protein":
                        nutrition["protein"] = nutri_val[i].string
                        prot = 1
        if cal == 0:
            nutrition["calories"] = "---"
        if fat == 0:
            nutrition["fat"] = "---"
        if carb == 0:
            nutrition["carbs"] = "---"
        if prot == 0:
            nutrition["protein"] = "---"
        # print(nutrition)

        # nutritionList = soup.find_all(
        #     "dt", class_="m-NutritionTablea-Headline")
        # nutritionKeys = []
        # for nutrition in nutritionList:
        #     idx1 = str(nutrition).find(">")
        #     idx2 = str(nutrition).find("</")
        #     nutritionName = str(nutrition)[idx1+1:idx2]
        #     nutritionKeys.append(nutritionName)
        #
        # nutritionValList = soup.find_all(
        #     "dd", class_="m-NutritionTablea-Description")
        # nutritionVals = []
        # for nutrition in nutritionValList:
        #     idx1 = str(nutrition).find(">")
        #     idx2 = str(nutrition).find("</")
        #     nutritionName = str(nutrition)[idx1+1:idx2]
        #     nutritionVals.append(nutritionName)
        #
        # nutritionDict = dict(zip(nutritionKeys, nutritionVals))

        # Container to hold "stats" (e.g., times, serving sizes, nutrition)
        stat_dict = {}
        stat_dict = {
            "nutrition": nutrition,
            "totalTime": strippedTimes,
            "servings": strippedServings
        }

        # Container to hold recipe info
        tempDict = {}
        tempDict["title"] = title
        tempDict["url"] = url
        tempDict["dataSource"] = "FoodNetwork"
        tempDict["stats"] = stat_dict
        tempDict["ingredients"] = strippedIngredients
        tempDict["directions"] = strippedDirections

        # print(tempDict)
        try:
            self.collection.insert_one(tempDict)
            print("Inserted: " + title)
        except:
            print("Error inserting: " + title)

    # Crawl method which parses through specified subpages of FoodNetwork.com
    def crawl(self):

        # Crawl if and while possible
        while self.queue:
            url = self.queue.pop(0)
            try:
                with urllib.request.urlopen(url) as response:
                    htmltext = response.read()
            except:
                print("Error: " + url)
                break
            # BeautifulSoup parser
            soup = BeautifulSoup(htmltext, features="html.parser")

            if soup.find("body", class_="recipePage"):
                self.parsePage(url, soup)

            # DFS to visit all relevant links on the recipe page
            for tag in soup.findAll('a', href=True):
                if "https://www.foodnetwork.com/recipes/" in tag['href'] and tag['href'] not in self.visited:
                    self.visited.append(tag['href'])
                    self.queue.append(tag['href'])
                    self.links.append(tag['href'])


# Test Harness
if __name__ == "__main__":
    crawler = Crawler(
        "https://www.foodnetwork.com/recipes/food-network-kitchen/sweet-and-sour-couscous-stuffed-peppers-recipe-2121036","recipes-master","foodnetwork-recipes")
    crawler.crawl()
    # print(len(crawler.get_visited))   # causes error
