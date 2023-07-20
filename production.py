import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pymongo import MongoClient
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns

class GUI:
    def __init__(self,data):
        self.data = data
        self.txAntennaFilePath = None
        self.txParamsFilePath = None
        self.rows = ['C18A', 'C18F', 'C188']
                
        #gui init
        self.root = tk.Tk()
        self.root.title('Production')
        self.groupFrame = tk.Frame(self.root, width=100, height=100)
        self.buttonFrame = tk.Frame(self.groupFrame, width=10, height=100)
        
        #gui elements
        self.graphFrame = tk.Frame(self.groupFrame)
        self.__placeholder_graph()
        self.table = ttk.Treeview(self.groupFrame)
        self.__create_table
        self.txAntennaButton = tk.Button(self.buttonFrame, text='Find TxAntenna File', command=self.__update_antenna_filePath)
        self.txAntennaFilePathText =  tk.Text(self.buttonFrame, height=5, width=15)
        self.txParamsButton = tk.Button(self.buttonFrame, text='Find TxParams File', command=self.__update_params_filePath)
        self.txParamsFilePathText =  tk.Text(self.buttonFrame, height=5, width=15)
        self.load_csv_button = tk.Button(self.buttonFrame,text='Load From CSV', command=self.__load_from_csv)
        self.load_database_button = tk.Button(self.buttonFrame, text='Load From Database', command=self.__load_from_database)
        self.save_database_button = tk.Button(self.buttonFrame, text='Save To Database', command=self.__save_to_database)
        self.correlation_graph_button = tk.Button(self.buttonFrame, text='Standard Correlation Graph', command=self.__populate_correlation_graph)
        self.location_correl_graph_button = tk.Button(self.buttonFrame, text='Location Correlation Graph', command=self.__populate_location_correlation_graph)
            
        #gui layout
        # better looking layout
        self.groupFrame.grid(row=0,column=0)
        self.graphFrame.grid(row=0, column=0, sticky='nsew')
        self.table.grid(row=0, column=1, sticky='nsew')
        self.buttonFrame.grid(row=0,column=2, sticky='nsew')
        
        widgets = [self.txAntennaButton, self.txAntennaFilePathText, self.txParamsButton, self.txParamsFilePathText, self.load_csv_button, self.load_database_button, self.save_database_button, self.correlation_graph_button, self.location_correl_graph_button]
        for i, widget in enumerate(widgets):
            widget.pack(fill=tk.BOTH, expand=True)
        self.rowbuttons = {}
        for i, row in enumerate(self.rows):
            self.rowbuttons[row] = tk.BooleanVar(value=True) 
            checkbutton = tk.Checkbutton(self.buttonFrame, text=row, variable=self.rowbuttons[row], command=self.__update_rows)
            checkbutton.pack()     
                    
        self.root.mainloop()
        
    def __create_table(self):
        self.table["columns"] = ['Constraint', 'Mean', 'Median', 'Mode']

        self.table.heading("#0", text="ID")
        self.table.heading("Constraint", text="Constraint")
        self.table.heading("Mean", text="Mean")
        self.table.heading("Median", text="Median")
        self.table.heading("Mode", text="Mode")
    
    def __placeholder_graph(self):
        fig = plt.Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(1, 1, 1)

        # Create a FigureCanvasTkAgg widget that can be used in a Tkinter application
        canvas = FigureCanvasTkAgg(fig, master=self.graphFrame)
        canvas.draw()

        # Pack the canvas to fill the entire widget
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
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
        powerStatistics = self.data.power_statistics(self.rows)
        if powerStatistics: 
            heightConstraint = powerStatistics['heightConstraint']
            dateConstraint = powerStatistics['dateConstraint']
            content = [
                ['Height', heightConstraint['mean'], heightConstraint['median'],heightConstraint['mode']],
                ['Date', dateConstraint['mean'], dateConstraint['median'],dateConstraint['mode']]]
            for i, row in enumerate(content):
                self.table.insert("", "end", text=f"{i}", values=row)
            
        
    def __populate_correlation_graph(self):
        self.data.visualize_correlations(self.graphFrame, self.rows)
        
    def __populate_location_correlation_graph(self):
        self.data.visualize_location_impact_on_correlation(self.graphFrame, self.rows)
        
                
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
     
        
serverAddress = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.10.1'
databaseName = 'test'
collection  = 'DAB2'

data = Data(serverAddress, databaseName, collection)
gui = GUI(data)
