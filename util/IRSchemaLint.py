# standard schema for ReciPy, don't modify this dict
a= {'url': 'https://www.simplyrecipes.com/seafood-congee-tang-jai-jook-recipe-7089691', 'title': 'Seafood Congee (Tang Jai Jook) ', 'stats': {'totalTime': '2 hrs', 'servings': '4 to 6 servings', 'nutrition': {'calories': '286', 'fat': '15g', 'carbs': '21g', 'protein': '16g'}}, 'dataSource': 'SimplyRecipes', 'ingredients': ['1/2 pound lean boneless pork shoulder, very thinly sliced', '1 tablespoon Shaoxing wine', '1 tablespoon kosher salt, plus more to taste', '2 teaspoons ground ginger', '2 teaspoons freshly ground white pepper', '1 cup jasmine rice', '10 cups water', '1/2 pound calamari strips', '1 (2-inch) piece ginger, peeled and very thinly sliced', '3 green onions, thinly sliced', '1/4 cup roasted red skin peanuts, lightly salted', '2 youtiao, to serve, optional'], 'directions': ['Season the pork: Add the sliced pork, Shaoxing wine, salt, ground ginger, and white pepper to a medium bowl and stir to combine. Cover and refrigerate until the congee is ready.', 'Prepare the rice: Wash and rinse the rice with cold water until the water runs clear. Strain.', 'Cook the congee: Add the water to a pot over high heat and bring to a rolling boil. Lower the heat to medium and add the rinsed and drained rice. With a spatula or wooden spoon, give the rice a gentle stir so it is evenly distributed in the pot.', 'Add the pork and seafood and cook: Place the lid slightly ajar on top of the pot and adjust the heat to maintain a low simmer. Cook the congee, without stirring, until the outline of the grains of rice is no longer visible, 1 1/2 hours.', 'Garnish and serve: Remove the lid and gently stir the congee. If desired, you can add additional water for a looser consistency.']}
# change b dict to check your schema
b ={'ur': 'https://www.allrecipes.com/recipe/8525671/baked-buttermilk-chicken-tenders/', 'title': 'Baked Buttermilk Chicken Tenders', 'stats': {'totalTime': '2 hrs 30 mins', 'servings': '4', 'nutrition': {'calories': '316', 'fat': '8g', 'carbs': '24g', 'potein': '34g'}}, 'dataSource': 'allrecipes', 'ingredients': ['1 pound chicken tenderloins', '½ cup buttermilk', '¼ teaspoon salt', '⅛ teaspoon cayenne pepper'], 'directions': ['Combine chicken tenders, buttermilk, salt, and cayenne in a large resealable plastic bag. Refrigerate for at least 2 hours.', 'Preheat the oven to 375 degrees F (190 degrees C). Line a baking sheet with aluminum foil for easy cleanup.', 'Combine flour, paprika, and salt in a shallow bowl. Whisk egg and 2 tablespoons buttermilk in another bowl. Mix breadcrumbs, Parmesan cheese, seafood seasoning, and garlic powder in a third bowl.', 'Drain chicken and discard marinade. Dredge chicken in flour mixture, shaking off the excess. Dip into egg mixture, and turn in breadcrumb mixture, pressing down to make sure the breading adheres to the chicken tender.', 'Place the crumb-coated tenders on the prepared baking sheet, giving each side a good spray of olive oil.', 'Bake in the preheated oven until chicken is no longer pink in the center and the juices run clear, 15 to 18 minutes depending on thickness, flipping halfway through. An instant-read thermometer inserted into the center should read at least 165 degrees F (74 degrees C).']}



c1 = a.keys()==b.keys()
c2 = a['stats'].keys()==b['stats'].keys()
c3 = a['stats']["nutrition"].keys()==b['stats']["nutrition"].keys()


# If all the keys match, print "Valid", else print the keys that don't match and the reason, i.e. "Parent Keys Don't match" etc.
if(c1 and c2 and c3):
    print("Valid")
else:
    if not c1:
        print("Parent Keys Don't match")
    if not c2:
        print("Stat Keys Don't match")
    if not c3:
        print("Nutrition Keys Don't match")
    
