import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import base64
from io import BytesIO

class UserSettings:
    def __init__(self, root, auth, current_user, dashboard_callback, robot_instance):
        self.root = root
        self.auth = auth
        self.current_user = current_user
        self.dashboard_callback = dashboard_callback
        self.robot_instance = robot_instance
        
        self.setup_ui()
    
    def setup_ui(self):
        bg_color = "#ecf0f1"
        self.root.configure(bg=bg_color)
        
        window_width = 500
        window_height = 650
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.title("User Settings")
        self.root.resizable(False, False)
        
        main_frame = tk.Frame(self.root, bg=bg_color, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        tk.Label(main_frame, text="User Settings", font=("Arial", 18, "bold"),
                bg=bg_color, fg="#2c3e50").pack(pady=(0, 20))
        
        # 2FA Section
        self.create_2fa_section(main_frame)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Password Change Section
        self.create_password_section(main_frame)
        
        # Back button
        tk.Button(main_frame, text="Back to Dashboard", command=self.go_back,
                 font=("Arial", 11, "bold"), width=20, bg="#95a5a6", fg="white",
                 relief="flat", cursor="hand2").pack(pady=20)
    
    def create_2fa_section(self, parent):
        frame = tk.Frame(parent, bg="#ecf0f1")
        frame.pack(fill="x", pady=10)
        
        tk.Label(frame, text="Two-Factor Authentication", font=("Arial", 14, "bold"),
                bg="#ecf0f1", fg="#2c3e50").pack()
        
        if self.auth.is_2fa_enabled(self.current_user):
            tk.Label(frame, text="2FA is ENABLED", font=("Arial", 11),
                    bg="#ecf0f1", fg="#27ae60").pack(pady=5)
            
            tk.Button(frame, text="Disable 2FA", command=self.show_disable_2fa_verification,
                     font=("Arial", 10, "bold"), width=15, bg="#e74c3c", fg="white",
                     relief="flat", cursor="hand2").pack(pady=5)
        else:
            tk.Label(frame, text="2FA is DISABLED", font=("Arial", 11),
                    bg="#ecf0f1", fg="#e74c3c").pack(pady=5)
            
            tk.Button(frame, text="Enable 2FA", command=self.enable_2fa,
                     font=("Arial", 10, "bold"), width=15, bg="#27ae60", fg="white",
                     relief="flat", cursor="hand2").pack(pady=5)
    
    def create_password_section(self, parent):
        frame = tk.Frame(parent, bg="#ecf0f1")
        frame.pack(fill="x", pady=10)
        
        tk.Label(frame, text="Change Password", font=("Arial", 14, "bold"),
                bg="#ecf0f1", fg="#2c3e50").pack(pady=(0, 10))
        
        tk.Label(frame, text="Current Password:", font=("Arial", 11), bg="#ecf0f1").pack()
        self.old_pw = tk.Entry(frame, show="*", font=("Arial", 11), width=25, relief="solid", bd=1)
        self.old_pw.pack(pady=5)
        
        tk.Label(frame, text="New Password:", font=("Arial", 11), bg="#ecf0f1").pack()
        self.new_pw = tk.Entry(frame, show="*", font=("Arial", 11), width=25, relief="solid", bd=1)
        self.new_pw.pack(pady=5)
        
        tk.Label(frame, text="Confirm Password:", font=("Arial", 11), bg="#ecf0f1").pack()
        self.confirm_pw = tk.Entry(frame, show="*", font=("Arial", 11), width=25, relief="solid", bd=1)
        self.confirm_pw.pack(pady=5)
        
        tk.Button(frame, text="Change Password", command=self.change_password,
                 font=("Arial", 10, "bold"), width=15, bg="#3498db", fg="white",
                 relief="flat", cursor="hand2").pack(pady=10)
    
    def show_disable_2fa_verification(self):
        """Show verification window before disabling 2FA"""
        verify_window = tk.Toplevel(self.root)
        verify_window.title("Verify Identity - Disable 2FA")
        verify_window.geometry("400x350")
        verify_window.transient(self.root)
        verify_window.grab_set()
        verify_window.configure(bg="#ecf0f1")
        
        # Center the window
        verify_window.update_idletasks()
        x = (verify_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (verify_window.winfo_screenheight() // 2) - (350 // 2)
        verify_window.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(verify_window, bg="#ecf0f1", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        tk.Label(main_frame, text="Disable Two-Factor Authentication", 
                font=("Arial", 14, "bold"), bg="#ecf0f1", fg="#e74c3c").pack(pady=(0, 15))
        
        tk.Label(main_frame, text="For security, please verify your identity:", 
                font=("Arial", 11), bg="#ecf0f1").pack(pady=5)
        
        # Password field
        tk.Label(main_frame, text="Enter your password:", font=("Arial", 11), 
                bg="#ecf0f1").pack(pady=(15, 5))
        password_entry = tk.Entry(main_frame, show="*", font=("Arial", 11), 
                                  width=25, relief="solid", bd=1)
        password_entry.pack(pady=5)
        
        # 2FA code field
        tk.Label(main_frame, text="Enter 6-digit code from authenticator app:", 
                font=("Arial", 11), bg="#ecf0f1").pack(pady=(15, 5))
        code_entry = tk.Entry(main_frame, font=("Arial", 14), width=10, 
                              justify="center", relief="solid", bd=1)
        code_entry.pack(pady=5)
        
        def verify_and_disable():
            password = password_entry.get()
            totp_code = code_entry.get()
            
            if not password or not totp_code:
                messagebox.showerror("Error", "Please enter both password and 2FA code")
                return
            
            if len(totp_code) != 6:
                messagebox.showerror("Error", "Please enter a valid 6-digit code")
                return
            
            # Verify password
            if self.auth.hash_password(password) != self.auth.users[self.current_user]["password"]:
                messagebox.showerror("Error", "Incorrect password")
                return
            
            # Verify 2FA code
            secret = self.auth.users[self.current_user].get("totp_secret")
            if not secret:
                messagebox.showerror("Error", "2FA configuration error")
                return
            
            import pyotp
            totp = pyotp.TOTP(secret)
            if not totp.verify(totp_code):
                messagebox.showerror("Error", "Invalid 2FA code")
                return
            
            # Both verifications passed - disable 2FA
            if self.auth.disable_2fa(self.current_user):
                messagebox.showinfo("Success", "2FA has been disabled for your account.")
                verify_window.destroy()
                self.refresh_ui()
            else:
                messagebox.showerror("Error", "Failed to disable 2FA")
        
        button_frame = tk.Frame(main_frame, bg="#ecf0f1")
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Verify & Disable 2FA", command=verify_and_disable,
                 font=("Arial", 11, "bold"), bg="#e74c3c", fg="white", 
                 relief="flat", padx=15, pady=5).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Cancel", command=verify_window.destroy,
                 font=("Arial", 11), bg="#95a5a6", fg="white", 
                 relief="flat", padx=15, pady=5).pack(side="left", padx=5)
        
        # Bind Enter key to verify
        code_entry.bind('<Return>', lambda e: verify_and_disable())
        password_entry.bind('<Return>', lambda e: verify_and_disable())
    
    def enable_2fa(self):
        """Show QR code for 2FA enrollment"""
        secret, qr_base64, message = self.auth.setup_2fa(self.current_user)
        
        if not secret:
            messagebox.showerror("Error", message)
            return
        
        # Create enrollment window
        enroll_window = tk.Toplevel(self.root)
        enroll_window.title("Enable 2FA")
        enroll_window.geometry("550x700")
        enroll_window.transient(self.root)
        enroll_window.grab_set()
        enroll_window.configure(bg="#ecf0f1")
        
        # Center the window
        enroll_window.update_idletasks()
        x = (enroll_window.winfo_screenwidth() // 2) - (550 // 2)
        y = (enroll_window.winfo_screenheight() // 2) - (700 // 2)
        enroll_window.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(enroll_window, bg="#ecf0f1", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        tk.Label(main_frame, text="Enable Two-Factor Authentication", 
                font=("Arial", 16, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=(0, 10))
        
        instructions = tk.Label(main_frame, 
            text="1. Install Google Authenticator or any TOTP app on your phone\n"
                 "2. Scan the QR code below with the app\n"
                 "3. Enter the 6-digit code from the app to verify",
            font=("Arial", 10), bg="#ecf0f1", fg="#7f8c8d", justify="left")
        instructions.pack(pady=10)
        
        # Display QR code
        img_data = base64.b64decode(qr_base64)
        img = Image.open(BytesIO(img_data))
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
                self.refresh_ui()
            else:
                messagebox.showerror("Error", msg)
        
        button_frame = tk.Frame(main_frame, bg="#ecf0f1")
        button_frame.pack(pady=15)
        
        tk.Button(button_frame, text="Verify & Enable", command=verify_enrollment,
                 font=("Arial", 11, "bold"), bg="#27ae60", fg="white", 
                 relief="flat", padx=20, pady=5).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Cancel", command=enroll_window.destroy,
                 font=("Arial", 11), bg="#95a5a6", fg="white", 
                 relief="flat", padx=20, pady=5).pack(side="left", padx=5)
        
        code_entry.bind('<Return>', lambda e: verify_enrollment())
    
    def refresh_ui(self):
        """Refresh the UI to show updated 2FA status"""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()
    
    def change_password(self):
        old = self.old_pw.get()
        new = self.new_pw.get()
        confirm = self.confirm_pw.get()
        
        if not old or not new:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if new != confirm:
            messagebox.showerror("Error", "New passwords do not match")
            return
        
        if len(new) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters")
            return
        
        if self.auth.change_password(self.current_user, old, new):
            messagebox.showinfo("Success", "Password changed successfully!")
            self.go_back()
        else:
            messagebox.showerror("Error", "Current password is incorrect")
    
    def go_back(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.dashboard_callback.reload_dashboard()
