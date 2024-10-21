import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import random
import time

# Colors and Fonts for Blue and Orange Theme
PRIMARY_COLOR = '#0055A5'   # Blue
TEXT_COLOR = '#FFA500'      # Orange
FONT_TITLE = ("Verdana", 14, "bold")
FONT_BUTTON = ("Verdana", 12, "bold")
FONT_MAIN = ("Verdana", 12)

# Dropdown options
dropdown_options = ["Option 1", "Option 2", "Option 3"]

# Sample Data for Graphs
graphs_data = {
    "Graph 1": ([1, 2, 3, 4, 5], [1, 4, 9, 16, 25]),
    "Graph 2": ([1, 2, 3, 4, 5], [2, 3, 5, 7, 11]),
    "Graph 3": ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
    "Graph 4": ([1, 2, 3, 4, 5], [5, 10, 15, 20, 25]),
    "Graph 5": ([1, 2, 3, 4, 5], [5, 25, 125, 625, 3125]),
    "Graph 6": ([1, 2, 3, 4, 5], [25, 20, 15, 10, 5]),
    "Graph 7": ([1, 2, 3, 4, 5], [9, 16, 25, 36, 49]),
    "Graph 8": ([1, 2, 3, 4, 5], [8, 16, 24, 32, 40]),
    "Graph 9": ([1, 2, 3, 4, 5], [7, 14, 21, 28, 35]),
    "Graph 10": ([1, 2, 3, 4, 5], [12, 24, 36, 48, 60]),
    "Graph 11": ([1, 2, 3, 4, 5], [11, 22, 33, 44, 55]),
    "Graph 12": ([1, 2, 3, 4, 5], [6, 12, 18, 24, 30])
}

# Function to generate random data for graphs
def generate_random_data():
    for key in graphs_data:
        x_values = graphs_data[key][0]
        y_values = [random.randint(1, 100) for _ in x_values]
        graphs_data[key] = (x_values, y_values)

# Function to plot all graphs with dynamic data
def plot_all_graphs():
    fig, axs = plt.subplots(3, 4, figsize=(14, 8), dpi=100)
    fig.suptitle('12 Graphs - Blue & Orange Theme', fontsize=18, color='blue', weight='bold', fontname='Verdana')

    # Plot each graph in the grid with updated random data
    for idx, (graph_title, (x, y)) in enumerate(graphs_data.items()):
        row = idx // 4
        col = idx % 4
        ax = axs[row, col]
        ax.clear()

        # Styling the plots
        ax.plot(x, y, marker='o', color='blue', label='X vs Y', linewidth=2.0)
        ax.fill_between(x, y, color='orange', alpha=0.2)

        # Adding title and grid
        ax.set_title(graph_title, fontsize=12, weight='bold', color='darkblue', fontname='Verdana')
        ax.set_xlabel('X Axis', fontsize=10, fontname='Verdana')
        ax.set_ylabel('Y Axis', fontsize=10, fontname='Verdana')

        # Add gridlines
        ax.grid(True, linestyle='--', alpha=0.6)

        # Add legend
        ax.legend(loc='upper left', fontsize=8)

    # Adjust layout to prevent overlap
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    return fig

# Function to update the mission time dynamically
def update_mission_time():
    current_time = time.strftime("%H:%M:%S")
    mission_time_label.config(text=current_time)
    root.after(1000, update_mission_time)  # Update every 1 second

# Function to refresh the graphs with new data every second (1 Hz)
def update_graphs():
    generate_random_data()  # Generate new random data
    fig = plot_all_graphs()  # Plot the new data

    # Clear previous canvas and update with new figure
    for widget in frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()

    # Schedule the next update in 1 second (1 Hz)
    root.after(1000, update_graphs)

# Create the main window
root = tk.Tk()
root.title("12 Graph Plotter - Blue & Orange Theme")
root.configure(bg=PRIMARY_COLOR)

# Layout elements for the header and controls
team_id_label = tk.Label(
    root, text="Team ID: 1234", font=FONT_TITLE, 
    bg=PRIMARY_COLOR, fg=TEXT_COLOR
)
team_id_label.grid(row=0, column=0, sticky='w', padx=10, pady=10)

mission_time_label = tk.Label(
    root, text="--:--:--", font=FONT_TITLE, 
    bg=PRIMARY_COLOR, fg=TEXT_COLOR
)
mission_time_label.grid(row=0, column=1, sticky='w', padx=10, pady=10)

sim_mode_button = tk.Button(
    root, text="Simulation Mode", font=FONT_BUTTON, 
    bg=PRIMARY_COLOR, fg=TEXT_COLOR, bd=0
)
sim_mode_button.grid(row=0, column=2, padx=10, pady=10)

close_button = tk.Button(
    root, text="Close", font=FONT_BUTTON, bg=PRIMARY_COLOR, 
    fg=TEXT_COLOR, bd=0, command=root.quit
)
close_button.grid(row=0, column=3, padx=10, pady=10)

input_label = tk.Label(
    root, text="Input", font=(FONT_MAIN, 20), 
    bg=PRIMARY_COLOR, fg=TEXT_COLOR
)
input_label.grid(row=2, column=0, padx=10, pady=10)

dropdown = ttk.Combobox(
    root, values=dropdown_options, font=(FONT_MAIN, 20), width=20
)
dropdown.grid(row=2, column=1, padx=10, pady=10)

send_button = tk.Button(
    root, text="Send", font=FONT_BUTTON, width=10, bg=PRIMARY_COLOR, 
    fg=TEXT_COLOR, command=lambda: print("Data Sent!")
)
send_button.grid(row=2, column=2, padx=10, pady=10)

# Create a frame to hold the graphs
frame = tk.Frame(root, bg=PRIMARY_COLOR)
frame.grid(row=1, column=0, columnspan=4, padx=20, pady=20, sticky="nsew")

# Start the real-time mission time update
update_mission_time()

# Start updating graphs every second
update_graphs()

# Start the Tkinter event loop
root.mainloop()
