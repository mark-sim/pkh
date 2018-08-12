# pkh : players kill hierarchy tree for [PUBG](https://www.pubg.com/)

pkh is a django web application that allows you to view players kill hierarchy in a game. 

Using it is pretty straightforward. Just enter your IGN and click on any match to generate a kill hierarchy tree for that match.

You can try it out [here](http://pubg-pkh.herokuapp.com/). 

## How it was done
PUBG recently released their [Official API](https://developer.playbattlegrounds.com/).
1) Request information about the player and a list of their recent matches using the [players endpoint](https://documentation.pubg.com/en/players-endpoint.html).

Sample response looks something like this :
```
{
   "data":[
      {
         "type":"string",
         "id":"string",
         "attributes":{
            "name":"string",
            "shardId":"string",
            "stats":{

            },
            "createdAt":"string",
            "updatedAt":"string",
            "patchVersion":"string",
            "titleId":"string"
         },
         "relationships":{
            "assets":{
               "data":{

               }
            },
            "matches":{
               "data":[
                  {
                     "id":"string",
                     "type":"string"
                  }
               ]
            }
         },
         "links":{
            "schema":"string",
            "self":"string"
         }
      }
   ],
   "links":{
      "self":"string"
   },
   "meta":{

   }
}
```
Then match history of the player is retrieved by ```playerResponse['data'][0]['relationships']['matches']['data']```.

2) For each match retrieved, I made a request to the [matches endpoint](https://documentation.pubg.com/en/matches-endpoint.html) which contains the results of a completed match such as the game mode played, duration, and which players participated.

Sample response looks something like this :
```
{
   "data":{
      "type":"string",
      "id":"string",
      "attributes":{
         "createdAt":"string",
         "duration":0,
         "gameMode":"duo",
         "mapName":"Desert_Main",
         "isCustomMatch":true,
         "patchVersion":"string",
         "shardId":"string",
         "stats":{

         },
         "tags":{

         },
         "titleId":"string"
      },
      "relationships":{
         "assets":{
            "data":[
               {
                  "type":"string",
                  "id":"string"
               }
            ]
         },
         "rosters":{
            "data":[
               {
                  "type":"string",
                  "id":"string"
               }
            ]
         },
         "rounds":{

         },
         "spectators":{

         }
      },
      "links":{
         "schema":"string",
         "self":"string"
      }
   },
   "included":[
      null
   ],
   "links":{
      "self":"string"
   },
   "meta":{

   }
}
```
This response was used to populate the match tables.

3) The response above only has subset of the full match data. 

In order to get the full match data, I need to make a request to the [telemetry endpoint](https://documentation.pubg.com/en/telemetry.html) which provides further insight into a match.

In order to retrieve the telemetry object, from the match response retrieved above, get the telemetry id by
```telemetryId = matchResponse['data']['relationships']['assets']['data'][0]['id']``` 

then get the link to the telemetry data by iterating through ```matchResponse['included']``` and finding the dictionary that has ``` id == telemetryId```. 

That dictionary will contain a link to the telemetry data.

4) Then, I made a request to the telemetry data link which has bunch of [telemetry events](https://documentation.pubg.com/en/telemetry-events.html) and [telemetry objects](https://documentation.pubg.com/en/telemetry-objects.html). To generate a kill hierarchy tree I only needed ```LogPlayerKill``` which is in ```telemetry events```.
So I iterated through ```telemetry events``` and retrieved all dictionaries which has ``` _T == 'LogPlayerKill' ```.

5) After retrieving ```LogPlayerKill``` data, I created a tree then converted the tree into json format that's accepted by [d3.js collapsible tree](http://mbostock.github.io/d3/talk/20111018/tree.html). Also I added some logic to get rid of players that shouldn't be shown on the kill hierarchy trees (such as players without children and has no parent).
