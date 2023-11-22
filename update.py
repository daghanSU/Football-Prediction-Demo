from tqdm import tqdm
import pandas as pd
import requests
import json
import time

class UpdateData:

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    headers = {
        "X-RapidAPI-Key": "e8e412c9c9msh0027892229ec9d3p13a2d0jsn5dfaf9cdf379",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    def __init__(self,league_id,league_name,season):
        self.league_id = league_id
        self.league_name = league_name
        self.season = season
        self.fixtureJSON_name = self.league_name + "_2023_fixtures.json"
        self.updatedRD_name = self.league_name + "_Raw_Data_Updated.xlsx"
        self.RD2022_name = "Raw_" + self.league_name + "_Data2022.xlsx"
        self.MRD_name = "Merged_Raw_Data_"+self.league_name+".xlsx"

    def update(self):

        querystring = {"league":self.league_id,"season":self.season}
        response = requests.get(UpdateData.url,headers=UpdateData.headers,params=querystring)
        
        fixtures_data = response.json()
        with open("Files/"+self.fixtureJSON_name,"w") as file:
            json.dump(fixtures_data,file)

        df = pd.DataFrame(columns=["Fixture id","Home Id","Away Id","Home Score","Away Score","Half Home Score","Half Away Score",
                           "H SonG","H SoffG","H Total Shots","H Blocked Shots","H Shots In","H Shots Out","H Ball Poss","H GK Saves","H Total Pass","H Pass Acc %",
                           "A SonG","A SoffG","A Total Shots","A Blocked Shots","A Shots In","A Shots Out","A Ball Poss","A GK Saves","A Total Pass","A Pass Acc %"])  

        for i in tqdm(range(len(fixtures_data["response"])), desc=self.league_name+" Verileri Güncelleniyor", ncols=100):
            if fixtures_data["response"][i]["fixture"]["status"]["short"] == "FT":

                each_fix_id = fixtures_data["response"][i]["fixture"]["id"]
                home_id = fixtures_data["response"][i]["teams"]["home"]["id"]
                away_id = fixtures_data["response"][i]["teams"]["away"]["id"]

                home_score = fixtures_data["response"][i]["goals"]["home"]
                away_score = fixtures_data["response"][i]["goals"]["away"]
                half_home_score = fixtures_data["response"][i]["score"]["halftime"]["home"]
                half_away_score = fixtures_data["response"][i]["score"]["halftime"]["away"]

                url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics"
                querystring = {"fixture":str(each_fix_id)}

                response = requests.get(url, headers=UpdateData.headers, params=querystring)
                stats = response.json()

                json_stats = json.dumps(stats,indent=4)
                json_stats = json_stats.replace("null","0")
                json_stats = json_stats.replace("None","0")

                stats = json.loads(json_stats)

                # Set Ranks

                row = [each_fix_id,home_id,away_id,int(home_score),int(away_score),int(half_home_score),int(half_away_score),
                    int(stats["response"][0]["statistics"][0]["value"]), int(stats["response"][0]["statistics"][1]["value"]),int(stats["response"][0]["statistics"][2]["value"]),int(stats["response"][0]["statistics"][3]["value"]),int(stats["response"][0]["statistics"][4]["value"]),int(stats["response"][0]["statistics"][5]["value"]),int(stats["response"][0]["statistics"][9]["value"].replace("%","")),int(stats["response"][0]["statistics"][12]["value"]),int(stats["response"][0]["statistics"][13]["value"]),int(stats["response"][0]["statistics"][15]["value"].replace("%","")),
                    int(stats["response"][1]["statistics"][0]["value"]), int(stats["response"][1]["statistics"][1]["value"]),int(stats["response"][1]["statistics"][2]["value"]),int(stats["response"][1]["statistics"][3]["value"]),int(stats["response"][1]["statistics"][4]["value"]),int(stats["response"][1]["statistics"][5]["value"]),int(stats["response"][1]["statistics"][9]["value"].replace("%","")),int(stats["response"][1]["statistics"][12]["value"]),int(stats["response"][1]["statistics"][13]["value"]),int(stats["response"][1]["statistics"][15]["value"].replace("%",""))
                    ]

                df.loc[len(df)] = row
                time.sleep(2)
        
        df = df[::-1]
        df.insert(5,"Away Rank",None)
        df.insert(6,"Home Rank",None)

        for i in range(len(df)):
            ranks = dict()
            for j in range(i,len(df)):
                if df.iloc[j]["Home Id"] not in ranks:
                    ranks[df.iloc[j]["Home Id"]] = [0, 0]
                if df.iloc[j]["Away Id"] not in ranks:
                    ranks[df.iloc[j]["Away Id"]] = [0, 0]

                if df.iloc[j]["Home Score"] > df.iloc[j]["Away Score"]:
                    ranks[df.iloc[j]["Home Id"]][0] += 3
                elif df.iloc[j]["Away Score"] > df.iloc[j]["Home Score"]:
                    ranks[df.iloc[j]["Away Id"]][0] += 3
                else:
                    ranks[df.iloc[j]["Home Id"]][0] += 1
                    ranks[df.iloc[j]["Away Id"]][0] += 1

                ranks[df.iloc[j]["Home Id"]][1] += (df.iloc[j]["Home Score"] - df.iloc[j]["Away Score"])
                ranks[df.iloc[j]["Away Id"]][1] += (df.iloc[j]["Away Score"] - df.iloc[j]["Home Score"])

            sorted_ranks = dict(sorted(ranks.items(), key=lambda item: (item[1][0], item[1][1]), reverse=True))
            id_ranks = list(sorted_ranks.keys())

            df.loc[i, "Home Rank"] = id_ranks.index(df.iloc[i]["Home Id"]) + 1
            df.loc[i, "Away Rank"] = id_ranks.index(df.iloc[i]["Away Id"]) + 1

        df.to_excel("Files/"+self.updatedRD_name,index=False)
        df2022 = pd.read_excel("Files/"+self.RD2022_name)
        merged_raw_data = pd.concat([df,df2022],ignore_index=True)
        merged_raw_data.to_excel(self.MRD_name,index=False)

        print(self.league_name," başarıyla  güncellendi !")

