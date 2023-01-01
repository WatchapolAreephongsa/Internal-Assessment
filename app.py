'''
need to install kivymd, sqlalchemy,passlib,pandas-datareader,
matplotlib,numpy,pandas and yfinance(yahoo finance)
'''
import random
#import random to use random.randing
from datetime import date,datetime
#import datetime to get today date
from kivymd.app import MDApp
#MDApp to connect to class app to connect with kivy file
from kivymd.uix.datatables import MDDataTable
#MDDataTable to create datatable
from kivymd.uix.screen import MDScreen
#Use MDScreen to connect each class to the respective interface screen
#import from the SQLAlchemy the function to connect to a db
from sqlalchemy import create_engine, insert, select
#also the function to create a session and different tables from database_model.py
from sqlalchemy.orm import sessionmaker
from app_database import Base, users, stock_list
from passlib.context import CryptContext
#import cryptcontext to use sha256 to create hash of user's password
import pandas as pd
import pandas_datareader as web
#library to take stock data from internet
from yahoo_fin import stock_info as si #use yahoo_fin to get stock lists
import yfinance #use yfinance to get stock data from yahoo finance
import matplotlib.pyplot as plt #create a session to connect to the database
#import symbol list

##################################################################


#set the encryption with sha256 and hash 30000 rounds
pwd_context = CryptContext(
    schemes = ["pbkdf2_sha256"],
    default ="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds = 30000
)
#use cryptcontext to make hash of password 30,000 times
def encrypt_password(password):
    #encrypt the inputted password
    return pwd_context.encrypt(password)


def check_password(password,hashed):
    #compare the inputted password with the inputted hash from database
    return pwd_context.verify(password,hashed)

#connect to the database file to create the database and table in the database
db_engine = create_engine("sqlite:///application_database.db")
Base.metadata.bind = db_engine #bind the database to the base
db_session = sessionmaker(bind = db_engine) #create a session to connect to the database
session = db_session()

ticker = [si.tickers_dow(),si.tickers_sp500(),si.tickers_nasdaq()] #get the symbols list from yahoo finance

symbol = [] #create a list to store the symbols
for i in ticker: #loop to store symbols in ticker in symbols list
    df = pd.DataFrame(i)
    symbol +=set( symbol for symbol in df[0].values.tolist())

class LoginScreen(MDScreen):
    #class that links to the login screen to create function
    def login(self):
        #first function to login
        username = self.ids.username.text #get the username from the input in the login screen
        password =self.ids.password.text #get the password from the input in the login screen
        user_check = session.query(users).filter(users.username == username).first() #query the database to check if the username is in the database
        if not user_check:
            # if the user is not in the database text below will shows
            self.ids.msg.text = "User doesn't exist. Please register."
            self.ids.msg.text_color = 1, 0, 0, 1
        else:
            # if user exists the database will be query by email to check password using check_pass function
            pwd = session.query(users.password).filter(users.username == username)
            for row in pwd:
                pwd = row[0]
            checkpass = check_password(password, pwd) #check the password using check_password function
            if checkpass :
                # if the password is correct then the welcome screen will be opened
                self.parent.current = "HomeScreen"
            else:
                # if password is wrong the below message will be shown at the bottom of screen
                self.ids.msg.text = "Wrong password"
                self.ids.msg.text_color = 1, 0, 0, 1




class RegisterScreen(MDScreen): #class that links to the register screen to create function
    def register(self):
        #define variable for the inputted password,username and confirm password
        password = self.ids.password.text
        confirm = self.ids.confirm.text
        username = self.ids.username.text
        check_user = session.query(users).filter(users.username == username).all()
        #check if the username is used or not
        if password == ""or confirm == "": # check if the password is not empty
            self.ids.msg.text = "password needed"
            self.ids.msg.text_color = 1, 0, 0,1
        else:
            if password == confirm and not check_user:
                check_id = True # create unique random id
                while check_id:
                    id = random.randint(1, 99999)
                    check_id = session.query(users).filter(users.id == id).all()
                password = encrypt_password(password)
                new_user = users(id=id,
                            username=username,
                            password=password
                            ) #create new user
                session.add(new_user)#add new user to database
                session.commit()#commit the change to database
                self.parent.ids.loginscr.ids.username.text = self.ids.username.text
                self.parent.current = "HomeScreen" #go to home screen

            if password!=confirm:
                self.ids.msg.text = "password doesn't match"
                self.ids.msg.text_color = 1, 0, 0, 1
            else:
                self.ids.msg.text = "Username used, please change your user name or login."
                self.ids.msg.text_color = 1, 0, 0, 1
    def on_pre_enter(self, *args):
        # make all the textfield blank before enter the screen
        self.ids.confirm.text = ""
        self.ids.username.text = ""
        self.ids.password.text = ""
        self.ids.msg.text = ""
    def back(self): #go back to login screen
        self.parent.ids.loginscr.ids.username.text = ""
        self.parent.ids.loginscr.ids.password.text = ""
        self.parent.current = "LoginScreen"
        self.parent.ids.loginscr.ids.msg.text_color = 0, 0, 0, 1
        self.parent.ids.loginscr.ids.msg.text = 'Get Rich.'



class HomeScreen(MDScreen): #class that links to the home screen to create function
    def logout(self): #logout function
        self.parent.ids.loginscr.ids.username.text = ""
        self.parent.ids.loginscr.ids.password.text = ""
        self.parent.current = "LoginScreen"
        self.parent.ids.loginscr.ids.msg.text_color = 0, 0, 0, 1
        self.parent.ids.loginscr.ids.msg.text = 'Get Rich.'

class InfoScreen(MDScreen):
    def on_pre_enter(self, *args): #make datatable template, delete all the data in the datatable and clear the label
        self.data_tables = MDDataTable(
            size_hint=(0.9, 0.6),  # size of table
            use_pagination=True,  # use of pagination
            pos_hint={"center_x": 0.5, "center_y": 0.6},  # position of table
            column_data=[("Date", 50), ("High($)", 30), ("Low($)", 30), ("Open($)", 30), ("Close($)", 30),
                         ("Volume(Mil)", 40), ("Adj Close($)", 40), ("Change (%)", 40)],
        )
        self.ids.label.text = ""
        self.add_widget(self.data_tables)

    def on_leave(self, *args): #delete the textfield when leave the screen
        self.ids.symbol.text = ""
    def searching(self): #search function
        stock_search = self.ids.symbol.text #get the symbol from the input
        today = date.today() #get today's date
        year = today.year #get the year from today's date
        end = today.strftime("%Y-%m-%d") #format the date to be in the form of year-month-day
        start = datetime(int(year), 1, 1).strftime('%Y-%m-%d') #get the start date of the year
        search="" #create a variable to store the letter
        for i in range(len(stock_search)): #loop that change the lower cases inputs to upper cases
            if ord(stock_search[i])>=90:
                search += stock_search[i].upper()
            else:
                search += stock_search[i]
        self.ids.symbol.text = search
        if search not in symbol: #check if the symbol is in the list defined above of all the symbols or not
            self.ids.label.text_color = 1, 0, 0, 1
            self.ids.label.text = "Symbol invalid"
        else:
            name = yfinance.Ticker(stock_search) #get the name of the company
            name = name.info['longName']
            with pd.option_context('display.max_rows', None, 'display.max_columns',
                                   None):  # display all the rows and columns of the information retrieved
                data = web.DataReader(str(search), 'yahoo',start=start,end=end)
                change = data['Adj Close'].pct_change() * 100 #calculate the change of the stock price
                data = data.join(change, rsuffix=' Change')  # join the change column to the dataframe
                data = data[1:].round(decimals=3) #round the data to 3 decimal places
                data['Volume'] = data['Volume']//1000000 #change the volume to millions
                self.ids.label.text_color = 0, 0, 0, 1
                self.ids.label.text = f"This is the YTD stock price of {name}({search}) stock" #display the name of the company and the symbol
                data = data.sort_values(by='Date', ascending=False) #sort the data by date

                data = data.reset_index()
                result = data.values.tolist() #convert the dataframe to list
                info = [] #create a list to store the data of the stock
                for q in range(len(data)):
                    info.append(result[q])  # add data to the list
                self.data_tables = MDDataTable(
                    size_hint=(0.9, 0.6),  # size of table
                    use_pagination=True,  # use of pagination
                    pos_hint={"center_x": 0.5, "center_y": 0.6},  # position of table
                    column_data=[("Date", 50), ("High($)", 30), ("Low($)", 30), ("Open($)", 30), ("Close($)", 30),
                                 ("Volume(Mil)", 40), ("Adj Close($)", 40), ("Change (%)", 40)],
                    row_data= info,
                ) #create a datatable with the data of the stock
                self.add_widget(self.data_tables) #add the datatable to the screen

    def graph(self): #graph function
        symbol = self.ids.symbol.text
        today = date.today()
        year = today.year
        name = yfinance.Ticker(symbol)
        name = name.info['longName']
        end = today.strftime("%Y-%m-%d")
        start = datetime(int(year), 1, 1).strftime('%Y-%m-%d')

        with pd.option_context('display.max_rows', None, 'display.max_columns',
                               None):  # more options can be specified also
            data = web.DataReader(str(symbol), 'yahoo', start=start, end=end)
        fig, ax = plt.subplots(dpi=250, figsize=(15, 8)) #create a figure and axis for the graph
        if self.ids.shortma.active == True: #check if the 20 days moving average checkbox is checked
            data['Adj Close'].rolling(20).mean().plot(label='20 Day MA Adj Close') #plot the 20 days moving average
        if self.ids.longma.active == True:  # check if the 75 days moving average checkbox is checked
            data['Adj Close'].rolling(75).mean().plot(label='75 Day MA Adj Close') #plot the 75 days moving average
        if self.ids.bolinger.active == True: #check if the bolinger band checkbox is checked
            data['MA'] = data['Adj Close'].rolling(20).mean() #calculate the 20 days moving average
            data['STD'] = data['Adj Close'].rolling(20).std()  # calculate the standard deviation of the 20 days price
            data['BOL_UPPER'] = data['MA'] + 2 * data['STD'] #calculate the upper band of the bolinger band by adding 2 standard deviation to the moving average
            data['BOL_LOWER'] = data['MA'] - 2 * data['STD'] #calculate the lower band of the bolinger band by subtracting 2 standard deviation to the moving average
            data[['BOL_UPPER', 'BOL_LOWER']].plot(ax=ax, label='20 Days Bolinger Bands') #plot the bolinger bands
        data['Adj Close'].plot(ax=ax,ylabel='Price ($)',title=f"{name}({symbol}) Stock Price",label='Adj Close Price') #plot the adjusted close price
        plt.legend(loc=(1,0.5)) #display the legend
        plt.show() #show the graph

    def download(self): #download function
        symbol = self.ids.symbol.text
        today = date.today()
        year = today.year
        name = yfinance.Ticker(symbol)
        name = name.info['longName']
        end = today.strftime("%Y-%m-%d")
        start = datetime(int(year), 1, 1).strftime('%Y-%m-%d')

        with pd.option_context('display.max_rows', None, 'display.max_columns',
                               None):  # more options can be specified also
            data = web.DataReader(str(symbol), 'yahoo', start=start, end=end)
        fig, ax = plt.subplots(dpi=250, figsize=(15, 8))
        if self.ids.shortma.active == True:
            print("AA")
            data['Adj Close'].rolling(20).mean().plot(label='20 Day MA Adj Close')
        if self.ids.longma.active == True:
            data['Adj Close'].rolling(75).mean().plot(label='75 Day MA Adj Close')
        if self.ids.bolinger.active == True:
            data['MA'] = data['Adj Close'].rolling(20).mean()
            data['STD'] = data['Adj Close'].rolling(20).std()
            data['BOL_UPPER'] = data['MA'] + 2 * data['STD']
            data['BOL_LOWER'] = data['MA'] - 2 * data['STD']
            data[['BOL_UPPER', 'BOL_LOWER']].plot(ax=ax, label='20 Days Bolinger Bands')
        data['Adj Close'].plot(ax=ax, ylabel='Price ($)', title=f"{name}({symbol}) Stock Price",
                               label='Adj Close Price')
        plt.legend(loc=(1, 0.5))
        fig.savefig(f'{name}_graph.png', bbox_inches='tight') #save the graph as a png file
    def save(self): #save function
        username = self.parent.ids.loginscr.ids.username.text #get the username from the login screen
        user_id = session.query(users).filter(users.username == username).first().id #get the user id by querying the database with the username inputted
        stock_symbol = self.ids.symbol.text
        if stock_symbol in symbol: #check if the stock symbol is in the list of stock symbol
            check_stock_id = True  # create unique random id
            while check_stock_id: # check if the id is unique
                stock_id = random.randint(1, 99999) #generate a random id
                check_stock_id = session.query(stock_list).filter(stock_id == id).all() #check if the id is unique

            stock_name = yfinance.Ticker(stock_symbol)
            stock_name = stock_name.info['longName']
            new_stock = stock_list(id=stock_id, user_id=user_id, symbol=stock_symbol, stock_name=stock_name)
            session.add(new_stock)
            session.commit() #add the stock to the database
            self.ids.label.text_color = 0, 0, 0, 1
            self.ids.label.text = "Stock saved"


        else:
            self.ids.label.text_color = 1, 0, 0, 1
            self.ids.label.text = "Symbol invalid"





class StockScreen(MDScreen):

    def on_pre_enter(self, *args): #on pre enter function
        user_id = session.query(users).filter(users.username == self.parent.ids.loginscr.ids.username.text).first().id #get the user id by querying the database with the username inputted
        print(user_id)
        query = session.query(stock_list).filter(stock_list.user_id == user_id).all()
        print(query)
        result = [] #create a list to store the result
        for q in query: #loop through the query
            result.append([q.symbol, q.stock_name])
            print(q.symbol)
        self.data_tables = MDDataTable(
            size_hint=(0.9, 0.6),  # size of table
            use_pagination=True,  # use of pagination
            check = True,
            pos_hint={"center_x": 0.5, "center_y": 0.5},  # position of table
            column_data=[("Symbol",60), ("Stock Name", 150)],
            row_data = result
        ) #create a data table
        self.data_tables.bind(on_row_press=self.on_row_press)
        # bind with function row_press to detect when the row has been pressed
        self.add_widget(self.data_tables)


    def on_row_press(self,instance_table, instance_row): #on row press function
        result = instance_row.text
        if len(result)>5: #check if the length of the result is greater than 5
            result =  session.query(stock_list).filter(stock_list.stock_name ==result).first().symbol #get the stock symbol by querying the database with the stock name
        self.parent.ids.InfoScreen.ids.symbol.text = result #set the text of the symbol text input to the stock symbol
        index = instance_row.index #get the index of the row
        cols_num = len(instance_table.column_data)
        row_num = int(index / cols_num)
        col_num = index % cols_num
        cell_row = instance_table.table_data.view_adapter.get_visible_view(row_num * cols_num)
        if cell_row.ids.check.state == 'normal':
            instance_table.table_data.select_all('normal')
            cell_row.ids.check.state = 'down'
        else:
            cell_row.ids.check.state = 'normal'
        instance_table.table_data.on_mouse_select(instance_row)

    def delete(self): #delete row function
        user_id = session.query(users).filter(users.username == self.parent.ids.loginscr.ids.username.text).first().id #get the user id by querying the database with the username inputted
        symbol = session.query(stock_list).filter(stock_list.user_id == user_id,stock_list.symbol==self.parent.ids.InfoScreen.ids.symbol.text).delete()
        #delete the stock from the database by querying the database with the user id and the stock symbol
        session.commit() #commit the changes
        query = session.query(stock_list).filter(stock_list.user_id == user_id).all() #query the database with the user id
        result = [] #create a list to store the result
        for q in query: #loop through the query
            result.append([q.symbol, q.stock_name]) #append the stock symbol and the stock name to the list
        self.data_tables = MDDataTable(
            size_hint=(0.9, 0.6),  # size of table
            use_pagination=True,  # use of pagination
            check=True,
            pos_hint={"center_x": 0.5, "center_y": 0.5},  # position of table
            column_data=[("Symbol", 60), ("Stock Name", 150)],
            row_data=result
        ) #create a data table from the list
        self.data_tables.bind(on_row_press=self.on_row_press)
        # bind with function row_press to detect when the row has been pressed
        self.add_widget(self.data_tables)
    def info(self):
        self.parent.current = 'InfoScreen' #change the screen to the info screen




class app(MDApp): #main app class
    '''class with the same name 23as .kv file'''
    def build(self):
        return

k = app()
#define the variable which belong to class app to activate run method
# from MDApp class imported
k.run()

