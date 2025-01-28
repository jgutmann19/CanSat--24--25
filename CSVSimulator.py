import csv
import pandas as pd
from datetime import datetime
import random
import numpy as np
import time
import os

now = datetime.now()

state = "LAUNCH_WAIT"
mode = "S"
cmd = "CXON"
packet_count = 1

df = pd.DataFrame(np.empty((0, 25)))

df.columns = ["TEAM_ID","MISSION_TIME","PACKET_COUNT","MODE","STATE","ALTITUDE","TEMPERATURE", "PRESSURE", "VOLTAGE",
              "GYRO_R", "GYRO_P", "GYRO_Y", "ACCEL_R", "ACCEL_P", "ACCEL_Y", "MAGN_R", "MAGN_P", "MAGN_Y",
              "AUTO_GRYO_ROTATION_RATE", "GPS_TIME", "GPS_ALTITUDE", "GPS_LATITUDE", "GPS_LONGITUDE", "GPS_SATS", "CMD_ECHO"]

df.loc[0] = [2031, # Team_ID
            str(datetime.now())[11:][:-7], # Mission_Time
            packet_count, # Packet_Count
            mode, # Mode
            state, # State
            random.randint(1,100), # Altitude
            random.randint(1,100), # Temperature
            random.randint(1, 100), # Pressure
            random.randint(1, 100), # Voltage
            random.randint(1,360), # Gyro_R
            random.randint(1,360), # Gyro_P
            random.randint(1,360), # Gyro_Y
            random.randint(1,360), # Accel_R
            random.randint(1,360), # Accel_P
            random.randint(1,360), # Accel_Y
            random.randint(1,100), # Magn_R
            random.randint(1, 100), # Magn_P
            random.randint(1, 100), # Magn_Y
            random.randint(1,10), # Auto_Gyro_Rotation_Rate
            str(datetime.now())[11:][:-7], # GPS_Time
            random.randint(1,100), # GPS_Altitude
            random.randint(1, 100), # GPS_Latitude
            random.randint(1, 100), # GPS_Longitude
            random.randint(1, 3), # GPS_Sats
            cmd] # CMD

packet_count = 2


while(packet_count <= 1000):
    if state == "LAUNCH_WAIT":
        state = "ASCENT"
    else:
        state = "LAUNCH_WAIT"

    if mode == "S":
        mode = "F"
    else:
        mode = "S"

    if cmd == "CXON":
        cmd = "ST"
    else:
        cmd = "CXON"

    packet_count += 1

    start = time.perf_counter()
    df.loc[len(df.index)] = [2031, # Team_ID
                            str(datetime.now())[11:][:-7], # Mission_Time
                            packet_count, # Packet_Count
                            mode, # Mode
                            state, # State
                            random.randint(1,100), # Altitude
                            random.randint(1,100), # Temperature
                            random.randint(1, 100), # Pressure
                            random.randint(1, 100), # Voltage
                            random.randint(1,360), # Gyro_R
                            random.randint(1,360), # Gyro_P
                            random.randint(1,360), # Gyro_Y
                            random.randint(1,360), # Accel_R
                            random.randint(1,360), # Accel_P
                            random.randint(1,360), # Accel_Y
                            random.randint(1,100), # Magn_R
                            random.randint(1, 100), # Magn_P
                            random.randint(1, 100), # Magn_Y
                            random.randint(1,10), # Auto_Gryo_Rotation_Rate
                            str(datetime.now())[11:][:-7], # GPS_Time
                            random.randint(1,100), # GPS_Altitude
                            random.randint(1, 100), # GPS_Latitude
                            random.randint(1, 100), # GPS_Longitude
                            random.randint(1, 3), # GPS_Sats
                            cmd] # CMD
    # print(df)
    time.sleep(1.0)

    df.to_csv("SimCSV.csv")
    end = time.perf_counter()
    duration = round(end - start, 5)
    print(f'Time to push data: {duration} seconds')

# os.remove("SimCSV.csv")