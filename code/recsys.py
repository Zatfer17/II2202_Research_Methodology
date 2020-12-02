import pandas as pd
import numpy as np
import scipy.sparse as sps
import random
import json

def setup_ICM(path1, ICM_append):
    df1 = pd.read_json(path1)
    #df2 = pd.read_json(path2)
    df = df1.append(ICM_append, ignore_index = True)

    s = df.apply(lambda x: pd.Series(x['tags']), axis=1).stack().reset_index(level=1, drop=True)
    s.name = 'tags'
    ICM = df.drop('tags', axis=1).join(s)

    ICM['tags'] = pd.Series(ICM['tags'], dtype=object)
    ICM_link = ICM[["name", "link"]]
    ICM.rename(columns={"name": "ItemID", "tags": "FeatureID"}, inplace=True)
    ICM.drop(columns=["link"], inplace=True)

    return ICM, ICM_link

def get_k_most_popular_tags(path, k1, k2, num=15):
    banned_tags = ["Sexual Content", "Nudity", "Mature", "Dating Sim", "Gore", "NSFW", "Hentai", "Cute", "Otome"]
    with open(path) as json_file:
        types = json.load(json_file)["type"]
    with open(path) as json_file:
        genres = json.load(json_file)["genre"]
    k_types = []
    k_genres = []
    c1 = 0
    c2 = 0
    i1 = 0
    i2 = 0
    while c1 < k1:
        if types[i1][0] not in banned_tags:
            k_types.append(types[i1][0])
            c1 += 1
        i1 += 1

    while c2 < k2:
        if genres[i2][0] not in banned_tags:
            k_genres.append(genres[i2][0])
            c2 += 1
        i2 += 1
    #print(k_types)

    combos = []
    for i in range(num):
        copy_types = k_types.copy()
        copy_genres = k_genres.copy()
        random.shuffle(copy_types)
        random.shuffle(copy_genres)
        t1 = copy_types.pop()
        t2 = copy_genres.pop()
        while((t1, t2) in combos or (t2, t1) in combos):
            copy_types = k_types.copy()
            copy_genres = k_genres.copy()
            random.shuffle(copy_types)
            random.shuffle(copy_genres)
            t1 = copy_types.pop()
            t2 = copy_genres.pop()
        combos.append([t1, t2])

    liked_tags = {}
    disliked_tags = {}
    for i1, c1 in enumerate(combos):
        rating = input("Do you like this genres: " + str(c1) + " ? ")
        while rating not in ["y", "n", "d"]:
            rating = input("Do you like this genres: " + str(c1) + " ? ")
        if rating == "y":
            for t in c1:
                if t not in liked_tags:
                    liked_tags[t] = 0
                liked_tags[t] += 1
        elif rating == "n":
            for t in c1:
                if t not in disliked_tags:
                    disliked_tags[t] = 0
                disliked_tags[t] += 1

    flattened = [item for sublist in combos for item in sublist]
    flattened = list(set(flattened))
    num_games = int(len(flattened) / 5)

    ratings = []
    data_set = []

    ratings.append([0, "game", 1.0])
    data_set.append(["game", None, flattened])

    ICM_to_append = pd.DataFrame(data=data_set,columns=["name", "link", "tags"])
    URM = pd.DataFrame(ratings, columns=["UserID", "ItemID", "Interaction"])

    return ICM_to_append, URM, liked_tags, disliked_tags

def create_URM(path):

    df = pd.read_json(path)
    ratings = []

    indexes = list(range(df.shape[0]))
    to_ask = []

    for i in range(10):
        p = random.choice(indexes)
        indexes.remove(p)
        to_ask.append(p)

    #"""
    print()
    for i in to_ask:
        rating = input("Do you like this game: \"" + str(df.at[i, 'name']) + "\" (" + df.at[i, "link"] + ") ? y (Yes), n (No) or d (Don't know): ")
        while rating not in ["y", "n", "d"]:
            rating = input("Do you like this game: \"" + str(df.at[i, 'name']) + "\" (" + df.at[i, "link"] + ") ? y (Yes), n (No) or d (Don't know): ")
        if rating == "y":
            ratings.append([0, df.at[i, "name"], 5.0])
        elif rating == "n":
            ratings.append([0, df.at[i, "name"], -5.0])
    print()
    URM = pd.DataFrame(ratings, columns=["UserID", "ItemID", "Interaction"])
    #"""
    #URM = pd.DataFrame(np.array([[0, "Destiny 2", 5.0], [0, "Motorsport Manager", -5.0]]),
                    #columns=["UserID", "ItemID", "Interaction"])
    #URM["Interaction"] = URM["Interaction"].astype(np.float)

    return URM

def create_mappings(ICM, URM):
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

    return user_original_ID_to_index_dict, item_original_ID_to_index_dict, feature_original_ID_to_index_dict

def apply_mappings(ICM, URM, userID_to_index, itemID_to_index, featureID_to_index):

    URM["UserID"] = [userID_to_index[user_original] for user_original in URM["UserID"].values]
    URM["ItemID"] = [itemID_to_index[item_original] for item_original in URM["ItemID"].values]

    ICM["ItemID"] = [itemID_to_index[item_original] for item_original in ICM["ItemID"].values]
    ICM["FeatureID"] = [featureID_to_index[feature_original] for feature_original in ICM["FeatureID"].values]

def convert_to_sparse(ICM, URM, userID_to_index, itemID_to_index, featureID_to_index):

    n_users = len(userID_to_index)
    n_items = len(itemID_to_index)
    n_features = len(featureID_to_index)

    ICM_all = sps.csr_matrix((np.ones(len(ICM["ItemID"].values)), (ICM["ItemID"].values, ICM["FeatureID"].values)),
                             shape=(n_items, n_features))
    # ICM_all.data = np.ones_like(ICM_all.data)
    # ICM_all = sps.csr_matrix(ICM_all)

    URM_all = sps.csr_matrix((URM["Interaction"].values, (URM["UserID"].values, URM["ItemID"].values)),
                             shape=(n_users, n_items))

    return ICM_all, URM_all


