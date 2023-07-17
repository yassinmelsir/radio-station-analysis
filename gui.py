import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GUI:
    def __init__(self,data):
        self.data = data
        self.rows = []
        self.columns = []
        
        #gui init
        self.root = tk.Tk()
        self.root.title('Production')
        
        #gui elements
        self.canvas = tk.Canvas(self.root, width=400, height=300)
        self.text =  tk.Text(self.root)
        self.load_csv_button = tk.Button(self.root,text='Load From CSV', command=self.__load_from_csv)
        self.load_database_button = tk.Button(self.root, text='Load From Database', command=self.__load_from_database)
        self.save_database_button = tk.Button(self.root, text='Save To Database', command=self.__save_to_database)
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(self.root, textvariable=self.entry_var)
        self.entry.bind("<KeyRelease>", self.__update_rows)
        self.checkbuttons = {}
        for i, column in enumerate(self.data.get_df()):
            self.checkbuttons[column] = tk.BooleanVar() 
            checkbutton = tk.Checkbutton(self.root, text=column, variable=self.checkbuttons[column], command=self.__update_columns)
            checkbutton.grid(row=(i+3), column=1)
            
            
        #gui layout
        self.canvas.grid(row=0,column=0)
        self.text.grid(row=1,column=0)
        self.load_csv_button.grid(row=0,column=1)
        self.load_database_button.grid(row=1,column=1)
        self.save_database_button.grid(row=2,column=1)
        self.entry.grid(row=3,column=1)
        
        
        self.roof.mainloop()
        
    def __load_from_csv(self):
        print('load from csv')
        
    def __load_from_database(event):
        print('load from database')
    
    def __save_to_database(self):
        print('save to database')
    
    def __update_rows(self):
        self.rows.clear()
        try:
            rows = int(self.entry.get().split(' ')) # update validation
        except:
            print('Entry Not in Range') # show to window
        self.rows = [row for row in rows if row in range(0,100)] # update range
        
    def __update_columns(self):
        self.columns.clear()
        for column, var in self.checkbuttons.items():
            if var.get():
                self.columns.append(column)
            
        
        


        