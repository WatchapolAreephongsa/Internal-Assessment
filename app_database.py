#database_models
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base
#import base and elements in the table and define it
Base = declarative_base()

class users(Base):
    #create table by making class of that table and define the table name as users
    __tablename__ = "users"
    #Give the detail to each column of table
    id = Column(Integer, primary_key=True) #set as the primary unique key for each user
    username = Column(String(250),unique=True)
    password = Column(String(256), nullable=False)
#another data table to store the stock information for each user with id being the key and user id be the connector with the user tabe
class stock_list(Base):
    __tablename__ = "stock_list"
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer)
    symbol = Column(String(10))
    stock_name = Column(String(20))


db_engine = create_engine("sqlite:///application_database.db")
#create the database
Base.metadata.create_all(db_engine)
