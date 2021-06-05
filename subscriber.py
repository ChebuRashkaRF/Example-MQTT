import paho.mqtt.client as mqtt
import time
from influxdb import InfluxDBClient
from queue import Queue

INFLUXDB_ADDRESS = '127.0.0.1'
INFLUXDB_USER = 'telegraf'
INFLUXDB_PASSWORD = 'telegraf'
INFLUXDB_DATABASE = 'arconoid'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER,
                                 INFLUXDB_PASSWORD, database=INFLUXDB_DATABASE)


# json данные тележки
def send_coords_cart_to_influxdb(x: int, y: int) -> None:
    json_body = [
        {
            "measurement": "cart",
            "tags": {
                "host": "game",
            },
            "fields": {
                "cart_x": int(x),
                "cart_y": int(y)
            }
        }
    ]
    influxdb_client.write_points(json_body)
    return None


# json данные шарика
def send_coords_ball_to_influxdb(x: int, y: int) -> None:
    json_body = [
        {
            "measurement": "ball",
            "tags": {
                "host": "game",
            },
            "fields": {
                "ball_x": int(x),
                "ball_y": int(y)
            }
        }
    ]
    influxdb_client.write_points(json_body)
    return None


# создание БД
def init_influxdb_database() -> None:
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE,
                       databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)
    return None


# Функция для получение данных
def on_message(client, userdata, message):
    data = str(message.payload.decode("utf-8"))
    if message.topic == 'arconoid/cart':
        print("message received cart coords: ",
              str(message.payload.decode("utf-8")))
        print("message topic: ", message.topic)
        q1.put(data)
    elif message.topic == 'arconoid/ball':
        print("message received ball coords: ",
              str(message.payload.decode("utf-8")))
        print("message topic: ", message.topic)
        q2.put(data)


q1 = Queue()
q2 = Queue()
time.sleep(15)
init_influxdb_database()
client = mqtt.Client("Subscriber")
client.on_message = on_message
client.connect("127.0.0.1", 1883, 60)
client.loop_start()
client.subscribe('arconoid/cart')
client.subscribe('arconoid/ball')

while True:
    client.on_message = on_message
    while not q1.empty():
        message = q1.get()
        message = message.split(',')
        x = int(message[0])
        y = int(message[1])
        send_coords_cart_to_influxdb(x, y)
        if message is None:
            continue
        print("received from queue cart: ", message)
    while not q2.empty():
        message = q2.get()
        message = message.split(',')
        x = int(message[0])
        y = int(message[1])
        send_coords_ball_to_influxdb(x, y)
        if message is None:
            continue
        print("received from queue ball: ", message)
    time.sleep(4)
