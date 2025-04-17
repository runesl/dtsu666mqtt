#!/usr/bin/python3
# -*- coding: utf-8 -*-
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4)

import logging
import logging.handlers as Handlers
import os
import time
#log = logging.getLogger("pymodbus.server")

log = logging.getLogger()
log.setLevel(logging.INFO)
#log.setLevel(logging.DEBUG)

from dtsu666emulator import dtsu666Emulator
import paho.mqtt.client as mqtt
import json
import math
import sys
import threading

#RS485Port = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A50285BI-if00-port0" # Smartmeter-input on inverter
RS485Port = "/dev/serial0" # Smartmeter-input on inverter


MQTT_Settings = {
	"Server":	"192.168.0.60",
	"Port":     	1883,
	"AMS_Topic":	"smartmeter",
	}

# Don't init until first message received
em1 = ""
last_received_timestamp = 0
max_secs_delay_warn=3
max_secs_delay_fail=10


def watchdog_task():
	logging.info("starting watchdog loop")
	while True:
		delay = time.time() - last_received_timestamp
		if delay > max_secs_delay_warn:
			log.warning(f"Delay is at {delay}")
		if delay > max_secs_delay_fail:
			log.warning(f"Delay is at {delay}. Exiting")
			os._exit(1)
		time.sleep(1)

#============================================================================

# The callback for when the client receives a CONNACK response from the server.
def mqtt_on_connect(client, userdata, flags, rc):
#	logging.info(f"MQTT connected with result code {rc}")

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe(MQTT_Settings['AMS_Topic']+"/#")


# The callback for when a PUBLISH message is received from the server.
def mqtt_on_message(client, userdata, msg):
#	log.info(f"got message! topic: {msg.topic}")
	global last_received_timestamp
	last_received_timestamp = time.time()
#	print(msg.topic)

	global em1

	if em1 == "":
		em1 = dtsu666Emulator(device=RS485Port)
		em1.startserver()
		logging.info('Got initial message. Smartmeter started...')
		watchdog_thread = threading.Thread(target=watchdog_task, name="watchdog", daemon=True)
		watchdog_thread.start()


	if msg.topic == MQTT_Settings['AMS_Topic'] + "/power":
		d = json.loads(msg.payload.decode("utf-8"))

#
#		logging.info("..update power.. Latency: {d.tsmp}")
		logging.debug(pp.pformat(d))
		em1.update(d)


	elif msg.topic == MQTT_Settings['AMS_Topic']+"/energy":
		d = json.loads(msg.payload.decode("utf-8"))

#		logging.info("..update energy..")
#		logging.info(pp.pformat(d))
		em1.update(d)


# ========================================================================================================================
mqttclient=mqtt.Client()
mqttclient.on_connect = mqtt_on_connect
mqttclient.on_message = mqtt_on_message
mqttclient.connect(MQTT_Settings['Server'], MQTT_Settings['Port'], 60)


# Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a manual interface.
mqttclient.loop_forever()


