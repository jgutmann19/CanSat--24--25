import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import random
import time

# Colors and Fonts for Blue and Orange Theme
PRIMARY_COLOR = '#F0F0F0'   # Light gray
TEXT_COLOR = '#DE9100'      # Orange
FONT_TITLE = ("Verdana", 12, "bold")
CMD_ECHO = ""  # Initialize CMD_ECHO with an empty string

global previous_command
previous_command = ""

# 14 point min text font
plt.rcParams.update({'font.size': 14})  # Set default font size for plots

# Sample Data for Graphs with specified names
x_values = [-7, -6, -5, -4, -3, -2, -1, 0]  # 8 x-values
graphs_data = {
    "Altitude": (x_values, [random.randint(0, 100) for _ in range(8)]),
    "Temperature": (x_values, [random.randint(-20, 40) for _ in range(8)]),
    "Pressure": (x_values, [random.randint(900, 1100) for _ in range(8)]),
    "Voltage": (x_values, [random.uniform(0, 5) for _ in range(8)]),
    "Gyro_R": (x_values, [random.uniform(-180, 180) for _ in range(8)]),
    "Gyro_P": (x_values, [random.uniform(-180, 180) for _ in range(8)]),
    "Gyro_Y": (x_values, [random.uniform(-180, 180) for _ in range(8)]),
    "Accel_R": (x_values, [random.uniform(-10, 10) for _ in range(8)]),
    "Accel_P": (x_values, [random.uniform(-10, 10) for _ in range(8)]),
    "Accel_Y": (x_values, [random.uniform(-10, 10) for _ in range(8)]),
    "Mag_R": (x_values, [random.uniform(-100, 100) for _ in range(8)]),
    "Mag_P": (x_values, [random.uniform(-100, 100) for _ in range(8)]),
    "Mag_Y": (x_values, [random.uniform(-100, 100) for _ in range(8)]),
    "Auto_Gyro_Rotation_Rate": (x_values, [random.uniform(-360, 360) for _ in range(8)])
}

# Function to generate random data for graphs
def generate_random_data():
    for key in graphs_data:
        y_values = [random.randint(0, 100) if "Temperature" not in key else random.randint(-20, 40) for _ in range(8)]
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

        # Customize y-axis labels and ticks
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
        
        # Highlight area under the curve
        if graph_title == "Temperature":
            ax.fill_between(x, y, -20, color='orange', alpha=0.2)
        else:
            ax.fill_between(x, y, color='orange', alpha=0.2)

        # Add title, axis labels, and other formatting
        ax.set_title(graph_title, weight='bold', color='darkblue', fontname='Verdana')
        ax.set_xlabel('Time (s)', fontname='Verdana')
        ax.set_ylabel('Y Axis', fontname='Verdana')
        ax.grid(True, linestyle='--', alpha=0.6)
        # ax.legend(loc='upper left')

        # Customize y-axis labels based on the graph title
        if graph_title == "Altitude":
            ax.set_ylabel('Altitude (m)', fontname='Verdana')
        elif graph_title == "Temperature":
            ax.set_ylabel('Temperature (°C)', fontname='Verdana')
        elif graph_title == "Pressure":
            ax.set_ylabel('Pressure (hPa)', fontname='Verdana')
        elif graph_title == "Voltage":
            ax.set_ylabel('Voltage (V)', fontname='Verdana')
        elif graph_title in ["Gyro_R", "Gyro_P", "Gyro_Y"]:
            ax.set_ylabel('Gyro Rate (°/s)', fontname='Verdana')
        elif graph_title in ["Accel_R", "Accel_P", "Accel_Y"]:
            ax.set_ylabel('Acceleration (m/s²)', fontname='Verdana')
        elif graph_title in ["Mag_R", "Mag_P", "Mag_Y"]:
            ax.set_ylabel('Magnetic Field (µT)', fontname='Verdana')

    # Adjust layout to prevent overlap
    plt.subplots_adjust(hspace=1.0, wspace=0.4)  # Adjust space between subplots
    canvas.draw()  # Redraw the canvas


# Function to update the mission time dynamically
def update_mission_time():
    current_time = time.strftime("Mission Time: %H:%M:%S")
    mission_time_label.config(text=current_time)
    root.after(1000, update_mission_time)  # Update every 1 second

# Function to refresh the graphs with new data every second (1 Hz)
def update_graphs():
    global updating_graphs
    if updating_graphs:
        return  # Skip if an update is already in progress
    updating_graphs = True
    generate_random_data()  # Generate new random dataf
    plot_all_graphs(fig, axs)  # Update the existing figure and axes
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
    previous_command = command
    print(f"Previous Command: {previous_command}")
    print(f"Command sent: {command}")  # Placeholder for actual command sending logic
    cmd_entry.delete(0, tk.END)  # Clear the command entry field

# Create the main window
root = tk.Tk()
root.title("14 Graph Plotter - Blue & Orange Theme")
root.geometry("1000x700")  # Set a fixed window size
root.configure(bg=PRIMARY_COLOR)

# Force full screen
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.geometry("%dx%d" % (width, height))  # Set to full screen

# Initialize updating_graphs flag
updating_graphs = False

# Static values
static_values = {
    "TEAM_ID": "1234",
    "PACKET_COUNT": "0",
    "MODE": "IDLE",
    "STATE": "OK",
    "GPS_ALTITUDE": "N/A",
    "GPS_LATITUDE": "N/A",
    "GPS_LONGITUDE": "N/A",
    "GPS_SATS": "0",
}

# Layout for static values
for idx, (label, value) in enumerate(static_values.items()):
    tk.Label(root, text=f"{label}: {value}", font=FONT_TITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR).grid(row=0, column=idx, padx=5, pady=5)

# Create a figure and axes for the plots
fig, axs = plt.subplots(4, 4, figsize=(15, 10), dpi=100, sticky="nsew")  # 16 graphs in a 4x4 grid
fig.patch.set_facecolor('#F0F0F0')  # Light gray background
canvas = FigureCanvasTkAgg(fig, master=root)

# Ensure the figure canvas stretches dynamically
canvas.get_tk_widget().grid(row=1, column=0, columnspan=9, padx=10, pady=10, sticky="nsew")

# Set the main window to resize dynamically
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)

# Make the other rows and columns dynamically resizable
for col in range(9):  # Total number of columns used in the grid
    root.grid_columnconfigure(col, weight=1)
root.grid_rowconfigure(0, weight=0)  # Static labels row
root.grid_rowconfigure(1, weight=1)  # Graphs row
root.grid_rowconfigure(2, weight=0)  # CMD entry row

# Update CMD label, entry, and button to center them at the bottom
cmd_frame = tk.Frame(root, bg=PRIMARY_COLOR)  # Create a frame to contain the CMD controls
cmd_frame.grid(row=3, column=0, columnspan=9, padx=10, pady=10, sticky="ew")  # Span the entire width

cmd_frame.grid_columnconfigure(0, weight=1)  # Left spacer
cmd_frame.grid_columnconfigure(1, weight=0)  # CMD label
cmd_frame.grid_columnconfigure(2, weight=0)  # CMD entry
cmd_frame.grid_columnconfigure(3, weight=0)  # Send button
cmd_frame.grid_columnconfigure(4, weight=1)  # Right spacer

# Create a label for command echo
cmd_echo_label = tk.Label(cmd_frame, text=f"CMD_ECHO: {CMD_ECHO}", font=FONT_TITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR)
cmd_echo_label.grid(row=0, column=0, padx=5, pady=10)

# Add CMD label, entry, and button to the frame
cmd_label = tk.Label(cmd_frame, text="CMD:", font=FONT_TITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR)
cmd_label.grid(row=0, column=1, padx=(0, 5), pady=10, sticky="e")

cmd_entry = tk.Entry(cmd_frame, font=FONT_TITLE, width=30)
cmd_entry.grid(row=0, column=2, padx=10, pady=10)

send_button = tk.Button(cmd_frame, text="Send", font=FONT_TITLE, command=send_command)
send_button.grid(row=0, column=3, padx=0, pady=10, sticky="w")

# Create mission time label
mission_time_label = tk.Label(root, text="--:--:--", font=FONT_TITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR)
mission_time_label.grid(row=0, column=4, padx=5, pady=5)

# Start the real-time mission time update
update_mission_time()

# Start updating graphs every second
update_graphs()

# Start the Tkinter event loop
root.mainloop()
