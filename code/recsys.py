from Base.Similarity.Compute_Similarity_Python import Compute_Similarity_Python
import pandas as pd
import numpy as np
import scipy.sparse as sps

def get_key(my_dict, val):
    for key, value in my_dict.items():
        if val == value:
            return key

class ItemKNNCBFRecommender(object):

    def __init__(self, URM, ICM):
        self.URM = URM
        self.ICM = ICM

    def fit(self, topK=50, shrink=100, normalize=True, similarity="cosine"):
        similarity_object = Compute_Similarity_Python(self.ICM.T, shrink=shrink,
                                                      topK=topK, normalize=normalize,
                                                      similarity=similarity)
        self.W_sparse = similarity_object.compute_similarity()

    def recommend(self, user_id, at=None, exclude_seen=True):
        user_profile = self.URM[user_id]
        scores = user_profile.dot(self.W_sparse).toarray().ravel()

        if exclude_seen:
            scores = self.filter_seen(user_id, scores)
        ranking = scores.argsort()[::-1]
        return ranking[:at]

    def filter_seen(self, user_id, scores):
        start_pos = self.URM.indptr[user_id]
        end_pos = self.URM.indptr[user_id + 1]
        user_profile = self.URM.indices[start_pos:end_pos]
        scores[user_profile] = -np.inf
        return scores

    def get_tags_map(self, user_id):
        print(self.URM[user_id])


df = pd.read_json("../resources/games.json")

s = df.apply(lambda x: pd.Series(x['tags']), axis=1).stack().reset_index(level=1, drop=True)
s.name = 'tags'
ICM = df.drop('tags', axis=1).join(s)
ICM['tags'] = pd.Series(ICM['tags'], dtype=object)
ICM.rename(columns={"name": "ItemID", "tags": "FeatureID"}, inplace=True)
ICM.drop(columns=["link"], inplace=True)

URM = pd.DataFrame(np.array([[0, "Football Manager 2021", 5.0], [0, "Motorsport Manager", 0.0]]),
                   columns=["UserID", "ItemID", "Interaction"])
URM["Interaction"] = URM["Interaction"].astype(np.float)

user_original_ID_to_index_dict = {}
for user_id in URM["UserID"].unique():
    user_original_ID_to_index_dict[user_id] = len(user_original_ID_to_index_dict)
item_original_ID_to_index_dict = {}
for item_id in URM["ItemID"].unique():
    item_original_ID_to_index_dict[item_id] = len(item_original_ID_to_index_dict)
for item_id in ICM["ItemID"].unique():
    if item_id not in item_original_ID_to_index_dict:
        item_original_ID_to_index_dict[item_id] = len(item_original_ID_to_index_dict)
feature_original_ID_to_index_dict = {}
for feature_id in ICM["FeatureID"].unique():
    feature_original_ID_to_index_dict[feature_id] = len(feature_original_ID_to_index_dict)

URM["UserID"] = [user_original_ID_to_index_dict[user_original] for user_original in URM["UserID"].values]
URM["ItemID"] = [item_original_ID_to_index_dict[item_original] for item_original in URM["ItemID"].values]

ICM["ItemID"] = [item_original_ID_to_index_dict[item_original] for item_original in ICM["ItemID"].values]
ICM["FeatureID"] = [feature_original_ID_to_index_dict[feature_original] for feature_original in ICM["FeatureID"].values]

n_users = len(user_original_ID_to_index_dict)
n_items = len(item_original_ID_to_index_dict)
n_features = len(feature_original_ID_to_index_dict)

URM_all = sps.csr_matrix((URM["Interaction"].values, (URM["UserID"].values, URM["ItemID"].values)),
                         shape=(n_users, n_items))
ICM_all = sps.csr_matrix((np.ones(len(ICM["ItemID"].values)), (ICM["ItemID"].values, ICM["FeatureID"].values)),
                         shape=(n_items, n_features))
ICM_all.data = np.ones_like(ICM_all.data)

ICM_all = sps.csr_matrix(ICM_all)

recommender = ItemKNNCBFRecommender(URM_all, ICM_all)
recommender.fit(shrink=10, topK=50)
games = recommender.recommend(0, at=5)

recommendations = []
for game in games:
    recommendations.append(get_key(item_original_ID_to_index_dict, game))

print(recommendations)

tags = {}

liked_games = URM.loc[(URM["UserID"]==0) & (URM["Interaction"]==5.0)]["ItemID"].values
liked_tags = ICM[ICM["ItemID"].isin(liked_games)]["FeatureID"].values
for tag in liked_tags:
    t = get_key(feature_original_ID_to_index_dict, tag)
    if t not in tags:
        tags[t] = 0
    tags[t] += 1

disliked_games = URM.loc[(URM["UserID"]==0) & (URM["Interaction"]==0.0)]["ItemID"].values
disliked_tags = ICM[ICM["ItemID"].isin(disliked_games)]["FeatureID"].values
for tag in disliked_tags:
    t = get_key(feature_original_ID_to_index_dict, tag)
    if t not in tags:
        tags[t] = 0
    tags[t] -= 1
print(tags)

import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

def color(word=None, font_size=None, position=None, orientation=None, font_path=None, random_state=None):
    if word not in tags:
        h = int(0)
        s = int(0)
        l = int(50)
    else:
        if tags[word] > 0:
            h = int(140)
            s = int(100)
            l = int(50)
        elif tags[word] == 0:
            h = int(0)
            s = int(0)
            l = int(50)
        else:
            h = int(0)
            s = int(100)
            l = int(50)
    return "hsl({}, {}%, {}%)".format(h, s, l)

for game in games:
    recommended_tags = ICM[ICM["ItemID"] == game]["FeatureID"].values
    recommended_tags_ID = []

    for r in recommended_tags:
        recommended_tags_ID.append(get_key(feature_original_ID_to_index_dict, r))

    file_content = ' '.join(recommended_tags_ID)
    wordcloud = WordCloud(stopwords=STOPWORDS,
                          background_color='white',
                          width=1200,
                          height=1000,
                          color_func=color
                          ).generate(file_content)

    plt.imshow(wordcloud)
    plt.axis('off')
    plt.show()
