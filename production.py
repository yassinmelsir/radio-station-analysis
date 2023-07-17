import tkinter as tk
from tkinter import filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.geocoders import Nominatim

class GUI:
    def __init__(self,data):
        self.data = data
        self.txAntennaFilePath = None
        self.txParamsFilePath = None
        self.rows = []
        self.columns = []
        
        #gui init
        self.root = tk.Tk()
        self.root.title('Production')
        
        #gui elements
        self.canvas = tk.Canvas(self.root, width=400, height=300)
        self.text =  tk.Text(self.root)
        self.txAntennaButton = tk.Button(self.root, text='Find TxAntenna File', command=self.__update_antenna_filePath)
        self.txParamsButton = tk.Entry(self.root, text='Find TxParams File', command=self.__update_params_filePath)
        self.load_csv_button = tk.Button(self.root,text='Load From CSV', command=self.__load_from_csv)
        self.load_database_button = tk.Button(self.root, text='Load From Database', command=self.__load_from_database)
        self.save_database_button = tk.Button(self.root, text='Save To Database', command=self.__save_to_database)
        self.row_entry_var = tk.StringVar()
        self.row_entry = tk.Entry(self.root, textvariable=self.row_entry_var)
        self.row_entry.bind("<KeyRelease>", self.__update_rows)
        # populate statistics button
        # populate correlation graph button
        # populate location-correlation graph button
            
        #gui layout
        self.canvas.grid(row=0,column=0)
        self.text.grid(row=1,column=0)
        widgets = [self.txAntennaButton, self.txParamsButton, self.load_csv_button, self.load_database_button, self.save_database_button, self.row_entry]
        for i, widget in widgets:
            widget.grid(row=i, collumn=1)
        self.checkbuttons = {}
        for i, column in enumerate(self.data.get_df()):
            self.checkbuttons[column] = tk.BooleanVar() 
            checkbutton = tk.Checkbutton(self.root, text=column, variable=self.checkbuttons[column], command=self.__update_columns)
            checkbutton.grid(row=(i+len(widgets)), column=1)        
        
        self.roof.mainloop()
        
    def __load_from_csv(self):
        #check and prompt for correct input
        if self.txAntennaFilePath and self.txParamsFilePath:
            success = self.data.initialize_client_dataset(self.antennaFilePath, self.paramsFilePath)
            print('Dataset successfully loaded!') if success else print('One or more file paths incorrect!')
        else:
            print('One or more file paths incorrect!')
        
    def __load_from_database(self):
        #check and prompt for correct input
        success = self.data.load_from_database()
        print('Dataset successfully loaded!') if success else print('No Data on Files')
    
    def __save_to_database(self):
        #check and prompt for correct input
        success = self.data.save_to_database()
        print('Dataset successfully Saved!') if success else print('Save Unsuccessful!')
    
    def __update_rows(self,event):
        #check and prompt for correct input
        self.rows.clear()
        try:
            rows = int(self.row_entry.get().split(' ')) # update validation
        except:
            print('Entry Not in Range') # show to window
        self.rows = [row for row in rows if row in range(0,100)] # update range
        
    def __update_columns(self):
        #check and prompt for correct input and ouput
        self.columns.clear()
        for column, var in self.checkbuttons.items():
            if var.get():
                self.columns.append(column)
                
    def __update_antenna_filePath(self):
        #check and prompt for correct input
        self.txAntennaFilePath = filedialog.askopenfilename()
        # add to FilePath Text 
        
    def __update_params_filePath(self, event):
        #check and prompt for correct input
        self.txParamsFilePath = filedialog.askopenfilename()
        # add to FilePath Text
        
    def __populate_statistics(self):
        print('Populate Power Statistics')
        
    def __populate_correlation_graph():
        print('populate correlation graph')
        
    def __populate_location_correlation_graph():
        print('populate location correlation graph')
        
                
class Data:
    def __init__(self, serverAddress, databaseName, collectionName, antennaFilePath,paramsFilePath):
        self.serverAddress = serverAddress
        self.databaseName = databaseName
        self.collectionName = collectionName
        self.dfDAB = None
    
    def get_df(self):
        return self.dfDAB
    
    def __connect_to_server(self):
        client = MongoClient(self.serverAddress)
        database = client[self.databaseName]
        collection = database[self.collectionName]
        return client, collection
        
    def save_to_database(self):
        if self.dfDAB is not None:
            client, collection = self.__connect_to_server()
            formatted_df = self.dfDAB.to_dict(orient='records')
            success = None
            try: 
                collection.insert_many(formatted_df)
                sucess = True
            except:
                print('could not save data to collection')
                sucess = False
            client.close()
            return success
        else: print('No Data in Working Space!')
        
    def load_from_database(self):
        client, collection = self.__connect_to_server()
        results = collection.find()
        formatted_results = list(results)
        if formatted_results: 
            self.dfDAB = formatted_results
            client.close()
            return True
        else:
            print('No Data Saved in This collection!')
            client.close()
            return False
        
        
    def __cleaning_shaping(dfAntenna,dfParams):
        dfDAB = dfParams.merge(dfAntenna['NGR', 'Site Height', 'In-Use Ae Ht', 'In-Use ERP Total'], on='Id', how='left')
        dfDAB = dfDAB.query("EID in ['C18A', 'C18F', 'C188']")
        dfDAB = dfDAB['EID', 'Site', 'Site Height', 'In-Use Ae Ht', 'In-Use ERP Total', 'Freq', 'Block', 'Serv Label1', 'Serv Label2', 'Serv Label3', 'Serv label4','Serv Label10']
        dfDAB = dfDAB.rename({'In-Use Ae Ht': 'Aerial height (m)', 'In-Use ERP Total': 'Power (kW)'})
        return dfDAB

    def initialize_client_dataset(self, antennaFilePath, paramsFilePath):
        #load from file
        try:
            dfAntenna = pd.read_csv(antennaFilePath)
            dfParams = pd.read_csv(paramsFilePath)
        except:
            return False
        #shape and clean
        dfDAB = self.__cleaning_shaping(dfAntenna, dfParams)
        #load into workingspace
        self.dfDAB = dfDAB
        if self.dfDAB: return True
    
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