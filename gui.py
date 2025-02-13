import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime, timezone
import csv
import threading
import GCSXbee

# Colors and Fonts for Blue and Orange Theme
PRIMARY_COLOR = '#F0F0F0'   # Light gray
TEXT_COLOR = '#DE9100'      # Orange
FONT_TITLE = ("Verdana", 14, "bold")
CMD_ECHO = ""  # Initialize CMD_ECHO with an empty string

# various global variables
global path
global previous_command
global curr_packet
global last_packet
global generate_new_packet
global simulation_active
path = "SimCSVle.csv"
previous_command = ""
curr_packet = ""
last_packet = ""
generate_new_packet = True
simulation_active = False

# 14 point min text font
plt.rcParams.update({'font.size': 14})  # Set default font size for plots

# Sample Data for Graphs with specified names
x_values = [-7, -6, -5, -4, -3, -2, -1, 0]  # 8 x-values
graphs_data = {
    "Temperature": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Pressure": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "GPS_Sats": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Voltage": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Accel_R": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Accel_P": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Accel_Y": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Altitude": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Gyro_R": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Gyro_P": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Gyro_Y": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Gyro_Rotation_Rate": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Mag_R": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Mag_P": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
    "Mag_Y": (x_values, [0, 0, 0, 0, 0, 0, 0, 0]),
}
# Data arrays for the 3D plot
gyro_latitude_points = [0, 1, 2, 3, 4, 5, 6, 7]
gyro_longitude_points = [0, 1, 2, 3, 4, 5, 6, 7]
gyro_altitude_points = [0, 1, 2, 3, 4, 5, 6, 7]

# Collect current graph data from the latest packet  Old: (Function to generate random data for graphs)
def collect_graph_data():
    # Just in case the CSV stops being updated. This keeps the graphs as the last 8 available values instead of turning
    # into a single point on a plot
    if curr_packet == last_packet:
        return

    # I'm going to keep the auto scrolling time values as it'll give a good point of reference on whether the packets are stalled
    for i in range(7):
        x_values[i] = x_values[i + 1]
        # If we only want the last 8 seconds (packets) of flight data for the 3d plot, uncomment these lines and adjust
        # the relevant "append" lines
        # gyro_altitude_points[i] = gyro_altitude_points[i + 1]
        # gyro_latitude_points[i] = gyro_latitude_points[i + 1]
        # gyro_longitude_points[i] = gyro_longitude_points[i + 1]

    x_values[7] = int(curr_packet[2])
    # Currently tracks all GPS data for the 3D plot
    gyro_altitude_points.append(int(curr_packet[20]))
    gyro_latitude_points.append(int(curr_packet[21]))
    gyro_longitude_points.append(int(curr_packet[22]))

    # Collect data from the latest packet for each field in the graphs_data dictionary
    for key in graphs_data:
        y_values = graphs_data[key][1]
        for i in range(len(y_values) - 1):
            y_values[i] = y_values[i + 1]

        if key == "Altitude":
            y_values[-1] = int(curr_packet[5])

        elif key == "Temperature":
            y_values[-1] = int(curr_packet[6])

        elif key == "Pressure":
            y_values[-1] = int(curr_packet[7])

        elif key == "Voltage":
            y_values[-1] = int(curr_packet[8])

        elif key in ["Gyro_R", "Gyro_P", "Gyro_Y"]:
            if key == "Gyro_R":
                y_values[-1] = int(curr_packet[9])
            elif key == "Gyro_P":
                y_values[-1] = int(curr_packet[10])
            elif key == "Gyro_Y":
                y_values[-1] = int(curr_packet[11])

        elif key == "Gyro_Rotation_Rate": #"Auto_Gyro_Rotation_Rate":
            y_values[-1] = int(curr_packet[18])

        elif key in ["Accel_R", "Accel_P", "Accel_Y"]:
            if key == "Accel_R":
                y_values[-1] = int(curr_packet[12])
            elif key == "Accel_P":
                y_values[-1] = int(curr_packet[13])
            elif key == "Accel_Y":
                y_values[-1] = int(curr_packet[14])

        elif key in ["Mag_R", "Mag_P", "Mag_Y"]:
            if key == "Mag_R":
                y_values[-1] = int(curr_packet[15])
            elif key == "Mag_P":
                y_values[-1] = int(curr_packet[16])
            elif key == "Mag_Y":
                y_values[-1] = int(curr_packet[17])

        elif key == "GPS_Altitude":
            y_values[-1] = int(curr_packet[20])

        elif key == "GPS_Sats":
            y_values[-1] = int(curr_packet[23])

        graphs_data[key] = (x_values, y_values) # Update the dictionary with the new values

# Adjust subplot layout dynamically
def plot_all_graphs(fig_func, axs_func):
    total_graphs = len(graphs_data)  # Number of graphs to plot
    rows = (total_graphs + 3) // 4  # Dynamically calculate number of rows
    cols = 4  # Fixed number of columns

    # Hide unused axes
    for ax in axs_func.flatten()[total_graphs:]:
        ax.set_visible(False)

    for idx, (graph_title, (x, y)) in enumerate(graphs_data.items()):
        row = idx // cols  # Calculate row position
        col = idx % cols   # Calculate column position
        
        ax = axs_func[row, col]
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

    print("Post IF statement")
    # Adjust layout to prevent overlap
    plt.subplots_adjust(hspace=1.0, wspace=1.4)  # Adjust space between subplots
    print("Post subplots_adjust")
    canvas.draw()  # Redraw the canvas
    print("Post canvas.draw()")

# Like the previous function but just for the 3D plot for some separation
def plot_3d_graphs(fig_3d_func, axs_3d_func):
    global gyro_latitude_points, gyro_longitude_points, gyro_altitude_points

    axs_3d_func.clear() # Clear out the plot for new data
    axs_3d_func.set_title('GPS Position') # Plot title
    axs_3d_func.set_xlabel('GPS Latitude') # Rename the axis, mostly sure they are on the correct axis
    axs_3d_func.set_ylabel('GPS Longitude')
    axs_3d_func.set_zlabel('GPS Altitude')
    axs_3d_func.plot(gyro_latitude_points, gyro_longitude_points, gyro_altitude_points, color='darkblue')
    fig_3d_func.patch.set_facecolor('#F0F0F0')
    canvas_3d.draw()

# Function to update the mission time dynamically
def update_mission_time():
    current_time = datetime.now(timezone.utc).strftime('%H:%M:%S') # Get the current time in UTC
    mission_time_label.config(text=f"Mission Time: {current_time}")
    root.after(50, update_mission_time)  # Update every 1 second

# Function to refresh all displayed variables with new data every second (1 Hz)
def update_everything():
    global updating_graphs, curr_packet, packet_counter, previous_command
    get_last_csv_row(path) # Get the last row in the csv
    print("Post csv")
    try:
        current_time = "GPS Time: " + str(curr_packet[19]) # First attempt to get the latest GPS time
    except:
        current_time = "GPS Time: " + str(last_packet[19]) # Just in case the csv was mid write when the line was accessed
    gps_time_label.config(text=current_time)

    # Update variables along the top of the UI

    # There are 25 values sent in the telemetry packets, but the generated csv creates a 0th column with the
    # number representing the current row, this causes the telemetry data to be effectively 1 indexed. I don't
    # think this should be changed when the XBEE is implemented because it represents how many packets we have
    # received not how many packets have been sent as is represented in the telemetry packet - Joel


    packet_count_label.config(text=f"Packet Count: {curr_packet[2]}")
    team_id_label.config(text=f"Team ID: {curr_packet[0]}")
    mode_label.config(text=f"Mode: {curr_packet[3]}")
    state_label.config(text=f"State: {curr_packet[4]}")
    cmd_echo_label.config(text=f"Command Echo: {curr_packet[24]}")

    print("IF statement")

    # if telemetry_handler.sim_enable and not telemetry_handler.sim_activate:
    #     simulation_label.config(text="Simulation Mode: ENABLED")
    # elif telemetry_handler.sim_activate:
    #     simulation_label.config(text="Simulation Mode: ACTIVE")
    # else:
    #     simulation_label.config(text="Simulation Mode: OFF")

    if not updating_graphs: # Skips if an update is already in progress
        updating_graphs = True
        collect_graph_data()  # Generate new random dataf
        plot_all_graphs(fig, axs)  # Update the existing figure and axes
        print("Post collect")
        plot_3d_graphs(fig_3d, axs_3d) # Update the 3D figure and axes
        updating_graphs = False
    
    print("Post IF statement")
    root.after(50, update_everything) # Because the packets come in at 1Hz, update the graphs ASAP after the new packet is received


# FIXME : May replace this function with a bunch of IF statements in the normal functions (idk I need to sit down and figure this out) -------------------------------------------------------------------------------
def simulation_mode():

    pass
    # Set up multithreading to run the commands while still displaying the graphs
    # t = threading.Thread(target=telemetry_handler.send_command, args=(command)) # Will be added with the rest of the function
    # try:
    #     t.start()
    # except Exception as e:
    #     print(f"Error sending command: {e}")

# Function to send command
def send_command():
    command = cmd_entry.get()
    global previous_command

    if (previous_command == "SIMULATION ENABLE" and command == "SIMULATION ACTIVATE"):
        simulation_active = True
        t = threading.Thread(target=telemetry_handler.set_simulation_mode, args=(True))
        try:
            t.start()
        except Exception as e:
            print(f"Error sending command: {e}")

    elif command == "SIMULATION DISABLE":
        simulation_active = False
        t = threading.Thread(target=telemetry_handler.set_simulation_mode, args=(False))
        try:
            t.start()
        except Exception as e:
            print(f"Error sending command: {e}")

    # This is because I can't be bothered to look for a nice way to close the window after forced fullscreen - Joel
    elif command in ["EXIT", "exit"]:
        telemetry_handler.stop_telemetry()
        root.destroy()

    if simulation_active:
        simulation_mode()

    elif command == "SIMULATION ENABLE":
        t = threading.Thread(target=telemetry_handler.send_command, args=(command))
        try:
            t.start()
        except Exception as e:
            print(f"Error sending command: {e}")

    else:
        # Set up multithreading to run the commands while still displaying the graphs
        t = threading.Thread(target=telemetry_handler.send_command, args=(command))
        try:
            t.start()
        except Exception as e:
            print(f"Error sending command: {e}")

    previous_command = curr_packet[24]
    cmd_entry.delete(0, tk.END)  # Clear the command entry field

# Gather the latest packet of data using the csv as a middle man
def get_last_csv_row(filename):

    # There are 25 values sent in the telemetry packets, but the generated csv creates a 0th column with the
    # number representing the current row, this causes the telemetry data to be effectively 1 indexed. I don't
    # think this should be changed when the XBEE is implemented because it represents how many packets we have
    # received not how many packets have been sent as is represented in the telemetry packet - Joel

    global curr_packet, last_packet, packet_counter, generate_new_packet
    last_packet = curr_packet
    if generate_new_packet and not updating_graphs: # ensure that the graphs are in a stable state and not currently collecting a packet
        generate_new_packet = False
        try: # Always have this when doing anything with a file, should only ever be 'read' in this program
            with open(filename, 'r') as file:
                open_csv = csv.reader(file)
                last_row = None
                for row in open_csv: # Only need the latest packet in the csv
                    last_row = row
                curr_packet = last_row
        except: # Just incase the CSV has not been created yet or is not read correctly
            curr_packet = [0 for _ in range(25)]

        generate_new_packet = True

# Create the main window
root = tk.Tk()
root.title("14 Graph Plotter - Blue & Orange Theme")
# root.geometry("1000x700")  # Set a fixed window size (Changed to forced fullscreen)
root.configure(bg=PRIMARY_COLOR)

# Force full screen
# root.attributes("-fullscreen", True)

width= root.winfo_screenwidth() 
height= root.winfo_screenheight()
#setting tkinter window size
root.geometry("%dx%d" % (width, height))

# Initialize updating_graphs flag
updating_graphs = False

# Create a figure and axes for the plots
fig, axs = plt.subplots(4, 4, figsize=(20, 15), dpi=80, constrained_layout=True)  # 16 graphs in a 4x4 grid
fig.patch.set_facecolor('#F0F0F0')  # Light gray background
canvas = FigureCanvasTkAgg(fig, master=root)

# Create 3D graph
fig_3d = plt.figure()
axs_3d = fig_3d.add_subplot(projection='3d') # Designates the axes as a 3d plot
axs_3d.set_title('GPS Position') # Plot title
axs_3d.set_xlabel('GPS Latitude') # X-axis
axs_3d.set_ylabel('GPS Longitude') # Y-axis
axs_3d.set_zlabel('GPS Altitude') # Z-axis
axs_3d.plot(gyro_latitude_points, gyro_longitude_points, gyro_altitude_points) # X Y Z
fig_3d.patch.set_facecolor('#F0F0F0') # Light gray background
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
cmd_frame.grid_columnconfigure(2, weight=0, minsize=3)  # CMD entry
cmd_frame.grid_columnconfigure(3, weight=0)  # Send button
cmd_frame.grid_columnconfigure(4, weight=1)  # Sim state label

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

# # Create label to display Simulation state
# simulation_label = tk.Label(root, text="Simulation Mode: OFF", font=FONT_TITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR)
# simulation_label.grid(row=0, column=4, sticky="ew", padx=5)

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

# Create a telemetry handler object
telemetry_handler = GCSXbee.TelemetryHandler("3174", "COM4")
print("Telemetry handler created")
telemetry_handler.start_telemetry()
print("Telemetry handler started")

print("Starting update everything...")
# Start updating graphs every second
update_everything()

print("Starting mission time...")
# Start the real-time mission time update
update_mission_time()

print("Starting GUI...")
# Start the Tkinter event loop
root.mainloop()

exit()
telemetry_handler.stop_telemetry()
