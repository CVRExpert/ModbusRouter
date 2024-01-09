import socket
import serial
import struct
import crcmod
import threading

UDP_PORT = 4001
SERIAL_PORT = "/dev/ttyUSB0"
SERIAL_PORT1 = "/dev/ttyUSB1"
SERIAL_PORT0 = "/dev/ttyS0"
DEST_IP = "10.11.11.1"
DEST_PORT = 4001

# Инициализация последовательного порта
ser = serial.Serial(SERIAL_PORT, 9600, timeout=1)
ser1 = serial.Serial(SERIAL_PORT1, 9600, timeout=1)
ser0 = serial.Serial(SERIAL_PORT0, 9600, timeout=1)
global chanel
chanel=0

# CRC16 Modbus
crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)

def change_address_and_crc(data, old_address, new_address):
    if not data:
        return data

    if data[0] == old_address:
        modified_data = bytes([new_address]) + data[1:-2]
        new_crc = struct.pack('<H', crc16(modified_data))
        return modified_data + new_crc
    return data

def udp_to_serial():
    global chanel
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', UDP_PORT))
    while True:
        data, addr = sock.recvfrom(1024)
        print(f'UDP > Serial request: "{data}"')
        modified_data = change_address_and_crc(data, 200, 1)
        if data[0] == 200:
            print(f'UDP > Serial request: "{data}", modified to "{modified_data}"')
            chanel=1
            ser1.write(modified_data)
        elif data[0] == 1:
            print(f'UDP > Serial request: "{data}" for sending to ttyS0')
            chanel=2
            ser0.write(modified_data)
        else:
            ser.write(modified_data)
            chanel=0
        print (f'___Working chanel now is ___"{chanel}"___')

def serial_to_udp():
    global chanel
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        data = ser.read(1024)
        print ("____chanel=",chanel)
        print(f'Received "{data}" from Serial')
        print (f'___Working chanel now is ___"{chanel}"___')
        if len(data)> 1:
            print(f'Received "{data}" from Serial, and sent to UDP')
            sock.sendto(data, (DEST_IP, DEST_PORT))
            print (f'___Working chanel now is ___"{chanel}"___')

def serial_to_udp1():
    global chanel
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        data1 = ser1.read(1024)
        print ("____chanel=",chanel)
        print(f'Received "{data1}" from Serial1')
        print (f'___Working chanel now is ___"{chanel}"___')
        if len(data1)> 1 and chanel==1:
          if data1[0] == 1:
            modified_data = change_address_and_crc(data1, 1, 200)
            print(f'Received "{data1}" from Serial, modified to "{modified_data}" and sent to UDP')
            sock.sendto(modified_data, (DEST_IP, DEST_PORT))
            chanel=0
            print (f'___Working chanel now is ___"{chanel}"___')

def serial_to_udp0():
    global chanel
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        data0 = ser0.read(1024)
        print ("____chanel=",chanel)
        print(f'Received "{data0}" from Serial0')
        print (f'___Working chanel now is ___"{chanel}"___')
        if len(data0)> 1 and chanel==2:
            print(f'Received "{data0}" from Serial0,  sent to UDP')
            sock.sendto(data0, (DEST_IP, DEST_PORT))
            chanel=0
            print (f'___Working chanel now is ___"{chanel}"___')

if __name__ == "__main__":
    threading.Thread(target=udp_to_serial).start()
    threading.Thread(target=serial_to_udp).start()
    threading.Thread(target=serial_to_udp1).start()
    threading.Thread(target=serial_to_udp0).start()
