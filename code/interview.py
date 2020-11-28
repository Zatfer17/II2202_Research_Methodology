import cbf
import recsys
import util
import presentation
import json

sfw_games = "../resources/sfw_games.json"
most_popular_games_steam = "../resources/most_popular_games_steam.json"

ICM, ICM_link = recsys.setup_ICM(sfw_games, most_popular_games_steam)
URM = recsys.create_URM(most_popular_games_steam)

userID_to_index, itemID_to_index, featureID_to_index = recsys.create_mappings(ICM, URM)
recsys.apply_mappings(ICM, URM, userID_to_index, itemID_to_index, featureID_to_index)

ICM_all, URM_all = recsys.convert_to_sparse(ICM, URM, userID_to_index, itemID_to_index, featureID_to_index)

recommender = cbf.Recommender(URM_all, ICM_all, ICM_link, itemID_to_index)
recommender.fit(shrink=10, topK=50)

games = recommender.recommend(0)
recommendations = []
presentation = presentation.Presentation(ICM, URM, itemID_to_index, featureID_to_index)

presentation.present_result(games, ICM_link)
