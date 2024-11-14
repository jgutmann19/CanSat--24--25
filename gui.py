import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import random
import time

# Colors and Fonts for Blue and Orange Theme
PRIMARY_COLOR = '#0055A5'   # Blue
TEXT_COLOR = '#FFA500'      # Orange
FONT_TITLE = ("Verdana", 12, "bold")

sim_command = 0

# Sample Data for Graphs with specified names
x_values = [1, 2, 3, 4, 5, 6, 7, 8]  # 8 x-values
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

# Function to plot all graphs with dynamic data
def plot_all_graphs(fig, axs):
    for idx, (graph_title, (x, y)) in enumerate(graphs_data.items()):
        row = idx // 4  # Change to 4 columns
        col = idx % 4
        ax = axs[row, col]
        ax.clear()

        # Styling the plots
        ax.plot(x, y, marker='o', color='blue', label='X vs Y', linewidth=2.0)

        # Highlight area under the curve
        if graph_title == "Temperature":
            ax.fill_between(x, y, -20, color='orange', alpha=0.2)  # Fill from -20 to the y-value
        else:
            ax.fill_between(x, y, color='orange', alpha=0.2)  # Fill from 0 to the y-value

        # Adding title and grid
        ax.set_title(graph_title, fontsize=10, weight='bold', color='darkblue', fontname='Verdana')
        ax.set_xlabel('X Axis', fontsize=8, fontname='Verdana')
        ax.set_ylabel('Y Axis', fontsize=8, fontname='Verdana')

        # Add gridlines
        ax.grid(True, linestyle='--', alpha=0.6)

        # Add legend
        ax.legend(loc='upper left', fontsize=7)

    # Adjust layout to prevent overlap
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    canvas.draw()  # Redraw the canvas

# Function to update the mission time dynamically
def update_mission_time():
    current_time = time.strftime("Mission Time: %H:%M:%S")
    mission_time_label.config(text=current_time)
    root.after(10, update_mission_time)  # Update every 1 second

# Function to refresh the graphs with new data every second (1 Hz)
def update_graphs():
    generate_random_data()  # Generate new random data
    plot_all_graphs(fig, axs)  # Update the existing figure and axes

    # Schedule the next update in 1 second (1 Hz)
    root.after(1000, update_graphs)

def simulation_mode():
    # Read CSV then print every 7 values for all graphs
    sim = 0

# Function to send command
def send_command():
    command = cmd_entry.get()
    global CMD_ECHO  # Use global variable to update CMD_ECHO
    CMD_ECHO = command  # Update CMD_ECHO with the command
    cmd_echo_label.config(text=f"CMD_ECHO: {CMD_ECHO}")  # Update the label
    if(command == "SIM ENABLE"): sim_command = 1
    if(sim_command == 1 and command == "SIM_ACTIVATE"): simulation_mode()
    print(f"Command sent: {command}")  # Placeholder for actual command sending logic
    cmd_entry.delete(0, tk.END)  # Clear the command entry field

# Create the main window
root = tk.Tk()
root.title("14 Graph Plotter - Blue & Orange Theme")
root.geometry("1000x700")  # Set a fixed window size
root.configure(bg=PRIMARY_COLOR)

# Variable to store the command echo
CMD_ECHO = ""

# Create static values
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

# Create a label for command echo
cmd_echo_label = tk.Label(root, text=f"CMD_ECHO: {CMD_ECHO}", font=FONT_TITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR)
cmd_echo_label.grid(row=2, column=3, padx=5, pady=5)

# Create a figure and axes for the plots
fig, axs = plt.subplots(4, 4, figsize=(15, 10), dpi=100)  # 16 graphs in a 4x4 grid
canvas = FigureCanvasTkAgg(fig, master=root)  # Create a canvas to hold the figure
canvas.get_tk_widget().grid(row=1, column=0, columnspan=9, padx=10, pady=10, sticky="nsew")

# Create CMD entry and send button
cmd_label = tk.Label(root, text="CMD:", font=FONT_TITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR)
cmd_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

cmd_entry = tk.Entry(root, font=FONT_TITLE, width=30)
cmd_entry.grid(row=2, column=1, padx=5, pady=5)

send_button = tk.Button(root, text="Send", font=FONT_TITLE, command=send_command)
send_button.grid(row=2, column=2, padx=5, pady=5)

# Create mission time label
mission_time_label = tk.Label(root, text="--:--:--", font=FONT_TITLE, bg=PRIMARY_COLOR, fg=TEXT_COLOR)
mission_time_label.grid(row=0, column=4, padx=5, pady=5)

# Start the real-time mission time update
update_mission_time()

# Start updating graphs every second
update_graphs()

# Start the Tkinter event loop
root.mainloop()