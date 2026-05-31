import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class SensorGraphs:
    def __init__(self, root, robot):
        self.root = root
        self.robot = robot
        self.running = True
        
        self.window = tk.Toplevel(root)
        
        self.window.title("Sensor History Graphs - Full History")
        self.window.geometry("1200x800")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Store ALL historical data from robot start
        # data stores from the robot's perspective
        self.temp_history = []
        self.humidity_history = []
        self.soil_history = []
        self.light_history = []
        
        # Track maximum history length
        self.max_history = 200
        
        # Load existing data from robot if available
        self.load_robot_history()
        
        self.setup_graphs()
        self.update_graphs()
    
    def load_robot_history(self):
        """Load historical data from robot if it has stored it"""
        # Initialize with current values
        self.temp_history.append(self.robot.temperature)
        self.humidity_history.append(self.robot.humidity)
        self.soil_history.append(self.robot.soil)
        self.light_history.append(self.robot.light)
        
        # If robot has history attribute, load it
        if hasattr(self.robot, 'temp_history'):
            self.temp_history = self.robot.temp_history.copy()
            self.humidity_history = self.robot.humidity_history.copy()
            self.soil_history = self.robot.soil_history.copy()
            self.light_history = self.robot.light_history.copy()
    
    def save_to_robot(self):
        """Save history to robot for persistence"""
        self.robot.temp_history = self.temp_history.copy()
        self.robot.humidity_history = self.humidity_history.copy()
        self.robot.soil_history = self.soil_history.copy()
        self.robot.light_history = self.light_history.copy()
    
    def setup_graphs(self):
        # Create figure with 4 subplots
        self.fig = Figure(figsize=(12, 8), facecolor='#ecf0f1')
        
        # Temperature subplot
        self.ax1 = self.fig.add_subplot(2, 2, 1)
        self.ax1.set_ylabel('Temperature (°C)', fontsize=10)
        self.ax1.set_xlabel('Time (seconds ago)', fontsize=10)
        self.ax1.set_title('Temperature History (Last 200 readings)', fontsize=12, fontweight='bold')
        self.ax1.set_facecolor('#f8f9fa')
        self.ax1.grid(True, alpha=0.3)
        self.temp_line, = self.ax1.plot([], [], 'r-', linewidth=2, label='Temperature')
        self.ax1.legend()
        self.ax1.axhline(y=30, color='r', linestyle='--', alpha=0.5, label='Warning (30°C)')
        
        # Humidity subplot
        self.ax2 = self.fig.add_subplot(2, 2, 2)
        self.ax2.set_ylabel('Humidity (%)', fontsize=10)
        self.ax2.set_xlabel('Time (seconds ago)', fontsize=10)
        self.ax2.set_title('Humidity History', fontsize=12, fontweight='bold')
        self.ax2.set_facecolor('#f8f9fa')
        self.ax2.grid(True, alpha=0.3)
        self.humidity_line, = self.ax2.plot([], [], 'b-', linewidth=2, label='Humidity')
        self.ax2.legend()
        
        # Soil Moisture subplot
        self.ax3 = self.fig.add_subplot(2, 2, 3)
        self.ax3.set_ylabel('Soil Moisture (%)', fontsize=10)
        self.ax3.set_xlabel('Time (seconds ago)', fontsize=10)
        self.ax3.set_title('Soil Moisture History', fontsize=12, fontweight='bold')
        self.ax3.set_facecolor('#f8f9fa')
        self.ax3.grid(True, alpha=0.3)
        self.soil_line, = self.ax3.plot([], [], 'g-', linewidth=2, label='Soil Moisture')
        self.ax3.legend()
        self.ax3.axhline(y=30, color='r', linestyle='--', alpha=0.5, label='Dry (30%)')
        
        # Light subplot
        self.ax4 = self.fig.add_subplot(2, 2, 4)
        self.ax4.set_ylabel('Light (lux)', fontsize=10)
        self.ax4.set_xlabel('Time (seconds ago)', fontsize=10)
        self.ax4.set_title('Light Intensity History', fontsize=12, fontweight='bold')
        self.ax4.set_facecolor('#f8f9fa')
        self.ax4.grid(True, alpha=0.3)
        self.light_line, = self.ax4.plot([], [], 'y-', linewidth=2, label='Light')
        self.ax4.legend()
        self.ax4.axhline(y=200, color='r', linestyle='--', alpha=0.5, label='Low (200 lux)')
        
        # Adjust layout
        self.fig.tight_layout()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add info label
        info_label = tk.Label(self.window, text="Showing complete history from robot start", 
                             font=("Arial", 10), bg="#ecf0f1", fg="#7f8c8d")
        info_label.pack(pady=5)
    
    def update_graphs(self):
        if not self.running:
            return
        
        # Add current readings to history
        self.temp_history.append(self.robot.temperature)
        self.humidity_history.append(self.robot.humidity)
        self.soil_history.append(self.robot.soil)
        self.light_history.append(self.robot.light)
        
        # Keep only last N readings
        if len(self.temp_history) > self.max_history:
            self.temp_history.pop(0)
            self.humidity_history.pop(0)
            self.soil_history.pop(0)
            self.light_history.pop(0)
        
        # Save to robot for persistence
        self.save_to_robot()
        
        # Create x-axis (time in reverse)
        x_data = list(range(len(self.temp_history)))
        x_labels = [f"-{len(self.temp_history)-i}" for i in range(len(self.temp_history))]
        
        # Update temperature plot
        self.temp_line.set_data(x_data, self.temp_history)
        self.ax1.set_xlim(0, max(10, len(self.temp_history)))
        if self.temp_history:
            temp_min = max(0, min(self.temp_history) - 5)
            temp_max = min(50, max(self.temp_history) + 5)
            self.ax1.set_ylim(temp_min, temp_max)
        
        # Update humidity plot
        self.humidity_line.set_data(x_data, self.humidity_history)
        self.ax2.set_xlim(0, max(10, len(self.humidity_history)))
        if self.humidity_history:
            hum_min = max(0, min(self.humidity_history) - 10)
            hum_max = min(100, max(self.humidity_history) + 10)
            self.ax2.set_ylim(hum_min, hum_max)
        
        # Update soil moisture plot
        self.soil_line.set_data(x_data, self.soil_history)
        self.ax3.set_xlim(0, max(10, len(self.soil_history)))
        if self.soil_history:
            soil_min = max(0, min(self.soil_history) - 10)
            soil_max = min(100, max(self.soil_history) + 10)
            self.ax3.set_ylim(soil_min, soil_max)
        
        # Update light plot
        self.light_line.set_data(x_data, self.light_history)
        self.ax4.set_xlim(0, max(10, len(self.light_history)))
        if self.light_history:
            light_min = max(0, min(self.light_history) - 50)
            light_max = min(1000, max(self.light_history) + 50)
            self.ax4.set_ylim(light_min, light_max)
        
        # Refresh canvas
        self.canvas.draw()
        
        # Schedule next update
        self.window.after(1000, self.update_graphs)
    
    def on_close(self):
        self.running = False
        self.window.destroy()
