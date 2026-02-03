import tkinter as tk
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
        
        # Color Palette - Theme 1
        self.bg_main = "#EAEFEF"      # Main Canvas
        self.bg_sidebar = "#BFC9D1"   # Sidebar
        self.text_primary = "#25343F" # Dark Navy
        self.text_secondary = "#4A5F70" # Muted Navy
        self.accent_main = "#FF9B51"  # Orange Accent
        self.accent_hover = "#E68A41" # Darker Orange
        self.btn_hover = "#AAB4BC"    # Warm Gray Blue
        self.card_border = "#AAB4BC"  # Warm Gray Blue
        self.card_bg = "#FFFFFF"      # Crisp White
        self.stop_color = "#E74C3C"   # Red for stop button
        self.placeholder_text = "#95A5A6" # Muted placeholder text

        # Algorithm complexity mapping
        self.complexity_map = {
            "Bubble Sort": "O(n²)",
            "Insertion Sort": "O(n²)",
            "Merge Sort": "O(n log n)"
        }

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
            self.after(0, self.update_n_max_label)
            
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
        # 1. Sidebar (narrower with subtle border)
        sidebar_container = tk.Frame(self, bg=self.card_border)
        sidebar_container.pack(side="left", fill="y")
        
        sidebar = tk.Frame(sidebar_container, bg=self.bg_sidebar, width=250)
        sidebar.pack(side="left", fill="y", padx=(0, 1))  # 1px right border
        sidebar.pack_propagate(False)

        # Title
        tk.Label(sidebar, text="STRESS TEST\nBENCHMARK", font=("Helvetica", 18, "bold"), 
                 bg=self.bg_sidebar, fg=self.text_primary, justify="left").pack(pady=(30, 15), padx=20, anchor="w")

        # Configurations Card
        config_frame = self.create_card_container(sidebar, 250, 300)
        
        tk.Label(config_frame, text="Configurations", font=("Segoe UI", 11, "bold"), bg=self.card_bg, fg=self.text_primary).pack(anchor="w", pady=(0, 10))
        
        # Helper for combos
        def add_combo(label, var, values):
            tk.Label(config_frame, text=label, bg=self.card_bg, fg=self.text_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 0))
            cb = ttk.Combobox(config_frame, textvariable=var, values=values, state="readonly", font=("Consolas", 10))
            cb.pack(fill="x", pady=(0, 5))
            return cb

        add_combo("Algorithm", self.algo_var, ["Bubble Sort", "Insertion Sort", "Merge Sort"])
        add_combo("Sort By", self.key_var, ["ID", "FirstName", "LastName"])
        
        # Custom Dataset Size Input with validation
        tk.Label(config_frame, text="Dataset Size (N)", bg=self.card_bg, fg=self.text_secondary, font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 0))
        
        # Entry field for custom input
        n_entry_frame = tk.Frame(config_frame, bg=self.card_bg)
        n_entry_frame.pack(fill="x", pady=(0, 2))
        
        self.n_entry = tk.Entry(n_entry_frame, textvariable=self.n_var, font=("Consolas", 10),
                                 bg=self.card_bg, fg=self.text_primary, insertbackground=self.text_primary,
                                 relief="solid", bd=1, highlightthickness=1,
                                 highlightbackground=self.card_border, highlightcolor=self.accent_main)
        self.n_entry.pack(fill="x")
        
        # Validation feedback label (shows max or error)
        self.n_validation_label = tk.Label(config_frame, text="Max: Loading...", bg=self.card_bg, 
                                            fg=self.text_secondary, font=("Segoe UI", 8))
        self.n_validation_label.pack(anchor="w")
        
        # Quick preset buttons (centered)
        preset_frame = tk.Frame(config_frame, bg=self.card_bg)
        preset_frame.pack(pady=(3, 0))
        
        def set_n_preset(value):
            self.n_var.set(value)
        
        presets = [("1K", "1000"), ("10K", "10000"), ("100K", "100000"), ("All", "All")]
        for label, value in presets:
            btn = tk.Button(preset_frame, text=label, font=("Segoe UI", 8), 
                           bg=self.bg_sidebar, fg=self.text_primary, bd=0, padx=8, pady=2,
                           activebackground=self.btn_hover, cursor="hand2",
                           command=lambda v=value: set_n_preset(v))
            btn.pack(side="left", padx=2)
        
        # Set up real-time validation trace
        self.n_var.trace_add("write", self.validate_n_input)
        
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

        # Progress Bar Style (bar will be placed in results area)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Latte.Horizontal.TProgressbar", 
                        foreground=self.accent_main, 
                        background=self.accent_main, 
                        troughcolor=self.bg_sidebar,
                        bordercolor=self.card_border,
                        lightcolor=self.accent_main, 
                        darkcolor=self.accent_main)

        # Data Preview Card
        preview_label = tk.Label(main_frame, text="Data Preview (First 5 Records)", font=("Segoe UI", 10, "bold"), 
                                  bg=self.bg_main, fg=self.text_secondary)
        preview_label.pack(anchor="w", pady=(0, 5))
        
        preview_container = tk.Frame(main_frame, bg=self.card_bg, highlightbackground=self.card_border, highlightthickness=1)
        preview_container.pack(fill="x", pady=(0, 15))
        
        self.preview_area = tk.Text(preview_container, font=("Consolas", 9), bg=self.card_bg, fg=self.text_secondary,
                                     bd=0, padx=15, pady=10, height=6, state=tk.DISABLED, cursor="arrow")
        self.preview_area.pack(fill="x")

        # Metric Status Cards
        metrics_frame = tk.Frame(main_frame, bg=self.bg_main)
        metrics_frame.pack(fill="x", pady=(0, 15))
        
        # Create 3 metric cards
        self.metric_time = self.create_metric_card(metrics_frame, "Sorting Time", "--", "s")
        self.metric_complexity = self.create_metric_card(metrics_frame, "Complexity", "--", "")
        self.metric_records = self.create_metric_card(metrics_frame, "Records Sorted", "--", "")
        
        # Results Area Label
        result_label = tk.Label(main_frame, text="Top 10 Sorted Records", font=("Segoe UI", 10, "bold"), 
                                 bg=self.bg_main, fg=self.text_secondary)
        result_label.pack(anchor="w", pady=(0, 5))
        
        # Treeview for results table (with integrated progress bar)
        result_container = tk.Frame(main_frame, bg=self.card_bg, highlightbackground=self.card_border, highlightthickness=1)
        result_container.pack(fill="both", expand=True)
        
        # Progress bar integrated into results area (Visual Thinking)
        progress_frame = tk.Frame(result_container, bg=self.card_bg)
        progress_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        self.progress = ttk.Progressbar(progress_frame, style="Latte.Horizontal.TProgressbar", 
                                         orient="horizontal", length=100, mode="determinate")
        self.progress.pack(fill="x")
        
        # Empty state placeholder (shown before user clicks Run)
        self.empty_state_frame = tk.Frame(result_container, bg=self.card_bg)
        self.empty_state_frame.pack(fill="both", expand=True)
        
        # Placeholder icon and text
        tk.Label(self.empty_state_frame, text="📊", font=("Segoe UI", 48), 
                 bg=self.card_bg, fg=self.placeholder_text).pack(pady=(40, 10))
        tk.Label(self.empty_state_frame, text="Configure settings and click RUN to begin benchmarking.", 
                 font=("Segoe UI", 11), bg=self.card_bg, fg=self.placeholder_text).pack()
        tk.Label(self.empty_state_frame, text="Results will appear here.", 
                 font=("Segoe UI", 9), bg=self.card_bg, fg=self.placeholder_text).pack(pady=(5, 0))
        
        # Treeview frame (hidden initially, shown when results are ready)
        self.treeview_frame = tk.Frame(result_container, bg=self.card_bg)
        
        # Configure Treeview style
        tree_style = ttk.Style()
        tree_style.configure("Results.Treeview", 
                             background=self.card_bg,
                             foreground=self.text_primary,
                             fieldbackground=self.card_bg,
                             font=("Consolas", 10),
                             rowheight=28)
        tree_style.configure("Results.Treeview.Heading",
                             background=self.bg_sidebar,
                             foreground=self.text_primary,
                             font=("Segoe UI", 10, "bold"))
        tree_style.map("Results.Treeview", background=[("selected", self.accent_main)])
        
        # Create Treeview with columns (inside treeview_frame)
        columns = ("ID", "FirstName", "LastName")
        self.result_tree = ttk.Treeview(self.treeview_frame, columns=columns, show="headings", 
                                         style="Results.Treeview", height=10)
        
        # Define column headings and widths
        self.result_tree.heading("ID", text="ID", anchor="w")
        self.result_tree.heading("FirstName", text="First Name", anchor="w")
        self.result_tree.heading("LastName", text="Last Name", anchor="w")
        
        self.result_tree.column("ID", width=120, minwidth=80, anchor="w")
        self.result_tree.column("FirstName", width=200, minwidth=120, anchor="w")
        self.result_tree.column("LastName", width=200, minwidth=120, anchor="w")
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(self.treeview_frame, orient="vertical", command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.result_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        tree_scroll.pack(side="right", fill="y", pady=10)
        
        # Status label below table
        self.result_status = tk.Label(main_frame, text="", font=("Segoe UI", 9), 
                                       bg=self.bg_main, fg=self.text_secondary)
        self.result_status.pack(anchor="w", pady=(5, 0))

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

    def create_metric_card(self, parent, title, value, unit):
        """Create a metric status card with large bold value."""
        card_w = 180
        card_h = 90
        
        canvas = tk.Canvas(parent, width=card_w, height=card_h, bg=self.bg_main, highlightthickness=0)
        canvas.pack(side="left", padx=(0, 15))
        
        # Draw rounded rectangle background
        self.create_rounded_rect(canvas, 2, 2, card_w-2, card_h-2, radius=15, 
                                 fill=self.card_bg, outline=self.card_border, width=1)
        
        # Title label (small, muted)
        title_label = canvas.create_text(card_w/2, 22, text=title, 
                                          fill=self.text_secondary, font=("Segoe UI", 9))
        
        # Value label (large, bold) - stored for updates
        value_text = f"{value}{unit}" if unit else value
        value_label = canvas.create_text(card_w/2, 55, text=value_text, 
                                          fill=self.text_primary, font=("Helvetica", 24, "bold"))
        
        # Store references for updating
        canvas.value_label = value_label
        canvas.unit = unit
        
        return canvas

    def update_metric_card(self, card, value):
        """Update the value displayed on a metric card."""
        display_text = f"{value}{card.unit}" if card.unit else str(value)
        card.itemconfig(card.value_label, text=display_text)

    def create_action_button(self, parent, text, command, role="run"):
        btn_w = 180
        btn_h = 45
        
        canvas = tk.Canvas(parent, width=btn_w, height=btn_h, bg=self.bg_sidebar, highlightthickness=0)
        canvas.pack(pady=8)
        
        # Color based on role
        if role == "stop":
            # Solid red fill for Stop button with white text
            fill_color = self.stop_color
            text_color = "#FFFFFF"
            hover_color = "#C0392B" # Darker Red
        else:
            # Using White Card style for Run button
            fill_color = self.card_bg
            text_color = self.accent_main
            hover_color = self.btn_hover # Light Gray/Blue
        
        shape = self.create_rounded_rect(canvas, 2, 2, btn_w-2, btn_h-2, radius=20, fill=fill_color, outline="")
        label = canvas.create_text(btn_w/2, btn_h/2, text=text, fill=text_color, font=("Segoe UI", 11, "bold"))
        
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
            btn.itemconfig(btn.shape, fill=self.btn_hover) # Use theme hover color (greyish)
        else:
            btn.itemconfig(btn.shape, fill=btn.fill_color)

    def update_n_max_label(self):
        """Update the max label to show the loaded data count."""
        if self.data_valid and self.full_data:
            self.n_validation_label.config(text=f"Max: {len(self.full_data):,}", fg=self.text_secondary)
        # Trigger validation for current value
        self.validate_n_input()
    
    def validate_n_input(self, *args):
        """Real-time validation of the N input field."""
        value = self.n_var.get().strip()
        
        # Empty input
        if not value:
            self.n_entry.config(highlightbackground=self.card_border, highlightcolor=self.accent_main)
            if self.data_valid:
                self.n_validation_label.config(text=f"Max: {len(self.full_data):,}", fg=self.text_secondary)
            return
        
        # "All" is always valid
        if value.lower() == "all":
            self.n_entry.config(highlightbackground="#27AE60", highlightcolor="#27AE60")
            if self.data_valid:
                self.n_validation_label.config(text=f"✓ Will use all {len(self.full_data):,} records", fg="#27AE60")
            return
        
        # Try to parse as integer
        try:
            n = int(value)
            if n <= 0:
                # Invalid: zero or negative
                self.n_entry.config(highlightbackground=self.stop_color, highlightcolor=self.stop_color)
                self.n_validation_label.config(text="✗ Must be greater than 0", fg=self.stop_color)
            elif self.data_valid and n > len(self.full_data):
                # Invalid: exceeds max
                self.n_entry.config(highlightbackground=self.stop_color, highlightcolor=self.stop_color)
                self.n_validation_label.config(text=f"✗ Exceeds max ({len(self.full_data):,})", fg=self.stop_color)
            else:
                # Valid
                self.n_entry.config(highlightbackground="#27AE60", highlightcolor="#27AE60")
                if self.data_valid:
                    self.n_validation_label.config(text=f"✓ Valid ({n:,} records)", fg="#27AE60")
                else:
                    self.n_validation_label.config(text=f"Max: Loading...", fg=self.text_secondary)
        except ValueError:
            # Not a valid number (and not "All")
            self.n_entry.config(highlightbackground=self.stop_color, highlightcolor=self.stop_color)
            self.n_validation_label.config(text="✗ Enter a number or 'All'", fg=self.stop_color)
    
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

    def estimate_sort_time(self, n, algo):
        """Estimate sorting time based on algorithm complexity and dataset size.
        
        These estimates are calibrated for typical Python performance on modern hardware.
        Bubble Sort: ~5,337,000 comparisons/swaps per second (slowest, most swaps)
        Insertion Sort: ~7,726,000 comparisons/shifts per second (fewer operations on average)
        Merge Sort: ~1,500,000 operations per second (O(n log n), very efficient)
        """
        import math
        
        if algo == "Bubble Sort":
            # O(n²) - worst case, every pair compared and many swaps
            ops = n * n
            ops_per_sec = 5337000
        elif algo == "Insertion Sort":
            # O(n²) but typically faster than bubble (fewer operations on average)
            ops = (n * n) / 2  # Average case is n²/2
            ops_per_sec = 7726000
        else:
            # O(n log n) algorithms - Merge Sort
            ops = n * math.log2(n) if n > 0 else 0
            ops_per_sec = 1500000
        
        seconds = ops / ops_per_sec
        
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.1f} minutes"
        else:
            return f"{seconds/3600:.1f} hours"

    def show_heat_warning(self, algo, n):
        """Show enhanced heat warning dialog for O(n²) algorithms on large datasets."""
        estimated_time = self.estimate_sort_time(n, algo)
        complexity = self.complexity_map.get(algo, "O(n²)")
        
        result = {"proceed": False, "closed": False}
        
        warning = tk.Toplevel(self)
        warning.title("⚠ Performance Warning")
        warning.geometry("420x320")
        warning.configure(bg=self.card_bg)
        warning.resizable(False, False)
        warning.transient(self)
        warning.grab_set()  # Make modal
        
        # Prevent double-close with a flag
        def close_dialog():
            if not result["closed"]:
                result["closed"] = True
                warning.grab_release()
                warning.destroy()
        
        warning.protocol("WM_DELETE_WINDOW", close_dialog)
        
        # Center the dialog
        warning.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 420) // 2
        y = self.winfo_y() + (self.winfo_height() - 320) // 2
        warning.geometry(f"+{x}+{y}")
        
        # Warning header with fire icon
        header_frame = tk.Frame(warning, bg="#FDEDEC", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🔥 HEAT WARNING", font=("Segoe UI", 14, "bold"),
                 bg="#FDEDEC", fg="#C0392B").pack(pady=15)
        
        # Content
        content = tk.Frame(warning, bg=self.card_bg, padx=25, pady=15)
        content.pack(fill="both", expand=True)
        
        tk.Label(content, text=f"You're about to run {algo}", font=("Segoe UI", 11),
                 bg=self.card_bg, fg=self.text_primary).pack(anchor="w")
        tk.Label(content, text=f"on {n:,} records.", font=("Segoe UI", 11),
                 bg=self.card_bg, fg=self.text_primary).pack(anchor="w", pady=(0, 10))
        
        # Stats frame with complexity and estimated time
        stats_frame = tk.Frame(content, bg="#F8F9F9", padx=15, pady=10)
        stats_frame.pack(fill="x", pady=5)
        
        tk.Label(stats_frame, text=f"Complexity: {complexity}", font=("Consolas", 10, "bold"),
                 bg="#F8F9F9", fg="#E74C3C").pack(anchor="w")
        tk.Label(stats_frame, text=f"Estimated Time: {estimated_time}", font=("Consolas", 10, "bold"),
                 bg="#F8F9F9", fg="#E67E22").pack(anchor="w")
        
        tk.Label(content, text="This may freeze the UI and consume significant resources.",
                 font=("Segoe UI", 9), bg=self.card_bg, fg=self.text_secondary,
                 wraplength=370).pack(pady=(10, 5), anchor="w")
        
        btn_frame = tk.Frame(content, bg=self.card_bg)
        btn_frame.pack(fill="x", pady=(15, 10))
        
        def on_proceed():
            result["proceed"] = True
            close_dialog()
        
        def on_cancel():
            close_dialog()
        
        tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 10),
                  bg="#ECF0F1", fg=self.text_primary, width=12, bd=0,
                  activebackground="#D5DBDB", cursor="hand2", command=on_cancel).pack(side="left", padx=(0, 10))
        
        tk.Button(btn_frame, text="Proceed Anyway", font=("Segoe UI", 10, "bold"),
                  bg="#E74C3C", fg="white", width=15, bd=0,
                  activebackground="#C0392B", cursor="hand2", command=on_proceed).pack(side="left")
        
        # Wait for dialog to close
        self.wait_window(warning)
        return result["proceed"]

    def start_sort(self):
        if not self.data_valid:
            messagebox.showerror("Error", "Data not loaded or invalid!")
            return
            
        n_str = self.n_var.get().strip()
        if n_str.lower() == "all":
            n = len(self.full_data)
        else:
            try:
                n = int(n_str)
                if n <= 0:
                    messagebox.showerror("Invalid Input", "Dataset size must be greater than 0.")
                    return
                if n > len(self.full_data):
                    messagebox.showerror("Invalid Input", f"Dataset size exceeds available records.\n\nYou entered: {n:,}\nMax available: {len(self.full_data):,}")
                    return
            except ValueError:
                messagebox.showerror("Invalid Input", f"Please enter a valid number (1 to {len(self.full_data):,}) or 'All'.")
                return
            
        algo = self.algo_var.get()
        key = self.key_var.get()
        
        # Show enhanced heat warning for O(n²) algorithms on large datasets
        if n > 10000 and algo in ["Bubble Sort", "Insertion Sort"]:
            if not self.show_heat_warning(algo, n):
                return
        
        # Reset state
        self.cancel_event.clear()
        self.progress['value'] = 0
        
        # Loading State: Change RUN button to SORTING... and disable
        self.set_button_state(self.btn_run, "disabled", "SORTING...")
        self.set_button_state(self.btn_stop, "normal")
        
        self.lbl_main_status.config(text="Benchmarking...")
        
        # Hide empty state placeholder, show treeview frame
        self.empty_state_frame.pack_forget()
        self.treeview_frame.pack(fill="both", expand=True)
        
        # Clear Treeview and reset metrics
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        self.update_metric_card(self.metric_time, "...")
        self.update_metric_card(self.metric_complexity, self.complexity_map.get(algo, "--"))
        self.update_metric_card(self.metric_records, f"{n:,}")
        self.result_status.config(text=f"Running {algo} on {n:,} records sorted by {key}...")
        
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
        
        # Reset metric cards
        self.update_metric_card(self.metric_time, "--")
        self.update_metric_card(self.metric_complexity, "--")
        self.update_metric_card(self.metric_records, "--")
        
        # Show empty state placeholder again
        self.treeview_frame.pack_forget()
        self.empty_state_frame.pack(fill="both", expand=True)
        
        # Update status
        self.result_status.config(text="⚠ Operation cancelled by user.")

    def show_error(self, error_msg):
        self.set_button_state(self.btn_run, "normal", "RUN BENCHMARK")
        self.set_button_state(self.btn_stop, "disabled")
        self.lbl_main_status.config(text="Error")
        
        # Reset metric cards
        self.update_metric_card(self.metric_time, "--")
        self.update_metric_card(self.metric_complexity, "--")
        self.update_metric_card(self.metric_records, "--")
        
        # Show empty state placeholder again
        self.treeview_frame.pack_forget()
        self.empty_state_frame.pack(fill="both", expand=True)
        
        # Show error in status
        self.result_status.config(text=f"❌ Error: {error_msg}")

    def show_results(self, data, duration, n, algo, key):
        self.set_button_state(self.btn_run, "normal", "RUN BENCHMARK")
        self.set_button_state(self.btn_stop, "disabled")
        self.lbl_main_status.config(text="Benchmark Complete")
        self.progress['value'] = 100
        
        # Update metric cards
        self.update_metric_card(self.metric_time, f"{duration:.4f}")
        self.update_metric_card(self.metric_complexity, self.complexity_map.get(algo, "--"))
        self.update_metric_card(self.metric_records, f"{n:,}")
        
        # Clear existing Treeview data
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # Insert top 10 records with zebra striping
        for i, row in enumerate(data[:10]):
            tag = "even" if i % 2 == 0 else "odd"
            self.result_tree.insert("", "end", values=(
                row.get('ID', 'N/A'),
                row.get('FirstName', 'N/A'),
                row.get('LastName', 'N/A')
            ), tags=(tag,))
        
        # Configure zebra stripe colors
        self.result_tree.tag_configure("even", background=self.card_bg)
        self.result_tree.tag_configure("odd", background="#F5F7F7")
        
        # Update status label
        extra_msg = ""
        if len(data) > 10:
            extra_msg = f"Showing top 10 of {len(data):,} sorted records • "
        self.result_status.config(text=f"{extra_msg}Algorithm: {algo} • Sort Key: {key}")

if __name__ == "__main__":
    app = ExamApp()
    app.mainloop()
