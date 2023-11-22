from update import UpdateData
from prediction import Predictor
import requests
import sys
import os
import time

leagues = [UpdateData("135","Seria","2023"),UpdateData("140","LaLiga","2023"),UpdateData("61","Ligue1","2023")]

while True:
    print("******************** MatchGPT beta ********************")
    print("| LaLiga: 140  Seria: 135  Ligue1: 61 | Veri Güncelleme: 1 |")

    lig_opt = str(input(" Seçim => "))
    if lig_opt == "140":
        league_name = "LaLiga"
    elif lig_opt == "135":
        league_name = "Seria"
    elif lig_opt == "61":
        league_name = "Ligue1"

    if lig_opt == "1":
        os.system("cls")
        for league in leagues:
            league.update()
        time.sleep(3)
        os.system("cls")
        continue
    elif lig_opt == "0":
        sys.exit()

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    querystring = {"league":lig_opt,"season":"2023"}

    headers = {
        "X-RapidAPI-Key": "ed853e5f28mshaa2dbf26393fb32p1c34d5jsn14317cec3349",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    fix_data = response.json()

    name_id_dict = dict()

    for fixture in fix_data["response"]:
        if fixture["teams"]["home"]["name"] not in name_id_dict:
            name_id_dict[fixture["teams"]["home"]["name"]] = fixture["teams"]["home"]["id"] 
        if fixture["teams"]["away"]["name"] not in name_id_dict:
            name_id_dict[fixture["teams"]["away"]["name"]] = fixture["teams"]["away"]["id"] 
    print(name_id_dict)


    home_id = str(input("Home Team Id => "))
    away_id = str(input("Away Team Id => "))

    matchPredicton = Predictor(lig_opt,league_name,"2023",home_id,away_id)
    print("------------------")
    print("Home Stats: ",matchPredicton.OSS1_HOME,"  ","Away Stats: ",matchPredicton.OSS1_AWAY)
    print("Common Stats: ",matchPredicton.DIFF_ADVANTAGE)
    print("------------------")
    print("Outcome: ",matchPredicton.KNN())
    print("Scores")
    a = 0
    for score in matchPredicton.POISSON_DISTRIBUTION():
        print("{}-{}: {}".format(score[0], score[1], '{:.1f}'.format(score[2] * 100)))
        a+=1
        if a == 5:
            break


    o = input("Exit(0) Continue(1):")
    os.system("cls")
    if o == "0":
        sys.exit()