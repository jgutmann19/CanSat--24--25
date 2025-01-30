import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.mplot3d import Axes3D
import random
import time
import csv

# Colors and Fonts for Blue and Orange Theme
PRIMARY_COLOR = '#F0F0F0'   # Light gray
TEXT_COLOR = '#DE9100'      # Orange
FONT_TITLE = ("Verdana", 12, "bold")
CMD_ECHO = ""  # Initialize CMD_ECHO with an empty string

global previous_command
global curr_packet
global last_packet
global generate_new_packet

previous_command = ""
curr_packet = ""
last_packet = ""
generate_new_packet = True

# 14 point min text font
plt.rcParams.update({'font.size': 14})  # Set default font size for plots

# Sample Data for Graphs with specified names
x_values = [-7, -6, -5, -4, -3, -2, -1, 0]  # 8 x-values
graphs_data = {
    "Temperature": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Pressure": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "GPS_Sats": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    # "GPS_Altitude": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Accel_R": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Accel_P": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Accel_Y": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Altitude": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Gyro_R": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Gyro_P": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Gyro_Y": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Gyro_Rotation_Rate": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]), #Auto_
    "Mag_R": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Mag_P": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Mag_Y": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Voltage": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
}
gyro_latitude_points = [0, 1, 2, 3, 4, 5, 6, 7]
gyro_longitude_points = [0, 1, 2, 3, 4, 5, 6, 7]
gyro_altitude_points = [0, 1, 2, 3, 4, 5, 6, 7]

# Collect current graph data from the latest packet  Old: (Function to generate random data for graphs)
def collect_graph_data():
    # I'm going to keep the auto scrolling time values as it'll give a good point of reference on whether the packets are stalled
    for i in range(7):
        x_values[i] = x_values[i + 1]
        gyro_altitude_points[i] = gyro_altitude_points[i + 1]
        gyro_latitude_points[i] = gyro_latitude_points[i + 1]
        gyro_longitude_points[i] = gyro_longitude_points[i + 1]

    x_values[7] = int(curr_packet[0])
    gyro_altitude_points[7] = int(curr_packet[21])
    gyro_latitude_points[7] = int(curr_packet[22])
    gyro_longitude_points[7] = int(curr_packet[23])

    for key in graphs_data:
        y_values = graphs_data[key][1]
        for i in range(len(y_values) - 1):
            y_values[i] = y_values[i + 1]

        if key == "Altitude":
            y_values[-1] = int(curr_packet[6])

        elif key == "Temperature":
            y_values[-1] = int(curr_packet[7])

        elif key == "Pressure":
            y_values[-1] = int(curr_packet[8])

        elif key == "Voltage":
            y_values[-1] = int(curr_packet[9])

        elif key in ["Gyro_R", "Gyro_P", "Gyro_Y"]:
            if key == "Gyro_R":
                y_values[-1] = int(curr_packet[10])
            elif key == "Gyro_P":
                y_values[-1] = int(curr_packet[11])
            elif key == "Gyro_Y":
                y_values[-1] = int(curr_packet[12])

        elif key == "Gyro_Rotation_Rate": #"Auto_Gyro_Rotation_Rate":
            y_values[-1] = int(curr_packet[19])

        elif key in ["Accel_R", "Accel_P", "Accel_Y"]:
            if key == "Accel_R":
                y_values[-1] = int(curr_packet[13])
            elif key == "Accel_P":
                y_values[-1] = int(curr_packet[14])
            elif key == "Accel_Y":
                y_values[-1] = int(curr_packet[15])

        elif key in ["Mag_R", "Mag_P", "Mag_Y"]:
            if key == "Mag_R":
                y_values[-1] = int(curr_packet[16])
            elif key == "Mag_P":
                y_values[-1] = int(curr_packet[17])
            elif key == "Mag_Y":
                y_values[-1] = int(curr_packet[18])

        elif key == "GPS_Altitude":
            y_values[-1] = int(curr_packet[21])

        elif key == "GPS_Sats":
            y_values[-1] = int(curr_packet[24])

        # else:
        #     gyro_graph_data_points[-1] = []

        graphs_data[key] = (x_values, y_values)

# Adjust subplot layout dynamically
def plot_all_graphs(fig, axs):
    total_graphs = len(graphs_data)  # Number of graphs to plot
    rows = (total_graphs + 3) // 4  # Dynamically calculate number of rows
    cols = 4  # Fixed number of columns

    # Hide unused axes
    for ax in axs.flatten()[total_graphs:]:
        ax.set_visible(False)

    for idx, (graph_title, (x, y)) in enumerate(graphs_data.items()):
        row = idx // cols  # Calculate row position
        col = idx % cols   # Calculate column position
        
        ax = axs[row, col]
        ax.clear()

        # Plot data as before
        ax.plot(x, y, marker='o', color='blue', label='X vs Y', linewidth=2.0)

        # Customize y and x-axis labels and ticks
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
        ax.xaxis.set_major_locator(MaxNLocator(nbins=4))

        # Add title, axis labels, and other formatting
        ax.set_title(graph_title, weight='bold', color='darkblue', fontname='Verdana')
        ax.set_xlabel('Packets', fontname='Verdana')
        ax.set_ylabel('Y Axis', fontname='Verdana')
        ax.grid(True, linestyle='--', alpha=0.6)

        # Customize y-axis labels based on the graph title
        if graph_title == "Altitude":
            ax.set_ylabel('Altitude (m)', fontname='Verdana')
        elif graph_title == "Temperature":
            ax.set_ylabel('Temp (°C)', fontname='Verdana')
        elif graph_title == "Pressure":
            ax.set_ylabel('Pressure (kPa)', fontname='Verdana')
        elif graph_title == "Voltage":
            ax.set_ylabel('Voltage (V)', fontname='Verdana')
        elif graph_title in ["Gyro_R", "Gyro_P", "Gyro_Y"]:
            ax.set_ylabel('Gyro Rate (°/s)', fontname='Verdana')
        elif graph_title == "Gyro_Rotation_Rate":
            ax.set_ylabel('Degrees (°/s)', fontname='Verdana')
        elif graph_title in ["Accel_R", "Accel_P", "Accel_Y"]:
            ax.set_ylabel('Accel (m/s²)', fontname='Verdana')
        elif graph_title in ["Mag_R", "Mag_P", "Mag_Y"]:
            ax.set_ylabel('Mag Field (µT)', fontname='Verdana')
        elif graph_title == "GPS_Altitude":
            ax.set_ylabel('GPS Altitude (m)', fontname='Verdana')
        elif graph_title == "GPS_Sats":
            ax.set_ylabel('GPS Satellites', fontname='Verdana')

    # Adjust layout to prevent overlap
    plt.subplots_adjust(hspace=1.0, wspace=1.4)  # Adjust space between subplots
    canvas.draw()  # Redraw the canvas

def plot_3d_graphs(fig_3d, axs_3d):
    global gyro_latitude_points, gyro_longitude_points, gyro_altitude_points

    axs_3d.clear()
    axs_3d.set_title('GPS Position')
    axs_3d.set_xlabel('GPS Latitude')
    axs_3d.set_ylabel('GPS Longitude')
    axs_3d.set_zlabel('GPS Altitude')
    axs_3d.plot(gyro_latitude_points, gyro_longitude_points, gyro_altitude_points, color='darkblue')
    fig_3d.patch.set_facecolor('#F0F0F0')

    canvas_3d.draw()

# Function to update the mission time dynamically
def update_mission_time():
    current_time = time.strftime("Mission Time: %H:%M:%S")
    mission_time_label.config(text=current_time)

    root.after(1000, update_mission_time)  # Update every 1 second

# Function to refresh the graphs with new data every second (1 Hz) (This might change to the "Update Everything" func)
# FIXME : Do we change this to update all?
def update_graphs():
    global updating_graphs, curr_packet, packet_counter
    get_last_csv_row("SimCSV.csv")

    try:
        current_time = "GPS Time: " + str(curr_packet[20])
    except:
        current_time = "GPS Time: " + str(last_packet[20])
    gps_time_label.config(text=current_time)

    packet_count_label.config(text=f"Packet Count: {curr_packet[0]}")
    team_id_label.config(text=f"Team ID: {curr_packet[1]}")
    mode_label.config(text=f"Mode: {curr_packet[4]}")
    state_label.config(text=f"State: {curr_packet[5]}")
    cmd_echo_label.config(text=f"Command Echo: {curr_packet[25]}")

    if updating_graphs:
        return  # Skip if an update is already in progress
    updating_graphs = True
    collect_graph_data()  # Generate new random dataf
    plot_all_graphs(fig, axs)  # Update the existing figure and axes
    plot_3d_graphs(fig_3d, axs_3d)

    updating_graphs = False
    root.after(500, update_graphs)  # Schedule the next update in 1 second

def simulation_mode():
    # Simulation mode logic
    print("Simulation mode activated!")

# Function to send command
def send_command():
    command = cmd_entry.get()
    global CMD_ECHO  # Use global variable to update CMD_ECHO
    CMD_ECHO = command  # Update CMD_ECHO with the command
    cmd_echo_label.config(text=f"CMD_ECHO: {CMD_ECHO}")  # Update the label
    global previous_command
    if (previous_command == "SIM ENABLE" and command == "SIM_ACTIVATE" 
       or previous_command == "SIM_ACTIVATE" and command == "SIM ENABLE"):
        simulation_mode()

    # This is because I can't be bothered to look for a nice way to close the window after forced fullscreen - Joel
    if command in ["EXIT", "exit"]:
        quit()

    previous_command = command
    print(f"Previous Command: {previous_command}")
    print(f"Command sent: {command}")  # Placeholder for actual command sending logic
    cmd_entry.delete(0, tk.END)  # Clear the command entry field

def get_last_csv_row(filename):
    global curr_packet, last_packet, packet_counter, generate_new_packet
    last_packet = curr_packet
    if generate_new_packet and not updating_graphs:
        generate_new_packet = False
        try:
            with open(filename, 'r') as file:
                open_csv = csv.reader(file)
                last_row = None
                for row in open_csv:
                    last_row = row
                curr_packet = last_row
        except: # Just incase the CSV has not been created yet
            curr_packet = [0 for _ in range(26)]
        generate_new_packet = True

# Create the main window
root = tk.Tk()
root.title("14 Graph Plotter - Blue & Orange Theme")
# root.geometry("1000x700")  # Set a fixed window size (Changed to forced fullscreen)
root.configure(bg=PRIMARY_COLOR)

# Force full screen
root.attributes("-fullscreen", True)

# Initialize updating_graphs flag
updating_graphs = False

# Create a figure and axes for the plots
fig, axs = plt.subplots(4, 4, figsize=(20, 15), dpi=80, constrained_layout=True)  # 16 graphs in a 4x4 grid
fig.patch.set_facecolor('#F0F0F0')  # Light gray background
canvas = FigureCanvasTkAgg(fig, master=root)

# Create 3D graph
fig_3d = plt.figure()
axs_3d = fig_3d.add_subplot(projection='3d')
axs_3d.set_title('GPS Position')
axs_3d.set_xlabel('GPS Latitude')
axs_3d.set_ylabel('GPS Longitude')
axs_3d.set_zlabel('GPS Altitude')
axs_3d.plot(gyro_latitude_points, gyro_longitude_points, gyro_altitude_points)
fig_3d.patch.set_facecolor('#F0F0F0')
canvas_3d = FigureCanvasTkAgg(fig_3d, master=root)

# Ensure the figure canvas stretches dynamically
canvas.get_tk_widget().grid(row=3, column=0, columnspan=4, sticky="nsew")
canvas_3d.get_tk_widget().grid(row=3, column=9, sticky='nsew')

# Set the main window to resize dynamically
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)

# Make the other rows and columns dynamically resizable
for col in range(9):  # Total number of columns used in the grid
    root.grid_columnconfigure(col, weight=1)
root.grid_rowconfigure(0, weight=0)  # Static labels row
root.grid_rowconfigure(1, weight=0)  # More labels
root.grid_rowconfigure(2, weight=0)  # CMD entry row
root.grid_rowconfigure(3, weight=2)  # Graphs row

# Update CMD label, entry, and button to center them above the graphs
cmd_frame = tk.Frame(root, bg=PRIMARY_COLOR)  # Create a frame to contain the CMD controls
cmd_frame.grid(row=2, column=0, columnspan=9,  sticky="ew")  # Span the entire width

cmd_frame.grid_columnconfigure(0, weight=1)  # Left spacer
cmd_frame.grid_columnconfigure(1, weight=0)  # CMD label
cmd_frame.grid_columnconfigure(2, weight=0)  # CMD entry
cmd_frame.grid_columnconfigure(3, weight=0)  # Send button
cmd_frame.grid_columnconfigure(4, weight=1)  # Right spacer

# Create a label for command echo
cmd_echo_label = tk.Label(cmd_frame, text=f"Command Echo: {CMD_ECHO}", font=FONT_TITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR)
cmd_echo_label.grid(row=0, column=0, padx=5)

# Add CMD label, entry, and button to the frame
cmd_label = tk.Label(cmd_frame, text="Command:", font=FONT_TITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR)
cmd_label.grid(row=0, column=1, padx=(0, 5), sticky="e")

cmd_entry = tk.Entry(cmd_frame, font=FONT_TITLE, width=30)
cmd_entry.grid(row=0, column=2, padx=10)

send_button = tk.Button(cmd_frame, text="Send", font=FONT_TITLE, command=send_command)
send_button.grid(row=0, column=3, padx=0, sticky="w")

# Create mission time label
mission_time_label = tk.Label(root, text="--:--:--", font=FONT_TITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR)
mission_time_label.grid(row=0, column=0, padx=5, pady=5)

# Create Team ID label
team_id_label = tk.Label(root, text="Team ID: 3174", font=FONT_TITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR)
team_id_label.grid(row=0, column=1, padx=5, pady=5)

# Create Packet Count label
packet_count_label = tk.Label(root, text="Packet Count: 0", font=FONT_TITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR)
packet_count_label.grid(row=0, column=2, padx=5, pady=5)

# Create Mode label
mode_label = tk.Label(root, text="Mode: IDLE", font=FONT_TITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR)
mode_label.grid(row=0, column=3, padx=5, pady=5)

# Create State label
state_label = tk.Label(root, text="State: OK", font=FONT_TITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR)
state_label.grid(row=1, column=1, padx=5, pady=5)

# Create GPS time label
gps_time_label = tk.Label(root, text="--:--:--", font=FONT_TITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR)
gps_time_label.grid(row=1, column=0, padx=5)

# Start updating graphs every second
update_graphs()

# Start the real-time mission time update
update_mission_time()

# Start the Tkinter event loop
root.mainloop()
