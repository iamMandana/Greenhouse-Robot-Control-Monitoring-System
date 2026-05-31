import tkinter as tk
from tkinter import ttk

class SensorsPanel:
    def __init__(self, parent, robot):
        self.parent = parent
        self.robot = robot
        
        # Create scrollable frame
        self.canvas = tk.Canvas(parent, bg="#ecf0f1", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
        self.frame = tk.Frame(self.canvas, bg="#ecf0f1")
        
        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window with proper width
        self.canvas_window = self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Update canvas width when parent resizes - FIXED
        def configure_canvas(event):
            # Update scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # Set canvas item width to match canvas width
            if event.width > 10:
                self.canvas.itemconfig(self.canvas_window, width=event.width)
        
        self.canvas.bind('<Configure>', configure_canvas)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Small delay to ensure proper initial sizing
        self.parent.after(100, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.create_widgets()
    
    def create_widgets(self):
        # Use grid for centering
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)
        
        row = 0
        
        # Title
        tk.Label(self.frame, text="ENVIRONMENT SENSORS", font=("Arial", 16, "bold"),
                 bg="#ecf0f1", fg="#2c3e50").grid(row=row, column=1, pady=10)
        row += 1
        
        # Sensor values container
        sensor_frame = tk.Frame(self.frame, bg="#ecf0f1")
        sensor_frame.grid(row=row, column=1, pady=10)
        row += 1
        
        # Temperature
        temp_frame = tk.Frame(sensor_frame, bg="#ecf0f1")
        temp_frame.pack(fill="x", pady=8)
        tk.Label(temp_frame, text="TEMPERATURE:", font=("Arial", 12, "bold"),
                 bg="#ecf0f1", width=18, anchor="w").pack(side="left")
        self.temp_value = tk.Label(temp_frame, text="25 C", font=("Arial", 12),
                                   bg="#ecf0f1", fg="#e74c3c", width=10, anchor="w")
        self.temp_value.pack(side="left")
        
        # Humidity
        hum_frame = tk.Frame(sensor_frame, bg="#ecf0f1")
        hum_frame.pack(fill="x", pady=8)
        tk.Label(hum_frame, text="HUMIDITY:", font=("Arial", 12, "bold"),
                 bg="#ecf0f1", width=18, anchor="w").pack(side="left")
        self.hum_value = tk.Label(hum_frame, text="60%", font=("Arial", 12),
                                  bg="#ecf0f1", fg="#3498db", width=10, anchor="w")
        self.hum_value.pack(side="left")
        
        # Soil Moisture
        soil_frame = tk.Frame(sensor_frame, bg="#ecf0f1")
        soil_frame.pack(fill="x", pady=8)
        tk.Label(soil_frame, text="SOIL MOISTURE:", font=("Arial", 12, "bold"),
                 bg="#ecf0f1", width=18, anchor="w").pack(side="left")
        self.soil_value = tk.Label(soil_frame, text="50%", font=("Arial", 12),
                                   bg="#ecf0f1", fg="#8e44ad", width=10, anchor="w")
        self.soil_value.pack(side="left")
        
        # Light
        light_frame = tk.Frame(sensor_frame, bg="#ecf0f1")
        light_frame.pack(fill="x", pady=8)
        tk.Label(light_frame, text="LIGHT:", font=("Arial", 12, "bold"),
                 bg="#ecf0f1", width=18, anchor="w").pack(side="left")
        self.light_value = tk.Label(light_frame, text="400 lux", font=("Arial", 12),
                                    bg="#ecf0f1", fg="#f39c12", width=10, anchor="w")
        self.light_value.pack(side="left")
        
        # Separator
        separator = ttk.Separator(self.frame, orient='horizontal')
        separator.grid(row=row, column=0, columnspan=3, sticky="ew", pady=15, padx=20)
        row += 1
        
        # Decision Panel
        tk.Label(self.frame, text="DECISION ENGINE", font=("Arial", 14, "bold"),
                 bg="#ecf0f1", fg="#2c3e50").grid(row=row, column=1, pady=10)
        row += 1
        
        self.decision_frame = tk.Frame(self.frame, bg="#34495e", relief="raised", bd=2, height=80)
        self.decision_frame.grid(row=row, column=1, sticky="ew", pady=5)
        self.decision_frame.grid_propagate(False)
        
        self.decision_label = tk.Label(self.decision_frame, text="Waiting for sensor data...",
                                       font=("Arial", 11, "bold"), bg="#34495e", fg="#f1c40f",
                                       wraplength=400)
        self.decision_label.pack(expand=True, pady=15)
        row += 1
        
        # Actuators Status Section
        tk.Label(self.frame, text="ACTUATORS STATUS", font=("Arial", 14, "bold"),
                 bg="#ecf0f1", fg="#2c3e50").grid(row=row, column=1, pady=(15, 5))
        row += 1
        
        # Actuators container
        actuators_frame = tk.Frame(self.frame, bg="#ecf0f1", relief="groove", bd=1)
        actuators_frame.grid(row=row, column=1, sticky="ew", pady=5, padx=10)
        row += 1
        
        # Fan status
        fan_frame = tk.Frame(actuators_frame, bg="#ecf0f1")
        fan_frame.pack(fill="x", pady=5, padx=10)
        tk.Label(fan_frame, text="COOLING FAN:", font=("Arial", 11, "bold"),
                 bg="#ecf0f1", width=18, anchor="w").pack(side="left")
        self.fan_status = tk.Label(fan_frame, text="OFF", font=("Arial", 11, "bold"),
                                   bg="#ecf0f1", fg="#e74c3c", width=10, anchor="w")
        self.fan_status.pack(side="left")
        
        # LED Light status
        light_frame = tk.Frame(actuators_frame, bg="#ecf0f1")
        light_frame.pack(fill="x", pady=5, padx=10)
        tk.Label(light_frame, text="GROW LIGHT:", font=("Arial", 11, "bold"),
                 bg="#ecf0f1", width=18, anchor="w").pack(side="left")
        self.light_actuator_status = tk.Label(light_frame, text="OFF", font=("Arial", 11, "bold"),
                                              bg="#ecf0f1", fg="#e74c3c", width=10, anchor="w")
        self.light_actuator_status.pack(side="left")
        
        # Water pump status
        water_frame = tk.Frame(actuators_frame, bg="#ecf0f1")
        water_frame.pack(fill="x", pady=5, padx=10)
        tk.Label(water_frame, text="WATER PUMP:", font=("Arial", 11, "bold"),
                 bg="#ecf0f1", width=18, anchor="w").pack(side="left")
        self.water_status = tk.Label(water_frame, text="OFF", font=("Arial", 11, "bold"),
                                     bg="#ecf0f1", fg="#e74c3c", width=10, anchor="w")
        self.water_status.pack(side="left")
        
        # Heater status (optional)
        heater_frame = tk.Frame(actuators_frame, bg="#ecf0f1")
        heater_frame.pack(fill="x", pady=5, padx=10)
        tk.Label(heater_frame, text="HEATER:", font=("Arial", 11, "bold"),
                 bg="#ecf0f1", width=18, anchor="w").pack(side="left")
        self.heater_status = tk.Label(heater_frame, text="OFF", font=("Arial", 11, "bold"),
                                      bg="#ecf0f1", fg="#e74c3c", width=10, anchor="w")
        self.heater_status.pack(side="left")
    
    def update(self):
        # Update sensor values
        self.temp_value.config(text=f"{self.robot.temperature} C")
        self.hum_value.config(text=f"{self.robot.humidity}%")
        self.soil_value.config(text=f"{self.robot.soil}%")
        self.light_value.config(text=f"{self.robot.light} lux")
        self.decision_label.config(text=f"{self.robot.decision}")
        
        # Update actuator status based on sensor readings and decisions
        # Fan control (temperature > 30)
        if self.robot.temperature > 30:
            self.fan_status.config(text="ON", fg="#27ae60")
        else:
            self.fan_status.config(text="OFF", fg="#e74c3c")
        
        # Light control (light < 200)
        if self.robot.light < 200:
            self.light_actuator_status.config(text="ON", fg="#27ae60")
        else:
            self.light_actuator_status.config(text="OFF", fg="#e74c3c")
        
        # Water pump control (soil moisture < 30)
        if self.robot.soil < 30:
            self.water_status.config(text="ON", fg="#27ae60")
        else:
            self.water_status.config(text="OFF", fg="#e74c3c")
        
        # Heater control (temperature < 18)
        if self.robot.temperature < 18:
            self.heater_status.config(text="ON", fg="#27ae60")
        else:
            self.heater_status.config(text="OFF", fg="#e74c3c")
        
        # Color coding for sensors
        if self.robot.temperature > 30:
            self.temp_value.config(fg="#e74c3c")
        elif self.robot.temperature < 18:
            self.temp_value.config(fg="#3498db")
        else:
            self.temp_value.config(fg="#2c3e50")
        
        if self.robot.soil < 30:
            self.soil_value.config(fg="#e74c3c")
        else:
            self.soil_value.config(fg="#8e44ad")
        
        if self.robot.light < 200:
            self.light_value.config(fg="#e74c3c")
        else:
            self.light_value.config(fg="#f39c12")
