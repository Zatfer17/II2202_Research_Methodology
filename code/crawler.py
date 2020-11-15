import pandas as pd
import requests
from bs4 import BeautifulSoup

soup = BeautifulSoup(open("resources/most_sold_games_steam.html"), 'html.parser')
rows = soup.find_all(href=True)

data_set = []
tags_set = []
i=0
for row in rows:
    print("Crawled " + str(i) + " out of " + str(len(rows)))
    if (len(row.contents) == 7):
        link = row.attrs.get("href")
        game = requests.get(link).content
        soup = BeautifulSoup(game, 'html.parser')
        try:
            name = soup.findAll("div", {"class": "apphub_AppName"}).pop().text
            tags = ' '.join(soup.findAll("div", {"class": "glance_tags popular_tags"}).pop().text.split()).split(" ")[:-1]
            for tag in tags:
                tags_set.append([tag, 1])
            data_set.append([name, link, tags])
            i += 1
            if i == 20:
                break
        except IndexError:
            continue

data_df = pd.DataFrame(data_set, columns = ["name", "link", "tags"])
tags_df = pd.DataFrame(tags_set, columns = ["tag", "popularity"])
print(data_df.head())
aggregation_functions = {'tag': 'first', 'popularity': 'sum'}
tags_df = tags_df.groupby('tag', as_index=False).aggregate(aggregation_functions)
print(tags_df)

