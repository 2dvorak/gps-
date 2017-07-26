# -*- coding: utf-8 -*-
import sys
import struct
from fractions import Fraction

SOI = b"\xff\xd8"
APP1 = b"\xff\xe1"
EXIF = b"\x45\x78\x69\x66"

ENDIAN_INTEL = b"\x49\x49"
ENDIAN_MOTOROLA = b"\x4d\x4d"

TAG_GPS = b"\x88\x25"

TAG_LAT_REF = b"\x00\x01"
TAG_LAT = b"\x00\x02"
TAG_LON_REF = b"\x00\x03"
TAG_LON = b"\x00\x04"
TAG_ALT_REF = b"\x00\x05"
TAG_ALT = b"\x00\x06"

TYPE_UBYTE = b"\x00\x01"
TYPE_ASCII = b"\x00\x02"
TYPE_USHORT =  b"\x00\x03"
TYPE_ULONG =  b"\x00\x04"
TYPE_URATIONAL =  b"\x00\x05"
TYPE_BYTE =  b"\x00\x06"
TYPE_UNDEFINED =  b"\x00\x07"
TYPE_SHORT =  b"\x00\x08"
TYPE_LONG =  b"\x00\x08"
TYPE_RATIONAL =  b"\x00\x0A"
TYPE_FLOAT =  b"\x00\x0B"
TYPE_DFLOAT =  b"\x00\x0C"

dms_lat_deg = 'dms_lat_deg'
dms_lat_min = 'dms_lat_min'
dms_lat_sec = 'dms_lat_sec'
dms_lon_deg = 'dms_lon_deg'
dms_lon_min = 'dms_lon_min'
dms_lon_sec = 'dms_lon_sec'
dm_lat_deg = 'dm_lat_deg'
dm_lat_min = 'dm_lat_min'
dm_lon_deg = 'dm_lon_deg'
dm_lon_min = 'dm_lon_min'
dd_lat_deg = 'dd_lat_deg'
dd_lon_deg = 'dd_lon_deg'
lat_ref = 'lat_ref'
lon_ref = 'lon_ref'

unpack_endian = ''

CC = 0

class Gps_info():
	def __init__(self,form,gps):
		self._form = form
		self._gps = gps
		if form == "dd":
			self._gps[dms_lat_deg] = int(gps[dd_lat_deg])
			self._gps[dms_lat_min] = int((gps[dd_lat_deg] - self._gps[dms_lat_deg] )* 60)
			self._gps[dms_lat_sec] = (gps[dd_lat_deg] - self._gps[dms_lat_deg] - self._gps[dms_lat_min]/60) * 3600
			self._gps[dms_lon_deg] = int(gps[dd_lon_deg])
			self._gps[dms_lon_min] = int((gps[dd_lon_deg] - self._gps[dms_lon_deg]) * 60)
			self._gps[dms_lon_sec] = (gps[dd_lon_deg] - self._gps[dms_lon_deg] - self._gps[dms_lon_min]/60) * 3600
			self._gps[dm_lat_deg] = int(gps[dd_lat_deg])
			self._gps[dm_lat_min] = (gps[dd_lat_deg] - int(gps[dd_lat_deg]))*60
			self._gps[dm_lon_deg] = int(gps[dd_lon_deg])
			self._gps[dm_lon_min] = (gps[dd_lon_deg] - int(gps[dd_lon_deg]))*60
		elif form == "dm":
			self._gps[dms_lat_deg] = gps[dm_lat_deg]
			self._gps[dms_lat_min] = int(gps[dm_lat_min])
			self._gps[dms_lat_sec] = (gps[dm_lat_min] - int(gps[dm_lat_min]))*60
			self._gps[dms_lon_deg] = gps[dm_lon_deg]
			self._gps[dms_lon_min] = int(gps[dm_lon_min])
			self._gps[dms_lon_sec] = (gps[dm_lon_min] - int(gps[dm_lon_min]))*60
			self._gps[dd_lat_deg] = gps[dm_lat_deg] + gps[dm_lat_min]/60
			self._gps[dd_lon_deg] = gps[dm_lon_deg] + gps[dm_lon_min]/60
		elif form == "dms":
			self._gps[dm_lat_deg] = gps[dms_lat_deg]
			self._gps[dm_lat_min] = float(gps[dms_lat_min] + (gps[dms_lat_sec]/60))
			self._gps[dm_lon_deg] = gps[dms_lon_deg]
			self._gps[dm_lon_min] = float(gps[dms_lon_min] + (gps[dms_lon_sec]/60))
			self._gps[dd_lat_deg] = float(gps[dms_lat_deg] + (gps[dms_lat_min]/60) + (gps[dms_lat_sec]/3600))
			self._gps[dd_lon_deg] = float(gps[dms_lon_deg] + (gps[dms_lon_min]/60) + (gps[dms_lon_sec]/3600))
		else:
			print("wrong format input!\n")
			return
	def __repr__(self):
		return "GPS INFO\nDMS_LAT : {0}°{1}'{2}\", DMS_LON : {3}°{4}'{5}\"\nDD_LAT : {6}, DD_LON : {7}".format(self._gps[dms_lat_deg], self._gps[dms_lat_min], self._gps[dms_lat_sec], self._gps[dms_lon_deg], self._gps[dms_lon_min], self._gps[dms_lon_sec], self._gps[dd_lat_deg], self._gps[dd_lon_deg])
	def __getitem__(self,key):
		if key not in self._gps:
			print("Given key not found. Check GPS format.\n")
			return
		return self._gps[key]
	def __setitem__(self,key,val):
		self._gps[key] = val

def struct_unpack(data):
	global unpack_endian
	if len(data) == 1:
		return struct.unpack(unpack_endian + 'B',data)[0]
	elif len(data) == 2:
		return struct.unpack(unpack_endian + 'H',data)[0]
	elif len(data) == 4:
		return struct.unpack(unpack_endian + 'L',data)[0]
	elif len(data) == 8:
		return struct.unpack(unpack_endian + 'Q',data)[0]

def check_input(data):
	if data[0:2] != SOI or data[2:4] != APP1:
		return False
	if data[6:10] != EXIF:
		return False
	return True

def interpret_gps(data):
	pos_info = dict()
	gps_tag = data.find(TAG_GPS)
	global unpack_endian
	if data[12:14] == ENDIAN_INTEL:
		unpack_endian = '<'
	elif data[12:14] == ENDIAN_MOTOROLA:
		unpack_endian = '>'
	else:
		print("Unknown byte order of file!\n")
		return
	#print("%d\n"%len(data[gps_tag + 8: gps_tag + 12]))
	gps_index = struct_unpack(data[gps_tag + 8: gps_tag + 12])
	gps_index += 0xc
	#print("GPS index : %x\n" % gps_index)
	gps_len = struct_unpack(data[gps_index:gps_index+2])
	#print("gps components num : %d"%gps_len)
	gps_dict = dict()
	pos = gps_index+2
	for i in range(gps_len):
		if data[pos:pos+2] == TAG_LAT_REF:
			if data[pos+2:pos+4] != TYPE_ASCII:
				print("Lat_ref type not 0x02(ascii)!\n")
				return
			if data[pos+8:pos+9] != b"\x4e" and data[pos+8:pos+9] != b"\x53":
				print("Lat_ref not \"N\" nor \"S\"!\n")
				return
			if data[pos+8] == b"\x4e":
				gps_dict[lat_ref] = 'N'
			elif data[pos+8:pos+9] == b"\x53":
				gps_dict[lat_ref] = 'S'
			pos_info[lat_ref] = pos+8
		elif data[pos:pos+2] == TAG_LAT:
			if data[pos+2:pos+4] != TYPE_URATIONAL:
				print("Lat type not 0x05(urational)!\n")
				return
			if struct_unpack(data[pos+4:pos+8]) != 3:
				print("Lat components number is not 3!(%x)\n" % struct_unpack(data[pos+4:pos+8]))
				return
			lat_pos = struct_unpack(data[pos+8:pos+12])
			lat_pos += 0xc
			# store pos info
			pos_info[dms_lat_deg] = lat_pos
			gps_dict[dms_lat_deg] = float(struct_unpack(data[lat_pos:lat_pos+4])/ struct_unpack(data[lat_pos+4:lat_pos+8]))
			gps_dict[dms_lat_min] = float(struct_unpack(data[lat_pos+8:lat_pos+12])/ struct_unpack(data[lat_pos+12:lat_pos+16]))
			gps_dict[dms_lat_sec] = float(struct_unpack(data[lat_pos+16:lat_pos+20])/ struct_unpack(data[lat_pos+20:lat_pos+24]))
			if CC:
				print(struct_unpack(data[lat_pos:lat_pos+4]))
				print(struct_unpack(data[lat_pos+4:lat_pos+8]))
				print(struct_unpack(data[lat_pos+8:lat_pos+12]))
				print(struct_unpack(data[lat_pos+12:lat_pos+16]))
				print(struct_unpack(data[lat_pos+16:lat_pos+20]))
				print(struct_unpack(data[lat_pos+20:lat_pos+24]))
		elif data[pos:pos+2] == TAG_LON_REF:
			if data[pos+2:pos+4] != TYPE_ASCII:
				print("Lon_ref type not 0x02(ascii)!(%s at %x)\n" % (data[pos+2:pos+4].hex(), pos))
				return
			if data[pos+8:pos+9] != b"\x45" and data[pos+8:pos+9] != b"\x57":
				print("Lon_ref not \"E\" nor \"W\"!\n")
				return
			if data[pos+8:pos+9] == b"\x45":
				gps_dict[lat_ref] = 'E'
			elif data[pos+8:pos+9] == b"\x57":
				gps_dict[lat_ref] = 'W'
			pos_info[lon_ref] = pos+8
		elif data[pos:pos+2] == TAG_LON:
			if data[pos+2:pos+4] != TYPE_URATIONAL:
				print("Lon type not 0x05(urational)!\n")
				return
			if struct_unpack(data[pos+4:pos+8]) != 3:
				print("Lon components number is not 3!(%x)\n" % struct_unpack(data[pos+4:pos+8]))
				return
			lon_pos = struct_unpack(data[pos+8:pos+12])
			lon_pos += 0xc
			# store pos info
			pos_info[dms_lon_deg] = lon_pos
			gps_dict[dms_lon_deg] = float(struct_unpack(data[lon_pos:lon_pos+4])/ struct_unpack(data[lon_pos+4:lon_pos+8]))
			gps_dict[dms_lon_min] = float(struct_unpack(data[lon_pos+8:lon_pos+12])/ struct_unpack(data[lon_pos+12:lon_pos+16]))
			gps_dict[dms_lon_sec] = float(struct_unpack(data[lon_pos+16:lon_pos+20])/ struct_unpack(data[lon_pos+20:lon_pos+24]))
			if CC:
				print(struct_unpack(data[lon_pos:lon_pos+4]))
				print(struct_unpack(data[lon_pos+4:lon_pos+8]))
				print(struct_unpack(data[lon_pos+8:lon_pos+12]))
				print(struct_unpack(data[lon_pos+12:lon_pos+16]))
				print(struct_unpack(data[lon_pos+16:lon_pos+20]))
				print(struct_unpack(data[lon_pos+20:lon_pos+24]))
		pos += 12
	try:
		ret_gps_info = Gps_info("dms", gps_dict)
	except:
		print("Error in making new Gps_info instance with interpreted data!\n")
		return
	print(ret_gps_info)
	return ret_gps_info, pos_info

def rebuild_gps(data,new_gps,pos_info):
	new_data = bytearray(len(data))
	new_data[:] = data
	print(new_gps)
	pos_lat_ref = pos_info[lat_ref]
	pos_lon_ref = pos_info[lon_ref]
	pos_lat_deg = pos_info[dms_lat_deg]
	pos_lon_deg = pos_info[dms_lon_deg]
	#print(new_data[pos_lat_ref])
	#print(new_gps[lat_ref])
	new_data[pos_lat_ref] = ord(new_gps[lat_ref])
	new_data[pos_lon_ref] = ord(new_gps[lon_ref])
	new_data[pos_lat_deg:pos_lat_deg+4] = struct.pack('>L',Fraction(new_gps[dms_lat_deg]).numerator)
	new_data[pos_lat_deg+4:pos_lat_deg+8] = struct.pack('>L',Fraction(new_gps[dms_lat_deg]).denominator)
	new_data[pos_lat_deg+8:pos_lat_deg+12] = struct.pack('>L',Fraction(new_gps[dms_lat_min]).numerator)
	new_data[pos_lat_deg+12:pos_lat_deg+16] = struct.pack('>L',Fraction(new_gps[dms_lat_min]).denominator)
	#print(Fraction(new_gps[dms_lat_sec]).numerator)
	new_data[pos_lat_deg+16:pos_lat_deg+20] = struct.pack('>L',Fraction(new_gps[dms_lat_sec]).limit_denominator(1000).numerator)
	new_data[pos_lat_deg+20:pos_lat_deg+24] = struct.pack('>L',Fraction(new_gps[dms_lat_sec]).limit_denominator(1000).denominator)
	# now longitude	
	new_data[pos_lon_deg:pos_lon_deg+4] = struct.pack('>L',Fraction(new_gps[dms_lon_deg]).numerator)
	new_data[pos_lon_deg+4:pos_lon_deg+8] = struct.pack('>L',Fraction(new_gps[dms_lon_deg]).denominator)
	new_data[pos_lon_deg+8:pos_lon_deg+12] = struct.pack('>L',Fraction(new_gps[dms_lon_min]).numerator)
	new_data[pos_lon_deg+12:pos_lon_deg+16] = struct.pack('>L',Fraction(new_gps[dms_lon_min]).denominator)
	new_data[pos_lon_deg+16:pos_lon_deg+20] = struct.pack('>L',Fraction(new_gps[dms_lon_sec]).limit_denominator(1000).numerator)
	new_data[pos_lon_deg+20:pos_lon_deg+24] = struct.pack('>L',Fraction(new_gps[dms_lon_sec]).limit_denominator(1000).denominator)
	if CC:
		print(Fraction(new_gps[dms_lat_deg]))
		print(Fraction(new_gps[dms_lat_min]))
		print(Fraction(new_gps[dms_lat_sec]))
		print(Fraction(new_gps[dms_lon_deg]))
		print(Fraction(new_gps[dms_lon_min]))
		print(Fraction(new_gps[dms_lon_sec]))
	return new_data

def main():
	try:
		f = open(sys.argv[1],"rb")
	except:
		print("Error opening input file!\n")
		return -1
	data = f.read()
	if check_input(data) is False:
		print("File format error!\n")
		return
	gps, pos_info = interpret_gps(data)
	if gps is None:
		print("GPS info not found!\n")
	new_gps = Gps_info("dd",{dd_lat_deg:35.255153,dd_lon_deg:129.085912,lat_ref:'N',lon_ref:'E'})
	new_data = rebuild_gps(data,new_gps,pos_info)
	try:
		g = open("gps_" + sys.argv[1], "wb")
		g.write(new_data)
	except:
		print("Error writing to file!\n")
		return -1
	g.close()
	f.close()

main()
