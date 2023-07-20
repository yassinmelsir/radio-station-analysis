from gui import GUI
from data import Data

serverAddress = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.10.1' # fill with your mongo server address
databaseName = 'blank' # give new database name
collection  = 'blank' # give new collection name

data = Data(serverAddress, databaseName, collection)
gui = GUI(data)