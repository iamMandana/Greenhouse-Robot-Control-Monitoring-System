import tkinter as tk
from tkinter import ttk, messagebox

class RobotPanel:
    def __init__(self, parent, robot, role):
        self.parent = parent
        self.robot = robot
        self.role = role
        
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
        title = tk.Label(self.frame, text="ROBOT STATUS", font=("Arial", 16, "bold"),
                         bg="#ecf0f1", fg="#2c3e50")
        title.grid(row=row, column=1, pady=10)
        row += 1
        
        # Position
        self.pos_label = tk.Label(self.frame, text="Position: (0, 0)",
                                  font=("Arial", 12), bg="#ecf0f1")
        self.pos_label.grid(row=row, column=1, pady=5)
        row += 1
        
        # Battery label
        tk.Label(self.frame, text="Battery", font=("Arial", 12, "bold"),
                 bg="#ecf0f1").grid(row=row, column=1, pady=(10, 0))
        row += 1
        
        # Battery bar
        self.battery_bar = ttk.Progressbar(self.frame, length=300, mode='determinate')
        self.battery_bar.grid(row=row, column=1, pady=5)
        row += 1
        
        # Battery percent
        self.battery_percent = tk.Label(self.frame, text="100%", font=("Arial", 11),
                                        bg="#ecf0f1")
        self.battery_percent.grid(row=row, column=1)
        row += 1
        
        # State
        self.state_label = tk.Label(self.frame, text="State: IDLE",
                                    font=("Arial", 12), bg="#ecf0f1", fg="#2c3e50")
        self.state_label.grid(row=row, column=1, pady=10)
        row += 1
        
        # Separator
        separator = ttk.Separator(self.frame, orient='horizontal')
        separator.grid(row=row, column=0, columnspan=3, sticky="ew", pady=10, padx=20)
        row += 1
        
        # Control Panel title
        tk.Label(self.frame, text="CONTROL PANEL", font=("Arial", 14, "bold"),
                 bg="#ecf0f1", fg="#2c3e50").grid(row=row, column=1, pady=10)
        row += 1
        
        # Manual controls
        self.create_manual_controls(row)
        row += 2
        
        # Action buttons
        self.create_action_buttons(row)
    
    def create_manual_controls(self, start_row):
        control_frame = tk.Frame(self.frame, bg="#ecf0f1")
        control_frame.grid(row=start_row, column=1, pady=10)
        
        btn_width = 12
        btn_font = ("Arial", 10, "bold")
        
        # Row 0
        tk.Button(control_frame, text="FORWARD", command=lambda: self.move("forward"),
                  width=btn_width, height=1, bg="#3498db", fg="white", font=btn_font).grid(row=0, column=1, pady=3, padx=3)
        
        # Row 1
        tk.Button(control_frame, text="LEFT", command=lambda: self.move("left"),
                  width=btn_width, height=1, bg="#3498db", fg="white", font=btn_font).grid(row=1, column=0, pady=3, padx=3)
        tk.Button(control_frame, text="BACKWARD", command=lambda: self.move("backward"),
                  width=btn_width, height=1, bg="#3498db", fg="white", font=btn_font).grid(row=1, column=1, pady=3, padx=3)
        tk.Button(control_frame, text="RIGHT", command=lambda: self.move("right"),
                  width=btn_width, height=1, bg="#3498db", fg="white", font=btn_font).grid(row=1, column=2, pady=3, padx=3)
    
    def create_action_buttons(self, start_row):
        btn_frame = tk.Frame(self.frame, bg="#ecf0f1")
        btn_frame.grid(row=start_row, column=1, pady=10, sticky="ew")
        
        btn_width = 16
        btn_font = ("Arial", 9, "bold")
        
        # Configure grid columns
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        # Row 0 - Start/Stop Autonomous
        self.toggle_auto_btn = tk.Button(btn_frame, text="START AUTO", 
                                         command=self.toggle_autonomous,
                                         bg="#27ae60", fg="white", font=btn_font)
        self.toggle_auto_btn.grid(row=0, column=0, columnspan=2, sticky="ew", pady=3)
        
        # Row 1 - Go Home & Emergency Stop
        tk.Button(btn_frame, text="GO HOME", command=self.go_home,
                  bg="#f39c12", fg="white", font=btn_font).grid(row=1, column=0, sticky="ew", padx=3, pady=3)
        tk.Button(btn_frame, text="EMERGENCY STOP", command=self.emergency_stop,
                  bg="#e74c3c", fg="white", font=btn_font).grid(row=1, column=1, sticky="ew", padx=3, pady=3)
        
        # Row 2 - Power On & Shutdown
        self.power_on_btn = tk.Button(btn_frame, text="POWER ON", command=self.power_on,
                                      bg="#2ecc71", fg="white", font=btn_font)
        self.power_on_btn.grid(row=2, column=0, sticky="ew", padx=3, pady=3)
        
        tk.Button(btn_frame, text="SHUTDOWN", command=self.shutdown,
                  bg="#95a5a6", fg="white", font=btn_font).grid(row=2, column=1, sticky="ew", padx=3, pady=3)
        
        # Row 3 - Resume Toggle
        self.resume_toggle_btn = tk.Button(btn_frame, text="RESUME AFTER CHARGE: ON", 
                                           command=self.toggle_resume,
                                           bg="#3498db", fg="white", font=("Arial", 8, "bold"))
        self.resume_toggle_btn.grid(row=3, column=0, columnspan=2, sticky="ew", pady=3)
        
        # Row 4 - Stop Charging
        tk.Button(btn_frame, text="STOP CHARGING", command=self.stop_charging,
                  bg="#e67e22", fg="white", font=btn_font).grid(row=4, column=0, columnspan=2, sticky="ew", pady=3)
        
        # Row 5 - Resume Charging
        tk.Button(btn_frame, text="RESUME CHARGING", command=self.resume_charging,
                  bg="#27ae60", fg="white", font=btn_font).grid(row=5, column=0, columnspan=2, sticky="ew", pady=3)
    
    def update(self):
        self.pos_label.config(text=f"Position: ({self.robot.x}, {self.robot.y})")
        
        battery_percent = round(self.robot.battery, 1)
        self.battery_bar['value'] = battery_percent
        self.battery_percent.config(text=f"{battery_percent}%")
        
        if battery_percent < 20:
            self.battery_bar['style'] = 'red.Horizontal.TProgressbar'
        elif battery_percent < 50:
            self.battery_bar['style'] = 'yellow.Horizontal.TProgressbar'
        else:
            self.battery_bar['style'] = 'green.Horizontal.TProgressbar'
        
        self.state_label.config(text=f"State: {self.robot.state}")
        
        if self.robot.state == "SHUTDOWN":
            self.toggle_auto_btn.config(text="SYSTEM OFF", state="disabled", bg="#95a5a6")
            self.power_on_btn.config(state="normal", bg="#2ecc71")
        elif self.robot.state == "CHARGING":
            self.toggle_auto_btn.config(text="CHARGING...", state="disabled", bg="#95a5a6")
            self.power_on_btn.config(state="disabled", bg="#95a5a6")
        elif self.robot.autonomous:
            self.toggle_auto_btn.config(text="STOP AUTO", state="normal", bg="#e74c3c")
            self.power_on_btn.config(state="disabled", bg="#95a5a6")
        else:
            self.toggle_auto_btn.config(text="START AUTO", state="normal", bg="#27ae60")
            self.power_on_btn.config(state="disabled", bg="#95a5a6")
    
    # All control methods remain the same
    def move(self, direction):
        if self.robot.state == "SHUTDOWN":
            messagebox.showwarning("Warning", "Robot is shut down. Power on first.")
            return
        if self.robot.autonomous:
            messagebox.showwarning("Warning", "Disable autonomous mode first")
            return
        if self.robot.state == "CHARGING":
            messagebox.showwarning("Warning", "Cannot move while charging! Use STOP CHARGE first.")
            return

        if direction == "forward":
            self.robot.y += 1
        elif direction == "backward":
            self.robot.y -= 1
        elif direction == "left":
            self.robot.x -= 1
        elif direction == "right":
            self.robot.x += 1

        self.robot.state = f"MANUAL {direction.upper()}"
    
    def toggle_autonomous(self):
        if self.robot.state == "SHUTDOWN":
            messagebox.showwarning("Warning", "Cannot start - robot is SHUT DOWN! Use POWER ON first.")
            return
        if self.robot.state == "CHARGING":
            messagebox.showwarning("Warning", "Cannot change mode while charging! Use STOP CHARGE first.")
            return
        
        if self.robot.autonomous:
            self.stop()
        else:
            self.start()
    
    def start(self):
        if self.robot.state == "SHUTDOWN":
            messagebox.showwarning("Warning", "Cannot start - robot is SHUT DOWN! Use POWER ON first.")
            return
        if self.robot.state == "CHARGING":
            messagebox.showwarning("Warning", "Robot is charging. Use STOP CHARGE first.")
            return
        self.robot.start_autonomous()
    
    def stop(self):
        if self.robot.going_home and self.robot.battery <= 20:
            messagebox.showerror("Error", "Cannot stop - battery too low")
            return
        self.robot.stop()
    
    def go_home(self):
        if self.robot.state == "SHUTDOWN":
            messagebox.showwarning("Warning", "Robot is shut down. Power on first.")
            return
        if self.robot.state == "CHARGING":
            messagebox.showwarning("Warning", "Robot is already charging at home")
            return
        self.robot.go_home()
    
    def emergency_stop(self):
        if self.robot.state == "SHUTDOWN":
            messagebox.showwarning("Warning", "Robot is already shut down")
            return
        self.robot.emergency_stop()
        messagebox.showwarning("EMERGENCY STOP", "Robot has been emergency stopped!")
    
    def shutdown(self):
        if self.role == "admin":
            result = messagebox.askyesno("Shutdown", "Are you sure you want to shutdown the robot?")
            if result:
                self.robot.shutdown()
                messagebox.showinfo("Shutdown", "Robot has been shut down. Use POWER ON to restart.")
        else:
            messagebox.showerror("Error", "Only admin can shutdown the robot")
    
    def power_on(self):
        if self.robot.state == "SHUTDOWN":
            self.robot.power_on()
            messagebox.showinfo("Power On", "Robot has been powered on and is now in IDLE mode")
        else:
            messagebox.showwarning("Warning", "Robot is not in SHUTDOWN state")
    
    def stop_charging(self):
        if self.robot.state == "CHARGING":
            self.robot.state = "IDLE"
            self.robot.autonomous = False
            self.robot.going_home = False
            self.robot.waiting_full_charge = False
            self.robot.decision = "Charging stopped by user"
            messagebox.showinfo("Charging Stopped", "Robot has stopped charging and is now in IDLE mode")
        else:
            messagebox.showwarning("Warning", "Robot is not currently charging")
    
    def resume_charging(self):
        if (self.robot.x, self.robot.y) == self.robot.home:
            if self.robot.state != "CHARGING":
                self.robot.state = "CHARGING"
                self.robot.waiting_full_charge = True
                self.robot.autonomous = False
                self.robot.going_home = False
                messagebox.showinfo("Charging Resumed", "Robot is now charging")
            else:
                messagebox.showwarning("Warning", "Robot is already charging")
        else:
            messagebox.showwarning("Warning", "Robot is not at home position. Use GO HOME first.")
    
    def toggle_resume(self):
        self.robot.toggle_resume_after_charge()
        status = "ON" if self.robot.resume_after_charge else "OFF"
        self.resume_toggle_btn.config(text=f"RESUME AFTER CHARGE: {status}")
