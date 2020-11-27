from external_libraries.Base.Similarity.Compute_Similarity_Python import Compute_Similarity_Python
import numpy as np
import util
import requests
from bs4 import BeautifulSoup

class Recommender(object):

    def __init__(self, URM, ICM, ICM_link, itemID_to_index):
        self.URM = URM
        self.ICM = ICM
        self.ICM_link = ICM_link
        self.itemID_to_index = itemID_to_index

    def fit(self, topK=50, shrink=100, normalize=True, similarity="cosine"):
        similarity_object = Compute_Similarity_Python(self.ICM.T, shrink=shrink,
                                                      topK=topK, normalize=normalize,
                                                      similarity=similarity)
        self.W_sparse = similarity_object.compute_similarity()

    def recommend(self, user_id, exclude_seen=True):
        user_profile = self.URM[user_id]
        scores = user_profile.dot(self.W_sparse).toarray().ravel()

        if exclude_seen:
            scores = self.filter_seen(user_id, scores)
        ranking = scores.argsort()[::-1]

        already_known = "y"
        while already_known == "y":
            for recommended in ranking:

                name = util.get_key(self.itemID_to_index, recommended)
                link = self.ICM_link[self.ICM_link["name"] == name]["link"].iloc[0]
                website = requests.get(link).content
                soup = BeautifulSoup(website, 'html.parser')

                dlc = False
                tags = soup.findAll("div", {"class": "game_area_details_specs"})
                for t in tags:
                    if "https://steamstore-a.akamaihd.net/public/images/v6/ico/ico_dlc.png" in str(t):
                        dlc = True

                if not dlc:
                    print("Recommended game: " + str(name))
                    already_known = input("Do you already know this game? y or n: ")
                    if already_known == "y":
                        print("Suggesting a new one...")
                        print()
                    else:
                        break

        return [recommended]

    def filter_seen(self, user_id, scores):
        start_pos = self.URM.indptr[user_id]
        end_pos = self.URM.indptr[user_id + 1]
        user_profile = self.URM.indices[start_pos:end_pos]
        scores[user_profile] = -np.inf
        return scores