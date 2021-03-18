from flask import request
from flask import Flask
import ast
from kafka import KafkaProducer
import json

# Initialise Flask app and Kafka Producer 
app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers=["localhost:9092"],
                         api_version=(0, 10)
                         )


@app.route('/order', methods=['GET', 'POST'])
def order():
    publish(dict(request.args), 'order')
    return '0'


@app.route('/user', methods=['GET', 'POST'])
def user():
    publish(dict(request.args), 'user')
    return '0'


def publish(value, topic):
    print(value)

    for val in value:
        try:
            value[val] = ast.literal_eval(value[val])
        except:
            pass
    producer.send(topic, json.dumps(value).encode("utf-8"))
    print("Done")


if __name__ == '__main__':
    app.run()
