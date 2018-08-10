import requests
import json
import os.path
import time
import math

from .player import Player
from .jsonutil import Jsonutil
from dateutil import parser
from datetime import timezone
from django.shortcuts import render
from django.http import HttpResponse

header = {
    "Authorization": "Bearer " + open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pkh.config"), "r").read() ,
    "Accept": "application/vnd.api+json"
}

MAX_MATCH_HISTORY = 10

# Create your views here.
def index(request):
    return render(request, 'pkh/index.html')

def matches(request):
    userValue = request.GET['user']

    # First search in the database whether or not the same player has been searched already.

    # for not pc-na, but can create a button with different regions and take input from that.
    # handle 404
    r = requests.get("https://api.pubg.com/shards/pc-na/players?filter[playerNames]=" + userValue, headers=header)

    if r.status_code != 200 :
        return render(request, 'pkh/nosuchplayer.html', {'userValue' : userValue})

    jsonData = r.json()
    listOfMatches = jsonData['data'][0]['relationships']['matches']['data']

    listOfMatchesJson = []
    listOfTelemetryMatchId = []
    for i in range(0, min(MAX_MATCH_HISTORY, len(listOfMatches))) :
        listOfMatchesJson.append(requests.get("https://api.pubg.com/shards/pc-na/matches/" + listOfMatches[i]['id'], headers= header).json())
        telemetryMatchId = listOfMatchesJson[i]['data']['relationships']['assets']['data'][0]['id']
        listOfTelemetryMatchId.append(telemetryMatchId)
        request.session[telemetryMatchId] = listOfMatchesJson[i]

    dateArray = []
    rankingArray = []
    killArray = []
    damageArray = []
    distanceArray = []

    for matchJson in listOfMatchesJson:
        for includedElement in matchJson["included"] :
            try:
                if includedElement['attributes']['stats']['name'] == userValue :
                    dateArray.append(parser.parse(matchJson["data"]["attributes"]["createdAt"]).replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%m/%d/%Y'))
                    rankingArray.append(includedElement['attributes']['stats']['winPlace'])
                    killArray.append(includedElement['attributes']['stats']['kills'])
                    damageArray.append(math.floor(includedElement['attributes']['stats']['damageDealt']))
                    # prob need to add rideDistance and swimDistance. If it's a string gotta parse it into long or int first.
                    distance = math.floor(float(includedElement['attributes']['stats']['walkDistance'] + includedElement['attributes']['stats']['rideDistance'] + includedElement['attributes']['stats']['swimDistance']))
                    distanceArray.append(distance)
                    break
            except Exception:
                continue
    zipList = zip(dateArray, rankingArray, killArray, damageArray, distanceArray, listOfTelemetryMatchId)
    return render(request, 'pkh/matches.html', {'zipList' : zipList})

def hierarchy(request, matchId):
    matchJson = request.session[matchId]

    for includedArr in matchJson['included']:
        try:
            if includedArr['id'] == matchId:
                # This is the telemetry URL with all data about the match.
                telemetryURL = includedArr['attributes']['URL']
        except Exception:
            # This means we're at a dictionary that we don't care about
            continue

    telemetryObject = requests.get(telemetryURL, headers = header).json()

    # get rid of this after.
    listOfKills = []
    # list of players already constructed. 
    players = []

    for telemetryEvent in telemetryObject :
        if telemetryEvent['_T'] == "LogPlayerKill":
            listOfKills.append(telemetryEvent)
            killerName = telemetryEvent['killer']['name']
            victimName = telemetryEvent['victim']['name']
            
            # if killerName is an empty string that means this isn't a player kill so we should ignore it
            if killerName == "" :
                continue

            killerObject = None
            victimObject = None

            if killerName in players :
                killerObject = players[players.index(killerName)]
            else :
                killerObject = Player(killerName)
                players.append(killerObject)

            if victimName in players :
                victimObject = players[players.index(victimName)]
            else :
                victimObject = Player(victimName)
                players.append(victimObject)

            killerObject.appendVictim(victimObject)

    rootPlayers = []
    for player in players :
        # if parent is None and has at least one victim then it should be the root on the hierarchy.
        if player.hasVictim() and player.isRoot() :
            rootPlayers.append(player)

    jsonUtil = Jsonutil()
    tree = jsonUtil.jsonStartingFromRoot(rootPlayers)

    return render(request, 'pkh/hierarchy.html', {'rootPlayers': json.dumps(tree)})