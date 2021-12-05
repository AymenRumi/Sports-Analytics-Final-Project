import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial import distance
from sklearn.decomposition import PCA
import plotly.express as px
from keras.models import load_model
import warnings
from NBA_Web_Scraper import NBA_Web_Scraper
warnings.filterwarnings("ignore")

class NBA_Roster_Analysis(object):
    
    
    def __init__(self):
        """ initializing module, importing and defining data required for analysis

        """

        # importing data

        mapping=pd.read_csv('mapping.csv',index_col=0)
        self.players=pd.merge(pd.read_csv('NBA_Player_Data_1999-2020.csv',index_col=0) ,mapping,on='TEAM')
        self.teams=pd.read_csv('NBA_Team_Data_1999-2020.csv',index_col=0).replace('LA Clippers','Los Angeles Clippers')
        self.minutes=pd.read_csv('minutes_played.csv',index_col=0)


        # importing saved objects

        self.kde=pd.read_pickle('kde.pkl')
        self.knn=pd.read_pickle('knn.pkl')


        # saving required data list

        self.player_stats_required=['POS', 'MIN', 'PTS', 'FGM', 'FGA',
       'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'REB', 'AST', 'STL',
       'BLK', 'TO', 'DD2', 'TD3', 'PER', 'AGE', 'OFFRTG', 'DEFRTG', 'NETRTG',
       'AST%', 'AST/TO', 'AST RATIO', 'OREB%', 'DREB%', 'REB%', 'TO RATIO',
       'EFG%', 'TS%', 'USG%', 'PACE', 'PIE', 'POSS']

        self.team_stats_required=['WIN%', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA',
       'FT%', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF',
       'PFD', '+/-', 'OFFRTG', 'DEFRTG', 'NETRTG', 'AST%', 'AST/TO',
       'AST\nRATIO', 'OREB%', 'DREB%', 'REB%', 'TOV%', 'EFG%', 'TS%', 'PACE',
       'PIE', 'POSS']


       # saving required dataframes

        self.corr=self.players.drop(['PLAYER','YEAR','TEAM NAME','TEAM'],axis=1).corr()
        self.team_stats=self.teams.drop(['TEAM','YEAR','GP','W','L','MIN'],axis=1)
        self.normalized_team_stats=self.normalize_team_stats(self.team_stats)
        
        
    def download_team_data(self,years,filename,filetype='csv'):
        """Downloading player data for years specified
        """
        web_scraper=NBA_Web_Scraper()
        web_scraper.download_team_data(years,filename,filetype='csv')
    
    
    def download_player_data(self,years,filename,filetype='csv'):
        """Downloading player data for years specified
        """
        web_scraper=NBA_Web_Scraper()
        web_scraper.download_player_data(years,filename,filetype='csv')

    
    def visualize_teams(self,color:str ='Clusters',hover_data:list =['WIN%']):
        """ visualizing NBA team through 1999 - 2020 in 2D w/ Principal Component Analysis
        
        Args: 
            color (str): team statistic to color data points by
            hover_data (list): list of team statistics to show when hovering on datapoints
        
        Returns:
            fig: visual of teams with Plotly
            df (pd.Dataframe): dataframe of teams

        """
        
        # Principal Component Analysis
        pca = PCA(n_components=2)
        components = pca.fit_transform(self.normalized_team_stats)
        pca=pd.DataFrame(data=components,  columns=["PC1", "PC2"])
        
        # Adding teams & clusters
        pca['TEAM']=self.teams['TEAM']+" "+self.teams['YEAR']
        pca['Clusters']=self.knn.labels_
        pca['Clusters']=pca['Clusters'].astype('O')
        
        # Adding all other team metrics
        pca=pd.concat([pca,self.team_stats],axis=1)

        # Plotting with Plotly
        fig = px.scatter(pca, x='PC1', y='PC2',color=color,hover_data=hover_data)
        fig.show()
        
        # returning dataframe
        return pca.drop(['PC1','PC2'],axis=1)
    
    
    def normalize_team_stats(self,team_stats):
        """ normalizing team statistics with MinMaxScaler
        
        Args: 
            team_stats (pd.DataFrame): team stats
        
        Returns:
            normalized_team_stats (pd.DataFrame): normalized team stats

        """

        scaler = MinMaxScaler()
        scaler.fit(team_stats)
        normalized_team_stats=scaler.transform(team_stats)
        normalized_team_stats=pd.DataFrame(normalized_team_stats)
        normalized_team_stats.columns=team_stats.columns
        return normalized_team_stats

    
    
    def view_available_players(self):
        """ viewing list of available players to choose roster for 
        
        Args: 
            None
        
        Returns:
            player (list): list of unique players

        """

        return list(self.players['PLAYER'].unique())
    
    
    
    def adjust_to_minutes(self,minutes:float, player_stats:pd.DataFrame):
        """ given minutes and players statistics, this function adjust the players stats
        Args: 
            minutes (float): minutes played
            player_stats (pd.Dataframe): a dataframe containing the stats of the player
        
        Returns:
            adjusted_player_stats (list)
        """

        adjusted_player_stat=[]

        for i in self.player_stats_required:
            if i=='POS':
                adjusted_player_stat.append(max(set(list(player_stats[i])), key=list(player_stats[i]).count))
            elif i=='MIN':
                adjusted_player_stat.append(minutes)

            # correlation matrix is used to identify variables that have strong association with minutes

            elif (i in self.corr[(self.corr['MIN']>0.5) & (self.corr['MIN']!=1)][['MIN']].index):
                adjusted_player_stat.append(np.mean((player_stats[i])/np.mean(player_stats['MIN']))*minutes)

            else:
                adjusted_player_stat.append(np.mean((player_stats[i])))

        return adjusted_player_stat



    def player_stats_sampling(self,player: str, minutes: float,stats_selection_method:str = 'prime' , prime_window=None):
        """ given a player, and minutes he will play, this function will return a sample of his statistics
        Args: 
            player (string): name of NBA player
            minutes(float): minutes the player will play
            stats_selection_method (str): choose from 'best' or'prime'. 'best' will sample stats from player's best season, 'prime' will sample stats from a window of seasons defined by prime_window
            prime_window (int): number of years to consider a player's 'prime', the default is 5 years chosen when stats_selection_method='prime'
        Returns:
            adjusted_player_stats (list)

        Raise: 
            Exception: when player chosen does not exist
        """

        if player not in self.players['PLAYER'].unique():
            raise Exception("Invalid player: '{}' - Please select from player list shown at .view_available_players()".format(player))

        player_stats=self.players[self.players['PLAYER']==player]

        if stats_selection_method=='best':
            return [player]+self.adjust_to_minutes(minutes,player_stats.sort_values('PIE',ascending=False).head(1)[self.player_stats_required])

        elif stats_selection_method=='prime':
            if prime_window==None:
                years=5
            else:
                years=prime_window

            return [player]+self.adjust_to_minutes(minutes,player_stats.sort_values('PIE',ascending=False).head(years)[self.player_stats_required])

        else:
            return [player]+self.adjust_to_minutes(minutes,player_stats[self.player_stats_required])




    def team_stats_sampling(self,team:list, minutes_selection_method:str ='sample', stats_selection_method:str = 'prime' , prime_window=None, output_df=False):
        """ given a list of 8 players, how their minutes and stats, this function will sample their player stats
        Args: 
            team (list): name of NBA player
            minutes_selection_method (str): minutes the player will play
            stats_selection_method (str): choose from 'best' or'prime'. 'best' will sample stats from player's best season, 'prime' will sample stats from a window of seasons defined by prime_window
            prime_window (int): number of years to consider a player's 'prime', the default is 5 years chosen when stats_selection_method='prime'
            output_df (bool): 
        Returns:
            team_stats (np.array)
            or 
            team_stats (pd.DataFrame)

        Raise: 
            Exception: when player chosen does not exist
        """

        if len(team)!=8:
            raise Exception("Team must contain 8 players, contains '{}' players".format(len(team)))

        if minutes_selection_method not in ['sample','average']:
            raise Exception("Invalid minutes_selection_method: '{}' - Please select from ['sample','average']".format(minutes_selection_method))

        if stats_selection_method not in ['prime','average','best']:
             raise Exception("stats_selection_method: '{}' - Please select from ['prime','average','best']".format(stats_selection_method))

        if stats_selection_method!='prime':
            if prime_window!=None:
                raise Exception("prime_window requires stats_selection_method='prime'".format(stats_selection_method))


        if minutes_selection_method=='sample':
            minutes=self.kde.sample(1)[0]
        else:
            minutes=[np.mean(self.minutes[self.minutes['player']==i]['minutes']) for i in sorted(self.minutes['player'].unique())]


        team_stats=[]

        for player,minute in zip(team,minutes):

            team_stats.append(self.player_stats_sampling(player,minutes=minute,stats_selection_method=stats_selection_method,prime_window=prime_window))

        if output_df==True:

            return pd.DataFrame(team_stats,columns=['PLAYER']+self.player_stats_required)
        else:
            return team_stats

    
    def normalize_sampled_stats(self,team:list, minutes_selection_method:str ='sample', stats_selection_method:str = 'prime' , prime_window=None):
        """ given a list of 8 players, how their minutes and stats, this function will give their normalized stats
        Args: 
            team (list): name of NBA player
            minutes_selection_method (str): minutes the player will play
            stats_selection_method (str): choose from 'best' or'prime'. 'best' will sample stats from player's best season, 'prime' will sample stats from a window of seasons defined by prime_window
            prime_window (int): number of years to consider a player's 'prime', the default is 5 years chosen when stats_selection_method='prime'
            output_df (bool): 
        Returns:
            normalized stats
  
        """
        sampled_players=pd.DataFrame(self.team_stats_sampling(team,minutes_selection_method,stats_selection_method,prime_window),columns=['PLAYER']+self.player_stats_required)
        all_players=self.players[['PLAYER']+self.player_stats_required]
        
        
        aggregated_players=pd.concat([sampled_players,all_players])

        
        
        numeric_data=aggregated_players[self.player_stats_required]
    
        numeric_data=pd.concat([ pd.get_dummies(numeric_data['POS']),numeric_data.drop(['POS'],axis=1)], axis=1)
        
        
        scaler = MinMaxScaler()
        scaler.fit(numeric_data)
        
        normalized_data=scaler.transform(numeric_data)
        normalized_data=pd.DataFrame(normalized_data)
        
        normalized_data.columns=numeric_data.columns
        
        
        return pd.concat([aggregated_players[['PLAYER']].reset_index(drop=True), normalized_data], axis=1).head(8)
        
        
    
    def predict_roster_cluster(self,team:list, minutes_selection_method:str ='sample', stats_selection_method:str = 'prime' , prime_window=None):
        """ given a list of 8 players, how their minutes and stats, this function will predict the cluster it belongs to
        Args: 
            team (list): name of NBA player
            minutes_selection_method (str): minutes the player will play
            stats_selection_method (str): choose from 'best' or'prime'. 'best' will sample stats from player's best season, 'prime' will sample stats from a window of seasons defined by prime_window
            prime_window (int): number of years to consider a player's 'prime', the default is 5 years chosen when stats_selection_method='prime'
            output_df (bool): 
        Returns:
            cluster
        """
        roster=np.asarray(self.normalize_sampled_stats(team,minutes_selection_method,stats_selection_method,prime_window).drop(['PLAYER'],axis=1))
        roster=roster.reshape(1,roster.shape[0],roster.shape[1],1)
        
        # loading cluster predicting convolutional neural network
        model = load_model('models/CLUSTER.h5')
        pred=model.predict(roster)
        
        return list(pred[0]).index(max(pred[0]))
        
    
    def predict_team_stats(self,team:list, minutes_selection_method:str ='sample', stats_selection_method:str = 'prime' , prime_window=None):
        """ given a list of 8 players, how their minutes and stats, this function will predict their team stats from neural networks trained
        Args: 
            team (list): name of NBA player
            minutes_selection_method (str): minutes the player will play
            stats_selection_method (str): choose from 'best' or'prime'. 'best' will sample stats from player's best season, 'prime' will sample stats from a window of seasons defined by prime_window
            prime_window (int): number of years to consider a player's 'prime', the default is 5 years chosen when stats_selection_method='prime'
            output_df (bool): 
        Returns:
            predicted team stats
        """
        
        roster=np.asarray(self.normalize_sampled_stats(team,minutes_selection_method,stats_selection_method,prime_window).drop(['PLAYER'],axis=1))
        roster=roster.reshape(1,roster.shape[0],roster.shape[1],1)
        
        def r2_keras(y_true, y_pred):
            SS_res =  K.sum(K.square( y_true - y_pred )) 
            SS_tot = K.sum(K.square( y_true - K.mean(y_true) ) ) 
            return ( 1 - SS_res/(SS_tot + K.epsilon()) )
        
        
        stats={}
        
        # calling each convolutional neural network model saved
        for stat in self.team_stats_required:
            filename="models/{}.h5".format(stat.replace("/","_"))
            model = load_model(filename,custom_objects={"r2_keras":r2_keras})
            stats[stat]=model.predict(roster)[0][0]
            
        
        return pd.Series(stats)
    
    
    def k_nearest_neighbors(self,team:list, minutes_selection_method:str ='sample', stats_selection_method:str = 'prime' , prime_window=None,k=5,visualize=False):
        """ given a list of 8 players, how their minutes and stats, this function will output K nearest historical teams, as well as option to view location
        Args: 
            team (list): name of NBA player
            minutes_selection_method (str): minutes the player will play
            stats_selection_method (str): choose from 'best' or'prime'. 'best' will sample stats from player's best season, 'prime' will sample stats from a window of seasons defined by prime_window
            prime_window (int): number of years to consider a player's 'prime', the default is 5 years chosen when stats_selection_method='prime'
            output_df (bool): 
        Returns:
            visuals and k hisrorical nba teams
        """
        predicted_team_stats=self.predict_team_stats(team, minutes_selection_method, stats_selection_method , prime_window)
        
        normalized_predicted_team_stats=(self.normalize_team_stats(self.team_stats.append(predicted_team_stats,ignore_index=True))).iloc[-1]
    
        euclidean_distances = self.normalized_team_stats.apply(lambda row: distance.euclidean(row, normalized_predicted_team_stats), axis=1)

        k_nearest=pd.DataFrame(euclidean_distances,columns=['Distance']).sort_values('Distance').head(k).index
        
        print("Cluster: {}".format(self.knn.predict(np.asarray(normalized_predicted_team_stats).reshape(1, -1))[0]))
        
        
        if visualize==True:
            self.visualize_new_roster(self.normalize_team_stats(self.team_stats.append(predicted_team_stats,ignore_index=True)),predicted_team_stats,cluster=self.knn.predict(np.asarray(normalized_predicted_team_stats).reshape(1, -1))[0])
        
        return self.teams.loc[k_nearest][['TEAM','YEAR','WIN%']]
    
    
    def visualize_new_roster(self,normalized_stats,predicted_stats,cluster):
        """ shows visual location of new roster
        """
        teams_with_new=self.teams.copy()
        
        new_team={}
        for i in teams_with_new.columns:
            if i=='TEAM':
                new_team[i]='Theoretical Roster'
            else:
                try:
                    new_team[i]=predicted_stats[i]
                except:
                    if teams_with_new[i].dtype==float or teams_with_new[i].dtype==int:
                        new_team[i]=0
                    else:
                        new_team[i]=""

        teams_with_new=teams_with_new.append(pd.Series(new_team),ignore_index=True)
        
        pca = PCA(n_components=2)
        components = pca.fit_transform(normalized_stats)
        pca=pd.DataFrame(data=components,  columns=["PC1", "PC2"])
        
        pca['TEAM']=teams_with_new['TEAM']+" "+teams_with_new['YEAR']
        pca['Clusters']=np.concatenate((self.knn.labels_, np.array([cluster])), axis=0)
        
       
        pca['Clusters']=pca['Clusters'].astype('O')
        
        pca=pd.concat([pca,teams_with_new.drop(['TEAM','YEAR','GP','W','L','MIN'],axis=1)],axis=1)
        
        def is_real(team):
    
            if 'Theoretical' in team:
                return False
            else:
                return True
        
        
        pca['IS_REAL'] = pca.apply(lambda x: is_real(x['TEAM']), axis=1)
        fig = px.scatter(pca, x='PC1', y='PC2',color='IS_REAL',hover_data=['WIN%','TEAM'])
        fig.show()
        fig = px.scatter(pca, x='PC1', y='PC2',symbol='IS_REAL',color='Clusters',hover_data=['WIN%','TEAM'])
        fig.show()
        
        return pca.drop(['PC1','PC2'],axis=1)
    
    
    
    
    