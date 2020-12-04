import mysql.connector


class ConnectToSQL():

    def __init__(self):
        mydb = mysql.connector.connect(
            host="localhost",
            user="newuser",
            password="password"
        )

        self.cursor = mydb.cursor()