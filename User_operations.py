from kafka import KafkaConsumer
import mysql.connector
import json


class UserOperation:

    def __init__(self):
        self.consumer = KafkaConsumer('user',
                                      bootstrap_servers=["localhost:9092"],
                                      api_version=(0, 10)
                                      )
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="newuser",
            password="password"
        )
        self.cursor = self.mydb.cursor(buffered=True)
        self.cursor.execute("use demodb")
        self.initiate()

    def initiate(self):
        for message in self.consumer:
            value = message.value
            value = json.loads(value)
            print(value)
            operation_type = value['type']
            del value['type']
            if operation_type == 'C':
                return self.create_user(value)
            elif operation_type == 'R':
                return self.read_values(value)
            elif operation_type == 'U':
                return self.update_user(value)
            elif operation_type == 'D':
                return self.delete_user(value)
            else:
                return "Invalid Operation token. Allowed 'type' values are 'C', 'R', 'U', 'D'"

    def get_total_number_of_entries(self):
        self.cursor.execute("select count(*) from User;")
        return self.cursor.fetchall()[0][0]

    def create_user(self, value):
        sql_query = "Insert into User values("
        uid = self.get_total_number_of_entries() + 1
        values = str(uid)
        for val in value.values():
            if type(val) is str:
                val = "'" + val + "'"
            values += "," + str(val)
        sql_query += values + ")"
        self.cursor = self.mydb.cursor(buffered=True)
        self.cursor.execute(sql_query)
        self.cursor.execute("Commit")
        if self.cursor.rowcount > 0:
            return "User Added successfully"
        else:
            return "Unable to add successfully"

    def read_values(self, value):
        sql_query = "select * from User where "
        for key, values in value.items():
            if type(values) is str:
                values = "'" + values + "'"
            sql_query += key + " = " + str(values) + " >>> "
        sql_query = ' and '.join(sql_query.split(">>>")[:-1])
        self.cursor.execute(sql_query)
        return self.cursor.fetchall()

    def update_user(self, value):
        sql_query = "Update User set "
        for key, values in value['new_val'].items():
            if type(values) is str:
                values = "'" + values + "'"
            sql_query += key + " = " + str(values) + " >>> "
        sql_query = ' and '.join(sql_query.split(">>>")[:-1])

        sql_query += " where "
        for key, values in value['old_val'].items():
            if type(values) is str:
                values = "'" + values + "'"
            sql_query += key + " = " + str(values) + " >>> "
        sql_query = ' and '.join(sql_query.split(">>>")[:-1])
        self.cursor.execute(sql_query)

        if self.cursor.rowcount > 0:
            print("User Updated successfully : " + str(self.cursor.rowcount))
        else:
            print("Unable to updated the values successfully")
        self.cursor.execute("Commit")

    def delete_user(self, value):
        sql_query = "Delete from User where "
        for key, values in value.items():
            if type(values) is str:
                values = "'" + values + "'"
            sql_query += key + " = " + str(values) + " >>> "
        sql_query = ' and '.join(sql_query.split(">>>")[:-1])

        self.cursor.execute(sql_query)
        if self.cursor.rowcount > 0:
            print("User Deleted successfully : " + str(self.cursor.rowcount))
        else:
            print("Unable to delete the user successfully")
        self.cursor.execute("Commit")


# if __name__ == "__main__":
#     UserOperation().delete_user({'name': 'Arpana'})  # ,\

    # 'name':'Arpana',\
    # 'credit_limit':90000,\
    # 'credit_balance':90000})
    # UserOperation().update_user({'old_val' : {'name':'Arpana'}, "new_val" : {"credit_balance":85000}})#,
