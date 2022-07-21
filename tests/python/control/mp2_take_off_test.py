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
        self.send_cmd()

    
    def send_cmd(self):

        cmd_dict = {}
        cmd_dict['Command'] = 'TakeOff'

        self.mqtt_client.publish('control/command/13', json.dumps(cmd_dict))
        sleep(1)


test = TestSend()