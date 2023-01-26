import psycopg2
from sys import exit

class Database_connect:
    def __init__(self,username,password,database):
        self.conn = None
        try:
            self.conn = psycopg2.connect(
                                 user=username,
                                 password=password,
                                 host="localhost",
                                 database=database
                             )
            self.conn.autocommit = True
        except Exception as e:
            exit(f"Something went wrong during database connection...\nError: {e}")
    def close(self):
        if self.conn != None:
            self.conn.close()
