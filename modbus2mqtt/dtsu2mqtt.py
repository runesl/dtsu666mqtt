import minimalmodbus
import json
import paho.mqtt.client as paho
import time
from register_mapping import Registermapping
from modbus_readahead import ModbusReadahead
instrument = minimalmodbus.Instrument('/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0',
                                      1)  # port name, slave address (in decimal)
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.stopbits = 1
instrument.serial.timeout = 1
instrument.debug = False
instrument.mode = minimalmodbus.MODE_RTU

broker = "192.168.0.60"
port = 1883

def on_publish(client, userdata, result):  # create function for callback
	#  print(f"data published {userdata}\n")
	pass

client1 = paho.Client("dtsu2mqtt")  # create client object
client1.on_publish = on_publish  # assign function to callback
client1.connect(broker, port)  # establish connection

power_sent = None
energy_sent = None
power_regs = [
	"Active_Power_L1",
	"Active_Power_L2",
	"Active_Power_L3"
]
energy_regs = [
	"ImpEp",
	"ImpEpA",
	"ImpEpB",
	"ImpEpC",
	"NetImpEp",
	"ExpEp"
]

mra = ModbusReadahead(instrument)

while True:
	try:
		mra.read_float_ahead(Registermapping[power_regs[0]]["addr"], len(power_regs))
		mra.read_float_ahead(Registermapping[energy_regs[0]]["addr"], len(energy_regs))

		power = {reg: mra.read_float(Registermapping[reg]["addr"])*Registermapping[reg]["scale"] for reg in power_regs}
		energy = {reg: mra.read_float(Registermapping[reg]["addr"])*Registermapping[reg]["scale"] for reg in energy_regs}
		if power != power_sent:
			client1.publish(f"smartmeter/power", json.dumps(power))
			print(f"publish power: {power}")
			power_sent = power
		if energy != energy_sent:
			client1.publish(f"smartmeter/energy", json.dumps(energy))
			print(f"publish energy: {energy}")
			energy_sent = energy
	except Exception as e:
		print(f"Exception caught: {e}. Resetting serial modbus")
		instrument.serial.close()
		instrument.serial.open()
		time.sleep(1)
	time.sleep(0.05) # rs485usb com is more stable with this

