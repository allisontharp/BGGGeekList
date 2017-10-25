from itertools import groupby
from operator import itemgetter
import urllib.request, urllib.parse, time, sys
from http.cookiejar import CookieJar
from xml.dom.minidom import parse
from bs4 import BeautifulSoup
from boardgamegeek import BGGClient


def find_between(h, first, last):
    try:
        start = h.index(first) + len(first)
        end = h.index(last, start)
        return h[start:end]
    except ValueError:
        return ""


def getAvgPlayTime(bggid):
    url = "https://boardgamegeek.com/xmlapi2/plays?id={bggid}&page=".format(bggid=bggid)
    time.sleep(2)
    dom = parse(urllib.request.urlopen(url))
    nodes = dom.getElementsByTagName('play')
    pg = 1
    playData = []
    while nodes and pg < 5:
        nURL = url + str(pg)
        time.sleep(2)
        dom = parse(urllib.request.urlopen(nURL))
        nodes = dom.getElementsByTagName('play')
        for i in range(len(nodes)):
            count = 0
            nNode = nodes.item(i)
            if nNode.nodeType == 1:  # it is an element_node
                dur = int(nNode.attributes['length'].value)
                if dur > 0:
                    players = nNode.getElementsByTagName('player')
                    for items in players:
                        try:
                            items.attributes['name'].value
                            count += 1
                        except IndexError:
                            pass
                    if count > 0:
                        playData.append([dur, count])

        pg += 1
    playData = sorted(playData, key=lambda tup: tup[1])
    if playData:
        avgPlayTime = []

        playDur, counter, numPlayers = 0, 0, 0
        for plays in playData:
            playDur += plays[0]
            numPlayers += plays[1]
            counter += 1
        avgPlayTime.append([round(playDur * 1.0 / counter, 2), round(numPlayers * 1.0 / counter, 2), counter])

        for groupByID, rows in groupby(playData, key=itemgetter(1)):
            playDur, counter = 0, 0
            for row in rows:
                playDur += row[0]
                counter += 1
            avgPlayTime.append([round(playDur * 1.0 / counter, 2), groupByID, counter])
    else:
        avgPlayTime = [[-1, -1, -1]]

    return avgPlayTime


def getPlays(bggid):
    plays = -1
    url = 'https://boardgamegeek.com/boardgame/'
    url += str(bggid)
    try:
        result = urllib.request.urlopen(url)
    except:
        e = sys.exc_info()[0]
        print("The following URL couldn't be reached")
        print(bggid, url)
        raise ValueError('Could not reach URL')

    soup = BeautifulSoup(result, "html.parser")
    scriptSection = soup.script.text
    scriptArray = scriptSection.split(",")
    for i in range(0, len(scriptArray)):

        if scriptArray[i].startswith('\"numplays\"'):
            plays = scriptArray[i].split(":")
            plays = int(plays[1].strip('"'))

            if plays > 2000000:
                plays = -1
    return plays


def add_geeklist_item(user, passwd, glid, gliid, giid, comment):
    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent', 'RedditTesting')]
    urllib.request.install_opener(opener)

    login_url = "https://www.boardgamegeek.com/login"
    login_data = {'username': user, 'password': passwd, 'B1': 'Submit'}
    data = urllib.parse.urlencode(login_data).encode('utf-8')
    loginrequest = urllib.request.Request(login_url)
    urllib.request.urlopen(loginrequest, data=data)
    response = [None]
    req = urllib.request.Request("https://boardgamegeek.com/geekcomment.php ")
    req.add_header("X-Requested-With", "XMLHttpRequest")
    req.add_header("Accept", "text/javascript, text/html, application/xml, text/xml, */*")
    req.add_header("Content-type", "application/x-www-form-urlencoded; charset=utf-8")
    req.add_header("Accept-Language", "en-US")
    req.add_header("Accept-Encoding", "gzip, deflate")
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko")
    req.add_header("Connection", "Keep-Alive")
    req.add_header("Pragma", "no-cache")
    body = dict(action="save", objectid=gliid, objecttype="listitem", geek_link_select_1="",body=comment, ajax=1)
    body = urllib.parse.urlencode(body).encode('utf-8')
    response[0] = urllib.request.urlopen(req, data=body)

def defineCommentTotalPlays(bggid):
    comment = ''
    startTags = '[floatleft][floatleft][floatleft]'
    endTags = '[/floatleft][/floatleft][/floatleft]'
    totPlays = getPlays(bggid)
    avgPlayTime = getAvgPlayTime(bggid)
    comment += "[b]Total Plays: {tp}[/b]".format(tp=totPlays)
    comment += '\n'

    commentPlayerCount = startTags + '\n' + '[u]Player Count[/u]'
    commentAvgPlayTime = endTags + '\n' + startTags + '[u]Average Play Time (minutes)[/u]'
    commentTotalPlays = endTags + startTags + '[u]Total Plays[/u]'
    for playerCount in avgPlayTime:
        commentPlayerCount += "\n"
        commentAvgPlayTime += "\n"
        commentTotalPlays += "\n"

        commentPlayerCount += str(playerCount[1])
        commentAvgPlayTime += str(playerCount[0])
        commentTotalPlays += str(playerCount[2])

    comment += commentPlayerCount + commentAvgPlayTime + commentTotalPlays + '\n' + endTags
    return comment


def defineCommentMechanics(bggid):
    bgg = BGGClient()
    comment = ''
    game = bgg.game(game_id=bggid)
    mechanics = game.mechanics
    categories = game.categories

    comment += '[b]Mechanics:[/b]\n'
    comment +='\n'.join(mechanics)

    comment +='\n[b]Categories:[/b]\n'
    comment +='\n'.join(categories)

    return comment

