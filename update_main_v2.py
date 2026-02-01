
import os

content = r'''import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import os
import csv
import sys

# Ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import sorting_algorithms

DATA_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'generated_data.csv')

class ExamApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Sorting Algorithm Stress Test (Prelim Exam)")
        self.geometry("1100x800")
        
        # Color Palette - Latte Theme
        self.bg_main = "#F9F8F6"      # Main Canvas
        self.bg_sidebar = "#EFE9E3"   # Sidebar
        self.text_primary = "#3E342F" # Dark Roast Brown
        self.text_secondary = "#8D8076" # Muted Brown
        self.accent_main = "#C9B59C"  # Latte
        self.accent_hover = "#B8A38B" # Darker Latte
        self.btn_hover = "#D9CFC7"    # Warm Gray
        self.card_border = "#D9CFC7"  # Warm Gray
        self.card_bg = "#FFFFFF"      # Crisp White

        self.configure(bg=self.bg_main)
        
        # Data
        self.full_data = [] # List of dicts
        self.load_data_thread()
        
        # UI State
        self.algo_var = tk.StringVar(value="Bubble Sort")
        self.key_var = tk.StringVar(value="ID")
        self.n_var = tk.StringVar(value="1000")
        
        self.create_layout()
        
    def load_data_thread(self):
        t = threading.Thread(target=self.load_data_bg)
        t.start()
        
    def load_data_bg(self):
        try:
            start = time.perf_counter()
            with open(DATA_FILE_PATH, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = []
                for row in reader:
                    try:
                        row['ID'] = int(row['ID'])
                    except ValueError:
                        pass
                    data.append(row)
            self.full_data = data
            end = time.perf_counter()
            self.update_status(f"Loaded {len(data)} records in {end-start:.4f}s")
        except Exception as e:
            self.update_status(f"Error loading data: {e} Check path: {DATA_FILE_PATH}")
            
    def update_status(self, msg):
        self.after(0, lambda: self.lbl_sub_status.config(text=msg))

    def create_rounded_rect(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1 + radius, y1,
            x1 + radius, y1,
            x2 - radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1 + radius,
            x1, y1
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def create_layout(self):
        # 1. Sidebar
        sidebar = tk.Frame(self, bg=self.bg_sidebar, width=300)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Title
        tk.Label(sidebar, text="STRESS TEST\nBENCHMARK", font=("Helvetica", 24, "bold"), 
                 bg=self.bg_sidebar, fg=self.accent_main, justify="left").pack(pady=(40, 20), padx=30, anchor="w")

        # Configurations Card
        config_frame = self.create_card_container(sidebar, 300) # Width matches sidebar roughly
        
        tk.Label(config_frame, text="Configurations", font=("Segoe UI", 11, "bold"), bg=self.card_bg, fg=self.text_primary).pack(anchor="w", pady=(0, 10))
        
        # Helper for combos
        def add_combo(label, var, values):
            tk.Label(config_frame, text=label, bg=self.card_bg, fg=self.text_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 0))
            cb = ttk.Combobox(config_frame, textvariable=var, values=values, state="readonly", font=("Consolas", 10))
            cb.pack(fill="x", pady=(0, 10))
            return cb

        add_combo("Algorithm", self.algo_var, ["Bubble Sort", "Insertion Sort", "Merge Sort"])
        add_combo("Sort By", self.key_var, ["ID", "FirstName", "LastName"])
        add_combo("Dataset Size (N)", self.n_var, ["1000", "10000", "100000", "All"])
        
        # Run Button
        self.btn_run = self.create_action_button(sidebar, "RUN BENCHMARK", self.start_sort)

        # 2. Main Area
        main_frame = tk.Frame(self, bg=self.bg_main)
        main_frame.pack(side="right", fill="both", expand=True, padx=40, pady=40)
        
        # Header
        self.lbl_main_status = tk.Label(main_frame, text="Ready to Benchmark", font=("Segoe UI", 24), bg=self.bg_main, fg=self.text_primary)
        self.lbl_main_status.pack(anchor="w")
        
        self.lbl_sub_status = tk.Label(main_frame, text="Configure settings in the sidebar and click Run.", font=("Segoe UI", 11), bg=self.bg_main, fg=self.text_secondary)
        self.lbl_sub_status.pack(anchor="w", pady=(5, 15))

        # Results Area (Card Style)
        result_container = tk.Frame(main_frame, bg=self.card_bg, highlightbackground=self.card_border, highlightthickness=1)
        result_container.pack(fill="both", expand=True)

        self.result_area = scrolledtext.ScrolledText(result_container, 
                                                     font=("Consolas", 10), 
                                                     bg=self.card_bg, 
                                                     fg=self.text_primary,
                                                     bd=0, 
                                                     padx=30, pady=30,
                                                     state=tk.DISABLED,
                                                     cursor="arrow")
        self.result_area.pack(fill="both", expand=True)

    def create_card_container(self, parent, width):
        # Create a canvas based 'Card' like in Lab 2 but simpler for layout
        # Actually, simpler approach: A Frame inside a Canvas or just a styled Frame does weird borders.
        # Let's reproduce the Lab 2 'Canvas as background' trick.
        
        container_w = width - 40 # Margin
        container_h = 280 # Height for all configs
        
        canvas = tk.Canvas(parent, width=container_w, height=container_h, bg=self.bg_sidebar, highlightthickness=0)
        canvas.pack(pady=10)
        
        # Rounded Rect Background
        self.create_rounded_rect(canvas, 2, 2, container_w-2, container_h-2, radius=20, 
                                 fill=self.card_bg, outline=self.card_border, width=1)
        
        # Inner Frame
        inner = tk.Frame(canvas, bg=self.card_bg)
        canvas.create_window(container_w/2, container_h/2, window=inner, anchor="center", width=container_w-40, height=container_h-40)
        
        return inner

    def create_action_button(self, parent, text, command):
        btn_w = 240
        btn_h = 55
        
        canvas = tk.Canvas(parent, width=btn_w, height=btn_h, bg=self.bg_sidebar, highlightthickness=0)
        canvas.pack(pady=30)
        
        # Draw Button Shape
        # Default state
        shape = self.create_rounded_rect(canvas, 2, 2, btn_w-2, btn_h-2, radius=20, fill=self.accent_main, outline="")
        
        label = canvas.create_text(btn_w/2, btn_h/2, text=text, fill="white", font=("Segoe UI", 12, "bold"))
        
        def on_click(e):
            if canvas.state != "disabled":
                command()
        
        def on_enter(e):
            if canvas.state != "disabled":
                canvas.itemconfig(shape, fill=self.accent_hover)
                
        def on_leave(e):
            if canvas.state != "disabled":
                canvas.itemconfig(shape, fill=self.accent_main)

        canvas.bind("<Button-1>", on_click)
        canvas.tag_bind(label, "<Button-1>", on_click)
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        
        canvas.state = "normal"
        canvas.shape = shape
        canvas.label = label
        
        return canvas

    def set_button_state(self, btn, state, text=None):
        btn.state = state
        if text:
            btn.itemconfig(btn.label, text=text)
            
        if state == "disabled":
            btn.itemconfig(btn.shape, fill="#D9CFC7") # Greyed out
        else:
            btn.itemconfig(btn.shape, fill=self.accent_main)

    def start_sort(self):
        if not self.full_data:
            messagebox.showerror("Error", "Data not loaded yet!")
            return
            
        n_str = self.n_var.get()
        if n_str == "All":
            n = len(self.full_data)
        else:
            try:
                n = int(n_str)
            except ValueError:
                n = 1000 
            
        algo = self.algo_var.get()
        key = self.key_var.get()
        
        if n > 10000 and algo in ["Bubble Sort", "Insertion Sort"]:
            if not messagebox.askyesno("Performance Warning", f"{algo} with N={n} is extremely slow.\nProceed?"):
                return
        
        self.set_button_state(self.btn_run, "disabled", "RUNNING...")
        self.lbl_main_status.config(text="Benchmarking...")
        self.result_area.config(state=tk.NORMAL)
        self.result_area.delete('1.0', tk.END)
        self.result_area.insert(tk.END, f"Initializing {algo} with N={n}...\n\n")
        self.result_area.config(state=tk.DISABLED)
        
        threading.Thread(target=self.run_sort_thread, args=(n, algo, key)).start()
        
    def run_sort_thread(self, n, algo, key):
        subset = list(self.full_data[:n])
        
        start = time.perf_counter()
        
        sorted_data = []
        try:
            if algo == "Bubble Sort":
                sorted_data = sorting_algorithms.bubble_sort(subset, key)
            elif algo == "Insertion Sort":
                sorted_data = sorting_algorithms.insertion_sort(subset, key)
            elif algo == "Merge Sort":
                sorted_data = sorting_algorithms.merge_sort(subset, key)
        except Exception as e:
            self.after(0, lambda: self.show_error(str(e)))
            return
            
        end = time.perf_counter()
        duration = end - start
        
        self.after(0, lambda: self.show_results(sorted_data, duration, n, algo, key))

    def show_error(self, error_msg):
        self.set_button_state(self.btn_run, "normal", "RUN BENCHMARK")
        self.result_area.config(state=tk.NORMAL)
        self.result_area.insert(tk.END, f"Error: {error_msg}\n")
        self.result_area.config(state=tk.DISABLED)

    def show_results(self, data, duration, n, algo, key):
        self.set_button_state(self.btn_run, "normal", "RUN BENCHMARK")
        self.lbl_main_status.config(text="Benchmark Complete")
        
        # Nice Tabular Format
        header = f"{'ID':<15} | {'FirstName':<20} | {'LastName':<20}"
        div = "-" * len(header)
        
        rows = ""
        for row in data[:15]: # Show top 15
            rows += f"{row['ID']:<15} | {row['FirstName']:<20} | {row['LastName']:<20}\n"
            
        if len(data) > 15:
            rows += f"... and {len(data)-15} more records."

        msg = f"""
Algorithm: {algo}
Sort Key:  {key}
Dataset N: {n}

Time Taken: {duration:.6f} seconds
------------------------------------------------------------

{header}
{div}
{rows}
"""
        self.result_area.config(state=tk.NORMAL)
        self.result_area.delete('1.0', tk.END)
        self.result_area.insert(tk.END, msg)
        self.result_area.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = ExamApp()
    app.mainloop()
'''

target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PRELIM-EXAM", "src", "main.py")
with open(target_path, "w", encoding='utf-8') as f:
    f.write(content)
print("Updated main.py")
