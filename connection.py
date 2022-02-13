import mysql.connector
from mysql.connector import Error

class DBConnection:
    def __init__(self, db):
        self.con = mysql.connector.connect(
          host="ADD YOUR HOST",
          database=db,
          user="ADD DATABASE USER",
          password="ADD USER'S PASSWORD")

    def get_connection(self):
        return self.con
