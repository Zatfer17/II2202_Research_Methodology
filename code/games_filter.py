import json

f = open("./resources/games.json")
games = json.load(f)

banned_tags = ["Sexual Content", "Nudity", "Mature", "Dating Sim", "Gore", "NSFW", "Hentai", "Cute", "Otome"]

########################################################################################################################

#########################
#    CODE COMPARISON    #
#########################

########################################################################################################################

###################
#    VERSION 1    #
###################

filtered_games = filter(lambda game: not any(tag in game["tags"] for tag in banned_tags), games)
with open('./resources/sfw_games.json', 'w') as outfile:
        json.dump(list(filtered_games), outfile, indent=4)

########################################################################################################################

###################
#    VERSION 2    #
###################

def purge_nsfw_content():
    new_data = []
    with open('../resources/games.json') as json_file:
        data = json.load(json_file)
        for d in data:
            nsfw = False
            for t in banned_tags:
                if t in d["tags"]:
                    nsfw = True
                    break
            if not nsfw:
                new_data.append(d)
    with open('../resources/sfw_games.json', 'w') as outfile:
        json.dump(new_data, outfile)

########################################################################################################################

# CHI TRA ME E POTTER HA SCRITTO LA 1 E CHI LA 2? 