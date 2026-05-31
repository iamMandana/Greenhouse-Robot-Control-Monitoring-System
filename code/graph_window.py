import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphWindow:
    def __init__(self, root, robot):
        self.root = root
        self.robot = robot
        self.running = True
        
        self.window = tk.Toplevel(root)
        self.window.title("Battery Graph")
        self.window.geometry("600x500")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.setup_graph()
    
    def setup_graph(self):
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().pack()
        
        self.data = []
        self.update_graph()
    
    def update_graph(self):
        if not self.running:
            return
        
        self.data.append(self.robot.battery)
        if len(self.data) > 20:
            self.data.pop(0)
        
        self.ax.clear()
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, 20)
        self.ax.plot(self.data, linewidth=2, color='#27ae60')
        self.ax.set_title('Battery Level Over Time', fontsize=14)
        self.ax.set_xlabel('Time (seconds)', fontsize=12)
        self.ax.set_ylabel('Battery (%)', fontsize=12)
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
        
        self.window.after(1000, self.update_graph)
    
    def on_close(self):
        self.running = False
        self.window.destroy()
