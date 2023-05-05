import urllib
import urllib.request
from bs4 import BeautifulSoup
from pymongo import MongoClient


class Crawler:
    def __init__(self, url, db, collection):
        cluster = MongoClient("mongodb://localhost:27017/")  # NOTE: check validity/ generalizable
        self.db = cluster[db]
        self.collection = self.db[collection]

        self.url = url
        self.links = []
        self.visited = []
        self.queue = []
        self.queue.append(self.url)
        self.visited.append(self.url)
        self.crawl()

    def parse_tags(self, soup):
        # ------------
        # >>> Tags <<<
        # ------------
        # Find tags that can help with querying
        tag_soup = soup.find("div", class_="loc tag-nav-content")
        tags = tag_soup.find_all("li", class_="link-list__item tag-nav__item")
        tag_list = {}
        for i in range(len(tags)):
            tag_list[i] = tags[i].text.strip()
        # print(tag_list)
        return tag_list

    def parse_description(self, soup):
        # -------------------
        # >>> Description <<<
        # -------------------
        return soup.find("meta", attrs={"name": "description"})["content"]  # Tested
        # print(description)

    def parse_title(self, soup):
        # -------------
        # >>> Title <<<
        # -------------
        # SimplyRecipes always has Recipe in the tile, remove once obtained
        title = soup.find("title")
        if title:
            return title.text.strip().replace("Recipe", "")
            # print(title)
        else:
            return "---"

    def parse_stats(self, soup):
        # -------------
        # >>> Stats <<<
        # -------------
        # Find all times present in the recipe description
        recipe_stats = {"totalTime": "---", "servings": "---"}
        stat_bucket = soup.find("div", class_="comp project-meta")
        if stat_bucket:
            stat_keys = stat_bucket.find_all("span", class_="meta-text__label")
            stat_vals = stat_bucket.find_all("span", class_="meta-text__data")
            if stat_keys and stat_vals:
                for i in range(len(stat_keys)):
                    temp_stat = stat_keys[i].text.strip()
                    if temp_stat == "Total Time":
                        # exclude random character found during testing
                        recipe_stats["totalTime"] = str(stat_vals[i].text.strip()).replace("\n", " ")
                    if temp_stat == "Servings":
                        # exclude random character found during testing
                        recipe_stats["servings"] = str(stat_vals[i].text.strip()).replace("\n", " ")

        # Find Nutritional Info
        nutri_soup = soup.find_all("td", class_="nutrition-info__table--cell")
        nutrition = {"calories": "---", "fat": "---", "carbs": "---", "protein": "---"}
        if nutri_soup:
            i = 0
            while i < len(nutri_soup) - 1:
                # strBuilder = str(nutri_soup[i].text.strip()) + ' ' + str(nutri_soup[i + 1].text.strip())
                # nutrition.append(strBuilder)
                nutrition[str(nutri_soup[i + 1].text.strip()).lower()] = nutri_soup[i].text.strip()
                i = i + 2
            # print(nutrition)
        recipe_stats["nutrition"] = nutrition
        # print(recipe_stats)
        return recipe_stats

    def parse_ingredients(self, soup):
        # -------------------
        # >>> Ingredients <<<
        # -------------------
        # Obtain all ingredients
        ing_list = []
        ingredient_list = soup.find("div", id="structured-ingredients_1-0")
        if ingredient_list:
            ingredients = ingredient_list.find_all("li", class_="structured-ingredients__list-item")
            if ingredients:
                for i in range(len(ingredients)):
                    # exclude random character found during testing
                    ing_list.append(ingredients[i].text.strip().replace("\xa0", ' '))
                # print(ing_list)
        elif soup.find("section", id="section--ingredients_1-0"):
            ingredient_list = soup.find("section", id="section--ingredients_1-0")
            ingredients = \
                ingredient_list.find_all("li", class_="simple-list__item js-checkbox-trigger ingredient text-passage")
            if ingredients:
                for i in range(len(ingredients)):
                    # exclude random character found during testing
                    ing_list.append(ingredients[i].text.strip().replace("\xa0", ' '))
                # print(ing_list)
            else:
                ing_list = ["---"]
        else:
            ing_list = ["---"]
        return ing_list

    def parse_directions(self, soup):
        # ------------------
        # >>> Directions <<<
        # ------------------
        # Find Directions
        dir_list = []
        dir_soup = soup.find("section", id="section--instructions_1-0")
        if dir_soup:
            dir_head = dir_soup.find_all("span", class_="mntl-sc-block-subheading__text")
            dir_body = dir_soup.find_all("p", class_="comp mntl-sc-block mntl-sc-block-html")
            if dir_head and dir_body:
                if len(dir_head) == len(dir_body):
                    for i in range(len(dir_head)):
                        temp_dir = str(dir_head[i].text.strip()) + ' ' + str(dir_body[i].text.strip())
                        temp_dir = temp_dir.replace("\xa0", " ")
                        dir_list.append(temp_dir)
                    # print(dir_list)
                else:
                    for i in range(len(dir_head)):
                        temp_dir = str(dir_head[i].text.strip())
                        temp_dir = temp_dir.replace("\xa0", " ")
                        dir_list.append(temp_dir)
                    # print(dir_list)
            else:
                dir_list = ["---"]
        else:
            dir_list = ["---"]
        return dir_list

    def parse_page(self, url, soup):
        # print(url)
        temp_dict = {"url": url,
                     "title": self.parse_title(soup),
                     "stats": self.parse_stats(soup),
                     "dataSource": "SimplyRecipes",
                     "ingredients": self.parse_ingredients(soup),
                     "directions": self.parse_directions(soup)}

        # print(temp_dict)

        try:
            self.collection.insert_one(temp_dict)
            print("Inserted: " + temp_dict["title"])
        except:
            print("Error inserting: " + temp_dict["title"])

    def crawl(self):
        while self.queue:
            url = self.queue.pop(0)
            try:
                with urllib.request.urlopen(url) as response:
                    htmltext = response.read()
            except:
                print("Error: " + url)
                break
            soup = BeautifulSoup(htmltext, features="html.parser")

            is_recipe = soup.find("meta", attrs={"data-recipe-id": True})
            # print(is_recipe)
            # there is no specific subdirectory, pages that are recipes have ID
            if is_recipe is not None:
                self.parse_page(url, soup)

            # DFS to visit all relevant links on the recipe page
            for tag in soup.findAll('a', href=True):
                if "https://www.simplyrecipes.com/" in tag['href'] and tag['href'] not in self.visited:
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
    crawler = Crawler("https://www.simplyrecipes.com/seafood-congee-tang-jai-jook-recipe-7089691", "recipes-master",
                      "simplyrecipes-recipes")
    crawler.crawl()
