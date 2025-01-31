import csv
import pandas as pd
from datetime import datetime
import random
import numpy as np
import time
from datetime import datetime, timezone
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

# There are 25 values sent in the telemetry packets, but the generated csv creates a 0th column with the
# number representing the current row, this causes the telemetry data to be effectively 1 indexed. I don't
# think this should be changed when the XBEE is implemented because it represents how many packets we have
# received not how many packets have been sent as is represented in the telemetry packet - Joel

df.loc[0] = [3174, # Team_ID                                            1
            str(datetime.now())[11:][:-7], # Mission_Time               2
            packet_count, # Packet_Count                                3
            mode, # Mode                                                4
            state, # State                                              5
            random.randint(1,100), # Altitude                     6
            random.randint(1,100), # Temperature                  7
            random.randint(1, 100), # Pressure                    8
            random.randint(1, 100), # Voltage                     9
            random.randint(1,360), # Gyro_R                       10
            random.randint(1,360), # Gyro_P                       11
            random.randint(1,360), # Gyro_Y                       12
            random.randint(1,360), # Accel_R                      13
            random.randint(1,360), # Accel_P                      14
            random.randint(1,360), # Accel_Y                      15
            random.randint(1,100), # Magn_R                       16
            random.randint(1, 100), # Magn_P                      17
            random.randint(1, 100), # Magn_Y                      18
            random.randint(1,10), # Auto_Gyro_Rotation_Rate       19
            str(datetime.now())[11:][:-7], # GPS_Time                   20
            random.randint(1,100), # GPS_Altitude                 21
            random.randint(1, 50), # GPS_Latitude                22
            random.randint(1, 50), # GPS_Longitude               23
            random.randint(1, 3), # GPS_Sats                      24
            cmd] # CMD                                                  25


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
    df.loc[len(df.index)] = [3174, # Team_ID
                            datetime.now(timezone.utc).strftime('%H:%M:%S'), # Mission_Time in UTC
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