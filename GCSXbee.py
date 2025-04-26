import csv
import os
import time
from threading import Thread
from datetime import datetime, timezone

# os.environ["KUBECONFIG"] = os.path.abspath("kube_config.yaml")

from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress

class TelemetryHandler:
    def __init__(self, team_id, port="COM3", baudrate=9600, path=None, mac_addr="0013A20041E060D1"): # default port val for Fernando's laptop
        """
        Initialize the telemetry handler.

        Args:
            team_id (str): Four-digit team identification number.
            port (str): Serial port for communication.
            baudrate (int): Baud rate for XBee communication.
        """
        self.team_id = team_id
        self.is_receiving = False
        self.csv_file = None
        self.csv_writer = None
        self.packet_count = 0
        self.sim_enable = False
        self.sim_activate = False
        self.SIM_CSV_PATH = "E:/simulated_data.csv"
        self.filepath = path
        if self.filepath == None:
            raise Exception(f"GCSXbee [INTIALIZATION] : No file path given")
        
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
            raise Exception(f"GCSXbee [START TELEMETRY] Failed to open XBee device: {e}")
        # Create CSV file with specified naming format
        self.csv_file = open(self.filepath, 'w', newline='')
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
            CXON = f"CMD,{self.team_id},CX,ON"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=CXON)
            except Exception as e:
                print(f"ERROR [COMMAND CXON]: Error sending command - {e}")

        elif command == "CX OFF":
            CXOFF = f"CMD,{self.team_id},CX,OFF"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_async(remote_xbee=self.receiver ,data=CXOFF)
            except Exception as e:
                print(f"ERROR [COMMAND CXOFF]: Error sending command - {e}")
        
        elif command == "SIMULATION ENABLE":
            ENABLE = f"CMD,{self.team_id},SIM,ENABLE"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=ENABLE)
            except Exception as e:
                print(f"ERROR [COMMAND SIM ENABLE]: Error sending command - {e}")

        elif command == "SIMULATION ACTIVATE":
            ACTIVATE = f"CMD,{self.team_id},SIM,ACTIVATE"
            try:
                if self.xbee_device.is_open() and self.sim_enable:
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=ACTIVATE)
            except Exception as e:
                print(f"ERROR [COMMAND SIM ACTIVATE]: Error sending command - {e}")
        
        elif command == "SIMULATION DISABLE":
            DISABLE = f"CMD,{self.team_id},SIM,DISABLE"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=DISABLE)
            except Exception as e:
                print(f"ERROR [COMMAND SIM DISABLE]: Error sending command - {e}")

        elif command == "CAL":
            CAL = f"CMD,{self.team_id},CAL"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=CAL)
            except Exception as e:
                print(f"ERROR [COMMAND CAL]: Error sending command - {e}")

        elif command == "ST GPS":
            ST_GPS = f"CMD,{self.team_id},ST,GPS"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=ST_GPS)
            except Exception as e:
                print(f"ERROR [COMMAND ST GPS]: Error sending command - {e}")

        elif command[0:2] == "ST":
            current_time = "00:00:00"
            try:
                current_time = command[3:]
                if current_time == "":
                    current_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
                elif current_time.count(":") != 2:
                    current_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
                elif current_time[2] != ":" or current_time[5] != ":":
                    current_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
                elif len(current_time) != 8:
                    current_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
            
            except:
                current_time = datetime.now(timezone.utc).strftime('%H:%M:%S') # Get the current time in UTC
            print(current_time)
            ST = f"CMD,{self.team_id},ST,{current_time}"
            print(ST)
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_async(remote_xbee=self.receiver, data=ST)
            except Exception as e:
                print(f"ERROR [COMMAND ST]: Error sending command - {e}")

        # FIXME : Add any MEC commands here -------------------------------------------------------------------------------

    def _receive_telemetry(self):
        """Internal method to receive and process telemetry data."""
        while self.is_receiving:
            try:
                xbee_message = self.xbee_device.read_data(20)
                if xbee_message:
                    # Read and decode the message
                    line = xbee_message.data.decode('utf-8').strip()
                    data = line.split(',')

                    # Validate team ID and basic data format
                    if (len(data) >= len(self.telemetry_fields)) and (data[0] == self.team_id):
                        # Write to CSV file
                        self.csv_writer.writerow(data)
                        self.csv_file.flush()  # Ensure data is written to disk

                        # Update packet count
                        self.packet_count += 1

                    # FIXME : This may need to be updated to handle the format that FSW sends us -------------------------
                    if data[24] == "SIM ENABLE":
                        self.sim_enable = True

                    elif data[24] == "SIM ACTIVATE":
                        self.sim_activate = True
                        

                    elif data[24] == "SIM DISABLE":
                        self.sim_activate = False
                        self.sim_enable = False

            except Exception as e:
                print(f"ERROR [RECEIVE TELEMETRY] : {e}")

    def start_sim(self, pressure):
        """
        Send simulated pressure data (simulation mode only).

        Args:
            pressure (int): Pressure in pascals.
        """
        # self.send_command(f"CMD,{self.team_id},SIMP,{pressure}")

        if (self.sim_enable and self.sim_activate):
            self.simulation_thread = Thread(target=self._send_command_pressure, args=(self.SIM_CSV_PATH))
            self.simulation_thread.start()

    def _send_command_pressure(self, csv_path):
        """
        Send simulated pressure data (simulation mode only).

        Args:
            pressure (int): Pressure in pascals.
        """
        with open(csv_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                self.send_command(f"CMD,{self.team_id},SIMP,{row[0]}")
                time.sleep(1)
