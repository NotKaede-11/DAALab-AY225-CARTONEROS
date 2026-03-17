# Midterm Lab 2: Network Analyzer (V2)

This Python application integrates dual functionalities to solve the shortest path problems according to **Lab 1** logic (finding the best overall starting city out of all cities) and **Lab 2** logic (visual point-to-point routing).

## Features

- **No External Libraries Required:** This application runs purely on Python's built-in libraries (such as `tkinter` and `heapq`). There is absolutely no need to run `pip install` commands. Standard Python is all you need!
- **Unified Welcome Screen:** Choose between evaluating the best total hub (Lab 1 logic) or computing navigation routes between specific nodes (Lab 2 logic).
- **Thick Path Visualizations:** Visual elements on the graph have been thickened, and node text clearly shows the full name, making the application much easier to read.
- **Custom Color Palette:** Uses a clean color palette: `#cbcbcb`, `#f2f2f2`, `#174d38` (dark green theme), and `#4d1717` (dark red elements).

## How It Works

The program contains hardcoded node distances, times, and fuel consumption metrics representing various cities (Imus, Bacoor, Dasma, etc.).

### Option 1: Find Best Overall Starting City (Lab 1 Logic)

If chosen, the tool evaluates each potential "Starting city" by computing the path to _every other_ city on the map. It does this independently for Distance, Time, and Fuel. Finally, it tells you exactly which node is the most efficient central hub for each respective metric.

### Option 2: Point-to-Point Routing (Lab 2 Logic)

If chosen, the tool directs you to an interactive diagram of the graph. You can:

1. Select an **Origin Node** and **Destination Node**.
2. Select whether to optimize for **Distance**, **Time**, or **Fuel**.
3. View the highlighted route dynamically mapping across the cities on screen.
4. Read the exact travel costs in the detailed left-side dashboard.

## Requirements & Running the Program

1. Ensure **Python** is installed on your system (Python 3.7+ is recommended).
2. The application uses the built-in `tkinter` library. On Windows, this is included with Python. On Linux, you might need to install it via your package manager (e.g., `sudo apt-get install python3-tk`).
3. To start the tool, open your terminal, navigate into the folder `MIDTERM-LAB-WORK-2/` and execute the script:

   ```bash
   python MidtermLab2-CARTONEROS.py
   ```

No extra dependencies to install via `pip`. Enjoy!

## Difficulties Encountered

The only real difficulty I faced was how to interpret the instructions. I didn't know whether to use the old format for lab work 1 or use the format that my classmates said were correct. So in the end, I just decided to put those 2 in 1.
