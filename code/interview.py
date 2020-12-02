import cbf
import recsys
import util
import presentation
import json

#recsys.get_k_most_popular_tags("../resources/tags_sorted.json", 50)

#"""
sfw_games = "../resources/sfw_games.json"
most_popular_games_steam = "../resources/most_popular_games_steam.json"
tags = "../resources/tags_sorted.json"

ICM_append, URM, liked_tags, disliked_tags = recsys.get_k_most_popular_tags(tags, 20)
ICM, ICM_link = recsys.setup_ICM(sfw_games, ICM_append)


userID_to_index, itemID_to_index, featureID_to_index = recsys.create_mappings(ICM, URM)
recsys.apply_mappings(ICM, URM, userID_to_index, itemID_to_index, featureID_to_index)

ICM_all, URM_all = recsys.convert_to_sparse(ICM, URM, userID_to_index, itemID_to_index, featureID_to_index)

recommender = cbf.Recommender(URM_all, ICM_all, ICM_link, itemID_to_index)
recommender.fit(shrink=10, topK=50)

games = recommender.recommend(0)
recommendations = []
presentation = presentation.Presentation(ICM, liked_tags, disliked_tags, itemID_to_index, featureID_to_index)

presentation.present_result(games, ICM_link)
#"""