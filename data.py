from pymongo import MongoClient
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class Data:
    def __init__(self, serverAddress, databaseName, collectionName):
        self.serverAddress = serverAddress
        self.databaseName = databaseName
        self.collectionName = collectionName
        self.dfDAB = None
    
    def get_df(self):
        if self.dfDAB: return self.dfDAB
    
    def get_multiplexes(self):
        if self.dfDAB : return self.dfDAB['EID'].unique()
    
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
                client.close()
                return True
            except:
                print('could not save data to collection')
                client.close()
                return False
        else: print('No Data in Working Space!')
        
    def load_from_database(self):
        client, collection = self.__connect_to_server()
        results = collection.find()
        formatted_results = list(results)
        if formatted_results: 
            self.dfDAB = pd.DataFrame(formatted_results)
            print(self.dfDAB)
            client.close()
            return True
        else:
            print('No Data Saved in This collection!')
            client.close()
            return False
        
        
    def __cleaning_shaping(self,dfAntenna,dfParams):
        dfDAB = dfParams.join(dfAntenna[['NGR', 'Site Height', 'In-Use Ae Ht', 'In-Use ERP Total']])
        dfDAB = dfDAB.query("EID in ['C18A', 'C18F', 'C188']")
        dfDAB = dfDAB[['EID', 'Site', 'Freq.', 'Block', 'Serv Label1 ', 'Serv Label2 ', 'Serv Label3 ', 'Serv Label4 ','Serv Label10 ','Site Height', 'In-Use Ae Ht', 'In-Use ERP Total','Date']]
        dfDAB['Aerial height (m)'], dfDAB['Power (kW)'] = dfDAB['In-Use Ae Ht'].copy(), dfDAB['In-Use ERP Total'].copy()
        dfDAB.drop(columns=['In-Use Ae Ht','In-Use ERP Total'])
        dfDAB['Date'] = dfDAB['Date'].apply(lambda x: x[-4:]).astype(int)
        dfDAB['Power (kW)'] = dfDAB['Power (kW)'].apply(lambda x: x.replace(',','')).astype(float)
        labels = ['Serv Label1 ', 'Serv Label2 ', 'Serv Label3 ', 'Serv Label4 ', 'Serv Label10 ']
        dfDAB[labels] = dfDAB[labels].applymap(len) # apply numerical normilzation to data
        labelencoder = LabelEncoder()
        dfDAB['Block'] = labelencoder.fit_transform(dfDAB['Block'])
        dfDAB['Site'] = labelencoder.fit_transform(dfDAB['Site'])
        return dfDAB

    def initialize_client_dataset(self, antennaFilePath, paramsFilePath):
        #load from file
        dfAntenna = pd.read_csv(antennaFilePath)
        dfParams = pd.read_csv(paramsFilePath, encoding='latin-1')
        #shape and clean
        dfDAB = self.__cleaning_shaping(dfAntenna, dfParams)
        #load into workingspace
        self.dfDAB = dfDAB
        return True if self.dfDAB.shape[0] > 0 else False
    
    def clear_working_space(self):
        self.dfDAB = None
        
    def power_statistics(self,rows):
        # working statistics
        if self.dfDAB.shape[0] > 0:
            
            df = self.dfDAB.query(f'EID in {rows}')
            # mean mode median for multiplex with site height greater than 75
            dfSiteHeight75 = df[df['Site Height'] > 75]
            powerDfSiteHeight75 = dfSiteHeight75['Power (kW)']
            powerStatisticsSiteHeightAbove75 = {
                'mean':powerDfSiteHeight75.mean(), 'median': powerDfSiteHeight75.median(), 'mode': powerDfSiteHeight75.mode().values[0]
            }
            # mean mode median for multiplex with date from 2001 onwards
            dfDate2001Onwards = df[df['Date'] >= 2001]
            powerDfDate2001Onwards = dfDate2001Onwards['Power (kW)']
            powerStatisticsDate2001Onward = {
                'mean':powerDfDate2001Onwards.mean(), 'median': powerDfDate2001Onwards.median(), 'mode': powerDfDate2001Onwards.mode().values[0]
            }
            return {
                'heightConstraint': powerStatisticsSiteHeightAbove75, 'dateConstraint': powerStatisticsDate2001Onward
            }
        else:
            print('No Data in Working Space!')
    
    def visualize_correlations(self, graphFrame, rows):
        for child in graphFrame.winfo_children():
            child.destroy()
        if self.dfDAB.shape[0] > 0:
            correlation_matrix = self.__compute_correlation_matrix(rows)
            figure, ax = plt.subplots()
            sns.heatmap(correlation_matrix, cmap='coolwarm', annot=True, fmt='.2f', square=True, ax=ax)
            ax.set_title('Correlation Statistics')
            canvas = FigureCanvasTkAgg(figure, master=graphFrame)
            canvas.draw()
            canvas.get_tk_widget().pack()
        else:
            print('No Data in Working Space!')
    
    def visualize_location_impact_on_correlation(self, graphFrame, rows):
        for child in graphFrame.winfo_children():
            child.destroy()
        if self.dfDAB.shape[0] > 0:
            df = self.dfDAB.query(f"EID in {rows}")   
            grouped_df = df.groupby('EID')
            groups = df['EID'].unique()
            columns = ['Site','Freq.', 'Block','Serv Label1 ', 'Serv Label2 ', 'Serv Label3 ', 'Serv Label4 ', 'Serv Label10 '] 
            
            figure, ax = plt.subplots()
            bar_width = 0.35
            bar_spacing = 0.2
            for i, column in enumerate(columns):
                x = [j + i * (bar_width + bar_spacing) for j in range(len(groups))]
                bars = ax.bar(x, grouped_df[column].mean(), width=bar_width, label=column)
            
            ax.set_xticks([])

            for i, column in enumerate(columns):
                x = [j + i * (bar_width + bar_spacing) for j in range(len(groups))]
                for j, value in enumerate(grouped_df[column].mean()):
                    ax.text(x[j], value, groups[j], ha='center', va='bottom')

            ax.set_xticks([j + bar_width / 2 + (len(columns) - 1) * (bar_width + bar_spacing) / 2 for j in range(len(groups))])
            ax.set_xticklabels(groups)
            ax.set_xlabel('Group')
            ax.set_ylabel('Mean Value')
            ax.set_title('Bar Graph for Each Group and Numerical Columns')
            ax.legend()
                        
            canvas = FigureCanvasTkAgg(figure, master=graphFrame)
            canvas.draw()
            canvas.get_tk_widget().pack()
            
        else:
            print('No Data in Working Space!')
    
    def __compute_correlation_matrix(self, rows):
        if self.dfDAB.shape[0] > 0:
            df = self.dfDAB.query(f"EID in {rows}")
            correlation_columns = ['Freq.', 'Block','Serv Label1 ', 'Serv Label2 ', 'Serv Label3 ', 'Serv Label4 ', 'Serv Label10 ']
            correlation_matrix = df[correlation_columns].corr()
            return correlation_matrix
        else:
            print('No Data in Working Space!')
