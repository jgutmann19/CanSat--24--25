import csv
import os
import time
from threading import Thread
from datetime import datetime, timezone

# os.environ["KUBECONFIG"] = os.path.abspath("kube_config.yaml")

from digi.xbee.devices import XBeeDevice
from xbee import ZigBee

class TelemetryHandler:
    def __init__(self, team_id, port="COM3", baudrate=9600): # default port val for Fernando's laptop
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
        self.xbee_device = XBeeDevice(port, baudrate)
        try:
            print("Opening XBee device...")
            self.xbee_device.open()
            print("XBee device opened successfully.")
        except Exception as e:
            raise Exception(f"Failed to open XBee device: {e}")

    def start_telemetry(self):
        """Start receiving telemetry data."""
        # Create CSV file with specified naming format
        filename = f"Flight_{self.team_id}.csv"
        self.csv_file = open(filename, 'w', newline='')
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
        print("Sending command:", command)

        if command == "CXON":
            CXON = f"CMD,{self.team_id},CXON"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_unicast(command.strip())
            except Exception as e:
                print(f"Error sending command: {e}")

        elif command == "CXOFF":
            CXOFF = f"CMD,{self.team_id},CXOFF"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_unicast(command.strip())
            except Exception as e:
                print(f"Error sending command: {e}")
        
        elif command == "SIMULATION ENABLE":
            ENABLE = f"CMD,{self.team_id},SIM,ENABLE"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_unicast(command.strip())
            except Exception as e:
                print(f"Error sending command: {e}")

        elif command == "SIMULATION ACTIVATE":
            ACTIVATE = f"CMD,{self.team_id},SIM,ACTIVATE"
            try:
                if self.xbee_device.is_open() and self.sim_enable:
                    self.xbee_device.send_data_unicast(command.strip())
            except Exception as e:
                print(f"Error sending command: {e}")
        
        elif command == "SIMULATION DISABLE":
            DISABLE = f"CMD,{self.team_id},SIM,DISABLE"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_unicast(command.strip())
            except Exception as e:
                print(f"Error sending command: {e}")

        elif command == "CAL":
            CAL = f"CMD,{self.team_id},CAL"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_unicast(command.strip())
            except Exception as e:
                print(f"Error sending command: {e}")

        elif command == "ST GPS":
            ST_GPS = f"CMD,{self.team_id},ST,GPS"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_unicast(command.strip())
            except Exception as e:
                print(f"Error sending command: {e}")

        elif command == "ST":
            current_time = datetime.now(timezone.utc).strftime('%H:%M:%S') # Get the current time in UTC
            ST = f"CMD,{self.team_id},ST,{current_time}"
            try:
                if self.xbee_device.is_open():
                    self.xbee_device.send_data_unicast(command.strip())
            except Exception as e:
                print(f"Error sending command: {e}")

        # FIXME : Add any MEC commands here -------------------------------------------------------------------------------

    def _receive_telemetry(self):
        """Internal method to receive and process telemetry data."""
        while self.is_receiving:
            try:
                xbee_message = self.xbee_device.read_data()
                if xbee_message:
                    # Read and decode the message
                    line = xbee_message.data.decode('utf-8').strip()
                    data = line.split(',')

                    # Validate team ID and basic data format
                    if len(data) >= len(self.telemetry_fields) and data[0] == self.team_id:
                        # Write to CSV file
                        self.csv_writer.writerow(data)
                        self.csv_file.flush()  # Ensure data is written to disk

                        # Update packet count
                        self.packet_count = int(data[2])

                    if data[24] == "SIMULATION ENABLE":
                        self.sim_enable = True

                    elif data[24] == "SIMULATION ACTIVATE":
                        self.sim_activate = True

                    elif data[24] == "SIMULATION DISABLE":
                        self.sim_activate = False
                        self.sim_enable = False

            except Exception as e:
                print(f"Error receiving telemetry: {e}")

    def set_pressure(self, pressure):
        """
        Send simulated pressure data (simulation mode only).

        Args:
            pressure (int): Pressure in pascals.
        """
        # self.send_command(f"CMD,{self.team_id},SIMP,{pressure}")

        self.is_receiving = True
        self.receive_thread = Thread(target=self.send_command_pressure, args=("F:/sim.csv"))
        self.receive_thread.start()

    def send_command_pressure(self, csv_path):
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
