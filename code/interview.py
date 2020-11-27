import cbf
import recsys
import util
import presentation

ICM, ICM_link = recsys.setup_ICM("../resources/sfw_games.json", "../resources/most_popular_games_steam.json")
URM = recsys.create_URM("../resources/most_popular_games_steam.json")

userID_to_index, itemID_to_index, featureID_to_index = recsys.create_mappings(ICM, URM)
recsys.apply_mappings(ICM, URM, userID_to_index, itemID_to_index, featureID_to_index)

ICM_all, URM_all = recsys.convert_to_sparse(ICM, URM, userID_to_index, itemID_to_index, featureID_to_index)

recommender = cbf.Recommender(URM_all, ICM_all, ICM_link, itemID_to_index)
recommender.fit(shrink=10, topK=50)
games = recommender.recommend(0)

recommendations = []

presentation = presentation.Presentation(ICM, URM, itemID_to_index, featureID_to_index, mode="transparency")
for game in games:
    presentation.present_result(game, ICM_link)