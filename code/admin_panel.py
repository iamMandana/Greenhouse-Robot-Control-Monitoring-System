import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

class AdminPanel:
    def __init__(self, root, auth, role, username, dashboard_callback, robot_instance):
        self.root = root
        self.auth = auth
        self.role = role
        self.username = username
        self.dashboard_callback = dashboard_callback
        self.robot_instance = robot_instance
        self.after_id = None  # Store after callback ID
        
        self.setup_ui()
    
    def setup_ui(self):
        bg_color = "#ecf0f1"
        self.root.configure(bg=bg_color)
        
        window_width = 1000
        window_height = 650
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.title("Admin Panel - User Management")
        self.root.resizable(False, False)
        
        main_frame = tk.Frame(self.root, bg=bg_color, padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)
        
        # Heading with background color
        heading_frame = tk.Frame(main_frame, bg="#2c3e50", height=50)
        heading_frame.pack(fill="x", pady=(0, 15))
        heading_frame.pack_propagate(False)
        
        tk.Label(heading_frame, text="ADMIN PANEL - USER MANAGEMENT", 
                font=("Arial", 16, "bold"), bg="#2c3e50", fg="white").pack(expand=True)
        
        # User list frame
        list_frame = tk.Frame(main_frame, bg=bg_color)
        list_frame.pack(pady=10, fill="both", expand=True)
        
        # Create scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Create Treeview with columns
        columns = ("Username", "Role", "Status", "Locked")
        self.user_tree = ttk.Treeview(list_frame, columns=columns, show="headings", 
                                      height=15, yscrollcommand=scrollbar.set)
        
        # Define headings
        self.user_tree.heading("Username", text="Username")
        self.user_tree.heading("Role", text="Role")
        self.user_tree.heading("Status", text="Status")
        self.user_tree.heading("Locked", text="Locked")
        
        # Define column widths
        self.user_tree.column("Username", width=200, anchor="center")
        self.user_tree.column("Role", width=150, anchor="center")
        self.user_tree.column("Status", width=200, anchor="center")
        self.user_tree.column("Locked", width=150, anchor="center")
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        
        self.user_tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.user_tree.yview)
        
        self.load_users()
        
        # Buttons frame
        btn_frame = tk.Frame(main_frame, bg=bg_color)
        btn_frame.pack(pady=15)
        
        button_style = {"font": ("Arial", 9, "bold"), "width": 14, "height": 1,
                       "relief": "flat", "cursor": "hand2"}
        
        buttons = [
            ("Add User", self.open_add_user_window, "#27ae60"),
            ("Delete User", self.delete_user, "#e74c3c"),
            ("Unlock User", self.unlock_user, "#f39c12"),
            ("Reset Password", self.reset_password, "#3498db"),
            ("Set Password", self.set_new_password, "#9b59b6"),
            ("Lock User", self.lock_user, "#e67e22"),
            ("Change Role", self.change_user_role, "#1abc9c"),
            ("Back", self.go_back, "#95a5a6")
        ]
        
        row = 0
        col = 0
        for text, command, color in buttons:
            tk.Button(btn_frame, text=text, command=command, bg=color, fg="white",
                     **button_style).grid(row=row, column=col, padx=3, pady=3)
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        self.msg_label = tk.Label(main_frame, text="", font=("Arial", 10), bg=bg_color)
        self.msg_label.pack(pady=5)
    
    def load_users(self):
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        users = self.auth.get_all_users()
        for username, data in users.items():
            role = data["role"]
            locked = data.get("locked", False)
            locked_by_admin = data.get("locked_by_admin", False)
            
            if locked:
                if locked_by_admin:
                    status = "LOCKED BY ADMIN"
                else:
                    status = "LOCKED (Failed Attempts)"
            else:
                status = "ACTIVE"
            
            locked_status = "Yes" if locked else "No"
            
            item_id = self.user_tree.insert('', 'end', values=(username, role, status, locked_status))
            
            if locked:
                if locked_by_admin:
                    self.user_tree.tag_configure('admin_locked', foreground='darkred', font=('Arial', 10, 'bold'))
                    self.user_tree.item(item_id, tags=('admin_locked',))
                else:
                    self.user_tree.tag_configure('locked', foreground='red')
                    self.user_tree.item(item_id, tags=('locked',))
    
    def get_selected_user(self):
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user first")
            return None
        values = self.user_tree.item(selection[0])['values']
        return values[0] if values else None
    
    def show_message(self, text, color="blue"):
        # Cancel any pending after callbacks
        if hasattr(self, 'after_id') and self.after_id:
            self.root.after_cancel(self.after_id)
        
        self.msg_label.config(text=text, fg=color)
        self.after_id = self.root.after(3000, lambda: self.clear_message())
    
    def clear_message(self):
        """Clear message label safely"""
        try:
            if self.msg_label and self.msg_label.winfo_exists():
                self.msg_label.config(text="")
        except:
            pass
        self.after_id = None
    
    def change_user_role(self):
        user = self.get_selected_user()
        if not user:
            return
        
        if user == "admin":
            self.show_message("Cannot change role of admin user", "red")
            return
        
        current_role = self.auth.users[user]["role"]
        
        win = tk.Toplevel(self.root)
        win.title("Change User Role")
        win.geometry("350x250")
        win.transient(self.root)
        win.grab_set()
        win.configure(bg="#ecf0f1")
        
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (350 // 2)
        y = (win.winfo_screenheight() // 2) - (250 // 2)
        win.geometry(f"+{x}+{y}")
        
        tk.Label(win, text=f"Change role for: {user}", font=("Arial", 14, "bold"),
                bg="#ecf0f1", fg="#2c3e50").pack(pady=15)
        
        tk.Label(win, text=f"Current role: {current_role}", font=("Arial", 11),
                bg="#ecf0f1", fg="#7f8c8d").pack()
        
        tk.Label(win, text="Select new role:", font=("Arial", 11), bg="#ecf0f1").pack(pady=(10,5))
        
        role_var = tk.StringVar(win, value=current_role)
        role_options = ["operator", "admin"]
        role_menu = tk.OptionMenu(win, role_var, *role_options)
        role_menu.config(font=("Arial", 11), width=15, bg="white", relief="solid", bd=1)
        role_menu.pack(pady=5)
        
        def apply_role_change():
            new_role = role_var.get()
            if new_role != current_role:
                self.auth.users[user]["role"] = new_role
                self.auth.save_users()
                self.load_users()
                self.show_message(f"Role for '{user}' changed to '{new_role}'", "green")
                messagebox.showinfo("Success", f"Role changed to {new_role}")
                win.destroy()
            else:
                win.destroy()
        
        button_frame = tk.Frame(win, bg="#ecf0f1")
        button_frame.pack(pady=15)
        
        tk.Button(button_frame, text="Apply", command=apply_role_change, font=("Arial", 10, "bold"),
                 bg="#27ae60", fg="white", width=10, relief="flat").pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=win.destroy, font=("Arial", 10, "bold"),
                 bg="#95a5a6", fg="white", width=10, relief="flat").pack(side="left", padx=5)
    
    def unlock_user(self):
        user = self.get_selected_user()
        if user:
            if self.auth.unlock_user(user):
                self.load_users()
                self.show_message(f"User '{user}' unlocked", "green")
            else:
                self.show_message(f"Failed to unlock '{user}'", "red")
    
    def reset_password(self):
        user = self.get_selected_user()
        if user:
            if self.auth.admin_reset_password(user):
                messagebox.showinfo("Reset", f"Password for '{user}' reset to 1234")
                self.load_users()
                self.show_message(f"Password reset for '{user}'", "orange")
            else:
                self.show_message(f"Failed to reset password for '{user}'", "red")
    
    def set_new_password(self):
        user = self.get_selected_user()
        if not user:
            return
        
        new_pw = simpledialog.askstring("New Password", f"Enter new password for '{user}':", show="*")
        if new_pw and len(new_pw) >= 4:
            self.auth.users[user]["password"] = self.auth.hash_password(new_pw)
            self.auth.save_users()
            self.show_message(f"Password updated for '{user}'", "green")
            messagebox.showinfo("Success", f"Password updated for '{user}'")
        elif new_pw:
            messagebox.showerror("Error", "Password must be at least 4 characters")
    
    def delete_user(self):
        user = self.get_selected_user()
        if not user:
            return
        
        if user == "admin":
            self.show_message("Cannot delete admin user", "red")
            return
        
        confirm = messagebox.askyesno("Confirm", f"Delete user '{user}'?")
        if confirm:
            if self.auth.delete_user(user):
                self.load_users()
                self.show_message(f"User '{user}' deleted", "green")
            else:
                self.show_message(f"Failed to delete '{user}'", "red")
    
    def lock_user(self):
        user = self.get_selected_user()
        if user:
            if user == "admin":
                self.show_message("Cannot lock admin user", "red")
                return
            
            self.auth.lock_user(user)
            self.load_users()
            self.show_message(f"User '{user}' locked by admin", "red")
    
    def open_add_user_window(self):
        win = tk.Toplevel(self.root)
        win.title("Add New User")
        win.geometry("400x400")
        win.transient(self.root)
        win.grab_set()
        win.configure(bg="#ecf0f1")
        
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (400 // 2)
        y = (win.winfo_screenheight() // 2) - (400 // 2)
        win.geometry(f"+{x}+{y}")
        
        tk.Label(win, text="Create New User", font=("Arial", 16, "bold"),
                bg="#ecf0f1", fg="#2c3e50").pack(pady=15)
        
        tk.Label(win, text="Username:", font=("Arial", 11), bg="#ecf0f1").pack(pady=(10,0))
        user_entry = tk.Entry(win, font=("Arial", 11), width=25, relief="solid", bd=1)
        user_entry.pack(pady=5)
        
        tk.Label(win, text="Password:", font=("Arial", 11), bg="#ecf0f1").pack(pady=(10,0))
        pass_entry = tk.Entry(win, show="*", font=("Arial", 11), width=25, relief="solid", bd=1)
        pass_entry.pack(pady=5)
        
        tk.Label(win, text="Role:", font=("Arial", 11), bg="#ecf0f1").pack(pady=(10,0))
        
        role_var = tk.StringVar(win, value="operator")
        role_options = ["operator", "admin"]
        role_menu = tk.OptionMenu(win, role_var, *role_options)
        role_menu.config(font=("Arial", 11), width=20, bg="white", relief="solid", bd=1)
        role_menu.pack(pady=5)
        
        def create():
            username = user_entry.get().strip()
            password = pass_entry.get()
            role = role_var.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Username and password required")
                return
                
            if len(password) < 4:
                messagebox.showerror("Error", "Password must be 4+ characters")
                return
                
            if self.auth.add_user(username, password, role):
                messagebox.showinfo("Success", f"User '{username}' created!")
                self.load_users()
                win.destroy()
                self.show_message(f"User '{username}' created", "green")
            else:
                messagebox.showerror("Error", "Username already exists")
        
        button_frame = tk.Frame(win, bg="#ecf0f1")
        button_frame.pack(pady=15)
        
        tk.Button(button_frame, text="Create", command=create, font=("Arial", 11, "bold"),
                 width=12, bg="#27ae60", fg="white", relief="flat").pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=win.destroy, font=("Arial", 11, "bold"),
                 width=12, bg="#95a5a6", fg="white", relief="flat").pack(side="left", padx=5)
    
    def go_back(self):
        # Cancel any pending after callbacks before destroying
        if hasattr(self, 'after_id') and self.after_id:
            self.root.after_cancel(self.after_id)
        
        # Destroy current window and reload dashboard
        for widget in self.root.winfo_children():
            widget.destroy()
        self.dashboard_callback.reload_dashboard()
