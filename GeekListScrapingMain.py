from funcs import *
from bs4 import BeautifulSoup

username = 'mad4hatter'
pw = 'Hunter2'
numPages = 2

baseURL = "https://boardgamegeek.com/geeklist/231577/games-play-bggcon-2017/page/{pg}"

for i in range(1,numPages+1):
    url = baseURL.format(pg=i)
    print(url)
    result = urllib.request.urlopen(url)
    soup = BeautifulSoup(result, "html.parser")
    links = soup.find_all('a', href=True)
    for a in links:
        if '/boardgame/' in a['href']:
            try:
                if a.parent.parent['class'][0] == 'geeklist_item_title':
                    bggid = find_between(a['href'], '/boardgame/', '/')
                    geeklistItemID = find_between(a.parent.prettify(), '/item/', '#')

                    attrID = 'comments_{geeklistItemID}'.format(geeklistItemID=geeklistItemID)
                    cmts = soup.find_all('div', attrs={'id':attrID})[0].find_all('div', attrs={'class':'comment_ctrl'})[0]['data-ng-init']

                    if 'Total Plays:' in cmts:
                        print("Already added total plays to bggid: ", bggid, "GeeklistItemID:", geeklistItemID)
                    else:
                        print("Adding total plays comment to bggid ", bggid)
                        comment = defineCommentTotalPlays(bggid)
                        add_geeklist_item(username, pw, 231577, geeklistItemID, bggid, comment)

                    if 'Mechanics:' in cmts:
                        print("Already added Mechanics to bggid: ", bggid, "GeeklistItemID:", geeklistItemID)
                    else:
                        print("Adding Mechanics and Categories comment to bggid ", bggid)
                        comment = defineCommentMechanics(bggid)
                        add_geeklist_item(username, pw, 231577, geeklistItemID, bggid, comment)
            except KeyError:
                pass

print("Complete!")

