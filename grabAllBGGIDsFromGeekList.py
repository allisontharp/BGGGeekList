from funcs import *
import urllib.request
from boardgamegeek import BGGClient
from operator import itemgetter

bgg = BGGClient()
geeklistid = 231577
numPages = 2

baseUrl = "https://boardgamegeek.com/geeklist/{geeklistid}".format(geeklistid=geeklistid)

pg = 1
gamesAndTimes = []

for i in range(1, numPages+1):
    print(i)
    url = baseUrl + "/page/{pg}".format(pg=i)
    result = urllib.request.urlopen(url)
    soup = BeautifulSoup(result, "html.parser")
    links = soup.find_all('a', href=True)
    for a in links:
        if '/boardgame/' in a['href']:
            try:
                if a.parent.parent['class'][0] == 'geeklist_item_title':
                    bggid = find_between(a['href'], '/boardgame/', '/')
                    print(bggid)
                    g = bgg.game(game_id=bggid)
                    g = g.name
                    avgPlayTime = getAvgPlayTime(bggid)
                    avgPlayTime = avgPlayTime[0][0]
                    gamesAndTimes.append([g, avgPlayTime])
            except KeyError:
                pass

sortedList = sorted(gamesAndTimes,key=itemgetter(1))
for g in sortedList:
    print(g)
print("Done!")

