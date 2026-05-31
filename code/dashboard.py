import tkinter as tk
from tkinter import ttk, messagebox
from robot_panel import RobotPanel
from sensors_panel import SensorsPanel
from PIL import Image, ImageTk
import base64
from io import BytesIO

class Dashboard:
    def __init__(self, root, auth, role, username, robot_instance=None):
        self.root = root
        self.auth = auth
        self.role = role
        self.current_user = username
        self.running = True
        self.graph_window = None
        
        if robot_instance:
            self.robot = robot_instance
        else:
            from robot import Robot
            self.robot = Robot()
        
        # Clear any existing geometry management
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.setup_window()
        self.create_menu()
        self.create_top_bar(role, username)
        self.create_main_panels()
        
        # Check if 2FA needs to be set up (after UI is ready)
        self.root.after(500, self.check_2fa_enrollment)
        
        self.update()
    
    def setup_window(self):
        self.root.geometry("1200x700")
        self.root.title("Greenhouse Robot Control System")
        self.root.resizable(False, False)
        
        # Configure grid for root
        self.root.grid_rowconfigure(0, weight=0)  # Top bar fixed
        self.root.grid_rowconfigure(1, weight=1)  # Main content expands
        self.root.grid_columnconfigure(0, weight=45)  # Left panel 45%
        self.root.grid_columnconfigure(1, weight=55)  # Right panel 55%
    
    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        
        system_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="System", menu=system_menu)
        
        if self.role == "admin":
            system_menu.add_command(label="Admin Panel", command=self.open_admin)
        
        system_menu.add_separator()
        system_menu.add_command(label="Logout", command=self.logout)
        system_menu.add_command(label="Exit", command=self.exit_app)
        
        view_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Sensor Graphs", command=self.open_sensor_graphs)
        view_menu.add_command(label="Settings", command=self.open_user_settings)
        
        help_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_top_bar(self, role, username):
        top_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        top_frame.grid_propagate(False)
        
        # Use grid inside top_frame
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_columnconfigure(2, weight=1)
        
        # Left side - User info
        tk.Label(top_frame, text=f"{username} ({role})", 
                font=("Arial", 11, "bold"), bg="#2c3e50", fg="white").grid(row=0, column=0, padx=15, sticky="w")
        
        # Center - Mode
        self.mode_label = tk.Label(top_frame, text="MODE: MANUAL", 
                                   font=("Arial", 11, "bold"), bg="#2c3e50", fg="#f39c12")
        self.mode_label.grid(row=0, column=1)
        
        # Right side - Status
        self.status_indicator = tk.Label(top_frame, text="ONLINE", 
                                        font=("Arial", 10, "bold"), bg="#2c3e50", fg="#2ecc71")
        self.status_indicator.grid(row=0, column=2, padx=15, sticky="e")
    
    def create_main_panels(self):
        # Left panel container
        left_container = tk.Frame(self.root, bg="#ecf0f1")
        left_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        left_container.grid_rowconfigure(0, weight=1)
        left_container.grid_columnconfigure(0, weight=1)
        
        # Right panel container
        right_container = tk.Frame(self.root, bg="#ecf0f1")
        right_container.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        right_container.grid_rowconfigure(0, weight=1)
        right_container.grid_columnconfigure(0, weight=1)
        
        self.robot_panel = RobotPanel(left_container, self.robot, self.role)
        self.sensors_panel = SensorsPanel(right_container, self.robot)
    
    def check_2fa_enrollment(self):
        """Check if user needs to set up 2FA"""
        user_data = self.auth.users.get(self.current_user, {})
        
        # Only prompt for non-admin users who haven't set up 2FA
        if not user_data.get("totp_enabled", False) and self.role != "admin":
            # Ask if user wants to set up 2FA now
            result = messagebox.askyesno(
                "Security Setup", 
                "Two-Factor Authentication (2FA) is recommended for better security.\n\n"
                "Would you like to set up 2FA now?\n\n"
                "You can also set it up later from the Settings menu."
            )
            if result:
                self.show_2fa_enrollment()
    
    def show_2fa_enrollment(self):
        """Show QR code for 2FA enrollment"""
        secret, qr_base64, message = self.auth.setup_2fa(self.current_user)
        
        if not secret:
            messagebox.showerror("Error", message)
            return
        
        # Create enrollment window
        enroll_window = tk.Toplevel(self.root)
        enroll_window.title("2FA Setup - Scan QR Code")
        enroll_window.geometry("550x700")
        enroll_window.transient(self.root)
        enroll_window.grab_set()
        enroll_window.configure(bg="#ecf0f1")
        
        # Center the window
        enroll_window.update_idletasks()
        x = (enroll_window.winfo_screenwidth() // 2) - (550 // 2)
        y = (enroll_window.winfo_screenheight() // 2) - (700 // 2)
        enroll_window.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(enroll_window, bg="#ecf0f1", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        tk.Label(main_frame, text="Two-Factor Authentication Setup", 
                font=("Arial", 16, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=(0, 10))
        
        # Instructions
        instructions = tk.Label(main_frame, 
            text="1. Install Google Authenticator or any TOTP app on your phone\n"
                 "2. Scan the QR code below with the app\n"
                 "3. Enter the 6-digit code from the app to verify",
            font=("Arial", 10), bg="#ecf0f1", fg="#7f8c8d", justify="left")
        instructions.pack(pady=10)
        
        # Display QR code
        img_data = base64.b64decode(qr_base64)
        img = Image.open(BytesIO(img_data))
        # Resize QR code for better visibility
        img = img.resize((250, 250), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        qr_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=2)
        qr_frame.pack(pady=15)
        qr_label = tk.Label(qr_frame, image=photo, bg="white")
        qr_label.image = photo
        qr_label.pack(padx=10, pady=10)
        
        # Secret key backup
        tk.Label(main_frame, text="Or enter this secret key manually:", 
                font=("Arial", 10), bg="#ecf0f1").pack()
        
        secret_frame = tk.Frame(main_frame, bg="#ecf0f1")
        secret_frame.pack(pady=5)
        
        secret_label = tk.Label(secret_frame, text=secret, font=("Courier", 11, "bold"), 
                                bg="#f8f9fa", fg="#2c3e50", relief="solid", bd=1, padx=10, pady=5)
        secret_label.pack(side="left")
        
        def copy_secret():
            self.root.clipboard_clear()
            self.root.clipboard_append(secret)
            messagebox.showinfo("Copied", "Secret key copied to clipboard!")
        
        tk.Button(secret_frame, text="Copy", command=copy_secret, 
                 font=("Arial", 9), bg="#3498db", fg="white", relief="flat").pack(side="left", padx=5)
        
        # Verification section
        tk.Label(main_frame, text="Verify Setup", font=("Arial", 12, "bold"),
                bg="#ecf0f1", fg="#2c3e50").pack(pady=(15, 5))
        
        tk.Label(main_frame, text="Enter the 6-digit code from your authenticator app:", 
                font=("Arial", 10), bg="#ecf0f1").pack()
        
        code_entry = tk.Entry(main_frame, font=("Arial", 18), width=10, 
                              justify="center", relief="solid", bd=1)
        code_entry.pack(pady=10)
        code_entry.focus()
        
        def verify_enrollment():
            code = code_entry.get().strip()
            if not code or len(code) != 6:
                messagebox.showerror("Error", "Please enter a valid 6-digit code")
                return
            
            ok, msg = self.auth.verify_2fa_enrollment(self.current_user, code)
            if ok:
                messagebox.showinfo("Success", "2FA enabled successfully!\n\n"
                                           "You will now need to enter a code from your authenticator app each time you log in.")
                enroll_window.destroy()
            else:
                messagebox.showerror("Error", msg)
        
        button_frame = tk.Frame(main_frame, bg="#ecf0f1")
        button_frame.pack(pady=15)
        
        tk.Button(button_frame, text="Verify & Complete", command=verify_enrollment,
                 font=("Arial", 11, "bold"), bg="#27ae60", fg="white", 
                 relief="flat", padx=20, pady=5).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Skip for Now", command=enroll_window.destroy,
                 font=("Arial", 11), bg="#95a5a6", fg="white", 
                 relief="flat", padx=20, pady=5).pack(side="left", padx=5)
        
        # Bind Enter key to verify
        code_entry.bind('<Return>', lambda e: verify_enrollment())
    
    def update(self):
        if not hasattr(self, "running") or not self.running:
            return
        
        self.robot.update()
        self.robot_panel.update()
        self.sensors_panel.update()
        
        mode_text = "AUTO" if self.robot.autonomous else "MANUAL"
        self.mode_label.config(text=f"MODE: {mode_text}")
        
        if self.robot.state == "SHUTDOWN":
            self.status_indicator.config(text="OFFLINE", fg="#e74c3c")
        elif self.robot.state == "CHARGING":
            self.status_indicator.config(text="CHARGING", fg="#f39c12")
        else:
            self.status_indicator.config(text="ONLINE", fg="#2ecc71")
        
        self.root.after(500, self.update)
    
    def logout(self):
        self.running = False
        if self.graph_window:
            try:
                if hasattr(self.graph_window, 'winfo_exists') and self.graph_window.winfo_exists():
                    self.graph_window.destroy()
            except:
                pass
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        from login_window import LoginWindow
        LoginWindow(self.root, self.auth, self.robot)
    
    def exit_app(self):
        if messagebox.askyesno("Exit", "Exit application?"):
            self.running = False
            self.root.quit()
            self.root.destroy()
    
    def show_about(self):
        messagebox.showinfo("About", "Greenhouse Robot Control System\nVersion 2.0\n\n"
                                    "Features:\n"
                                    "- Two-Factor Authentication\n"
                                    "- Account Recovery via 2FA\n"
                                    "- Automatic Greenhouse Control\n"
                                    "- Real-time Sensor Monitoring")
    
    def open_admin(self):
        self.running = False
        if self.graph_window:
            try:
                if hasattr(self.graph_window, 'winfo_exists') and self.graph_window.winfo_exists():
                    self.graph_window.destroy()
            except:
                pass
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        from admin_panel import AdminPanel
        AdminPanel(self.root, self.auth, self.role, self.current_user, self, self.robot)
    
    def open_sensor_graphs(self):
        from sensor_graphs import SensorGraphs
        self.graph_window = SensorGraphs(self.root, self.robot)
    
    def open_user_settings(self):
        self.running = False
        if self.graph_window:
            try:
                if hasattr(self.graph_window, 'winfo_exists') and self.graph_window.winfo_exists():
                    self.graph_window.destroy()
            except:
                pass
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        from user_settings import UserSettings
        UserSettings(self.root, self.auth, self.current_user, self, self.robot)
    
    def reload_dashboard(self):
        self.running = False
        if self.graph_window:
            try:
                if hasattr(self.graph_window, 'winfo_exists') and self.graph_window.winfo_exists():
                    self.graph_window.destroy()
            except:
                pass
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        Dashboard(self.root, self.auth, self.role, self.current_user, self.robot)
