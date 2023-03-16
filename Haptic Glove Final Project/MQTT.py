import network
import time

sta_if = network.WLAN(network.STA_IF)
sta_if.active(False)
sta_if.active(True)
while not sta_if.isconnected():
    print('connecting')
    sta_if.connect('pun', '123321123')
    time.sleep(1)
print(sta_if.ifconfig())
# MQTT
from umqtt.simple import MQTTClient

def mqtt_cb(topic, msg):
    print(topic, msg)

client_id = b"Mbits board"
broker = b"broker.hivemq.com"
port = 1883
sub_topic = b'thammasat/aueaphum/cmd'
pub_topic = b'thammasat/aueaphum/data'
client = MQTTClient(client_id, broker, port)
client.set_callback(mqtt_cb)
client.connect()
client.subscribe(sub_topic)

while True:
    client.publish(pub_topic, "OK")
    client.check_msg()
    time.sleep(1)
    
