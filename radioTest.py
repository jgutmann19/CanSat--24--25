import time
from threading import Thread
from datetime import datetime
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
import random


fields = ["TEAM_ID","MISSION_TIME","PACKET_COUNT","MODE","STATE","ALTITUDE","TEMPERATURE", "PRESSURE", "VOLTAGE",
              "GYRO_R", "GYRO_P", "GYRO_Y", "ACCEL_R", "ACCEL_P", "ACCEL_Y", "MAGN_R", "MAGN_P", "MAGN_Y",
              "AUTO_GRYO_ROTATION_RATE", "GPS_TIME", "GPS_ALTITUDE", "GPS_LATITUDE", "GPS_LONGITUDE", "GPS_SATS", "CMD_ECHO"]

state = "LAUNCH_WAIT"
mode = "S"
global cmd
cmd = "CXON"
packet_count = 1

message = [3174, # Team_ID                                              1
            str(datetime.now())[11:][:-7], # Mission_Time               2
            packet_count, # Packet_Count                                3
            mode, # Mode                                                4
            state, # State                                              5
            random.randint(1,100), # Altitude                           6
            random.randint(1,100), # Temperature                        7
            random.randint(1, 100), # Pressure                          8
            random.randint(1, 100), # Voltage                           9
            random.randint(1,360), # Gyro_R                             10
            random.randint(1,360), # Gyro_P                             11
            random.randint(1,360), # Gyro_Y                             12
            random.randint(1,360), # Accel_R                            13
            random.randint(1,360), # Accel_P                            14
            random.randint(1,360), # Accel_Y                            15
            random.randint(1,100), # Magn_R                             16
            random.randint(1, 100), # Magn_P                            17
            random.randint(1, 100), # Magn_Y                            18
            random.randint(1,10), # Auto_Gyro_Rotation_Rate             19
            str(datetime.now())[11:][:-7], # GPS_Time                   20
            random.randint(1,100), # GPS_Altitude                       21
            random.randint(1, 50), # GPS_Latitude                       22
            random.randint(1, 50), # GPS_Longitude                      23
            random.randint(1, 3), # GPS_Sats                            24
            cmd] # CMD                                                  25

xbee_device = XBeeDevice("COM5", 9600)
receiver = RemoteXBeeDevice(x64bit_addr=XBee64BitAddress.from_hex_string("0013A2004182CD94"), local_xbee=xbee_device)
try:
    xbee_device.open()
except:
    print("Could not open XBEE")
    quit()

num_sends = 1

def _receive_telemetry():
    global cmd
    while True:
            # print("Receiving telemetry data...")
            try:
                xbee_message = xbee_device.read_data(20)
                # print("Received telemetry data...................")
                # print(xbee_message)
                if xbee_message:
                    # Read and decode the message
                    line = xbee_message.data.decode('utf-8').strip()
                    data = line.split(',')
                    print(data)

                    # Validate team ID and basic data format
                    print(len(data))
                    if data[1] == "3174":
                        cmd = data[2]
                        print(data[2])
                        if cmd == "SIM":
                            if data[3] == "ENABLE":
                                cmd = "SIM ENABLE"
                            elif data[3] == "ACTIVATE":
                                cmd = "SIM ACTIVATE"
                            else:
                                cmd = "SIM DISABLE"
                            

                    time.sleep(1)
                else:
                    print(f"PACKET TESTER NOT RECIEVED")            

            except Exception as e:
                print(f"ERROR : receiving telemetry: {e}")

receive_thread = Thread(target=_receive_telemetry, daemon=True)
receive_thread.start()

while num_sends < 1000:
    if state == "LAUNCH_WAIT":
        state = "ASCENT"
    else:
        state = "LAUNCH_WAIT"

    if mode == "S":
        mode = "F"
    else:
        mode = "S"

    message = [3174, # Team_ID                              0
            str(datetime.now())[11:][:-7], # Mission_Time   1
            num_sends, # Packet_Count                       2
            mode, # Mode                                    3
            state, # State                                  4
            random.randint(1,100), # Altitude               5
            random.randint(1,100), # Temperature            6
            random.randint(1, 100), # Pressure              7
            random.randint(1, 100), # Voltage               8
            random.randint(1,360), # Gyro_R                 9
            random.randint(1,360), # Gyro_P                 10
            random.randint(1,360), # Gyro_Y                 11
            random.randint(1,360), # Accel_R                12
            random.randint(1,360), # Accel_P                13
            random.randint(1,360), # Accel_Y                14
            random.randint(1,100), # Magn_R                 15
            random.randint(1, 100), # Magn_P                17
            random.randint(1, 100), # Magn_Y                17
            random.randint(1,10), # Auto_Gyro_Rotation_Rate 18
            str(datetime.now())[11:][:-7], # GPS_Time       19
            random.randint(1,100), # GPS_Altitude           20
            random.randint(1, 50), # GPS_Latitude           21
            random.randint(1, 50), # GPS_Longitude          22
            random.randint(1, 3), # GPS_Sats                23
            cmd] # CMD                                      24

    xbee_device.send_data_async(remote_xbee=receiver ,data=f"3174,{message[1]},{num_sends},{message[3]},{message[4]},{message[5]},{message[6]},{message[7]},{message[8]},{message[9]},{message[10]},{message[11]},{message[12]},{message[13]},{message[14]},{message[15]},{message[16]},{message[17]},{message[18]},{message[19]},{message[20]},{message[21]},{message[22]},{message[23]},{message[24]}")

    num_sends += 1
    # print("Sent")
    time.sleep(1.5)

xbee_device.close()
