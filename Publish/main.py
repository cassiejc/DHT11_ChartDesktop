import time
from umqtt.simple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
from machine import Pin
import dht

esp.osdebug(None)

import gc
gc.collect()

SSID = '.'
PASSWORD = 'cassiejc'
MQTT_SERVER = 'broker.emqx.io'
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC_PUB_TEMP = b'temperature'
TOPIC_PUB_HUM = b'humidity'

LAST_MESSAGE = 0
MESSAGE_INTERVAL = 5

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(SSID, PASSWORD)

while not station.isconnected():
    pass

print('Connection successful')
print(station.ifconfig())

sensor = dht.DHT11(Pin(14))

def connect_mqtt():
    """Connect to the MQTT broker."""
    global CLIENT_ID, MQTT_SERVER
    client = MQTTClient(CLIENT_ID, MQTT_SERVER)
    client.connect()
    print('Connected to %s MQTT broker' % (MQTT_SERVER))
    return client

def restart_and_reconnect():
    """Restart and reconnect in case of failure."""
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(1)
    machine.reset()

def read_sensor():
    """Read data from the DHT11 sensor."""
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        if (isinstance(temp, float) and isinstance(hum, float)) or (isinstance(temp, int) and isinstance(hum, int)):
            temp = ('{0:3.1f}'.format(temp))
            hum =  ('{0:3.1f}'.format(hum))
            return temp, hum
        else:
            return 'Invalid sensor readings.', 'Invalid sensor readings.'
    except OSError as e:
        return 'Failed to read sensor.', 'Failed to read sensor.'

try:
    client = connect_mqtt()
except OSError as e:
    restart_and_reconnect()

while True:
    try:
        if (time.time() - LAST_MESSAGE) > MESSAGE_INTERVAL:
            temp, hum = read_sensor()
            print('Temperature:', temp)
            print('Humidity:', hum)
            client.publish(TOPIC_PUB_TEMP, temp)
            client.publish(TOPIC_PUB_HUM, hum)
            LAST_MESSAGE = time.time()
    except OSError as e:
        restart_and_reconnect()

