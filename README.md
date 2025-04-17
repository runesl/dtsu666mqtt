# DTSU666 MQTT
This project contains 2 python components:
- modbus2mqtt: Reads power and energy from DTSU666 and publishes to MQTT
- mqtt2modbus: Subscribes from mqtt and exposes a modbus server. Built for for Deye 12k-sg04lp3-eu

Why?
Using this, you don't need to pull a cable between smart meter and Deye inverter. 

Disadvantages:
The power updates are slightly delayed, which can mean that when solar production or house consumption change, the Deye cannot adjust it's production fast enough for grid power to remain very close to zero.

## Requirements:
You need something capable of running python in both ends with a rs485 interface on each for connecting to the dtsu and the deye respectively. 
You can use an rs485-USB converter or raspberry pi GPIO for rs485. If you go with raspberry pi, be aware that the GPIO pins are spec'ed at 3,3V, while rs485 is at 5V, so you may need a logic level converter.
In my experience raspberry pi GPIO is more stable than USB.

You also need an mqtt broker runningsuch as mosquitto.
