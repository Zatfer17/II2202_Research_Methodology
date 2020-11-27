import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import util
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from datetime import datetime
import os
from collections import Counter

class Presentation():

    def __init__(self, ICM, URM, itemID_to_index, featureID_to_index, mode="Transparency"):

        self.ICM = ICM
        self.URM = URM
        self.itemID_to_index = itemID_to_index
        self.featureID_to_index = featureID_to_index
        self.mode = mode

        self.tags = {}

        self.liked_tags = {}
        self.disliked_tags = {}
        self.indifferent_tags = {}

        liked_games = self.URM.loc[(URM["UserID"] == 0) & (self.URM["Interaction"] > 0.0)]["ItemID"].values
        liked_tags = self.ICM[self.ICM["ItemID"].isin(liked_games)]["FeatureID"].values
        for tag in liked_tags:
            t = util.get_key(self.featureID_to_index, tag)
            if t not in self.liked_tags:
                self.liked_tags[t] = 0.0
            self.liked_tags[t] += 1.0

        disliked_games = self.URM.loc[(self.URM["UserID"] == 0) & (self.URM["Interaction"] < 0.0)]["ItemID"].values
        disliked_tags = self.ICM[self.ICM["ItemID"].isin(disliked_games)]["FeatureID"].values
        for tag in disliked_tags:
            t = util.get_key(self.featureID_to_index, tag)
            if t not in self.disliked_tags:
                self.disliked_tags[t] = 0.0
            self.disliked_tags[t] += 1.0

    def color(self, word=None, font_size=None, position=None, orientation=None, font_path=None, random_state=None):
        if word in self.liked_tags and word in self.disliked_tags:
            if self.liked_tags[word] - self.disliked_tags[word] > 0.0:
                h = int(140)
                s = int(100)
                l = int(50)
            elif self.liked_tags[word] - self.disliked_tags[word] == 0.0:
                h = int(0)
                s = int(0)
                l = int(50)
            else:
                h = int(0)
                s = int(100)
                l = int(50)
        elif word in self.liked_tags and word not in self.disliked_tags:
            h = int(140)
            s = int(100)
            l = int(50)
        elif word not in self.liked_tags and word in self.disliked_tags:
            h = int(0)
            s = int(100)
            l = int(50)
        elif word in self.indifferent_tags:
            h = int(0)
            s = int(0)
            l = int(50)
        return "hsl({}, {}%, {}%)".format(h, s, l)

    def show_wordcloud(self, folder, game):
        recommended_tags = self.ICM[self.ICM["ItemID"] == game]["FeatureID"].values

        for r in recommended_tags:
            t = util.get_key(self.featureID_to_index, r)
            if t not in self.tags:
                self.indifferent_tags[t] = 1.0

        temp = Counter(self.liked_tags) + Counter(self.indifferent_tags)
        self.tags = temp + Counter(self.disliked_tags)

        wordcloud = WordCloud(stopwords=STOPWORDS,
                              background_color='white',
                              width=1200,
                              height=1000,
                              color_func=self.color
                              ).generate_from_frequencies(self.tags)

        name = util.get_key(self.itemID_to_index, game)
        plt.title(name, fontdict={
            'fontsize': 20})
        plt.imshow(wordcloud)
        plt.axis('off')
        #plt.show()
        plt.savefig("../outputs/" + folder + "/" + name + "_b.png")

    def present_result(self, game, ICM_link):
        name = util.get_key(self.itemID_to_index, game)
        link = ICM_link[ICM_link["name"] == name]["link"].iloc[0]
        website = requests.get(link).content
        soup = BeautifulSoup(website, 'html.parser')
        time = datetime.now()
        folder = time.strftime("%d_%m_%Y_%H:%M:%S")
        path = os.getcwd()
        destination_path = path.replace("code", "") + "outputs/" + folder
        os.mkdir(destination_path, 0o755)
        try:
            elem = str(list(soup.findAll("div", {"class": "game_header_image_ctn"}).pop().children)[1])
            img_link = elem.replace("<img class=\"game_header_image_full\" src=\"", "").replace("\"/>", "")
            response = requests.get(img_link)
            img = Image.open(BytesIO(response.content))
            img.convert('RGB').save("../outputs/" + folder + "/" + name + "_a.png", "PNG", optimize=True)

            """
            elem = list(soup.findAll("div", {"class": "game_area_description"}))
            for e in elem:
                if "About This Game" in str(e):
                    print(e)
            """
        except IndexError:
            print("Error")

        if self.mode == "transparency":
            self.show_wordcloud(folder, game)

        print(link)

