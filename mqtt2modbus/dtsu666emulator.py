#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import datetime
import logging

from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.version import version as ModbusVersion
from pymodbus.constants import Endian

#from pymodbus.server import StartSerialServer
#from pymodbus.server.async import StartSerialServer
from pymodbus.server.sync import StartSerialServer

from pymodbus.transaction import ModbusRtuFramer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

from threading import Thread
from register_mapping import Registermapping

wordorder = Endian.Big
byteorder = Endian.Big

header = [207, 701, 0, 0, 0, 0, 1, 10, 0, 0, 0, 1, 0, 0, 0, 1000, 0, 0, 1000, 0, 0, 1000, 0, 0, 1000, 1, 10, 0, 0, 0, 1000, 0, 0, 1000, 0, 0, 1000, 0, 0, 1000, 0, 0, 0, 0, 3, 3, 4]

class dtsu666Emulator:
	def __init__(self,
		device,
		SlaveID=0x01
		):

		self.threads = {}

		# ----------------------------------------------------------------------- #
		# initialize the server information
		i1 = ModbusDeviceIdentification()
		i1.VendorName = 'Pymodbus'
		i1.ProductCode = 'PM'
		i1.VendorUrl = 'http://github.com/riptideio/pymodbus/'
		i1.ProductName = 'Pymodbus Server'
		i1.ModelName = 'Pymodbus Server'
#		i1.MajorMinorRevision = '1.5'
		i1.MajorMinorRevision = ModbusVersion.short()


#		self.RS485Port=device
		self.RS485Settings = {
			'port': device,
			'baudrate': 9600,
			'timeout': 0.005,
			'stopbits': 1,
			'bytesize': 8,
			'parity': 'N',
#			'identity': i1
			}


		self.block = ModbusSequentialDataBlock(0, [0]*0x4052)
		# Add header:
		self._setval(0, header)

		self.store   = ModbusSlaveContext(hr=self.block)
		self.context = ModbusServerContext(slaves={SlaveID: self.store}, single=False)

	#------------------------------------------------
	def _setval(self, addr, data):
		self.block.setValues((addr+1), data)	# why +1 ?! ..ugly

	#------------------------------------------------
	def _startserver(self):
		srv = StartSerialServer(context=self.context, framer=ModbusRtuFramer, **self.RS485Settings)

		logging.info('Modbus server started')

	#------------------------------------------------
	def startserver(self):
		self.threads['srv'] = Thread(target=self._startserver)
		self.threads['srv'].start()

	#------------------------------------------------
	def update(self, data):
		prev_update_tsmp = 0
		publish_tsmp = 0
		for k,v in data.items():
			if k=="prev_update_tsmp":
				prev_update_tsmp = v
			elif k=="publish_tsmp":
				publish_tsmp = v
			else:
				reg = Registermapping[k]["addr"]

				d = v / Registermapping[k]["scale"]
				builder = BinaryPayloadBuilder(byteorder=byteorder, wordorder=wordorder)
				builder.add_32bit_float(d)

				self._setval(reg, builder.to_registers())
		now = time.time()
		logging.debug(f"delay_since_previous_update: {now-prev_update_tsmp:.3f} mqtt_delay: {now-publish_tsmp:.3f}")

# ==========================================================================================
# ==========================================================================================
if __name__ == "__main__":

#	RS485Port = '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A50285BI-if00-port0' # Smartmeter
#	RS485Port = "/dev/pts/7"
	RS485Port = "/dev/serial0"

	em1 = dtsu666Emulator(
		device=RS485Port
	)

	em1.startserver()

	Testdata = {'Volts_AB': 403.6, 'Volts_BC': 408.0, 'Volts_CA': 404.5, 'Volts_L1': 231.0, 'Volts_L2': 235.1, 'Volts_L3': 236.1, 'Current_L1': 0.339, 'Current_L2': 0.36, 'Current_L3': 0.352, 'Active_Power_L1': 2.8, 'Active_Power_L2': 11.8, 'Active_Power_L3': 8.5, 'Reactive_Power_L1': -76.7, 'Reactive_Power_L2': -80.0, 'Reactive_Power_L3': -79.7, 'Power_Factor_L1': 0.036, 'Power_Factor_L2': 0.14, 'Power_Factor_L3': 0.102, 'Total_System_Active_Power': 23.2, 'Total_System_Reactive_Power': -236.5, 'Total_System_Power_Factor': 0.094,}


	while True:
		logging.info("updating the context")
		em1.update(Testdata)
		time.sleep(10)

	print("bla")


