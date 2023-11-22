from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn import neighbors
import pandas as pd
import requests
import numpy as np
import math

class Predictor:

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    headers = {
        "X-RapidAPI-Key": "e8e412c9c9msh0027892229ec9d3p13a2d0jsn5dfaf9cdf379",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    def det_rank_coef(self,pos):

        if pos == 0:
            return 3.66
        elif pos == 1:
            return 1.6
        elif pos == 2:
            return 0.8
        elif pos == 3:
            return 0.70
        elif pos == 4:
            return 0.6
        elif pos == 5:
            return 0.5
        elif pos == 6:
            return 0.40
        elif pos == 7:
            return 0.31 
        elif pos == 8:
            return 0.20 
        elif pos == 9:
            return 0.10 
    def poissonFormula(self,rH, rA, n, m):
        e = 2.7182818284590
        pos = ((rH ** n)* (rA ** m) / (math.factorial(n)*math.factorial(m))) * (1/e ** (rH+rA))
        return '{:.3f}'.format(pos)

    def __init__(self,league_id,league_name,season,home_id,away_id):

        self.season = season
        self.querystring = {"league":league_id,"season":season}
        self.ml_data = pd.read_excel("Files/Processed_Data_2022_"+league_name+".xlsx")
        self.ml_data = self.ml_data[self.ml_data["Outcome"] != "MS0"]
        self.x = self.ml_data[["OSS1_HOME","OSS1_AWAY","DIFF_ADVANTAGE"]]
        self.y = self.ml_data["Outcome"]
        self.x_train,self.x_test,self.y_train,self.y_test = train_test_split(self.x,self.y,test_size=0.3,random_state=42)

        if league_name == "LaLiga":
            self.k_neighbours = 3

            self.home_goal_coef = 0.5
            self.away_goal_coef = 1.4
            self.home_coef = 1.2
            self.away_coef = 0.9
        elif league_name == "Seria":
            self.k_neighbours = 6

            self.home_goal_coef = 0.5
            self.away_goal_coef = 1.4
            self.home_coef = 1.2
            self.away_coef = 0.9
        elif league_name == "Ligue1":
            self.k_neighbours = 3

            self.home_goal_coef = 0.7
            self.away_goal_coef = 1.1
            self.home_coef = 1.1
            self.away_coef = 0.8

        # Collect Away and Home Data 
        merged_df = pd.read_excel("Files/"+league_name+"_Raw_Data_Updated.xlsx")

        # ML
        hGoals = 0
        hSonG = 0
        hTotalShots = 0
        hPassAcc_perc = 0
        c1 = 0

        aGoals = 0
        aSonG = 0
        aTotalShots = 0
        aPassAcc_perc = 0
        c2 = 0

        h_winH = 0
        h_winA = 0
        h_totalH = 0
        h_totalA = 0

        a_winH = 0
        a_winA = 0
        a_totalH = 0
        a_totalA = 0

        c3 = 0

        # POISSION
        coef_goal_h = 0
        total_goal_conceded_H = 0
        coef_goal_a = 0
        total_goal_conceded_A = 0
        all_goals = 0


        for i in range(len(merged_df)):
            all_goals += (merged_df.iloc[i]["Home Score"]+merged_df.iloc[i]["Away Score"])
            c3 += 1
            # Home Team
            if str(merged_df.iloc[i]["Home Id"]) == home_id:
                h_totalH += 1
                if merged_df.iloc[i]["Home Score"] > merged_df.iloc[i]["Away Score"]:
                    h_winH += 1

                hGoals += merged_df.iloc[i]["Home Score"]
                hSonG += merged_df.iloc[i]["H SonG"]
                hTotalShots += merged_df.iloc[i]["H Total Shots"]
                hPassAcc_perc += merged_df.iloc[i]["H Pass Acc %"]
                c1 += 1

                coef_goal_h += (self.det_rank_coef(merged_df.iloc[i]["Away Rank"]//10))*merged_df.iloc[i]["Home Score"] * self.home_goal_coef
                total_goal_conceded_H += merged_df.iloc[i]["Away Score"]

            elif str(merged_df.iloc[i]["Away Id"]) == home_id:
                h_totalA += 1
                if merged_df.iloc[i]["Away Score"] > merged_df.iloc[i]["Home Score"]:
                    h_winA += 1

                hGoals += merged_df.iloc[i]["Away Score"]
                hSonG += merged_df.iloc[i]["A SonG"]
                hTotalShots += merged_df.iloc[i]["A Total Shots"]
                hPassAcc_perc += merged_df.iloc[i]["A Pass Acc %"]
                c1 += 1

                coef_goal_h += (self.det_rank_coef(merged_df.iloc[i]["Home Rank"]//10))*merged_df.iloc[i]["Away Score"] * self.away_goal_coef
                total_goal_conceded_H += merged_df.iloc[i]["Home Score"]

            # Away Team 
            if str(merged_df.iloc[i]["Home Id"]) == away_id:
                a_totalH += 1
                if merged_df.iloc[i]["Home Score"] > merged_df.iloc[i]["Away Score"]:
                    a_winH += 1

                aGoals += merged_df.iloc[i]["Home Score"]
                aSonG += merged_df.iloc[i]["H SonG"]
                aTotalShots += merged_df.iloc[i]["H Total Shots"]
                aPassAcc_perc += merged_df.iloc[i]["H Pass Acc %"]
                c2 += 1

                coef_goal_a += (self.det_rank_coef(merged_df.iloc[i]["Away Rank"]//10))*merged_df.iloc[i]["Home Score"] * self.home_goal_coef
                total_goal_conceded_A += merged_df.iloc[i]["Away Score"]

            elif str(merged_df.iloc[i]["Away Id"]) == away_id:
                a_totalA += 1
                if merged_df.iloc[i]["Away Score"] > merged_df.iloc[i]["Home Score"]:
                    a_winA += 1

                aGoals += merged_df.iloc[i]["Away Score"]
                aSonG += merged_df.iloc[i]["A SonG"]
                aTotalShots += merged_df.iloc[i]["A Total Shots"]
                aPassAcc_perc += merged_df.iloc[i]["A Pass Acc %"]
                c2 += 1
    
                coef_goal_a += (self.det_rank_coef(merged_df.iloc[i]["Home Rank"]//10))*merged_df.iloc[i]["Away Score"] * self.away_goal_coef
                total_goal_conceded_A += merged_df.iloc[i]["Home Score"]


        self.OSS1_HOME = 0.25*(hGoals/c1)+0.1*(hSonG/c1)+0.2*hGoals/hTotalShots+0.05*(hPassAcc_perc/c1)
        self.OSS1_AWAY = 0.25*(aGoals/c2)+0.1*(aSonG/c2)+0.2*aGoals/aTotalShots+0.05*(aPassAcc_perc/c2)
            
        HOME_ADVANTAGE = ( (h_winH / h_totalH) - (h_winA / h_totalA) )
        AWAY_ADVANTAGE = ( (a_winA / a_totalA) - (a_winH / a_totalH) )
        self.DIFF_ADVANTAGE = HOME_ADVANTAGE-AWAY_ADVANTAGE

        # rH,  rA
        average_goal_H = coef_goal_h / c1
        average_goal_A = coef_goal_a / c2
        average_goal_conceded_A = total_goal_conceded_A / c2
        average_goal_conceded_H = total_goal_conceded_H / c1
        average_lig_goals = all_goals / c3

        self.rH = (average_goal_H/average_lig_goals)*(average_goal_conceded_A/average_lig_goals)*(all_goals/c3)*self.home_coef
        self.rA = (average_goal_A/average_lig_goals)*(average_goal_conceded_H/average_lig_goals)*(all_goals/c3)*self.away_coef

    def KNN(self):
        knn = neighbors.KNeighborsClassifier(self.k_neighbours)
        knn.fit(self.x_train,self.y_train)
        result = knn.predict([[self.OSS1_HOME,self.OSS1_AWAY,self.DIFF_ADVANTAGE]])
        return result
    
    def POISSON_DISTRIBUTION(self):
        poisson_values = []
        for n in range(7):
            for m in range(7):
                poisson = self.poissonFormula(self.rH, self.rA, n, m)
                poisson_values.append((n, m, float(poisson)))

        sorted_poisson = sorted(poisson_values, key=lambda x: float(x[2]), reverse=True)
        return sorted_poisson