import json
import paho.mqtt.client as mqtt
from time import sleep

# Imports for opening a file from a file dialog
import tkinter as tk
from tkinter import filedialog

class MQTTClient(mqtt.Client):
    def __init__(self):
        mqtt.Client.__init__(self)
    
    def run(self):
        self.connect("localhost", 1883, 60)
        rc = self.loop_start()
        return rc

    def stop(self):
        self.loop_stop()

class TestSend(object):
    def __init__(self):
        self.mqtt_client = MQTTClient()
        self.mqtt_client.run()

        # Ask to open a geojson file
        # If creating a PprzFP object, open a file dialog box to open a geojson file (.geojson)
        root = tk.Tk()
        root.withdraw()

        self.fp_json_path = '/home/dennis/Downloads/R1.json'#filedialog.askopenfilename(filetypes=[("json files", ".json")])
        self.send_fp()
    
    def send_fp(self):
        f = open(self.fp_json_path,"r")
        # Convert json to python dict
        fp_dict = json.load(f)
        f.close()

        self.mqtt_client.publish('control/flightplanupload/13', json.dumps(fp_dict))
        sleep(1)


test = TestSend()