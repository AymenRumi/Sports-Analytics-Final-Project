from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import pandas as pd

import time
import warnings
warnings.filterwarnings("ignore")



class NBA_Web_Scraper():
    
    def __init__(self):


        self.driver= webdriver.Chrome(ChromeDriverManager().install())
        
    
    def get_traditional_team_data(self,years):
        
        header_added=False
        # dictionary to add values
        data={}
        for year in range(years[0],years[1]):
            
            url='https://www.nba.com/stats/teams/traditional/?sort=TEAM_NAME&dir=-1&Season={}-{}&SeasonType=Regular%20Season'.format(year,str(year+1)[2:])

            self.driver.get(url)
            print("Downloading {}-{} Traditional Team Data....  ".format(year,year+1), end='')
            time.sleep(5)
            try:
                self.driver.find_element_by_xpath("/html/body/div[5]/div[3]/div/div/div[2]/div/div/button").click()
                time.sleep(5)

            except:
                pass


            # column headers
            if header_added==False:
                for i in range(2,29):

                    try:                         
                        col=self.driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/thead/tr/th[{}]'.format(i)).text
                    except:
                        col=self.driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[2]/table/thead/tr/th[{}]'.format(i)).text

                    if i==3:
                        data['YEAR']=[]
                    data[col]=[]

                header_added=True


            # keys 
            col_names=list(data.keys())
            
            # iterate through players
            index=1
            
            while True:
                
                try:
                    row=self.driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/tbody/tr[{}]'.format(index)).text.replace(",","")

                    team=row[:row.index("\n")]
                    stats=row[row.index("\n"):].split()

                    data['TEAM'].append(team)
                    data['YEAR'].append("{}-{}".format(str(year),str(year+1)[2:]))


                    for j in range(len(stats)):

                        data[col_names[j+2]].append(stats[j])
                        
                    index+=1
                except:
                    
                    break
            
            print("\u2713")



        return pd.DataFrame.from_dict(data)


    
    
    def get_advanced_team_data(self,years):
        
        header_added=False
        # dictionary to add values
        data={}
        for year in range(years[0],years[1]):
            
            url='https://www.nba.com/stats/teams/advanced/?sort=TEAM_NAME&dir=-1&Season={}-{}&SeasonType=Regular%20Season'.format(year,str(year+1)[2:])

            self.driver.get(url)
            print("Downloading {}-{} Advanced Team Data....  ".format(year,year+1), end='')
            time.sleep(5)
            try:
                self.driver.find_element_by_xpath("/html/body/div[5]/div[3]/div/div/div[2]/div/div/button").click()
                time.sleep(5)

            except:
                pass


            # column headers
            if header_added==False:
                for i in range(2,22):

                    try:                         
                        col=self.driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/thead/tr/th[{}]'.format(i)).text
                    except:
                        col=self.driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[2]/table/thead/tr/th[{}]'.format(i)).text

                    if i==3:
                        data['YEAR']=[]
                    data[col]=[]

                header_added=True


            # keys 
            col_names=list(data.keys())
            
            # iterate through players
            index=1
            
            while True:
                
                try:
                    row=self.driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/tbody/tr[{}]'.format(index)).text.replace(",","")

                    team=row[:row.index("\n")]
                    stats=row[row.index("\n"):].split()

                    data['TEAM'].append(team)
                    data['YEAR'].append("{}-{}".format(str(year),str(year+1)[2:]))


                    for j in range(len(stats)):

                        data[col_names[j+2]].append(stats[j])
                        
                    index+=1
                except:
                    
                    break
            
            print("\u2713")


    
        return pd.DataFrame.from_dict(data)  
    
    
    
    
    def get_traditional_player_data(self,years):

        header_added=False
        data={}
        for year in range(years[0],years[1]):
            url='https://www.espn.com/nba/stats/player/_/season/{}/seasontype/2'.format(year+1)
            self.driver.get(url)
            print("Downloading {}-{} Traditional Player Data....  ".format(year,year+1), end='')
            time.sleep(3)
            
            while True:
                try:                                   #/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[3]/div/div/select/option[1
                    self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[4]/div[3]/div/div/section/div/div[3]/div[2]/a').click()
                    time.sleep(2)
                except:
                    break

            if header_added==False:

                data['PLAYER']=[]
                data['YEAR']=[]

                for i in range(1,22):

                    col=self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[4]/div[3]/div/div/section/div/div[3]/div/div[2]/div/div[2]/table/thead/tr/th[{}]/span'.format(i)).text
                    data[col]=[]
                header_added=True
            col_names=list(data.keys())
            
            index=1
            while True:
                try:                                   
                    player=self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[4]/div[3]/div/div/section/div/div[3]/div[1]/div[2]/table/tbody/tr[{}]/td[2]/div/a'.format(index)).text
                    stats=self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[4]/div[3]/div/div/section/div/div[3]/div[1]/div[2]/div/div[2]/table/tbody/tr[{}]'.format(index)).text.split()


                    data['PLAYER'].append(player)
                    data['YEAR'].append("{}-{}".format(str(year),str(year+1)[2:]))

                    for j in range(len(stats)):
                        data[col_names[j+2]].append(stats[j])

                    index+=1
                except:
                    break
            print("\u2713")

        
        return pd.DataFrame.from_dict(data)
        
        
    def get_advanced_player_data(self,years):


        header_added=False
        # dictionary to add values
        data={}
        for year in range(years[0],years[1]):

            url='https://www.nba.com/stats/players/advanced/?sort=PLAYER_NAME&dir=-1&Season={}-{}&SeasonType=Regular%20Season'.format(year,str(year+1)[2:])

            self.driver.get(url)
            print("Downloading {}-{} Advanced Player Data....  ".format(year,year+1), end='')
            time.sleep(5)
            try:
                self.driver.find_element_by_xpath("/html/body/div[5]/div[3]/div/div/div[2]/div/div/button").click()
                time.sleep(5)

            except:
                pass

            # click to view all players

            for i in range(0,5):
                while True:
                    try:                                   #/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[3]/div/div/select/option[1
                        self.driver.find_element_by_xpath("/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[3]/div/div/select/option[1]").click()
                    except:
                        time.sleep(2)
                        pass
                    break



            time.sleep(7)

            # column headers
            if header_added==False:
                for i in range(2,25):

                    try:                         
                        col=self.driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/thead/tr/th[{}]'.format(i)).text
                    except:
                        col=self.driver.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[2]/table/thead/tr/th[{}]'.format(i)).text

                    if i==3:
                        data['YEAR']=[]
                    data[col]=[]

                header_added=True

            # number of total players
            total_players=int(self.driver.find_element_by_class_name('stats-table-pagination__info').text.split()[0])


            # getting NBA table
            table=self.driver.find_element_by_class_name('nba-stat-table')

            # keys 
            col_names=list(data.keys())

            # iterate through players
            for i in range(1,total_players+1):

                row=table.find_element_by_xpath('/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table/tbody/tr[{}]'.format(i)).text.replace(",","")

                player=row[:row.index("\n")]
                stats=row[row.index("\n"):].split()

                data['PLAYER'].append(player)
                data['YEAR'].append("{}-{}".format(str(year),str(year+1)[2:]))


                for j in range(len(stats)):

                    data[col_names[j+2]].append(stats[j])


            print("\u2713")


        
        return pd.DataFrame.from_dict(data)
        
    
    def download_player_data(self,years,filename,filetype='csv'):
        df_traditional=self.get_traditional_player_data(years)
        df_advanced=self.get_advanced_player_data(years)
        
        df=df_traditional.merge(df_advanced.drop(columns=['MIN']),on=['PLAYER','YEAR','GP'])
        
        df.to_csv('{}.csv'.format(filename))
        print("File Saved: {}.csv".format(filename))
        
        
    def download_team_data(self,years,filename,filetype='csv'):
        df_traditional=self.get_traditional_team_data(years)
        df_advanced=self.get_advanced_team_data(years)
        
        df=df_traditional.merge(df_advanced.drop(columns=['MIN']),on=['TEAM','YEAR','GP','W','L'])
        
        df.to_csv('{}.csv'.format(filename))
        print("File Saved: {}.csv".format(filename))
        
        
