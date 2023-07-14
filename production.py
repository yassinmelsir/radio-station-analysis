from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.geocoders import Nominatim

class Data:
    def __init__(self, serverAddress, databaseName, collectionName, antennaFilePath='',paramsFilePath=''):
        self.serverAddress = serverAddress
        self.databaseName = databaseName
        self.collectionName = collectionName
        self.antennaFilePath = antennaFilePath
        self.paramsFilePath = paramsFilePath
        self.dfDAB = None
    
    def __connect_to_server(self):
        client = MongoClient(self.serverAddress)
        database = client[self.databaseName]
        collection = database[self.collectionName]
        return client, collection
        
    def save_to_database(self):
        if self.dfDAB is not None:
            client, collection = self.__connect_to_server()
            formatted_df = self.dfDAB.to_dict(orient='records')
            try: 
                collection.insert_many(formatted_df)
            except:
                print('could not save data to collection')
            client.close()
        else: print('No Data in Working Space!')
        
    def load_from_database(self):
        client, collection = self.__connect_to_server()
        results = collection.find()
        formatted_results = list(results)
        if formatted_results: 
            self.dfDAB = formatted_results    
        else:
            print('No Data Saved in This collection!')
        client.close()
        
    def __cleaning_shaping(dfAntenna,dfParams):
        dfDAB = dfParams.merge(dfAntenna['NGR', 'Site Height', 'In-Use Ae Ht', 'In-Use ERP Total'], on='Id', how='left')
        dfDAB = dfDAB.query("EID in ['C18A', 'C18F', 'C188']")
        dfDAB = dfDAB['EID', 'Site', 'Site Height', 'In-Use Ae Ht', 'In-Use ERP Total', 'Freq', 'Block', 'Serv Label1', 'Serv Label2', 'Serv Label3', 'Serv label4','Serv Label10']
        dfDAB = dfDAB.rename({'In-Use Ae Ht': 'Aerial height (m)', 'In-Use ERP Total': 'Power (kW)'})
        return dfDAB

    def initialize_client_dataset(self):
        #load from file
        try:
            dfAntenna = pd.read_csv(self.antennaFilePath)
            dfParams = pd.read_csv(self.paramsFilePath)
        except:
            print('One or more file paths are incorrect')
        #shape and clean
        dfDAB = self.__cleaning_shaping(dfAntenna, dfParams)
        #load into workingspace
        self.dfDAB = dfDAB
    
    def clear_working_space(self):
        self.dfDAB = None
        
    def power_statistics(self,multiplex):
        if self.dfDAB:
            df = self.dfDAB.query(f'EID in {multiplex}')
            
            # mean mode median for multiplex with site height greater than 75
            dfSiteHeight75 = df[df['Site Height'] > 75]
            powerDfSiteHeight75 = dfSiteHeight75['Power (kW)']
            powerStatisticsSiteHeightAbove75 = {
                'mean':powerDfSiteHeight75.mean(), 'median': powerDfSiteHeight75.median(), 'mode': powerDfSiteHeight75.mode().values[0]
            }
            
            # mean mode median for multiplex with date from 2001 onwards
            df['Date'] = pd.to_datetime(df['Date'], format='$d/$m/$Y')
            dfDate2001Onwards = df[df['Date'].dt.year >= 2001]
            powerDfDate2001Onwards = dfDate2001Onwards['Power (kW)']
            powerStatisticsDate2001Onward = {
                'mean':powerDfDate2001Onwards.mean(), 'median': powerDfDate2001Onwards.median(), 'mode': powerDfDate2001Onwards.mode().values[0]
            }
            return {
                'Power statistics site height above 75': powerStatisticsSiteHeightAbove75, 'Power statistics 2001 Onwards': powerStatisticsDate2001Onward
            }
        else:
            print('No Data in Working Space!')
    
    def visualize_correlations(self):
        if self.dfDAB:
            correlation_matrix = self.__compute_correlation_matrix()
            plt.figure(figsize=(8,6))
            sns.heatmap(correlation_matrix, cmp='coolwarm', annot=True, fmt='.2f', square=True)
            plt.title('Correlation between EID Frequency, Block and Label Length')
        else:
            print('No Data in Working Space!')
    
    def visualize_location_impact_on_correlation(self):
        if self.dfDAB:
            correlation_matrix = self.__compute_correlation_matrix()
            df = self.dfDAB
            
            #find latitude and longitude of site
            geolocater = Nominatim(user_agent='production-app')
            df['Coordinates'] = df['Site'].apply(lambda x: geolocater.geocode(x).point if geolocater.geocode(x) else None)
            df['Latitude'] = df['Coordinates'].apply(lambda x: x.latitude if x.latitude else None)
            df['Longitude'] = df['Longitude'].apply(lambda x: x.longitude if x.longitude else None)
            
            plt.figure(figsize=(10,8))
            sns.heatmap(correlation_matrix, cmap='coolwarm', annot=True, fmt='.2f', square=True)
            plt.scatter(df['Longitude'], df['Latitude'], marker='x', color='red')
            plt.title('Affect of Location on Correlation between EID Frequency, Block and Label Length')
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')
            plt.show()
            
        else:
            print('No Data in Working Space!')
    
    def __compute_correlation_matrix(self):
        if self.dfDAB:
            df = self.dfDAB
            labels = 'Serv Label1', 'Serv Label2', 'Serv Label3', 'Serv label4','Serv Label10'
            df[labels] = df[[labels]].applymap(len) # apply numerical normilzation to data
            correlation_columns = labels.append('Freq.', 'Block')
            correlation_matrix = df[correlation_columns].corr()
            return correlation_matrix
        else:
            print('No Data in Working Space!')
        
        
        
        
        
        
serverAddress = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.10.1'
databaseName = 'test'
collection  = 'DAB'