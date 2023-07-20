import tkinter as tk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np


class GUI:
    def __init__(self,data):
        self.data = data
        self.txAntennaFilePath = None
        self.txParamsFilePath = None
        self.rows = ['C18A', 'C18F', 'C188']
                
        self.root = tk.Tk()
        self.root.title('Production')
        self.groupFrame = tk.Frame(self.root, width=100, height=100)
        self.buttonFrame = tk.Frame(self.groupFrame, width=10, height=100)
        
        self.graphFrame = tk.Frame(self.groupFrame)
        self.__placeholder_graph()
        self.statisticsText = tk.Text(self.groupFrame, wrap="word")
        self.txAntennaButton = tk.Button(self.buttonFrame, text='Find TxAntenna File', command=self.__update_antenna_filePath)
        self.txAntennaFilePathText =  tk.Text(self.buttonFrame, height=5, width=15)
        self.txParamsButton = tk.Button(self.buttonFrame, text='Find TxParams File', command=self.__update_params_filePath)
        self.txParamsFilePathText =  tk.Text(self.buttonFrame, height=5, width=15)
        self.load_csv_button = tk.Button(self.buttonFrame,text='Load From CSV', command=self.__load_from_csv)
        self.load_database_button = tk.Button(self.buttonFrame, text='Load From Database', command=self.__load_from_database)
        self.save_database_button = tk.Button(self.buttonFrame, text='Save To Database', command=self.__save_to_database)
        self.correlation_graph_button = tk.Button(self.buttonFrame, text='Standard Correlation Graph', command=self.__populate_correlation_graph)
        self.location_correl_graph_button = tk.Button(self.buttonFrame, text='Location Correlation Graph', command=self.__populate_location_correlation_graph)
            
        self.groupFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.graphFrame.grid(row=0, column=0, sticky='nsew')
        self.statisticsText.grid(row=0, column=1, sticky='nsew')
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
    
    
    def __placeholder_graph(self):
        fig = plt.Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(1, 1, 1)

        canvas = FigureCanvasTkAgg(fig, master=self.graphFrame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def __load_from_csv(self):
        if self.txAntennaFilePath and self.txParamsFilePath:
            success = self.data.initialize_client_dataset(self.txAntennaFilePath, self.txParamsFilePath)
            print('Dataset successfully loaded!') if success else print('Did not Load')
            if success: self.__populate_statistics()
        else:
            print('One or more file paths incorrect!')
        
    def __load_from_database(self):
        success = self.data.load_from_database()
        print('Dataset successfully loaded!') if success else print('No Data on Files')
        if success: self.__populate_statistics()
    
    def __save_to_database(self):
        success = self.data.save_to_database()
        print('Dataset successfully Saved!') if success else print('Save Unsuccessful!')
    
    def __update_rows(self):
        self.rows.clear()
        for row, var in self.rowbuttons.items():
            if var.get():
                self.rows.append(row)
        self.__populate_statistics()
        
    def __update_antenna_filePath(self):
        filePath = filedialog.askopenfilename()
        print(filePath)
        self.txAntennaFilePath = filePath
        if filePath:
            self.txAntennaFilePathText.delete("1.0",tk.END)
            self.txAntennaFilePathText.insert("1.0", filePath)
        
    def __update_params_filePath(self):
        filePath = filedialog.askopenfilename()
        print(filePath)
        self.txParamsFilePath = filePath
        if filePath:
            self.txParamsFilePathText.delete("1.0",tk.END)
            self.txParamsFilePathText.insert("1.0", filePath)
        
        
    def __populate_statistics(self):
        powerStatistics = self.data.power_statistics(self.rows)
        if powerStatistics:
            heightConstraint = powerStatistics['heightConstraint']
            dateConstraint = powerStatistics['dateConstraint']
            content = [
                ['Constraint:   ', 'Height>75     ', 'Date>=2001'],
                ['Mean       ', heightConstraint['mean'], dateConstraint['mean']],
                ['Median     ', heightConstraint['median'], dateConstraint['median']],
                ['Mode       ', heightConstraint['mode'], dateConstraint['mode']]]
            self.statisticsText.delete("1.0", tk.END)
            for i, row in enumerate(content):
                row = [ str(el)[0:3] if isinstance(el, np.float64) else str(el) for el in row]
                if i>0: self.statisticsText.insert("end", row[0]+'   '+row[1]+'            '+row[2]+ "\n")
                else: self.statisticsText.insert("end", ''.join(row)+ "\n")
            
        
    def __populate_correlation_graph(self):
        self.data.visualize_correlations(self.graphFrame, self.rows)
        
    def __populate_location_correlation_graph(self):
        self.data.visualize_location_impact_on_correlation(self.graphFrame, self.rows)