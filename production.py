import tkinter as tk
from tkinter import filedialog
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
        self.rows = None
        self.columns = []
        
        #gui init
        self.root = tk.Tk()
        self.root.title('Production')
        
        #gui elements
        self.figure = plt.figure(figsize=(10,8))
        self.ax = self.figure.add_subplot(111)
        self.canvas = tk.Canvas(self.figure, self.root)
        self.canvas.draw()
        self.text =  tk.Text(self.root)
        self.txAntennaButton = tk.Button(self.root, text='Find TxAntenna File', command=self.__update_antenna_filePath)
        self.txParamsButton = tk.Entry(self.root, text='Find TxParams File', command=self.__update_params_filePath)
        self.load_csv_button = tk.Button(self.root,text='Load From CSV', command=self.__load_from_csv)
        self.load_database_button = tk.Button(self.root, text='Load From Database', command=self.__load_from_database)
        self.save_database_button = tk.Button(self.root, text='Save To Database', command=self.__save_to_database)
        self.correlation_graph_button = tk.Button(self.root, text='Standard Correlation Graph', command=self.__populate_correlation_graph)
        self.location_correl_graph_button = tk.Button(self.root, text='Location Correlation Graph', command=self.__populate_location_correlation_graph)
            
        #gui layout
        self.canvas.grid(row=0,column=0)
        self.text.grid(row=1,column=0)
        widgets = [self.txAntennaButton, self.txParamsButton, self.load_csv_button, self.load_database_button, self.save_database_button, self.row_entry]
        for i, widget in widgets:
            widget.grid(row=i, collumn=1)
        self.rowbuttons = {}
        for i, row in enumerate(self.data.get_multiplexes()):
            self.rowbuttons[row] = tk.BooleanVar() 
            checkbutton = tk.Checkbutton(self.root, text=row, variable=self.rowbuttons[row], command=self.__update_rows)
            row =  i + len(widgets)
            checkbutton.grid(row=row, column=1)   
        self.columnbuttons = {}
        for i, column in enumerate(self.data.get_df()):
            self.columnbuttons[column] = tk.BooleanVar() 
            checkbutton = tk.Checkbutton(self.root, text=column, variable=self.columnbuttons[column], command=self.__update_columns)
            row = i + len(widgets) + len(self.data.get_multiplexes())
            checkbutton.grid(row=row, column=1)        
        
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
        for row, var in self.rowbuttons.items():
            if var.get():
                self.rows.append(row)
        self.__populate_statistics()
        
    def __update_columns(self):
        #check and prompt for correct input and ouput
        self.columns.clear()
        for column, var in self.checkbuttons.items():
            if var.get():
                self.columns.append(column)
        self.__populate_statistics()
                
    def __update_antenna_filePath(self):
        #check and prompt for correct input
        self.txAntennaFilePath = filedialog.askopenfilename()
        # add to FilePath Text 
        
    def __update_params_filePath(self, event):
        #check and prompt for correct input
        self.txParamsFilePath = filedialog.askopenfilename()
        # add to FilePath Text
        
    def __populate_statistics(self):
        #check and prompt for correct input
        powerStatistics = self.data.power_statistics(self.rows,self.columns)
        if powerStatistics: 
            heightConstraint = powerStatistics['heightConstraint']
            dateConstraint = powerStatistics['dateConstraint']
            content = [
                ['Constraint', 'Mean', 'Median', 'Mode'],
                ['Height', heightConstraint['mean'], heightConstraint['median'],heightConstraint['mode'],],
                ['Date', dateConstraint['mean'], dateConstraint['median'],dateConstraint['mode']]]
            for i, row in enumerate(content):
                for j, element in enumerate(row):
                    self.text.insert(tk.END, element + ' ')
                    self.text.grid(row=i, column=j)
            
        
    def __populate_correlation_graph(self):
        try:
            self.data.visualize_correlations(self.ax, self.canvas, self.rows, self.columns)
        except:
            print('No Visualization')
        
    def __populate_location_correlation_graph(self):
        self.data.visualize_location_impact_on_correlation(self.ax, self.canvas,self.rows, self.columns)
        
                
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
        
    def power_statistics(self,rows,columns):
        if self.dfDAB:
            df = self.dfDAB.query(f'EID in {rows}')
            df = df[columns]
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
                'heightConstraint': powerStatisticsSiteHeightAbove75, 'dateConstraint': powerStatisticsDate2001Onward
            }
        else:
            print('No Data in Working Space!')
    
    def visualize_correlations(self, ax, canvas, rows, columns):
        if self.dfDAB:
            correlation_matrix = self.__compute_correlation_matrix(rows, columns)
            canvas.delete("all")
            ax.clear()
            sns.heatmap(correlation_matrix, cmp='coolwarm', annot=True, fmt='.2f', square=True, ax=ax)
            ax.set_title('Correlation Statistics')
            canvas.draw()
        else:
            print('No Data in Working Space!')
    
    def visualize_location_impact_on_correlation(self, ax, canvas, rows, columns):
        if self.dfDAB:
            correlation_matrix = self.__compute_correlation_matrix(rows, columns)
            df = self.dfDAB
            
            #find latitude and longitude of site
            geolocater = Nominatim(user_agent='production-app')
            df['Coordinates'] = df['Site'].apply(lambda x: geolocater.geocode(x).point if geolocater.geocode(x) else None)
            df['Latitude'] = df['Coordinates'].apply(lambda x: x.latitude if x.latitude else None)
            df['Longitude'] = df['Longitude'].apply(lambda x: x.longitude if x.longitude else None)

            canvas.delete("all")
            ax.clear()
            sns.heatmap(correlation_matrix, cmap='coolwarm', annot=True, fmt='.2f', square=True, ax=ax)
            ax.scatter(df['Longitude'], df['Latitude'], marker='x', color='red')
            ax.set_title('Affect of Location on Correlation Statistics')
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            canvas.draw()
            
        else:
            print('No Data in Working Space!')
    
    def __compute_correlation_matrix(self, rows, columns):
        if self.dfDAB:
            df = self.dfDAB.query(f"EID in {rows}")
            labels = 'Serv Label1', 'Serv Label2', 'Serv Label3', 'Serv label4','Serv Label10'
            df[labels] = df[[labels]].applymap(len) # apply numerical normilzation to data
            correlation_columns = labels.append('Freq.', 'Block')
            correlation_columns = [label for label in labels if label in columns] # filters all labels not selected for in GUI
            correlation_matrix = df[correlation_columns].corr()
            return correlation_matrix
        else:
            print('No Data in Working Space!')
     
        
serverAddress = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.10.1'
databaseName = 'test'
collection  = 'DAB'