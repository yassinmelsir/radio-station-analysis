import tkinter as tk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns

class GUI:
    def __init__(self,data):
        self.data = data
        self.txAntennaFilePath = None
        self.txParamsFilePath = None
        self.rows = ['C18A', 'C18F', 'C188']
        self.columns = ['Freq.', 'Block','Serv Label1 ', 'Serv Label2 ', 'Serv Label3 ', 'Serv Label4 ','Serv Label10 ']
        
        #gui init
        self.root = tk.Tk()
        self.root.title('Production')
        
        #gui elements
        self.figure = plt.figure(figsize=(3,2))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.draw()
        self.text =  tk.Text(self.root)
        self.rightFrame = tk.Frame(self.root)
        self.txAntennaButton = tk.Button(self.rightFrame, text='Find TxAntenna File', command=self.__update_antenna_filePath)
        self.txAntennaFilePathText =  tk.Text(self.rightFrame, height=5)
        self.txParamsButton = tk.Button(self.rightFrame, text='Find TxParams File', command=self.__update_params_filePath)
        self.txParamsFilePathText =  tk.Text(self.rightFrame, height=5)
        self.load_csv_button = tk.Button(self.rightFrame,text='Load From CSV', command=self.__load_from_csv)
        self.load_database_button = tk.Button(self.rightFrame, text='Load From Database', command=self.__load_from_database)
        self.save_database_button = tk.Button(self.rightFrame, text='Save To Database', command=self.__save_to_database)
        self.correlation_graph_button = tk.Button(self.rightFrame, text='Standard Correlation Graph', command=self.__populate_correlation_graph)
        self.location_correl_graph_button = tk.Button(self.rightFrame, text='Location Correlation Graph', command=self.__populate_location_correlation_graph)
            
        #gui layout
        # better looking layout
        for i in range(0,1+1):
            self.root.grid_rowconfigure(i, weight=1)
            self.root.grid_columnconfigure(i, weight=1)
       
        
        self.canvas.get_tk_widget().grid(row=0,column=0)
        self.text.grid(row=1,column=0)
        self.rightFrame.grid(row=0,column=1, rowspan=2)
        widgets = [self.txAntennaButton, self.txAntennaFilePathText, self.txParamsButton, self.txParamsFilePathText, self.load_csv_button, self.load_database_button, self.save_database_button, self.correlation_graph_button, self.location_correl_graph_button]
        for i, widget in enumerate(widgets):
            widget.pack()
        self.rowbuttons = {}
        for i, row in enumerate(self.rows):
            self.rowbuttons[row] = tk.BooleanVar(value=True) 
            checkbutton = tk.Checkbutton(self.rightFrame, text=row, variable=self.rowbuttons[row], command=self.__update_rows)
            checkbutton.pack()
        self.columnbuttons = {}
        for i, column in enumerate(self.columns):
            self.columnbuttons[column] = tk.BooleanVar(value=True) 
            checkbutton = tk.Checkbutton(self.rightFrame, text=column, variable=self.columnbuttons[column], command=self.__update_columns)
            checkbutton.pack()     
                    
        self.root.mainloop()
        
        
    def __load_from_csv(self):
        #check and prompt for correct input
        if self.txAntennaFilePath and self.txParamsFilePath:
            success = self.data.initialize_client_dataset(self.txAntennaFilePath, self.txParamsFilePath)
            print('Dataset successfully loaded!') if success else print('Did not Load')
            if success: self.__populate_statistics()
        else:
            print('One or more file paths incorrect!')
        
    def __load_from_database(self):
        #check and prompt for correct input
        success = self.data.load_from_database()
        print('Dataset successfully loaded!') if success else print('No Data on Files')
        if success: self.__populate_statistics()
    
    def __save_to_database(self):
        #check and prompt for correct input
        success = self.data.save_to_database()
        print('Dataset successfully Saved!') if success else print('Save Unsuccessful!')
    
    def __update_rows(self):
        #check and prompt for correct input
        self.rows.clear()
        for row, var in self.rowbuttons.items():
            if var.get():
                self.rows.append(row)
        self.__populate_statistics()
        
    def __update_columns(self):
        #check and prompt for correct input and ouput
        self.columns.clear()
        for column, var in self.columnbuttons.items():
            if var.get():
                self.columns.append(column)
        self.__populate_statistics()
                
    def __update_antenna_filePath(self):
        #check and prompt for correct input
        filePath = filedialog.askopenfilename()
        print(filePath)
        # add to FilePath Text 
        self.txAntennaFilePath = filePath
        if filePath:
            self.txAntennaFilePathText.delete("1.0",tk.END)
            self.txAntennaFilePathText.insert("1.0", filePath)
        
    def __update_params_filePath(self):
        #check and prompt for correct input
        filePath = filedialog.askopenfilename()
        print(filePath)
        # add to FilePath Text 
        self.txParamsFilePath = filePath
        if filePath:
            self.txParamsFilePathText.delete("1.0",tk.END)
            self.txParamsFilePathText.insert("1.0", filePath)
        
        
    def __populate_statistics(self):
        #check and prompt for correct input
        powerStatistics = self.data.power_statistics(self.rows,self.columns)
        breakpoint()
        print(powerStatistics)
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
        self.data.visualize_correlations(self.ax, self.figure, self.canvas, self.rows, self.columns)
        
    def __populate_location_correlation_graph(self):
        self.data.visualize_location_impact_on_correlation(self.ax, self.figure, self.canvas, self.rows, self.columns)
        
                
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
        dfDAB = dfDAB[['EID', 'Site', 'Freq.', 'Block', 'Serv Label1 ', 'Serv Label2 ', 'Serv Label3 ', 'Serv Label4 ','Serv Label10 ','Site Height', 'In-Use Ae Ht', 'In-Use ERP Total']]
        dfDAB = dfDAB.rename({'In-Use Ae Ht': 'Aerial height (m)', 'In-Use ERP Total': 'Power (kW)'})
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
        
    def power_statistics(self,rows,columns):
        # working statistics
        if self.dfDAB.shape[0] > 0:
            
            df = self.dfDAB.query(f'EID in {rows}')
            df = df[columns]
            # mean mode median for multiplex with site height greater than 75
            breakpoint()
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
            print(powerStatisticsSiteHeightAbove75, powerStatisticsDate2001Onward)
            breakpoint()
            return {
                'heightConstraint': powerStatisticsSiteHeightAbove75, 'dateConstraint': powerStatisticsDate2001Onward
            }
        else:
            print('No Data in Working Space!')
    
    def visualize_correlations(self, ax, figure, canvas, rows, columns):
        # pretty up heatmap
        if self.dfDAB.shape[0] > 0:
            correlation_matrix = self.__compute_correlation_matrix(rows, columns)
            figure.clf()
            ax.clear()
            sns.heatmap(correlation_matrix, cmap='coolwarm', annot=True, fmt='.2f', square=True, ax=ax)
            ax.set_title('Correlation Statistics')
            canvas.draw()
        else:
            print('No Data in Working Space!')
    
    def visualize_location_impact_on_correlation(self, ax, figure, canvas, rows, columns):
        # working graph
        if self.dfDAB.shape[0] > 0:
            
            df = self.dfDAB.query(f"EID in {rows}")
            df = df[['EID','Site']+columns]
            stringColumns = df.columns.difference(['Freq.', 'Block'])
            labelEncoder = LabelEncoder()
            df['Block'] = labelEncoder.fit_transform(df['Block'])
            df[stringColumns] = df[stringColumns].applymap(len)
            
            
            grouped_df = df.groupby('EID')
            mean_values = grouped_df.mean()
            x_positions = np.arange(len(columns))
            bar_width = 0.2
            colors = ['red', 'green', 'blue']

            figure.clf(), ax.clear()
            print(mean_values)
            # Plot the bars for each EID
            for i, eid in enumerate(mean_values.index):
                ax.bar(x_positions + i * bar_width, mean_values.loc[eid, columns], width=bar_width, label=eid, color=colors[i])

            # Set the x-axis tick labels to the column names
            ax.set_xticks(x_positions)
            ax.set_xticklabels(columns)

            # Add labels, legend, and title
            ax.set_xlabel('Columns')
            ax.set_ylabel('Mean Values')
            ax.set_title('Mean Values for Different EIDs')

            # Show the legend
            ax.legend()
            
            canvas.draw()
            
        else:
            print('No Data in Working Space!')
    
    def __compute_correlation_matrix(self, rows, columns):
        if self.dfDAB.shape[0] > 0:
            df = self.dfDAB.query(f"EID in {rows}")
            labels = ['Serv Label1 ', 'Serv Label2 ', 'Serv Label3 ', 'Serv Label4 ', 'Serv Label10 ']
            df[labels] = df[labels].applymap(len) # apply numerical normilzation to data
            correlation_columns = labels + ['Freq.', 'Block']
            correlation_columns = [label for label in labels if label in columns] # filters all labels not selected for in GUI
            correlation_matrix = df[correlation_columns].corr()
            return correlation_matrix
        else:
            print('No Data in Working Space!')
     
        
serverAddress = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.10.1'
databaseName = 'test'
collection  = 'DAB'

data = Data(serverAddress, databaseName, collection)
gui = GUI(data)
