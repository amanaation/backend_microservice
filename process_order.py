from kafka import KafkaConsumer
import mysql.connector
import json
import time


class ProcessOrder:

    def __init__(self):
        self.consumer = KafkaConsumer('practise',
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
        # self.initiate_order()

    def initiate_order(self):
        for message in self.consumer:
            value = message.value
            value = json.loads(value)
            print(value)
            self.processing(value)
            print("Completed Processing ")

    def insert_data(self, values):
        print(" -*- "*10)
        print(values)
        self.cursor = self.mydb.cursor(buffered=True)

        # Convert each value to str type and add "'" to str type values which is mandatory for sql queries
        for i in range(len(values)):
            val = values[i]
            if type(val) is str:
                val = "'" + val + "'"
            values[i] = str(val)

        query_values = "(" + ', '.join(values) + ")"

        # Inserting Order initialised event
        initialize_event_query = "Insert into Order_details values " + query_values
        print(initialize_event_query)
        self.cursor.execute(initialize_event_query)
        self.cursor.execute("Commit")


    def processing(self, value):
        # Fetch last order id from Order_details table
        self.cursor.execute("select count(orderid) from Order_details;")
        new_order_id = self.cursor.fetchall()[0][0] + 1

        # Fetch last event id from Order_details table
        self.cursor.execute("select count(eventid) from Order_details;")
        new_event_id = self.cursor.fetchall()[0][0] + 1

        values = [new_event_id, new_order_id, value["uid"], "Initialised", time.ctime(), value['amount'],
                  " Order initalised"]
        # print("//////////  ", values)
        self.insert_data(values)
        values = [new_event_id, new_order_id, value["uid"], "Initialised", time.ctime(), value['amount'],
                  " Order initalised"]
        self.process_event(values)

    def process_event(self, values):
        values[0] += 1
        uid = values[2]
        ord_amount = values[5]
        self.cursor.execute("select credit_balance from User where uid = " + str(uid))
        crd_balance = self.cursor.fetchall()[0][0]

        if int(crd_balance) >= int(ord_amount):
            order_status = "Completed"
            order_notes = "Order placed successfully"
            self.update_balance(int(crd_balance) - int(ord_amount), uid)

        else:
            order_status = "Declined"
            order_notes = "Insufficient Balance!! Order Declined"
        values[3] = order_status
        time.sleep(2)
        values[4] = time.ctime()
        values[6] = order_notes
        #print("............", values)
        self.insert_data(values)

    def update_balance(self, balance, uid):
        self.cursor.execute("Update User set credit_balance = " + str(balance) \
                            + " where uid = " + str(uid))


if __name__ == "__main__":
    ProcessOrder().processing({'uid': '2',
                               'amount': 30000})
    # ProcessOrder().process_event([0,1,2,3,4,5])
    # ProcessOrder()
