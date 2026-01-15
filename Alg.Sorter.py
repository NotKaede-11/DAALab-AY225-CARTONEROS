import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import time
import os
import threading
import math
import glob
from collections import Counter

# --- BACKEND LOGIC ---

def read_dataset(filename):
    """Reads integers from a file. Auto-detects and splits concatenated numbers."""
    raw_values = []
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    # Handle comma/space-separated values first
                    if ',' in stripped or ' ' in stripped:
                        parts = stripped.replace(',', ' ').split()
                        for part in parts:
                            part = part.strip()
                            if part:
                                raw_values.append(part)
                    else:
                        raw_values.append(stripped)
    except FileNotFoundError:
        return None
    except Exception:
        return []
    
    if not raw_values:
        return []
    
    # First pass: collect digit lengths to find the typical (mode) length
    digit_lengths = Counter(len(v) for v in raw_values)
    typical_length = digit_lengths.most_common(1)[0][0]
    
    # Threshold: values longer than 1.5x typical are likely concatenated
    concat_threshold = int(typical_length * 1.5)
    
    # Second pass: parse values, splitting concatenated ones
    data = []
    for val in raw_values:
        try:
            if len(val) > concat_threshold and typical_length > 0:
                # Split into chunks of typical_length
                for i in range(0, len(val), typical_length):
                    chunk = val[i:i + typical_length]
                    if chunk:
                        data.append(int(chunk))
            else:
                data.append(int(val))
        except ValueError:
            continue  # Skip malformed values
    
    return data

def bubble_sort(arr, progress_callback=None, cancel_event=None, descending=True):
    n = len(arr)
    # Shallow copy to avoid sorting the original reference in place if reused
    arr = arr[:] 
    
    # Pre-fetch check for slightly faster access
    is_cancelled = cancel_event.is_set if cancel_event else (lambda: False)
    
    # Total expected comparisons for progress tracking (Sum of n-1 ... 1)
    total_comparisons = n * (n - 1) // 2
    comparisons_done = 0

    for i in range(n):
        if is_cancelled(): return None

        swapped = False
        # Inner loop does n-i-1 comparisons
        comparisons_in_pass = n - i - 1
        
        for j in range(0, comparisons_in_pass):
            # Comparison Logic
            should_swap = False
            if descending:
                if arr[j] < arr[j + 1]: should_swap = True
            else:
                if arr[j] > arr[j + 1]: should_swap = True
                
            if should_swap:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
            
            # Stride check inner loop
            if j % 1000 == 0 and is_cancelled():
                return None
        
        # Update progress (based on work done vs total estimated work)
        comparisons_done += comparisons_in_pass
        if progress_callback: 
            p = (comparisons_done / total_comparisons) * 100
            progress_callback(min(p, 99.9))
            
        if not swapped:
            break
            
    if progress_callback: progress_callback(100)
    return arr

def insertion_sort(arr, progress_callback=None, cancel_event=None, descending=True):
    arr = arr[:] # Copy
    n = len(arr)
    is_cancelled = cancel_event.is_set if cancel_event else (lambda: False)

    for i in range(1, n):
        if is_cancelled(): return None

        key = arr[i]
        j = i - 1
        
        # Comparison logic inside while
        while j >= 0:
            should_move = False
            if descending:
                if key > arr[j]: should_move = True
            else:
                if key < arr[j]: should_move = True
            
            if should_move:
                arr[j + 1] = arr[j]
                j -= 1
            else:
                break

        arr[j + 1] = key
        
        if progress_callback and i % 10 == 0:
            # Map progress to i^2 for quadratic time complexity
            # This makes progress bar linear with TIME rather than iteration count
            p = (i / n) ** 2 * 100
            progress_callback(p)
            
    if progress_callback: progress_callback(100)
    return arr

# Helper for merge sort to track progress
def merge_sort_wrapper(arr, progress_callback=None, cancel_event=None, descending=True):
    if not progress_callback and not cancel_event:
        # Fallback to simple recursive if no callback needed
        return merge_sort_recursive_simple(arr, descending)
    
    total_elements = len(arr)
    state = [0] # Shared progress counter
    is_cancelled = cancel_event.is_set if cancel_event else (lambda: False)
    
    # Total merge operations is approx N * log2(N)
    total_work = total_elements * math.log2(total_elements) if total_elements > 1 else 1

    def merge_sort_recursive(arr):
        if is_cancelled(): return None

        if len(arr) > 1:
            mid = len(arr) // 2
            left_half = arr[:mid]
            right_half = arr[mid:]

            l_res = merge_sort_recursive(left_half)
            if l_res is None: return None # Propagate cancel
            r_res = merge_sort_recursive(right_half)
            if r_res is None: return None # Propagate cancel

            i = j = k = 0

            while i < len(left_half) and j < len(right_half):
                if k % 1000 == 0 and is_cancelled(): return None

                # Selection Logic
                pick_left = False
                if descending:
                    if left_half[i] > right_half[j]: pick_left = True
                else:
                    if left_half[i] < right_half[j]: pick_left = True

                if pick_left:
                    arr[k] = left_half[i]
                    i += 1
                else:
                    arr[k] = right_half[j]
                    j += 1
                k += 1

            while i < len(left_half):
                arr[k] = left_half[i]
                i += 1
                k += 1

            while j < len(right_half):
                arr[k] = right_half[j]
                j += 1
                k += 1
            
            # Heuristic progress update
            state[0] += len(arr)
            
            p = (state[0] / total_work) * 100
            if p > 99.9: p = 99.9
            progress_callback(p)
                
        return arr

    res = merge_sort_recursive(arr[:])
    if res is None: return None
    if progress_callback: progress_callback(100)
    return res

def merge_sort_recursive_simple(arr, descending=True):
    if len(arr) > 1:
        mid = len(arr) // 2
        left_half = arr[:mid]
        right_half = arr[mid:]
        merge_sort_recursive_simple(left_half, descending)
        merge_sort_recursive_simple(right_half, descending)
        i=j=k=0
        while i < len(left_half) and j < len(right_half):
            pick_left = False
            if descending:
                if left_half[i] > right_half[j]: pick_left = True
            else:
                if left_half[i] < right_half[j]: pick_left = True
            
            if pick_left:
                arr[k] = left_half[i]
                i += 1
            else:
                arr[k] = right_half[j]
                j += 1
            k += 1
        while i < len(left_half):
            arr[k] = left_half[i]
            i += 1; k += 1
        while j < len(right_half):
            arr[k] = right_half[j]
            j += 1; k += 1
    return arr

# --- MODERN MINIMALIST GUI ---

class SorterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Data Sorting Algorithm")
        self.geometry("1000x750")
        
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

        # Data & File Setup
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.dataset_files = self.scan_datasets()
        self.current_dataset_name = self.dataset_files[0] if self.dataset_files else None
        
        # Load initial data
        if self.current_dataset_name:
            self.dataset_path = os.path.join(self.base_dir, self.current_dataset_name)
            self.data_cache = read_dataset(self.dataset_path) or []
        else:
            self.dataset_path = None
            self.data_cache = []
            
        self.data_count = len(self.data_cache)
        
        # Threading Event for Cancellation
        self.cancel_event = threading.Event()
        self.sort_descending = True # Default Sort Order

        self.create_layout()

    def scan_datasets(self):
        """Finds all .txt files in the script directory."""
        # Using os.listdir instead of glob because the path contains brackets []
        # which glob interprets as wildcard patterns.
        try:
            files = [f for f in os.listdir(self.base_dir) if f.lower().endswith('.txt')]
            return files
        except Exception as e:
            print(f"Error scanning datasets: {e}")
            return []

    def create_layout(self):
        # 1. Sidebar
        sidebar = tk.Frame(self, bg=self.bg_sidebar, width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Title
        tk.Label(sidebar, text="ALGORITHM\nSORTER", font=("Helvetica", 24, "bold"), 
                 bg=self.bg_sidebar, fg=self.accent_main, justify="left").pack(pady=(40, 20), padx=30, anchor="w")

        # Dataset Info Box / Selector
        # -- Converted to Rounded Canvas --
        dataset_w = 200
        dataset_h = 130 # Increased height to fit contents comfortably
        info_canvas = tk.Canvas(sidebar, width=dataset_w, height=dataset_h, bg=self.bg_sidebar, highlightthickness=0)
        info_canvas.pack(pady=10)
        
        # Draw background card
        self.create_rounded_rect(info_canvas, 2, 2, dataset_w-2, dataset_h-2, radius=20, 
                                 fill=self.card_bg, outline=self.card_border, width=1)
        
        # Inner Frame for Widgets (Transparent-ish hack: match bg to card_bg)
        # We place a Frame inside the Canvas using create_window
        inner_frame = tk.Frame(info_canvas, bg=self.card_bg)
        # Center the frame in the canvas
        info_canvas.create_window(dataset_w/2, dataset_h/2, window=inner_frame, anchor="center", width=dataset_w-30)
        
        tk.Label(inner_frame, text="Select Dataset:", font=("Segoe UI", 9, "bold"), bg=self.card_bg, fg=self.text_secondary).pack(anchor="w", pady=(0, 5))
        
        # Combobox for file selection
        self.combo_dataset = ttk.Combobox(inner_frame, values=self.dataset_files, state="readonly", font=("Consolas", 10))
        if self.current_dataset_name:
            self.combo_dataset.set(self.current_dataset_name)
        self.combo_dataset.pack(fill="x", pady=(0, 8))
        self.combo_dataset.bind("<<ComboboxSelected>>", self.on_dataset_change)
        
        # Sort Order Toggle (Segmented styled buttons)
        order_frame = tk.Frame(inner_frame, bg=self.card_bg)
        order_frame.pack(fill="x", pady=(0, 8))
        
        # Using a Canvas for custom toggle switch
        # We will create two clickable text/rect regions
        toggle_h = 28
        toggle_w = dataset_w - 30 # fill with margin
        self.toggle_canvas = tk.Canvas(order_frame, width=toggle_w, height=toggle_h, bg=self.card_bg, highlightthickness=0)
        self.toggle_canvas.pack()
        
        # Draw background container
        self.create_rounded_rect(self.toggle_canvas, 0, 0, toggle_w, toggle_h, radius=14, fill=self.bg_sidebar, outline=self.card_border)
        
        # Slider/Active Indicator (will move)
        self.toggle_slider = self.create_rounded_rect(self.toggle_canvas, 0, 0, toggle_w/2, toggle_h, radius=14, fill=self.accent_main, outline="")
        
        # Text Labels
        self.txt_desc = self.toggle_canvas.create_text(toggle_w*0.25, toggle_h/2, text="Desc", fill="#FFFFFF", font=("Segoe UI", 9, "bold"))
        self.txt_asc = self.toggle_canvas.create_text(toggle_w*0.75, toggle_h/2, text="Asc", fill=self.text_secondary, font=("Segoe UI", 9, "bold"))
        
        # Bind clicks
        self.toggle_canvas.bind("<Button-1>", self.on_toggle_order)
        # Ensure text labels also capture clicks
        self.toggle_canvas.tag_bind(self.txt_desc, "<Button-1>", self.on_toggle_order)
        self.toggle_canvas.tag_bind(self.txt_asc, "<Button-1>", self.on_toggle_order)
        
        # Update slider position based on default
        self.update_toggle_ui()
        
        self.lbl_item_count = tk.Label(inner_frame, text=f"{self.data_count:,} items", font=("Segoe UI", 12), bg=self.card_bg, fg=self.accent_main)
        self.lbl_item_count.pack(anchor="w")

        # Menu
        menu_container = tk.Frame(sidebar, bg=self.bg_sidebar)
        menu_container.pack(fill="x", pady=30)
        
        tk.Label(menu_container, text="MENU", font=("Segoe UI", 9, "bold"), bg=self.bg_sidebar, fg="#B0B0B0").pack(padx=30, anchor="w", pady=(0, 10))

        self.btn_bubble = self.create_nav_button(menu_container, "Bubble Sort", lambda: self.start_sort("Bubble"))
        self.btn_insert = self.create_nav_button(menu_container, "Insertion Sort", lambda: self.start_sort("Insertion"))
        self.btn_merge = self.create_nav_button(menu_container, "Merge Sort", lambda: self.start_sort("Merge"))
        
        # Separator for Stop Button
        tk.Frame(menu_container, bg=self.bg_sidebar, height=20).pack(fill="x")

        self.btn_stop = self.create_nav_button(menu_container, "Stop Sorting", self.cancel_sort, role="stop")

        # Store buttons in map for easy access
        self.buttons = {
            "Bubble": self.btn_bubble,
            "Insertion": self.btn_insert,
            "Merge": self.btn_merge
        }

        # 2. Main Area
        main_frame = tk.Frame(self, bg=self.bg_main)
        main_frame.pack(side="right", fill="both", expand=True, padx=40, pady=40)
        
        # Status
        self.lbl_main_status = tk.Label(main_frame, text="Ready to sort", font=("Segoe UI", 24), bg=self.bg_main, fg=self.text_primary)
        self.lbl_main_status.pack(anchor="w")
        
        self.lbl_sub_status = tk.Label(main_frame, text="Select an algorithm from the menu to begin.", font=("Segoe UI", 11), bg=self.bg_main, fg=self.text_secondary)
        self.lbl_sub_status.pack(anchor="w", pady=(5, 15))

        # Progress Bar Configuration
        style = ttk.Style()
        style.theme_use('clam')
        # Customizing the progress bar (Unified Theme)
        style.configure("Green.Horizontal.TProgressbar", 
                        foreground=self.accent_main, 
                        background=self.accent_main, 
                        troughcolor=self.bg_sidebar, # Matches sidebar/mute tone
                        bordercolor=self.card_border, # Matches other borders
                        lightcolor=self.accent_main, 
                        darkcolor=self.accent_main)
        
        self.progress = ttk.Progressbar(main_frame, style="Green.Horizontal.TProgressbar", orient="horizontal", length=100, mode="determinate")
        self.progress.pack(fill="x", pady=(0, 20))

        # Results
        # Card effect for results area - Seamless Integration
        result_container = tk.Frame(main_frame, bg=self.card_bg, highlightbackground=self.card_border, highlightthickness=1)
        result_container.pack(fill="both", expand=True)

        self.result_area = scrolledtext.ScrolledText(result_container, 
                                                     font=("Consolas", 10), 
                                                     bg=self.card_bg, # Matches card background
                                                     fg=self.text_primary,
                                                     bd=0, 
                                                     padx=20, pady=20,
                                                     state=tk.DISABLED,
                                                     cursor="arrow",
                                                     wrap="none")  # Prevent mid-number wrapping
        self.result_area.pack(fill="both", expand=True)
        
    def on_dataset_change(self, event):
        """Handles dataset selection change."""
        new_file = self.combo_dataset.get()
        if new_file and new_file != self.current_dataset_name:
            self.current_dataset_name = new_file
            self.dataset_path = os.path.join(self.base_dir, new_file)
            
            # Reload data
            self.data_cache = read_dataset(self.dataset_path) or []
            self.data_count = len(self.data_cache)
            
            # Update UI
            self.lbl_item_count.config(text=f"{self.data_count:,} items")
            self.lbl_main_status.config(text="Ready to sort", fg=self.text_primary)
            self.lbl_sub_status.config(text=f"Loaded {new_file}. Select an algorithm.")
            
            # Clear results
            self.result_area.config(state=tk.NORMAL)
            self.result_area.delete('1.0', tk.END)
            self.result_area.config(state=tk.DISABLED)
            self.progress['value'] = 0

    def on_toggle_order(self, event):
        # Allow toggling only if not sorting
        # If stop button is NOT disabled, sorting is running -> return
        if not getattr(self.btn_stop, 'is_disabled', True): return 
        
        # Determine click side
        w = int(self.toggle_canvas['width'])
        if event.x < w / 2:
            self.sort_descending = True
        else:
            self.sort_descending = False
        self.update_toggle_ui()
        
    def update_toggle_ui(self):
        w = int(self.toggle_canvas['width'])
        h = int(self.toggle_canvas['height'])
        
        if self.sort_descending:
            # Move slider left
            self.toggle_canvas.coords(self.toggle_slider, 0, 0, w/2, 0, w/2, h, 0, h) # Simplify: redraw rect logic in create_rounded_rect handles complex points
            # Actually create_rounded_rect returns generic polygon, updating coords is complex.
            # Easier to delete and redraw the slider
            self.toggle_canvas.delete(self.toggle_slider)
            self.toggle_slider = self.create_rounded_rect(self.toggle_canvas, 0, 0, w/2, h, radius=14, fill=self.accent_main, outline="")
            
            # Recolor text - redraw on top or lift?
            self.toggle_canvas.itemconfig(self.txt_desc, fill="#FFFFFF")
            self.toggle_canvas.itemconfig(self.txt_asc, fill=self.text_secondary)
        else:
            # Move slider right
            self.toggle_canvas.delete(self.toggle_slider)
            self.toggle_slider = self.create_rounded_rect(self.toggle_canvas, w/2, 0, w, h, radius=14, fill=self.accent_main, outline="")
            
            self.toggle_canvas.itemconfig(self.txt_desc, fill=self.text_secondary)
            self.toggle_canvas.itemconfig(self.txt_asc, fill="#FFFFFF")
        
        # Ensure text is on top
        self.toggle_canvas.tag_raise(self.txt_desc)
        self.toggle_canvas.tag_raise(self.txt_asc)

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

    def create_nav_button(self, parent, text, command, role="nav"):
        # Dimensions
        btn_w = 200 
        btn_h = 50
        
        canvas = tk.Canvas(parent, width=btn_w, height=btn_h, bg=self.bg_sidebar, highlightthickness=0)
        canvas.pack(pady=8) 
        
        # State
        canvas.is_disabled = False
        canvas.role = role
        canvas.is_active = False # For toggle state (nav items)
        
        # Colors based on role
        base_fill = self.card_bg
        base_outline = self.card_border
        text_color = self.text_primary
        
        if role == "stop":
            canvas.is_disabled = True # Start disabled
            # Distinct look for disabled stop button? Or just standard card
            
        # Draw Shape
        pad = 2
        # Use a slightly smaller rect so outline doesn't clip
        # x1, y1, x2, y2
        shape_id = self.create_rounded_rect(canvas, pad, pad, btn_w-pad, btn_h-pad, radius=20, 
                                            fill=base_fill, outline=base_outline, width=1)
        
        # Draw Text
        text_id = canvas.create_text(btn_w/2, btn_h/2, text=text, fill=text_color, 
                                     font=("Segoe UI", 11, "bold"), anchor="center")
        
        # Interaction Logic
        def on_click(e):
            if canvas.is_disabled: return
            if role == "nav":
                pass # active state handled by update_active_button
            command()
            
        def on_enter(e):
            if canvas.is_disabled: return
            if canvas.is_active and role == "nav": return 
            
            # Hover colors
            if role == "stop":
                 canvas.itemconfig(shape_id, fill="#E6B0AA", outline="#C0392B")
                 canvas.itemconfig(text_id, fill="#922B21")
            else:
                 canvas.itemconfig(shape_id, fill=self.btn_hover, outline=self.accent_main)
                 canvas.itemconfig(text_id, fill=self.text_primary)
                 
        def on_leave(e):
            if canvas.is_disabled: return
            if canvas.is_active and role == "nav": return
            
            # Reset colors
            canvas.itemconfig(shape_id, fill=self.card_bg, outline=self.card_border)
            canvas.itemconfig(text_id, fill=self.text_primary)
            
        # Bindings
        # Canvas Tag binding is sometimes better but binding to widget works for the whole area
        canvas.bind("<Button-1>", on_click)
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        # Also bind to the text item so it passes through
        canvas.tag_bind(text_id, "<Button-1>", on_click)
        canvas.tag_bind(text_id, "<Enter>", on_enter)
        canvas.tag_bind(text_id, "<Leave>", on_leave)
        
        # Attach IDs for external updates
        canvas.ids = {"shape": shape_id, "text": text_id}
        
        return canvas

    def start_sort(self, algorithm_name):
        # UI Selection State
        self.update_active_button(algorithm_name)
        
        # Reset output
        self.result_area.config(state=tk.NORMAL)
        self.result_area.delete('1.0', tk.END)
        self.result_area.config(state=tk.DISABLED)
        
        self.lbl_main_status.config(text=f"Running {algorithm_name} Sort...", fg=self.accent_hover)
        self.lbl_sub_status.config(text=f"Processing {self.data_count:,} items. Please wait...", fg="#E67E22")
        self.progress['value'] = 0
        
        # Reset cancel flag
        self.cancel_event.clear()
        self.current_algo_name = algorithm_name # Track current algo
        
        # Disable Sort buttons, Enable Stop button
        self.set_buttons_state(tk.DISABLED)
        
        threading.Thread(target=self.run_sort_process, args=(algorithm_name,), daemon=True).start()

    def cancel_sort(self):
        """Signals the sorting thread to stop."""
        if self.cancel_event.is_set(): return # Already cancelling
        
        self.cancel_event.set()
        self.lbl_main_status.config(text="Stopping...", fg="#C0392B")
        
        # Disable stop button immediately to prevent double click
        self.btn_stop.is_disabled = True
        self.btn_stop.config(cursor="arrow")
        self.btn_stop.itemconfig(self.btn_stop.ids["shape"], fill=self.bg_sidebar, outline=self.card_border)
        self.btn_stop.itemconfig(self.btn_stop.ids["text"], fill="#CDCDC1")

    def update_active_button(self, active_algo):
        """Highlights the active button and resets others."""
        for name, canvas in self.buttons.items():
            shape_id = canvas.ids["shape"]
            text_id = canvas.ids["text"]
            
            if name == active_algo:
                canvas.is_active = True
                # Active: Latte background, Dark Text
                canvas.itemconfig(shape_id, fill=self.accent_hover, outline=self.accent_hover)
                canvas.itemconfig(text_id, fill="#000000")
            else:
                canvas.is_active = False
                canvas.itemconfig(shape_id, fill=self.card_bg, outline=self.card_border)
                canvas.itemconfig(text_id, fill=self.text_primary)

    def run_sort_process(self, algo_type):
        # Use currently loaded cache which matches the selection
        data = self.data_cache if self.data_cache else read_dataset(self.dataset_path)
        
        if not data:
            self.update_gui_error("Dataset is empty or file missing.")
            return

        # Callback for progress with throttling
        # Closure to hold last update time
        last_update_time = [0] 

        def progress_cb(val):
            # Only update if not cancelled
            if not self.cancel_event.is_set():
                current_time = time.time()
                # Update if complete, or if > 0.05s has passed (20fps cap)
                if val >= 100 or (current_time - last_update_time[0] > 0.05):
                    last_update_time[0] = current_time
                    self.update_progress_from_thread(val)

        start_time = time.time()
        
        sorted_data = None
        # Pass the current sort_descending flag
        order_flag = self.sort_descending 
        
        if algo_type == "Bubble":
            sorted_data = bubble_sort(data, progress_cb, self.cancel_event, descending=order_flag)
        elif algo_type == "Insertion":
            sorted_data = insertion_sort(data, progress_cb, self.cancel_event, descending=order_flag)
        elif algo_type == "Merge":
            data_copy = data[:] 
            sorted_data = merge_sort_wrapper(data_copy, progress_cb, self.cancel_event, descending=order_flag)
        
        end_time = time.time()
        elapsed = end_time - start_time

        if sorted_data is None:
            # Cancellation occurred
            self.after(0, self.finalize_cancelled)
        else:
            # Get result area width for dynamic column layout
            widget_width = self.result_area.winfo_width()
            display_text = self.format_output(sorted_data, widget_width)
            self.after(0, lambda: self.finalize_gui(display_text, algo_type, elapsed))

    def update_progress_from_thread(self, value):
        self.after(0, lambda: self.progress.configure(value=value))

    def finalize_cancelled(self):
        self.progress['value'] = 0
        name = getattr(self, 'current_algo_name', 'Sort')
        self.lbl_main_status.config(text=f"{name} Sort Stopped", fg="#C0392B")
        self.lbl_sub_status.config(text="Operation stopped by user.", fg=self.text_secondary)
        self.set_buttons_state(tk.NORMAL)
        # Reset active button visualization
        self.update_active_button(None)

    def format_output(self, data, widget_width=700):
        if not data:
            return "No data to display"
        
        # Fixed number of items per row with generous spacing
        items_per_line = 9
        
        # Find max number width for consistent formatting
        max_num_width = max(len(str(num)) for num in data)
        
        output = []
        current_line = []
        left_margin = "    "  # Left padding for centered look
        
        for i, num in enumerate(data):
            current_line.append(str(num).rjust(max_num_width))
            
            # Check if line is full or last item
            if len(current_line) >= items_per_line or i == len(data) - 1:
                output.append(left_margin + ",    ".join(current_line))  # Extra spacing between numbers
                current_line = []
        
        return "\n".join(output)

    def finalize_gui(self, text, algo_name, elapsed_time):
        self.progress['value'] = 100
        self.result_area.config(state=tk.NORMAL)
        self.result_area.insert(tk.END, text)
        self.result_area.config(state=tk.DISABLED)
        
        self.lbl_main_status.config(text=f"{algo_name} Sort Complete", fg=self.accent_main)
        self.lbl_sub_status.config(text=f"Processed {self.data_count:,} items in {elapsed_time:.4f} seconds.", fg=self.text_secondary)
        self.set_buttons_state(tk.NORMAL)

    def update_gui_error(self, msg):
        self.after(0, lambda: self._show_error(msg))

    def _show_error(self, msg):
        self.lbl_main_status.config(text="Error Encountered", fg="#C0392B")
        self.lbl_sub_status.config(text=msg)
        self.set_buttons_state(tk.NORMAL)

    def set_buttons_state(self, state):
        """
        state: tk.NORMAL (enabled) or tk.DISABLED (disabled)
        """
        # Determine strict states
        enabled = (state == tk.NORMAL)
        sort_btns_disabled = not enabled
        stop_btn_disabled = enabled # If sorting enabled, stop is disabled
        
        # Update Sort Buttons
        for name, canvas in self.buttons.items():
            canvas.is_disabled = sort_btns_disabled
            canvas.config(cursor="arrow" if sort_btns_disabled else "hand2")
            
            shape_id = canvas.ids["shape"]
            text_id = canvas.ids["text"]
            
            if sort_btns_disabled:
                # Dim them
                canvas.itemconfig(shape_id, fill=self.bg_sidebar, outline=self.card_border) 
                canvas.itemconfig(text_id, fill="#A09085") 
            else:
                # Reset to normal or active
                if not canvas.is_active:
                     canvas.itemconfig(shape_id, fill=self.card_bg, outline=self.card_border)
                     canvas.itemconfig(text_id, fill=self.text_primary)
                else:
                     canvas.itemconfig(shape_id, fill=self.accent_hover, outline=self.accent_hover)
                     canvas.itemconfig(text_id, fill="#000000")

        # Update Stop Button
        self.btn_stop.is_disabled = stop_btn_disabled
        self.btn_stop.config(cursor="arrow" if stop_btn_disabled else "hand2")
        
        if stop_btn_disabled:
             self.btn_stop.itemconfig(self.btn_stop.ids["shape"], fill=self.bg_sidebar, outline=self.card_border)
             self.btn_stop.itemconfig(self.btn_stop.ids["text"], fill="#CDCDC1")
        else:
             # Stop button normal state (ready to be clicked)
             self.btn_stop.itemconfig(self.btn_stop.ids["shape"], fill=self.card_bg, outline=self.card_border)
             self.btn_stop.itemconfig(self.btn_stop.ids["text"], fill=self.text_primary)

if __name__ == "__main__":
    app = SorterApp()
    app.mainloop()
