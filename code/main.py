from login_window import LoginWindow
from auth import AuthSystem
import tkinter as tk
from tkinter import ttk

def setup_styles():
    style = ttk.Style()
    style.theme_use('default')
    style.configure('green.Horizontal.TProgressbar', background='#27ae60')
    style.configure('yellow.Horizontal.TProgressbar', background='#f39c12')
    style.configure('red.Horizontal.TProgressbar', background='#e74c3c')

def main():
    auth = AuthSystem()

    root = tk.Tk()
    root.title("Greenhouse Robot Control System")
    setup_styles()
    login = LoginWindow(root, auth)
    print("MAIN ROOT:", root)
    root.mainloop()

if __name__ == "__main__":
    main()
