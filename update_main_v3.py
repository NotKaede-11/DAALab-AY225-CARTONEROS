
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

# Required columns for data validation
REQUIRED_COLUMNS = ['ID', 'FirstName', 'LastName']

class ExamApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Sorting Algorithm Stress Test (Prelim Exam)")
        self.geometry("1100x850")
        
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
        self.stop_color = "#E74C3C"   # Red for stop button

        self.configure(bg=self.bg_main)
        
        # Data
        self.full_data = []
        self.data_valid = False
        
        # Threading
        self.cancel_event = threading.Event()
        self.sort_thread = None
        
        # UI State
        self.algo_var = tk.StringVar(value="Bubble Sort")
        self.key_var = tk.StringVar(value="ID")
        self.n_var = tk.StringVar(value="1000")
        
        self.create_layout()
        self.load_data_thread()
        
    def load_data_thread(self):
        t = threading.Thread(target=self.load_data_bg)
        t.start()
        
    def load_data_bg(self):
        """Load and validate data from CSV file."""
        try:
            start = time.perf_counter()
            with open(DATA_FILE_PATH, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Validate CSV schema
                if reader.fieldnames is None:
                    self.update_status("Error: CSV file is empty or has no headers.")
                    return
                    
                missing_cols = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
                if missing_cols:
                    self.update_status(f"Error: Missing required columns: {', '.join(missing_cols)}")
                    return
                
                data = []
                for row in reader:
                    try:
                        row['ID'] = int(row['ID'])
                    except (ValueError, KeyError):
                        pass  # Keep as-is if conversion fails
                    data.append(row)
                    
            self.full_data = data
            self.data_valid = True
            end = time.perf_counter()
            self.update_status(f"✓ Loaded {len(data):,} records in {end-start:.4f}s")
            self.after(0, self.show_data_preview)
            
        except FileNotFoundError:
            self.update_status(f"Error: File not found at {DATA_FILE_PATH}")
        except Exception as e:
            self.update_status(f"Error loading data: {e}")
            
    def update_status(self, msg):
        self.after(0, lambda: self.lbl_sub_status.config(text=msg))
        
    def update_progress(self, value):
        """Thread-safe progress bar update."""
        self.after(0, lambda: self.progress.configure(value=value))

    def create_rounded_rect(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1 + radius, y1, x1 + radius, y1,
            x2 - radius, y1, x2 - radius, y1,
            x2, y1, x2, y1 + radius, x2, y1 + radius,
            x2, y2 - radius, x2, y2 - radius, x2, y2,
            x2 - radius, y2, x2 - radius, y2,
            x1 + radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius, x1, y2 - radius,
            x1, y1 + radius, x1, y1 + radius, x1, y1
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
        config_frame = self.create_card_container(sidebar, 300, 280)
        
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
        
        # Buttons Container
        btn_container = tk.Frame(sidebar, bg=self.bg_sidebar)
        btn_container.pack(pady=20)
        
        # Run Button
        self.btn_run = self.create_action_button(btn_container, "RUN BENCHMARK", self.start_sort, "run")
        
        # Stop Button
        self.btn_stop = self.create_action_button(btn_container, "STOP", self.cancel_sort, "stop")
        self.set_button_state(self.btn_stop, "disabled")

        # 2. Main Area
        main_frame = tk.Frame(self, bg=self.bg_main)
        main_frame.pack(side="right", fill="both", expand=True, padx=40, pady=40)
        
        # Header
        self.lbl_main_status = tk.Label(main_frame, text="Ready to Benchmark", font=("Segoe UI", 24), bg=self.bg_main, fg=self.text_primary)
        self.lbl_main_status.pack(anchor="w")
        
        self.lbl_sub_status = tk.Label(main_frame, text="Loading dataset...", font=("Segoe UI", 11), bg=self.bg_main, fg=self.text_secondary)
        self.lbl_sub_status.pack(anchor="w", pady=(5, 15))

        # Progress Bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Latte.Horizontal.TProgressbar", 
                        foreground=self.accent_main, 
                        background=self.accent_main, 
                        troughcolor=self.bg_sidebar,
                        bordercolor=self.card_border,
                        lightcolor=self.accent_main, 
                        darkcolor=self.accent_main)
        
        self.progress = ttk.Progressbar(main_frame, style="Latte.Horizontal.TProgressbar", 
                                         orient="horizontal", length=100, mode="determinate")
        self.progress.pack(fill="x", pady=(0, 15))

        # Data Preview Card
        preview_label = tk.Label(main_frame, text="Data Preview (First 5 Records)", font=("Segoe UI", 10, "bold"), 
                                  bg=self.bg_main, fg=self.text_secondary)
        preview_label.pack(anchor="w", pady=(0, 5))
        
        preview_container = tk.Frame(main_frame, bg=self.card_bg, highlightbackground=self.card_border, highlightthickness=1)
        preview_container.pack(fill="x", pady=(0, 15))
        
        self.preview_area = tk.Text(preview_container, font=("Consolas", 9), bg=self.card_bg, fg=self.text_secondary,
                                     bd=0, padx=15, pady=10, height=6, state=tk.DISABLED, cursor="arrow")
        self.preview_area.pack(fill="x")

        # Results Area
        result_label = tk.Label(main_frame, text="Benchmark Results", font=("Segoe UI", 10, "bold"), 
                                 bg=self.bg_main, fg=self.text_secondary)
        result_label.pack(anchor="w", pady=(0, 5))
        
        result_container = tk.Frame(main_frame, bg=self.card_bg, highlightbackground=self.card_border, highlightthickness=1)
        result_container.pack(fill="both", expand=True)

        self.result_area = scrolledtext.ScrolledText(result_container, font=("Consolas", 10), bg=self.card_bg, 
                                                      fg=self.text_primary, bd=0, padx=20, pady=20, 
                                                      state=tk.DISABLED, cursor="arrow")
        self.result_area.pack(fill="both", expand=True)

    def create_card_container(self, parent, width, height):
        container_w = width - 40
        container_h = height
        
        canvas = tk.Canvas(parent, width=container_w, height=container_h, bg=self.bg_sidebar, highlightthickness=0)
        canvas.pack(pady=10)
        
        self.create_rounded_rect(canvas, 2, 2, container_w-2, container_h-2, radius=20, 
                                 fill=self.card_bg, outline=self.card_border, width=1)
        
        inner = tk.Frame(canvas, bg=self.card_bg)
        canvas.create_window(container_w/2, container_h/2, window=inner, anchor="center", 
                             width=container_w-40, height=container_h-40)
        
        return inner

    def create_action_button(self, parent, text, command, role="run"):
        btn_w = 240
        btn_h = 50
        
        canvas = tk.Canvas(parent, width=btn_w, height=btn_h, bg=self.bg_sidebar, highlightthickness=0)
        canvas.pack(pady=8)
        
        # Color based on role
        if role == "stop":
            fill_color = self.stop_color
            hover_color = "#C0392B"
        else:
            fill_color = self.accent_main
            hover_color = self.accent_hover
        
        shape = self.create_rounded_rect(canvas, 2, 2, btn_w-2, btn_h-2, radius=20, fill=fill_color, outline="")
        label = canvas.create_text(btn_w/2, btn_h/2, text=text, fill="white", font=("Segoe UI", 11, "bold"))
        
        def on_click(e):
            if canvas.state != "disabled":
                command()
        
        def on_enter(e):
            if canvas.state != "disabled":
                canvas.itemconfig(shape, fill=hover_color)
                
        def on_leave(e):
            if canvas.state != "disabled":
                canvas.itemconfig(shape, fill=fill_color)

        canvas.bind("<Button-1>", on_click)
        canvas.tag_bind(label, "<Button-1>", on_click)
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        
        canvas.state = "normal"
        canvas.shape = shape
        canvas.label = label
        canvas.role = role
        canvas.fill_color = fill_color
        
        return canvas

    def set_button_state(self, btn, state, text=None):
        btn.state = state
        if text:
            btn.itemconfig(btn.label, text=text)
            
        if state == "disabled":
            btn.itemconfig(btn.shape, fill="#D9CFC7")
        else:
            btn.itemconfig(btn.shape, fill=btn.fill_color)

    def show_data_preview(self):
        """Display first 5 records in the preview area."""
        if not self.full_data:
            return
            
        self.preview_area.config(state=tk.NORMAL)
        self.preview_area.delete('1.0', tk.END)
        
        header = f"{'ID':<10} | {'FirstName':<18} | {'LastName':<18}"
        div = "-" * len(header)
        
        lines = [header, div]
        for row in self.full_data[:5]:
            lines.append(f"{str(row.get('ID', 'N/A')):<10} | {row.get('FirstName', 'N/A'):<18} | {row.get('LastName', 'N/A'):<18}")
        
        self.preview_area.insert(tk.END, "\n".join(lines))
        self.preview_area.config(state=tk.DISABLED)

    def start_sort(self):
        if not self.data_valid:
            messagebox.showerror("Error", "Data not loaded or invalid!")
            return
            
        n_str = self.n_var.get()
        if n_str == "All":
            n = len(self.full_data)
        else:
            try:
                n = int(n_str)
                if n <= 0 or n > len(self.full_data):
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Invalid Input", f"Please select a valid dataset size (1 to {len(self.full_data):,}).")
                return
            
        algo = self.algo_var.get()
        key = self.key_var.get()
        
        if n > 10000 and algo in ["Bubble Sort", "Insertion Sort"]:
            if not messagebox.askyesno("Performance Warning", 
                    f"{algo} with N={n:,} is O(n²) and will be extremely slow.\n\n"
                    "Estimated time could be several minutes to hours.\n\nProceed anyway?"):
                return
        
        # Reset state
        self.cancel_event.clear()
        self.progress['value'] = 0
        
        self.set_button_state(self.btn_run, "disabled", "RUNNING...")
        self.set_button_state(self.btn_stop, "normal")
        
        self.lbl_main_status.config(text="Benchmarking...")
        self.result_area.config(state=tk.NORMAL)
        self.result_area.delete('1.0', tk.END)
        self.result_area.insert(tk.END, f"Starting {algo} on N={n:,} sorted by {key}...\n\n")
        self.result_area.config(state=tk.DISABLED)
        
        self.sort_thread = threading.Thread(target=self.run_sort_thread, args=(n, algo, key))
        self.sort_thread.start()
        
    def cancel_sort(self):
        """Signal the sorting thread to stop."""
        self.cancel_event.set()
        self.update_status("Cancelling... Please wait.")
        
    def run_sort_thread(self, n, algo, key):
        subset = list(self.full_data[:n])
        
        start = time.perf_counter()
        
        sorted_data = None
        try:
            if algo == "Bubble Sort":
                sorted_data = sorting_algorithms.bubble_sort(
                    subset, key, 
                    progress_callback=self.update_progress, 
                    cancel_event=self.cancel_event
                )
            elif algo == "Insertion Sort":
                sorted_data = sorting_algorithms.insertion_sort(
                    subset, key, 
                    progress_callback=self.update_progress, 
                    cancel_event=self.cancel_event
                )
            elif algo == "Merge Sort":
                sorted_data = sorting_algorithms.merge_sort(
                    subset, key, 
                    progress_callback=self.update_progress, 
                    cancel_event=self.cancel_event
                )
        except Exception as e:
            self.after(0, lambda: self.show_error(str(e)))
            return
        
        end = time.perf_counter()
        duration = end - start
        
        if sorted_data is None:
            # Cancelled
            self.after(0, self.on_sort_cancelled)
        else:
            self.after(0, lambda: self.show_results(sorted_data, duration, n, algo, key))

    def on_sort_cancelled(self):
        self.set_button_state(self.btn_run, "normal", "RUN BENCHMARK")
        self.set_button_state(self.btn_stop, "disabled")
        self.lbl_main_status.config(text="Cancelled")
        self.update_status("Sort operation was cancelled.")
        self.progress['value'] = 0
        
        self.result_area.config(state=tk.NORMAL)
        self.result_area.insert(tk.END, "\n⚠ Operation cancelled by user.\n")
        self.result_area.config(state=tk.DISABLED)

    def show_error(self, error_msg):
        self.set_button_state(self.btn_run, "normal", "RUN BENCHMARK")
        self.set_button_state(self.btn_stop, "disabled")
        self.lbl_main_status.config(text="Error")
        
        self.result_area.config(state=tk.NORMAL)
        self.result_area.insert(tk.END, f"Error: {error_msg}\n")
        self.result_area.config(state=tk.DISABLED)

    def show_results(self, data, duration, n, algo, key):
        self.set_button_state(self.btn_run, "normal", "RUN BENCHMARK")
        self.set_button_state(self.btn_stop, "disabled")
        self.lbl_main_status.config(text="Benchmark Complete")
        self.progress['value'] = 100
        
        # Nice Tabular Format
        header = f"{'ID':<15} | {'FirstName':<20} | {'LastName':<20}"
        div = "-" * len(header)
        
        rows = ""
        for row in data[:15]:
            rows += f"{str(row.get('ID', '')):<15} | {row.get('FirstName', ''):<20} | {row.get('LastName', ''):<20}\n"
            
        if len(data) > 15:
            rows += f"\n... and {len(data)-15:,} more records."

        msg = f"""
╔══════════════════════════════════════════════════════════╗
║                    BENCHMARK RESULTS                     ║
╠══════════════════════════════════════════════════════════╣
║  Algorithm:   {algo:<42} ║
║  Sort Key:    {key:<42} ║
║  Dataset N:   {n:<42,} ║
║  Time Taken:  {duration:.6f} seconds{' '*(34-len(f'{duration:.6f}'))} ║
╚══════════════════════════════════════════════════════════╝

Top 15 Sorted Records:
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
