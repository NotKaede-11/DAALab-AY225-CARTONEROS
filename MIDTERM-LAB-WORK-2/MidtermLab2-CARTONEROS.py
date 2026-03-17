import heapq
import tkinter as tk
from tkinter import ttk, messagebox

# ─────────────────────────────────────────
#  DATA LOADING (HARDCODED)
# ─────────────────────────────────────────

def build_graph():
    """Builds the adjacency list from hardcoded data."""
    graph = {}
    nodes = set()

    # Hardcoded data from the dataset
    connections = [
        ('Imus', 'Bacoor', 10, 15, 1.2),
        ('Bacoor', 'Dasma', 12, 25, 1.5),
        ('Dasma', 'Kawit', 12, 25, 1.5),
        ('Kawit', 'Indang', 12, 25, 1.2),
        ('Indang', 'Silang', 14, 25, 1.5),
        ('Silang', 'Gentri', 10, 25, 1.3),
        ('Gentri', 'Noveleta', 10, 25, 1.5),
        ('Noveleta', 'Imus', 10, 15, 1.2),
        ('Bacoor', 'Silang', 10, 25, 1.3),
        ('Dasma', 'Silang', 12, 25, 1.5),
        ('Noveleta', 'Bacoor', 10, 15, 1.2),
        ('Silang', 'Kawit', 14, 25, 1.2),
    ]

    for frm, to, dist, time, fuel in connections:
        nodes.add(frm)
        nodes.add(to)

        attrs = {'distance': dist, 'time': time, 'fuel': fuel}
        
        if frm not in graph: graph[frm] = []
        if to not in graph: graph[to] = []
        
        if not any(n == to for n, _ in graph[frm]):
            graph[frm].append((to, attrs))
        if not any(n == frm for n, _ in graph[to]):
            graph[to].append((frm, attrs))

    return graph, sorted(nodes)


# ─────────────────────────────────────────
#  DIJKSTRA ALGORITHM & ALL-PAIRS
# ─────────────────────────────────────────

def dijkstra(graph, start, end, weight_key):
    """
    Finds the shortest path minimizing the specific weight_key.
    Returns (cost, path, totals_dict)
    """
    if start not in graph or end not in graph:
        return None, [], {}

    pq = [(0, start, [start])]
    visited = {}

    while pq:
        cost, node, path = heapq.heappop(pq)

        if node in visited:
            continue
        visited[node] = (cost, path)

        if node == end:
            totals = {'distance': 0, 'time': 0, 'fuel': 0}
            for i in range(len(path) - 1):
                a, b = path[i], path[i + 1]
                for (nb, attrs) in graph.get(a, []):
                    if nb == b:
                        totals['distance'] += attrs['distance']
                        totals['time'] += attrs['time']
                        totals['fuel'] += attrs['fuel']
                        break
            return cost, path, totals

        for (nb, attrs) in graph.get(node, []):
            if nb not in visited:
                new_cost = cost + attrs[weight_key]
                heapq.heappush(pq, (new_cost, nb, path + [nb]))

    return None, [], {}

def get_all_pairs_from_node(graph, nodes, start, weight_key):
    """
    Compute shortest paths from the start node to all other nodes.
    Returns the total accumulated cost, and a dict of paths and costs.
    """
    total_cost = 0
    all_reachable = True
    paths_info = []

    for target in nodes:
        if target == start: continue
        cost, path, _ = dijkstra(graph, start, target, weight_key)
        if cost is not None:
            total_cost += cost
            paths_info.append({'target': target, 'cost': cost, 'path': path})
        else:
            all_reachable = False
    
    return total_cost if all_reachable else float('inf'), paths_info

def compute_best_global_node_advanced(graph, nodes):
    """
    Calculate comprehensive ranking and paths for all metrics to support UI.
    """
    results = {}
    for metric in ['distance', 'time', 'fuel']:
        node_totals = []
        for node in nodes:
            total_cost, paths_info = get_all_pairs_from_node(graph, nodes, node, metric)
            node_totals.append({
                'source': node,
                'total': total_cost,
                'paths': paths_info
            })
            
        # Sort by total cost ascending
        node_totals.sort(key=lambda x: x['total'])
        
        # Determine winner and ties
        min_total = node_totals[0]['total']
        is_tied = len(node_totals) > 1 and abs(node_totals[0]['total'] - node_totals[1]['total']) < 0.001
        
        winner = node_totals[0]
        
        if is_tied and metric in ['distance', 'time']:
            # Apply fuel tiebreaker if needed
            best_fuel = float('inf')
            tied_nodes = [nt for nt in node_totals if abs(nt['total'] - min_total) < 0.001]
            
            for nt in tied_nodes:
                fuel_total, _ = get_all_pairs_from_node(graph, nodes, nt['source'], 'fuel')
                nt['fuel_tiebreaker'] = fuel_total
                if fuel_total < best_fuel:
                    best_fuel = fuel_total
                    winner = nt
        
        results[metric] = {
            'rankings': node_totals,
            'winner': winner,
            'is_tied': is_tied
        }
    return results


# ─────────────────────────────────────────
#  NODE MAP (Canvas-based UI)
# ─────────────────────────────────────────

NODE_POSITIONS = {
    'Noveleta': (0.15, 0.25),
    'Kawit':    (0.48, 0.08),
    'Bacoor':   (0.80, 0.18),
    'Imus':     (0.85, 0.40),
    'Gentri':   (0.20, 0.55),
    'Dasma':    (0.65, 0.65),
    'Indang':   (0.25, 0.85),
    'Silang':   (0.75, 0.88),
}

# ── Color Palette ──
BG_MAIN        = '#f2f2f2'
BG_SIDEBAR     = '#cbcbcb'
BG_CARD        = '#e0e0e0'
FG_PRIMARY     = '#174d38' # Dark Green
FG_SECONDARY   = '#4d1717' # Dark Red
EDGE_COLOR     = '#a0a0a0'
EDGE_TEXT      = '#174d38'
NODE_FILL      = '#cbcbcb'
NODE_OUTLINE   = '#174d38'
HL_EDGE        = '#4d1717'
HL_NODE        = '#4d1717'

CANVAS_W       = 800
CANVAS_H       = 650
RADIUS         = 32


def draw_map(canvas, graph, nodes, highlight_path=None, active_metric='distance'):
    canvas.delete('all')
    
    W = canvas.winfo_width()
    H = canvas.winfo_height()
    
    # Fallback for initial render before pack finishes
    if W < 10: W = CANVAS_W
    if H < 10: H = CANVAS_H

    # Subtle dotted background grid
    for x in range(0, W, 50):
        canvas.create_line(x, 0, x, H, fill='#e5e5e5', width=1, dash=(2, 4))
    for y in range(0, H, 50):
        canvas.create_line(0, y, W, y, fill='#e5e5e5', width=1, dash=(2, 4))

    def pos(name):
        px, py = NODE_POSITIONS.get(name, (0.5, 0.5))
        return int(px * W), int(py * H)

    # Collect highlighted edges
    hl_edges = set()
    if highlight_path and len(highlight_path) > 1:
        for i in range(len(highlight_path) - 1):
            a, b = highlight_path[i], highlight_path[i + 1]
            hl_edges.add((min(a, b), max(a, b)))

    # Pass 1: Draw base lines
    drawn_edges = set()
    for node in graph:
        for (nb, attrs) in graph[node]:
            key = (min(node, nb), max(node, nb))
            if key in drawn_edges:
                continue
            drawn_edges.add(key)

            x1, y1 = pos(node)
            x2, y2 = pos(nb)
            canvas.create_line(x1, y1, x2, y2, fill=EDGE_COLOR, width=3.5, smooth=True, capstyle=tk.ROUND)

    # Pass 1.5: Draw highlighted route with directional arrows
    if highlight_path and len(highlight_path) > 1:
        for i in range(len(highlight_path) - 1):
            a, b = highlight_path[i], highlight_path[i + 1]
            x1, y1 = pos(a)
            x2, y2 = pos(b)
            
            dist = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
            if dist > 0:
                dx = (x2 - x1) / dist
                dy = (y2 - y1) / dist
                
                # Start just outside the origin node, end just outside destination node
                sx = x1 + dx * RADIUS
                sy = y1 + dy * RADIUS
                ex = x2 - dx * (RADIUS + 6)
                ey = y2 - dy * (RADIUS + 6)
                
                # Draw thick colorful route line with arrow
                canvas.create_line(sx, sy, ex, ey, fill='#e63946', width=6.0, arrow=tk.LAST, arrowshape=(18, 22, 8), smooth=True, capstyle=tk.ROUND)

    # Pass 2: Draw Edge Labels
    drawn_labels = set()
    for node in graph:
        for (nb, attrs) in graph[node]:
            key = (min(node, nb), max(node, nb))
            if key in drawn_labels:
                continue
            drawn_labels.add(key)
            
            x1, y1 = pos(node)
            x2, y2 = pos(nb)
            is_hl  = key in hl_edges
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2
            
            metric_val = attrs[active_metric]
            val_str = f"{metric_val:.1f}km"
            if active_metric == 'time': val_str = f"{metric_val:.0f} mins"
            if active_metric == 'fuel': val_str = f"{metric_val:.1f} L"
            
            bg_width = 54
            bg_height = 20
            canvas.create_rectangle(mx - bg_width//2, my - bg_height//2, 
                                    mx + bg_width//2, my + bg_height//2, 
                                    fill=BG_MAIN, outline=EDGE_COLOR, width=1)
            
            fg_label = HL_EDGE if is_hl else EDGE_TEXT
            canvas.create_text(mx, my, text=val_str, fill=fg_label, font=('Arial', 9, 'bold'))

    # Pass 3: Draw Nodes
    for name in nodes:
        x, y   = pos(name)
        is_hl  = highlight_path and name in highlight_path
        fill   = BG_MAIN
        outline = HL_NODE if is_hl else NODE_OUTLINE
        lw     = 4 if is_hl else 2

        # Shadow Effect
        canvas.create_oval(x - RADIUS + 3, y - RADIUS + 3, x + RADIUS + 3, y + RADIUS + 3,
                           fill='#cccccc', outline='')

        if is_hl:
            fill = '#ffe6e6' # subtle highlight background
            # Pulse ring
            canvas.create_oval(x - RADIUS - 6, y - RADIUS - 6, x + RADIUS + 6, y + RADIUS + 6,
                               fill='', outline=HL_NODE, width=2)
            outline = HL_NODE

        canvas.create_oval(x - RADIUS, y - RADIUS, x + RADIUS, y + RADIUS,
                           fill=fill, outline=outline, width=lw)
                           
        # Full Node text displayed clearly inside or below the node
        text_color = FG_SECONDARY if is_hl else FG_PRIMARY
        font_weight = 'bold' if is_hl else 'bold'
        canvas.create_text(x, y, text=name.upper(), fill=text_color, font=('Arial', 9, font_weight))


# ─────────────────────────────────────────
#  GUI SYSTEM
# ─────────────────────────────────────────

class AppUI:
    def __init__(self, root, graph, nodes):
        self.root = root
        self.graph = graph
        self.nodes = nodes
        
        self.font_h1 = ('Arial', 18, 'bold')
        self.font_h2 = ('Arial', 13, 'bold')
        self.font_p = ('Arial', 11)
        self.font_btn = ('Arial', 12, 'bold')
        self.font_small = ('Arial', 10)
        self.font_value = ('Arial', 15, 'bold')

        self.frames = {}
        self.current_path_l1 = None
        self.current_path_l2 = None
        self.resize_timer_l1 = None
        self.resize_timer_l2 = None
        
        self.create_welcome_screen()
        self.create_logic1_screen()
        self.create_logic2_screen()
        
        self.show_frame("welcome")

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].pack(fill='both', expand=True)
        
        if name == "logic2":
            self.reset_map_logic2()
        elif name == "logic1":
            self.run_logic1()

    # ─────────────────────────────────────────
    #  WELCOME SCREEN
    # ─────────────────────────────────────────
    def create_welcome_screen(self):
        frm = tk.Frame(self.root, bg=BG_MAIN)
        self.frames["welcome"] = frm

        # Uniform procedural background network data
        self.welcome_nodes = []
        self.dragged_welcome_node = None
        cols, rows = 16, 11
        for r in range(rows):
            for c in range(cols):
                ox = (r % 2) * 0.035
                x = c * 0.07 + ox - 0.02
                y = r * 0.10 - 0.01
                if -0.05 <= x <= 1.05 and -0.05 <= y <= 1.05:
                    self.welcome_nodes.append([x, y])

        # Decorative background canvas to make it impactful
        self.welcome_canvas = tk.Canvas(frm, bg=BG_MAIN, highlightthickness=0)
        self.welcome_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.welcome_canvas.bind("<ButtonPress-1>", self.on_welcome_node_press)
        self.welcome_canvas.bind("<B1-Motion>", self.on_welcome_node_drag)
        self.welcome_canvas.bind("<ButtonRelease-1>", self.on_welcome_node_release)
        
        container = tk.Frame(frm, bg=BG_MAIN)
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        self.lbl_welcome_title = tk.Label(container, text="ROUTE OPTIMIZER", bg=BG_MAIN, fg=FG_PRIMARY, font=('Arial', 28, 'bold'))
        self.lbl_welcome_title.pack(pady=(0, 10))
        self.lbl_welcome_sub = tk.Label(container, text="What would you like to know?", bg=BG_MAIN, fg=FG_SECONDARY, font=self.font_h2)
        self.lbl_welcome_sub.pack(pady=(0, 40))
        
        self.btn_logic1 = tk.Button(container, text="Find Best Overall Starting City", 
                               command=lambda: self.show_frame("logic1"),
                               bg=FG_PRIMARY, fg=BG_MAIN, font=self.font_btn, relief='flat', padx=30, pady=15, cursor='hand2')
        self.btn_logic1.pack(fill='x', pady=10)
        
        self.btn_logic2 = tk.Button(container, text="Point-to-Point Routing", 
                               command=lambda: self.show_frame("logic2"),
                               bg=FG_SECONDARY, fg=BG_MAIN, font=self.font_btn, relief='flat', padx=30, pady=15, cursor='hand2')
        self.btn_logic2.pack(fill='x', pady=10)

        frm.bind("<Configure>", self.on_welcome_resize)

    def on_welcome_node_press(self, event):
        w = self.welcome_canvas.winfo_width()
        h = self.welcome_canvas.winfo_height()
        for idx, (nx, ny) in enumerate(self.welcome_nodes):
            cx, cy = nx * w, ny * h
            if (event.x - cx)**2 + (event.y - cy)**2 <= 200: # Slightly larger hit area
                self.dragged_welcome_node = idx
                self.welcome_canvas.config(cursor="fleur")
                break
                
    def on_welcome_node_drag(self, event):
        if self.dragged_welcome_node is not None:
            w = max(1, self.welcome_canvas.winfo_width())
            h = max(1, self.welcome_canvas.winfo_height())
            nx = max(0.01, min(0.99, event.x / w))
            ny = max(0.01, min(0.99, event.y / h))
            self.welcome_nodes[self.dragged_welcome_node] = [nx, ny]
            self.redraw_welcome_nodes(w, h)
            
    def on_welcome_node_release(self, event):
        self.dragged_welcome_node = None
        self.welcome_canvas.config(cursor="")

    def redraw_welcome_nodes(self, w, h):
        self.welcome_canvas.delete('all')
        scale = min(max(1.0, w / 900.0), 2.0)
        
        # Calculate dynamic threshold based on grid spacing instead of fixed scale
        threshold = ((w * 0.07)**2 + (h * 0.10)**2)**0.5 * 1.35
        
        # Draw edges
        for i in range(len(self.welcome_nodes)):
            n1 = self.welcome_nodes[i]
            x1, y1 = n1[0]*w, n1[1]*h
            for j in range(i+1, len(self.welcome_nodes)):
                n2 = self.welcome_nodes[j]
                x2, y2 = n2[0]*w, n2[1]*h
                di = ((x1 - x2)**2 + (y1 - y2)**2)**0.5
                if di < threshold:
                    self.welcome_canvas.create_line(x1, y1, x2, y2, fill='#e2e2e2', width=2)
                    
        # Draw nodes
        for (nx, ny) in self.welcome_nodes:
            cx, cy = nx*w, ny*h
            self.welcome_canvas.create_oval(cx-7, cy-7, cx+7, cy+7, fill=BG_MAIN, outline=EDGE_COLOR, width=2)
            
        self.welcome_canvas.lower('all')

    def on_welcome_resize(self, event):
        if event.widget == self.frames["welcome"]:
            w, h = event.width, event.height
            if w < 100 or h < 100: return
            
            # Dynamic text scaling
            scale = min(max(1.0, w / 900.0), 2.0)
            t_size = int(28 * scale)
            s_size = int(14 * scale)
            b_size = int(12 * scale)
            
            self.lbl_welcome_title.config(font=('Arial', t_size, 'bold'))
            self.lbl_welcome_sub.config(font=('Arial', s_size, 'bold'))
            self.btn_logic1.config(font=('Arial', b_size, 'bold'))
            self.btn_logic2.config(font=('Arial', b_size, 'bold'))

            self.redraw_welcome_nodes(w, h)

    # ─────────────────────────────────────────
    #  LOGIC 1: OVERALL BEST NODE
    # ─────────────────────────────────────────
    def create_logic1_screen(self):
        frm = tk.Frame(self.root, bg=BG_MAIN)
        self.frames["logic1"] = frm
        
        header = tk.Frame(frm, bg=BG_SIDEBAR, pady=15)
        header.pack(fill='x')
        
        btn_back = tk.Button(header, text="← Back", command=lambda: self.show_frame("welcome"),
                             bg=BG_CARD, fg=FG_PRIMARY, relief='flat', font=self.font_p, cursor='hand2')
        btn_back.pack(side='left', padx=20)
        
        lbl_title = tk.Label(header, text="🏆 Best Source Node (Lowest Total Across All Destinations)", bg=BG_SIDEBAR, fg=FG_PRIMARY, font=self.font_h1)
        lbl_title.pack(side='left', fill='x', expand=True, padx=(0, 60))
        
        # Scrollable container setup
        content_container = tk.Frame(frm, bg=BG_MAIN)
        content_container.pack(fill='both', expand=True)

        self.canvas_l1 = tk.Canvas(content_container, bg=BG_MAIN, highlightthickness=0)
        self.canvas_l1.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(content_container, orient="vertical", command=self.canvas_l1.yview)
        scrollbar.pack(side='right', fill='y')

        self.canvas_l1.configure(yscrollcommand=scrollbar.set)

        content = tk.Frame(self.canvas_l1, bg=BG_MAIN, padx=40, pady=20)
        self.canvas_l1_window = self.canvas_l1.create_window((0, 0), window=content, anchor='nw')

        def on_configure_content(event):
            self.canvas_l1.configure(scrollregion=self.canvas_l1.bbox('all'))
        content.bind('<Configure>', on_configure_content)

        def on_configure_canvas(event):
            self.canvas_l1.itemconfig(self.canvas_l1_window, width=event.width)
        self.canvas_l1.bind('<Configure>', on_configure_canvas)

        # Mouse wheel support via hover
        def _on_mousewheel(event):
            self.canvas_l1.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas_l1.bind('<Enter>', lambda e: self.canvas_l1.bind_all("<MouseWheel>", _on_mousewheel))
        self.canvas_l1.bind('<Leave>', lambda e: self.canvas_l1.unbind_all("<MouseWheel>"))

        self.l1_cards = {}
        # 3-Column Grid
        col_frame = tk.Frame(content, bg=BG_MAIN)
        col_frame.pack(fill='both', expand=True)
        col_frame.columnconfigure(0, weight=1)
        col_frame.columnconfigure(1, weight=1)
        col_frame.columnconfigure(2, weight=1)

        metrics = [
            ("distance", "Lowest Total Distance", 0),
            ("time", "Lowest Total Time", 1),
            ("fuel", "Lowest Total Fuel", 2)
        ]

        for met_key, title, col in metrics:
            card = tk.Frame(col_frame, bg=BG_SIDEBAR, bd=0)
            card.grid(row=0, column=col, sticky='nsew', padx=10, pady=10)
            
            # Title
            tk.Label(card, text=title, bg=BG_SIDEBAR, fg=FG_PRIMARY, font=self.font_h2).pack(pady=(20, 10))
            
            # Big Number
            lbl_val = tk.Label(card, text="0.00", bg=BG_SIDEBAR, fg=FG_PRIMARY, font=('Arial', 28, 'bold'))
            lbl_val.pack(pady=(0, 20))
            
            # Explanations Panel
            expl_frame = tk.Frame(card, bg=BG_CARD, padx=15, pady=15, bd=0)
            expl_frame.pack(fill='both', expand=True, padx=15, pady=(0, 20))
            
            tk.Label(expl_frame, text="📊 HOW WE GOT THIS ANSWER", bg=BG_CARD, fg=FG_PRIMARY, font=('Arial', 9, 'bold')).pack(anchor='w', pady=(0, 5))
            
            lbl_ranking = tk.Label(expl_frame, text="", bg=BG_CARD, fg=FG_PRIMARY, font=self.font_small, justify='left', anchor='w', wraplength=280)
            lbl_ranking.pack(fill='x', pady=(5, 10))

            lbl_tiebreak = tk.Label(expl_frame, text="", bg=BG_CARD, fg=FG_PRIMARY, font=self.font_small, justify='left', anchor='w', wraplength=280)
            lbl_tiebreak.pack(fill='x', pady=0)
            lbl_winner = tk.Label(expl_frame, text="", bg=BG_CARD, fg=FG_SECONDARY, font=('Arial', 10, 'bold'), justify='left', anchor='w', wraplength=280)
            lbl_winner.pack(fill='x', pady=(5, 10))
            
            tk.Label(expl_frame, text="FROM WINNER TO ALL OTHERS:", bg=BG_CARD, fg=FG_PRIMARY, font=('Arial', 9, 'bold')).pack(anchor='w', pady=(10, 5))
            
            lbl_paths = tk.Label(expl_frame, text="", bg=BG_CARD, fg=FG_PRIMARY, font=self.font_small, justify='left', anchor='w', wraplength=280)
            lbl_paths.pack(fill='x')
            
            self.l1_cards[met_key] = {
                'val': lbl_val,
                'ranking': lbl_ranking,
                'tiebreak': lbl_tiebreak,
                'winner': lbl_winner,
                'paths': lbl_paths
            }
        
    def run_logic1(self):
        best_results = compute_best_global_node_advanced(self.graph, self.nodes)
        
        for metric, data in best_results.items():
            card = self.l1_cards[metric]
            
            win_total = data['winner']['total']
            win_node = data['winner']['source']
            card['val'].config(text=f"{win_total:.2f}")
            
            # Rankings
            rank_text = f"Total {metric} per source node:\n\n"
            min_val = data['rankings'][0]['total']
            
            tied_nodes = []
            for r in data['rankings']:
                is_tied = abs(r['total'] - min_val) < 0.001
                if is_tied and data['is_tied']:
                    tied_nodes.append(r)
                
                star = "★  " if is_tied else "      "
                tie_str = " (tied)" if (is_tied and data['is_tied']) else ""
                rank_text += f"{star}Node {r['source']} = {r['total']:.2f}{tie_str}\n"
                
            card['ranking'].config(text=rank_text)
            
            # Tiebreaker
            if data['is_tied'] and len(tied_nodes) > 1:
                tb_text = "⚖️ Tiebreaker — Lowest fuel usage:\n"
                for t in tied_nodes:
                    f_val = t.get('fuel_tiebreaker', 0)
                    tb_text += f"   Node {t['source']} fuel total = {f_val:.2f}\n"
                card['tiebreak'].config(text=tb_text)
                
                win_f = data['winner'].get('fuel_tiebreaker', 0)
                card['winner'].config(text=f"✅ Winner: Node {win_node} (lower fuel: {win_f:.2f})")
            else:
                card['tiebreak'].config(text="")
                card['winner'].config(text=f"✅ Winner: Node {win_node} (no tiebreaker needed)")
                
            # Paths
            paths_text = ""
            for p in data['winner']['paths']:
                path_str = " - ".join(p['path'])
                paths_text += f"→ Node {p['target']} ({p['cost']:.1f}):  {path_str}\n"
                
            card['paths'].config(text=paths_text.strip())
        
    # ─────────────────────────────────────────
    #  LOGIC 2: POINT-TO-POINT
    # ─────────────────────────────────────────
    def create_card(self, parent, title, row, col):
        card = tk.Frame(parent, bg=BG_CARD, padx=12, pady=10, bd=0)
        card.grid(row=row, column=col, sticky='nsew', padx=4, pady=4)
        
        tk.Label(card, text=title, bg=BG_CARD, fg=FG_PRIMARY, font=self.font_small).pack(anchor='w')
        val_lbl = tk.Label(card, text="-", bg=BG_CARD, fg=FG_SECONDARY, font=self.font_value)
        val_lbl.pack(anchor='w', pady=(4,0))
        return val_lbl

    def create_logic2_screen(self):
        frm = tk.Frame(self.root, bg=BG_MAIN)
        self.frames["logic2"] = frm
        
        # Sidebar
        self.sidebar = tk.Frame(frm, bg=BG_SIDEBAR, width=320)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        # Main Area
        self.main_area = tk.Frame(frm, bg=BG_MAIN)
        self.main_area.pack(side='right', fill='both', expand=True)

        self.canvas_l2 = tk.Canvas(self.main_area, width=CANVAS_W, height=CANVAS_H,
                                   bg=BG_MAIN, highlightthickness=0)
        self.canvas_l2.pack(fill='both', expand=True, padx=20, pady=20)
        self.canvas_l2.bind("<Configure>", self.on_canvas_resize)
        
        # Interactivity Bindings
        self.canvas_l2.bind("<ButtonPress-1>", self.on_node_press)
        self.canvas_l2.bind("<B1-Motion>", self.on_node_drag)
        self.canvas_l2.bind("<ButtonRelease-1>", self.on_node_release)
        self.canvas_l2.bind("<Motion>", self.on_node_hover)
        self.dragged_node = None
        
        # Header
        header_frm = tk.Frame(self.sidebar, bg=BG_SIDEBAR, pady=20, padx=20)
        header_frm.pack(fill='x')
        
        btn_back = tk.Button(header_frm, text="← Back", command=lambda: self.show_frame("welcome"),
                             bg=BG_CARD, fg=FG_PRIMARY, relief='flat', font=self.font_p, cursor='hand2')
        btn_back.pack(anchor='w', pady=(0, 10))
        
        tk.Label(header_frm, text="POINT-TO-POINT", bg=BG_SIDEBAR, fg=FG_PRIMARY, font=self.font_h1, anchor='w').pack(fill='x')

        tk.Frame(self.sidebar, bg=BG_MAIN, height=2).pack(fill='x', padx=20, pady=(0, 20))

        # Controls
        form_frm = tk.Frame(self.sidebar, bg=BG_SIDEBAR, padx=20)
        form_frm.pack(fill='x')

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox', fieldbackground=BG_MAIN, background=BG_SIDEBAR, foreground=FG_PRIMARY, borderwidth=0)

        # Dropdowns
        tk.Label(form_frm, text="Origin Node", bg=BG_SIDEBAR, fg=FG_PRIMARY, font=self.font_small).pack(anchor='w')
        self.frm_var = tk.StringVar()
        cb_origin = ttk.Combobox(form_frm, textvariable=self.frm_var, values=self.nodes, state='readonly', font=self.font_p)
        cb_origin.set("Select Origin...")
        cb_origin.pack(fill='x', pady=(4, 15), ipady=4)

        tk.Label(form_frm, text="Destination Node", bg=BG_SIDEBAR, fg=FG_PRIMARY, font=self.font_small).pack(anchor='w')
        self.to_var = tk.StringVar()
        cb_dest = ttk.Combobox(form_frm, textvariable=self.to_var, values=self.nodes, state='readonly', font=self.font_p)
        cb_dest.set("Select Destination...")
        cb_dest.pack(fill='x', pady=(4, 15), ipady=4)

        # Optimization Criteria
        tk.Label(form_frm, text="Optimize For", bg=BG_SIDEBAR, fg=FG_PRIMARY, font=self.font_small).pack(anchor='w', pady=(5, 5))
        self.opt_var = tk.StringVar(value='distance')
        
        radio_frm = tk.Frame(form_frm, bg=BG_SIDEBAR)
        radio_frm.pack(fill='x', pady=(0, 20))
        
        for text, val in [("Distance", "distance"), ("Time", "time"), ("Fuel", "fuel")]:
            rb = tk.Radiobutton(radio_frm, text=text, variable=self.opt_var, value=val,
                                bg=BG_SIDEBAR, fg=FG_PRIMARY, selectcolor=BG_MAIN,
                                activebackground=BG_SIDEBAR, activeforeground=FG_SECONDARY,
                                font=self.font_p, cursor='hand2', bd=0, highlightthickness=0,
                                command=self.on_metric_change)
            rb.pack(side='left', padx=(0, 10))

        # Action Buttons
        btn_frm = tk.Frame(form_frm, bg=BG_SIDEBAR)
        btn_frm.pack(fill='x', pady=10)

        calc_btn = tk.Button(btn_frm, text="Find Route", command=self.on_find_route_click,
                             bg=FG_SECONDARY, fg=BG_MAIN, font=self.font_btn,
                             relief='flat', pady=10, cursor='hand2')
        calc_btn.pack(fill='x', pady=(0, 10))

        reset_btn = tk.Button(btn_frm, text="Clear Map", command=self.reset_map_btn_click,
                              bg=FG_PRIMARY, fg=BG_MAIN, font=self.font_btn,
                              relief='flat', pady=10, cursor='hand2')
        reset_btn.pack(fill='x')

        # Results Dashboard (Initially Hidden)
        self.res_frm = tk.Frame(self.sidebar, bg=BG_SIDEBAR, padx=15, pady=20)
        # self.res_frm.pack(fill='both', expand=True) # Will pack dynamically
        
        metrics_grid = tk.Frame(self.res_frm, bg=BG_SIDEBAR)
        metrics_grid.pack(fill='x')
        metrics_grid.columnconfigure(0, weight=1)
        metrics_grid.columnconfigure(1, weight=1)

        self.lbl_dist = self.create_card(metrics_grid, "Total Distance", 0, 0)
        self.lbl_time = self.create_card(metrics_grid, "Est. Time", 0, 1)
        self.lbl_fuel = self.create_card(metrics_grid, "Fuel Usage", 1, 0)
        
        self.path_card = tk.Frame(metrics_grid, bg=BG_CARD, padx=12, pady=10, bd=0)
        self.path_card.grid(row=1, column=1, sticky='nsew', padx=4, pady=4)
        tk.Label(self.path_card, text="Path Sequence", bg=BG_CARD, fg=FG_PRIMARY, font=self.font_small).pack(anchor='w')
        self.lbl_path = tk.Label(self.path_card, text="-", bg=BG_CARD, fg=FG_SECONDARY, font=('Arial', 9, 'bold'), wraplength=100, justify='left')
        self.lbl_path.pack(anchor='w', pady=(4,0))

    def on_find_route_click(self):
        if self.frm_var.get() not in self.nodes or self.to_var.get() not in self.nodes:
            messagebox.showwarning("Incomplete", "Please select both an Origin and a Destination node.", parent=self.root)
            return

        if self.frm_var.get() == self.to_var.get():
            messagebox.showwarning("Invalid Selection", "Origin and Destination cannot be the same.", parent=self.root)
            self.hide_results()
            self.current_path_l2 = None
            draw_map(self.canvas_l2, self.graph, self.nodes, active_metric=self.opt_var.get())
        else:
            self.find_path()

    def on_metric_change(self):
        if hasattr(self, 'current_path_l2') and self.current_path_l2 is not None:
            # We already have an active route displayed, recalculate for the new metric
            if self.frm_var.get() in self.nodes and self.to_var.get() in self.nodes and self.frm_var.get() != self.to_var.get():
                self.find_path()
        else:
            if hasattr(self, 'canvas_l2'):
                draw_map(self.canvas_l2, self.graph, self.nodes, active_metric=self.opt_var.get())

    def hide_results(self):
        if hasattr(self, 'res_frm'):
            self.res_frm.pack_forget()

    def show_results(self):
        if hasattr(self, 'res_frm'):
            self.res_frm.pack(fill='both', expand=True)

    def reset_map_btn_click(self):
        self.frm_var.set("Select Origin...")
        self.to_var.set("Select Destination...")
        self.reset_map_logic2()

    def reset_map_logic2(self):
        self.current_path_l2 = None
        draw_map(self.canvas_l2, self.graph, self.nodes, active_metric=self.opt_var.get())
        self.hide_results()

    def find_path(self):
        start = self.frm_var.get()
        end   = self.to_var.get()
        opt   = self.opt_var.get()

        cost, path, totals = dijkstra(self.graph, start, end, opt)

        if not path:
            messagebox.showinfo("No Route", f"No accessible path found.", parent=self.root)
            self.hide_results()
            self.current_path_l2 = None
            draw_map(self.canvas_l2, self.graph, self.nodes, active_metric=self.opt_var.get())
            return

        self.current_path_l2 = path
        draw_map(self.canvas_l2, self.graph, self.nodes, highlight_path=path, active_metric=opt)
        
        self.show_results()
        
        self.lbl_dist.config(text=f"{totals['distance']:.1f} km")
        self.lbl_time.config(text=f"{totals['time']:.0f} min")
        self.lbl_fuel.config(text=f"{totals['fuel']:.1f} L")
        
        self.lbl_path.config(text=" → ".join(path))

    def on_canvas_resize(self, event):
        if self.resize_timer_l2:
            self.root.after_cancel(self.resize_timer_l2)
        self.resize_timer_l2 = self.root.after(100, self._redraw_canvas_l2)

    def on_node_press(self, event):
        W = self.canvas_l2.winfo_width()
        H = self.canvas_l2.winfo_height()
        for name, (px, py) in NODE_POSITIONS.items():
            x, y = int(px * W), int(py * H)
            if (event.x - x)**2 + (event.y - y)**2 <= RADIUS**2:
                self.dragged_node = name
                self.canvas_l2.config(cursor="fleur")
                break

    def on_node_drag(self, event):
        if hasattr(self, 'dragged_node') and self.dragged_node:
            W = self.canvas_l2.winfo_width()
            H = self.canvas_l2.winfo_height()
            nx = max(0.05, min(0.95, event.x / W))
            ny = max(0.05, min(0.95, event.y / H))
            NODE_POSITIONS[self.dragged_node] = (nx, ny)
            self._redraw_canvas_l2()

    def on_node_release(self, event):
        self.dragged_node = None
        self.canvas_l2.config(cursor="arrow")
        
    def on_node_hover(self, event):
        if hasattr(self, 'dragged_node') and self.dragged_node:
            return # Currently dragging
            
        W = self.canvas_l2.winfo_width()
        H = self.canvas_l2.winfo_height()
        for name, (px, py) in NODE_POSITIONS.items():
            x, y = int(px * W), int(py * H)
            if (event.x - x)**2 + (event.y - y)**2 <= RADIUS**2:
                self.canvas_l2.config(cursor="hand2")
                return
        self.canvas_l2.config(cursor="arrow")

    def _redraw_canvas_l2(self):
        draw_map(self.canvas_l2, self.graph, self.nodes, highlight_path=self.current_path_l2, active_metric=self.opt_var.get())

def main():
    graph, nodes = build_graph()
    
    root = tk.Tk()
    root.title("Midterm Lab 2 - Network Analyzer")
    root.geometry("1100x700")
    root.configure(bg=BG_MAIN)
    root.minsize(900, 600)
    
    app = AppUI(root, graph, nodes)
    root.mainloop()

if __name__ == '__main__':
    main()
