import paho.mqtt.client as mqtt
from collections import deque
from matplotlib import pyplot as plt

mqtt_server = 'broker.emqx.io'
topic_sub_temp = 'temperature'
topic_sub_hum = 'humidity'

class dhtdata:
    def __init__(self, maxdata=1000):
        self.axis_x = deque(maxlen=maxdata)
        self.axis_temp = deque(maxlen=maxdata)
        self.axis_hum = deque(maxlen=maxdata)

    def add(self, x, temp, hum):
        self.axis_x.append(x)
        self.axis_temp.append(temp)
        self.axis_hum.append(hum)

def main():
    global data, temp_plot, hum_plot
    data = dhtdata()
    print(data)
    fig, (ax_temp, ax_hum) = plt.subplots(2, 1, figsize=(10, 8))
    fig.suptitle("Temperature and Humidity Data")
    
    temp_plot = dhtplot(ax_temp, "Temperature (°C)", "Temperature")
    hum_plot = dhtplot(ax_hum, "Humidity (%)", "Humidity")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_server, 1883, 60)
    client.loop_start()

    while True:
        plt.pause(0.25)

class dhtplot:
    def __init__(self, axes, ylabel, label):
        self.axes = axes
        self.lineplot, = axes.plot([], [], "bo--", label=label)
        axes.set_ylabel(ylabel)
        axes.legend()

    def plot(self, axis_x, axis_y):
        self.lineplot.set_data(axis_x, axis_y)
        self.axes.set_xlim(min(axis_x), max(axis_x))
        ymin = min(axis_y) - 5
        ymax = max(axis_y) + 5
        self.axes.set_ylim(ymin, ymax)
        self.axes.relim()
        self.axes.autoscale_view()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic_sub_temp)
    client.subscribe(topic_sub_hum)

def on_message(client, userdata, msg):
    global data, temp_plot, hum_plot
    print(msg.topic + " " + msg.payload.decode())
    if msg.topic == topic_sub_temp:
        temp = float(msg.payload.decode())
        data.add(len(data.axis_x), temp, data.axis_hum[-1] if data.axis_hum else 0)
    elif msg.topic == topic_sub_hum:
        hum = float(msg.payload.decode())
        data.add(len(data.axis_x), data.axis_temp[-1] if data.axis_temp else 0, hum)

    temp_plot.plot(data.axis_x, data.axis_temp)
    hum_plot.plot(data.axis_x, data.axis_hum)

if __name__ == "__main__":
    main()
