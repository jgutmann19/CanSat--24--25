import csv
import os
import time
from threading import Thread
from datetime import datetime, timezone

# os.environ["KUBECONFIG"] = os.path.abspath("kube_config.yaml")

from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress



class TelemetryHandler:
    def __init__(self, team_id, port="COM3", baudrate=9600, write_path=None, mac_addr="0013A20041E060D1"): # default port val for Fernando's laptop
        """
        Initialize the telemetry handler.

        Args:
            team_id (str): Four-digit team identification number.
            port (str): Serial port for communication.
            baudrate (int): Baud rate for XBee communication.
        """

        ##################### File path for the simulated data to be used #####################
        self.SIM_CSV_PATH = "SIM_Pressure.csv"  # Path to the simulated data CSV file
        #######################################################################################

        # Some of these definitions are redundant, but they are here for clarity
        self.team_id = team_id
        self.is_receiving = False
        self.csv_file = None
        self.csv_writer = None
        self.packet_count = 0
        self.sim_enable = False
        self.sim_activate = False
        self.simulation_thread = None
        self.receiver = None
        self.write_filepath = write_path
        if self.write_filepath == None:
            raise Exception(f"GCSXbee (File: GCSXbee.py Function: __init__) [INITIALIZATION] : No file write_path given")

        # Define telemetry fields as per competition requirements
        self.telemetry_fields = [
            'TEAM_ID', 'MISSION_TIME', 'PACKET_COUNT', 'MODE', 'STATE',
            'ALTITUDE', 'TEMPERATURE', 'PRESSURE', 'VOLTAGE',
            'GYRO_R', 'GYRO_P', 'GYRO_Y',
            'ACCEL_R', 'ACCEL_P', 'ACCEL_Y',
            'MAG_R', 'MAG_P', 'MAG_Y',
            'AUTO_GYRO_ROTATION_RATE',
            'GPS_TIME', 'GPS_ALTITUDE', 'GPS_LATITUDE', 'GPS_LONGITUDE', 'GPS_SATS',
            'CMD_ECHO'
        ]

        # Initialize XBee connection
        self.mac_address = mac_addr # This is the MAC address of the FSW radio (the one on the Sat)
        self.xbee_device = XBeeDevice(port, baudrate)
        self.receiver = RemoteXBeeDevice(x64bit_addr=XBee64BitAddress.from_hex_string(self.mac_address), local_xbee=self.xbee_device)
        # FIXME : This MAC address will need to be updated to the actual FSW radio's MAC address

    def start_telemetry(self):
        """Start receiving telemetry data."""
        try:
            self.xbee_device.open()
        except Exception as e:
            raise Exception(f"GCSXbee (File: GCSXbee.py Function: start_telemetry) [START TELEMETRY] Failed to open XBee device: {e}")
        
        # Create CSV file with specified naming format
        self.csv_file = open(self.write_filepath, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)

        # Write header row
        self.csv_writer.writerow(self.telemetry_fields)

        # Start receiving data
        self.is_receiving = True
        self.receive_thread = Thread(target=self._receive_telemetry, daemon=True)
        self.receive_thread.start()

    def stop_telemetry(self):
        """Stop receiving telemetry data and close files."""
        self.is_receiving = False
        if self.receive_thread:
            self.receive_thread.join()

        if self.csv_file:
            self.csv_file.close()

        print(f"GCSXbee (File: GCSXbee.py Function: stop_telemetry) [STOP TELEMETRY] : Telemetry stopped. {self.packet_count} packets received.")

        # if self.xbee_device and self.xbee_device.is_open():
        #     self.send_command(f"CMD,{self.team_id},CX,OFF")
        #     self.xbee_device.close()

    def send_command(self, command):
        """
        Send a command to the CanSat.

        Args:
            command (str): Command string following competition format.
        """

        if command == "CX ON":
            CXON = f"CMD,{self.team_id},CX,ON\0\0\0\0\0\0\0\0"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=CXON)
                    # self.xbee_device.send_data_async(remote_xbee=self.receiver, data=CXON)
            except Exception as e:
                print(f"ERROR (File: GCSXbee.py Function: send_command) [COMMAND CXON]: Error sending command - {e}")

        elif command == "CX OFF":
            CXOFF = f"CMD,{self.team_id},CX,OFF\0\0\0\0\0\0\0"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_async(remote_xbee=self.receiver ,data=CXOFF)
                    # self.xbee_device.send_data_async(remote_xbee=self.receiver ,data=CXOFF)
            except Exception as e:
                print(f"ERROR (File: GCSXbee.py Function: send_command) [COMMAND CXOFF]: Error sending command - {e}")
        
        elif command == "SIM ENABLE":
            ENABLE = f"CMD,{self.team_id},SIM,ENABLE\0\0\0"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=ENABLE)
                    # self.xbee_device.send_data_async(remote_xbee=self.receiver, data=ENABLE)
            except Exception as e:
                print(f"ERROR (File: GCSXbee.py Function: send_command) [COMMAND SIM ENABLE]: Error sending command - {e}")

        elif command == "SIM ACTIVATE":
            ACTIVATE = f"CMD,{self.team_id},SIM,ACTIVATE\0"
            try:
                if self.xbee_device.is_open() and self.sim_enable:
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=ACTIVATE)
                    # self.xbee_device.send_data_async(remote_xbee=self.receiver, data=ACTIVATE)
            except Exception as e:
                print(f"ERROR (File: GCSXbee.py Function: send_command) [COMMAND SIM ACTIVATE]: Error sending command - {e}")
        
        elif command == "SIM DISABLE":
            DISABLE = f"CMD,{self.team_id},SIM,DISABLE\0\0"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=DISABLE)
                    print()
                    print("Command SIM DISABLE sent")
                    print()
                    # self.xbee_device.send_data_async(remote_xbee=self.receiver, data=DISABLE)
            except Exception as e:
                print(f"ERROR (File: GCSXbee.py Function: send_command) [COMMAND SIM DISABLE]: Error sending command - {e}")

        elif command == "CAL":
            CAL = f"CMD,{self.team_id},CAL\0\0\0\0\0\0\0\0\0\0"
            print(f"Sending command: {CAL}")
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=CAL)
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=CAL)
            except Exception as e:
                print(f"ERROR (File: GCSXbee.py Function: send_command) [COMMAND CAL]: Error sending command - {e}")

        elif command == "ST GPS":
            ST_GPS = f"CMD,{self.team_id},ST,GPS\0\0\0\0\0\0\0"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=ST_GPS)
                    # self.xbee_device.send_data_async(remote_xbee=self.receiver, data=ST_GPS)
            except Exception as e:
                print(f"ERROR (File: GCSXbee.py Function: send_command) [COMMAND ST GPS]: Error sending command - {e}")

        elif command[0:2] == "ST":
            current_time = "00:00:00"
            try:
                current_time = command[3:]
                if current_time == "":
                    current_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
                elif len(current_time) != 8:
                    current_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
                elif current_time.count(":") != 2:
                    current_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
                elif current_time[2] != ":" or current_time[5] != ":":
                    current_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
                elif int(current_time[0:2]) > 23 or int(current_time[3:5]) > 59 or int(current_time[6:8]) > 59:
                    current_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
            
            except:
                current_time = datetime.now(timezone.utc).strftime('%H:%M:%S') # Get the current time in UTC
            print(current_time)
            ST = f"CMD,{self.team_id},ST,{current_time}\0\0"
            print(ST)
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=ST)
                    # self.xbee_device.send_data_async(remote_xbee=self.receiver, data=ST)
            except Exception as e:
                print(f"ERROR (File: GCSXbee.py Function: send_command) [COMMAND ST]: Error sending command - {e}")

        elif command == "MEC WIRE ON":
            MEC_WIRE = f"CMD,{self.team_id},MEC,WIRE,ON\0\0"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=MEC_WIRE)
                    # self.xbee_device.send_data_async(remote_xbee=self.receiver, data=MEC_WIRE)
            except Exception as e:
                print(f"ERROR (File: GCSXbee.py Function: send_command) [COMMAND MEC WIRE ON]: Error sending command - {e}")

        elif command == "MEC WIRE OFF":
            MEC_WIRE = f"CMD,{self.team_id},MEC,WIRE,OFF\0"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=MEC_WIRE)
                    # self.xbee_device.send_data_async(remote_xbee=self.receiver, data=MEC_WIRE)
            except Exception as e:
                print(f"ERROR (File: GCSXbee.py Function: send_command) [COMMAND MEC WIRE OFF]: Error sending command - {e}")

        # FIXME : Add any MEC commands here -------------------------------------------------------------------------------

        else:
            print(f"ERROR (File: GCSXbee.py Function: send_command) [SEND_COMMAND]: Unknown command - {command}")

    def _receive_telemetry(self):
        """Internal method to receive and process telemetry data."""
        while self.is_receiving:
            try:
                xbee_message = self.xbee_device.read_data(20)
                if xbee_message:


                    # TODO: THIS IS A TEMPORARY PACKET FOR THE SAKE OF READING THE SENT "COMMAND"
                    # line = xbee_message.data.decode('utf-8').strip()
                    # print(line)
                    # xbee_message = self.xbee_device.read_data(20)



                    # Read and decode the message
                    line = xbee_message.data.decode('utf-8').strip()
                    xbee_message = self.xbee_device.read_data(20)  # Read the next message
                    if xbee_message is None:
                        # print(line)   
                        continue
                    line = line + xbee_message.data.decode('utf-8').strip()  # Append the next message data
                    data = line.split(',')
                    # print(line)
                    # print("GPS Time: ", data[19])

                    current_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
                    data[19] = current_time
                    # print("GPS Time: ", data[19])
                    # print()

                    # Validate team ID and basic data format
                    if (len(data) >= len(self.telemetry_fields)) and (data[0] == self.team_id):
                        # Write to CSV file
                        self.csv_writer.writerow(data)
                        self.csv_file.flush()  # Ensure data is written to disk

                        # Update packet count
                        self.packet_count += 1

                    # FIXME : This may need to be updated to handle the format that FSW sends us (the array index that is) -------------------------
                    if data[24] == "SIMENABLE":
                        self.sim_enable = True

                    elif data[24] == "SIMACT":
                        self.sim_activate = True
                        # if not self.simulation_thread.is_alive():  
                        self.start_sim()                     

                    elif data[24] == "SIMDIS":
                        self.sim_activate = False
                        self.sim_enable = False
                        if self.simulation_thread:
                            self.stop_sim()

            except Exception as e:
                print(f"ERROR (File: GCSXbee.py Function: _receive_telemetry) [RECEIVE TELEMETRY] : {e}")
                

    # def _receive_telemetry_serial(self):
    #     """Internal method to receive and process telemetry data over serial."""
    #     while self.is_receiving:
    #         try:
    #             xbee_message = self.xbee_device.read_data(20)
    #             if xbee_message:
    #                 # Read and decode the message
    #                 line = xbee_message.data.decode('utf-8').strip()
    #                 print(f"Received data: {line}")
    #                 data = line.split(',')

    #                 # Validate team ID and basic data format
    #                 if (len(data) >= len(self.telemetry_fields)) and (data[0] == self.team_id):
    #                     # Write to CSV file
    #                     self.csv_writer.writerow(data)
    #                     self.csv_file.flush()  # Ensure data is written to disk

    #                     # Update packet count
    #                     self.packet_count += 1

    #         except Exception as e:
    #             print(f"ERROR (File: GCSXbee.py Function: _receive_telemetry_serial) [RECEIVE TELEMETRY SERIAL] : {e}")

    def start_sim(self):
        """
        Send simulated pressure data (simulation mode only).

        Args:
            pressure (int): Pressure in pascals.
        """
        # self.send_command(f"CMD,{self.team_id},SIMP,{pressure}")

        if (self.sim_enable and self.sim_activate):
            print(self.SIM_CSV_PATH)
            self.simulation_thread = Thread(target=self._send_command_pressure)
            self.simulation_thread.start()

    def stop_sim(self):
        """
        Stop sending simulated pressure data.
        """
        # while self.simulation_thread:
        print("Waiting for simulation thread to finish...")
        self.simulation_thread.join()

        self.sim_enable = False
        self.sim_activate = False
        print("Simulation stopped.")

    def _send_command_pressure(self):
        """
        Send simulated pressure data (simulation mode only).

        Args:
            csv_path (string): Path to the CSV file containing pressure data.
        """
        with open(self.SIM_CSV_PATH, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if not self.sim_enable or not self.sim_activate: # Check if simulation is enabled and activated
                    print("Simulation disabled or not activated. Stopping simulation thread.")
                    break
                DATA = f"CMD,{self.team_id},SIMP,{row[0]}"
                self.xbee_device.send_data_async(remote_xbee=self.receiver, data=DATA)
                time.sleep(1)

        DATA = f"CMD,{self.team_id},SIM,DISABLE";
        self.xbee_device.send_data_async(remote_xbee=self.receiver, data=DATA)
        print("Simulation thread finished.")
