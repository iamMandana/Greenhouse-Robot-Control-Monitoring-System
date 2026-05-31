import tkinter as tk
from tkinter import messagebox

class LoginWindow:
    def __init__(self, root, auth, robot_instance=None):
        self.root = root
        self.auth = auth
        self.robot_instance = robot_instance
        self.pending_2fa_user = None

        # Reset the root window layout completely
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Reset grid configuration
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Remove any existing grid configurations from other rows/columns
        for i in range(10):
            self.root.grid_rowconfigure(i, weight=0)
        for i in range(10):
            self.root.grid_columnconfigure(i, weight=0)
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        window_width = 500
        window_height = 550
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        root.title("Greenhouse Robot Control System")
        root.resizable(False, False)

        bg_color = "#ecf0f1"
        root.configure(bg=bg_color)
        
        self.main_frame = tk.Frame(root, bg=bg_color)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Configure main_frame grid
        for i in range(10):
            self.main_frame.grid_rowconfigure(i, weight=0)
        self.main_frame.grid_rowconfigure(9, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.show_login_form()
    
    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_login_form(self):
        self.clear_frame()
        
        # Title
        title = tk.Label(self.main_frame, text="Greenhouse Robot System", 
                font=("Arial", 16, "bold"), bg="#ecf0f1", fg="#2c3e50")
        title.grid(row=0, column=0, pady=(0, 20))
        
        # Username
        tk.Label(self.main_frame, text="Username", font=("Arial", 11), bg="#ecf0f1").grid(row=1, column=0, pady=(10,0))
        self.user_entry = tk.Entry(self.main_frame, font=("Arial", 11), width=25, relief="solid", bd=1)
        self.user_entry.grid(row=2, column=0, pady=5)
        self.user_entry.bind('<Return>', lambda e: self.login())

        # Password
        tk.Label(self.main_frame, text="Password", font=("Arial", 11), bg="#ecf0f1").grid(row=3, column=0, pady=(10,0))
        self.pw_entry = tk.Entry(self.main_frame, show="*", font=("Arial", 11), width=25, relief="solid", bd=1)
        self.pw_entry.grid(row=4, column=0, pady=5)
        self.pw_entry.bind('<Return>', lambda e: self.login())

        # Buttons
        button_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        button_frame.grid(row=5, column=0, pady=15)
        
        tk.Button(button_frame, text="Login", command=self.login, 
                 font=("Arial", 11, "bold"), width=12, bg="#3498db", fg="white",
                 relief="flat", cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Unlock Account", command=self.show_unlock_form, 
                 font=("Arial", 10), width=14, bg="#f39c12", fg="white",
                 relief="flat", cursor="hand2").pack(side="left", padx=5)
        
        # Bottom buttons
        bottom_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        bottom_frame.grid(row=6, column=0, pady=10)
        
        tk.Button(bottom_frame, text="Forgot Password", command=self.show_reset_form, 
                 font=("Arial", 10), width=15, bg="#95a5a6", fg="white",
                 relief="flat", cursor="hand2").pack()
        
        # Center all content by configuring column weights
        self.main_frame.grid_columnconfigure(0, weight=1)
    
    def login(self):
        username = self.user_entry.get()
        password = self.pw_entry.get()
        
        ok, result = self.auth.login(username, password)
        
        if ok:
            for widget in self.root.winfo_children():
                widget.destroy()
            from dashboard import Dashboard
            Dashboard(self.root, self.auth, result, username, self.robot_instance)
        elif result == "2FA_REQUIRED":
            self.pending_2fa_user = username
            self.show_2fa_form()
        else:
            messagebox.showerror("Login Failed", result)
    
    def show_2fa_form(self):
        self.clear_frame()
        
        tk.Label(self.main_frame, text="Two-Factor Authentication", 
                font=("Arial", 16, "bold"), bg="#ecf0f1", fg="#2c3e50").grid(row=0, column=0, pady=(0, 20))
        
        tk.Label(self.main_frame, text=f"User: {self.pending_2fa_user}", 
                font=("Arial", 12), bg="#ecf0f1").grid(row=1, column=0, pady=10)
        
        tk.Label(self.main_frame, text="Open your authenticator app and enter the 6-digit code:", 
                font=("Arial", 11), bg="#ecf0f1").grid(row=2, column=0, pady=10)
        
        self.code_entry = tk.Entry(self.main_frame, font=("Arial", 18), width=10, 
                                   relief="solid", bd=1, justify="center")
        self.code_entry.grid(row=3, column=0, pady=10)
        self.code_entry.bind('<Return>', lambda e: self.verify_2fa())
        
        button_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        button_frame.grid(row=4, column=0, pady=15)
        
        tk.Button(button_frame, text="Verify", command=self.verify_2fa, 
                 font=("Arial", 11, "bold"), width=10, bg="#27ae60", fg="white",
                 relief="flat").pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Back", command=self.show_login_form, 
                 font=("Arial", 11), width=10, bg="#95a5a6", fg="white",
                 relief="flat").pack(side="left", padx=5)
        
        self.main_frame.grid_columnconfigure(0, weight=1)
    
    def verify_2fa(self):
        code = self.code_entry.get()
        if not code or len(code) != 6:
            messagebox.showerror("Error", "Please enter a valid 6-digit code")
            return
        
        ok, result = self.auth.login(self.pending_2fa_user, None, code)
        
        if ok:
            for widget in self.root.winfo_children():
                widget.destroy()
            from dashboard import Dashboard
            Dashboard(self.root, self.auth, result, self.pending_2fa_user, self.robot_instance)
        else:
            messagebox.showerror("2FA Failed", result)
            self.show_login_form()
    
    def show_unlock_form(self):
        self.clear_frame()
        
        tk.Label(self.main_frame, text="Unlock Account", 
                font=("Arial", 16, "bold"), bg="#ecf0f1", fg="#2c3e50").grid(row=0, column=0, pady=(0, 20))
        
        tk.Label(self.main_frame, text="Username", font=("Arial", 11), bg="#ecf0f1").grid(row=1, column=0, pady=5)
        self.unlock_user_entry = tk.Entry(self.main_frame, font=("Arial", 11), width=25, relief="solid", bd=1)
        self.unlock_user_entry.grid(row=2, column=0, pady=5)
        
        tk.Label(self.main_frame, text="Enter 6-digit code from authenticator app:", 
                font=("Arial", 11), bg="#ecf0f1").grid(row=3, column=0, pady=10)
        self.unlock_code_entry = tk.Entry(self.main_frame, font=("Arial", 18), width=10, 
                                          relief="solid", bd=1, justify="center")
        self.unlock_code_entry.grid(row=4, column=0, pady=5)
        
        button_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        button_frame.grid(row=5, column=0, pady=15)
        
        tk.Button(button_frame, text="Unlock", command=self.unlock_account, 
                 font=("Arial", 11, "bold"), width=10, bg="#27ae60", fg="white",
                 relief="flat").pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Back", command=self.show_login_form, 
                 font=("Arial", 11), width=10, bg="#95a5a6", fg="white",
                 relief="flat").pack(side="left", padx=5)
        
        self.main_frame.grid_columnconfigure(0, weight=1)
    
    def unlock_account(self):
        username = self.unlock_user_entry.get()
        code = self.unlock_code_entry.get()
        
        if not username or not code:
            messagebox.showerror("Error", "Please enter username and 6-digit code")
            return
        
        ok, message = self.auth.unlock_account(username, code)
        if ok:
            messagebox.showinfo("Success", message)
            self.show_login_form()
        else:
            messagebox.showerror("Failed", message)
    
    def show_reset_form(self):
        self.clear_frame()
        
        tk.Label(self.main_frame, text="Reset Password", 
                font=("Arial", 16, "bold"), bg="#ecf0f1", fg="#2c3e50").grid(row=0, column=0, pady=(0, 20))
        
        tk.Label(self.main_frame, text="Username", font=("Arial", 11), bg="#ecf0f1").grid(row=1, column=0, pady=5)
        self.reset_user_entry = tk.Entry(self.main_frame, font=("Arial", 11), width=25, relief="solid", bd=1)
        self.reset_user_entry.grid(row=2, column=0, pady=5)
        
        tk.Label(self.main_frame, text="Enter 6-digit code from authenticator app:", 
                font=("Arial", 11), bg="#ecf0f1").grid(row=3, column=0, pady=10)
        self.reset_code_entry = tk.Entry(self.main_frame, font=("Arial", 18), width=10, 
                                         relief="solid", bd=1, justify="center")
        self.reset_code_entry.grid(row=4, column=0, pady=5)
        
        tk.Label(self.main_frame, text="New Password", font=("Arial", 11), bg="#ecf0f1").grid(row=5, column=0, pady=(10,0))
        self.new_password_entry = tk.Entry(self.main_frame, show="*", font=("Arial", 11), 
                                           width=20, relief="solid", bd=1)
        self.new_password_entry.grid(row=6, column=0, pady=5)
        
        tk.Label(self.main_frame, text="Confirm Password", font=("Arial", 11), bg="#ecf0f1").grid(row=7, column=0, pady=(10,0))
        self.confirm_password_entry = tk.Entry(self.main_frame, show="*", font=("Arial", 11), 
                                               width=20, relief="solid", bd=1)
        self.confirm_password_entry.grid(row=8, column=0, pady=5)
        
        button_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        button_frame.grid(row=9, column=0, pady=15)
        
        tk.Button(button_frame, text="Reset Password", command=self.reset_password, 
                 font=("Arial", 11, "bold"), width=15, bg="#27ae60", fg="white",
                 relief="flat").pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Back", command=self.show_login_form, 
                 font=("Arial", 11), width=10, bg="#95a5a6", fg="white",
                 relief="flat").pack(side="left", padx=5)
        
        self.main_frame.grid_columnconfigure(0, weight=1)
    
    def reset_password(self):
        username = self.reset_user_entry.get()
        totp_code = self.reset_code_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if not username or not totp_code or not new_password:
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if len(new_password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters")
            return
        
        ok, message = self.auth.reset_password_with_2fa(username, totp_code, new_password)
        if ok:
            messagebox.showinfo("Success", message)
            self.show_login_form()
        else:
            messagebox.showerror("Error", message)
