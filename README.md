# DAA Compilation - Laboratory Activities & Projects

**Course:** Design and Analysis of Algorithms (DAA)  
**Student:** Cartoneros  
**Section:** AY225

This repository serves as a compilation of laboratory works and the preliminary exam project for the DAA course.

---

## 📂 Repository Structure

### 1. [Prelim Lab Work 1: Simple Bubble Sort](PRELIM-LAB-WORK-1/)

- **Description:** A console-based implementation of the Bubble Sort algorithm.
- **Key Features:** Command-line interface, sorting benchmarking.
- **Algorithm:** Bubble Sort ($O(n^2)$).

### 2. [Prelim Lab Work 2: GUI Sorting Visualizer](PRELIM-LAB-WORK-2/)

- **Description:** A graphical user interface (Tkinter) application for visualizing and benchmarking sorting algorithms.
- **Key Features:** GUI, Algorithm selection, Ascending/Descending toggles.
- **Algorithms:** Bubble Sort, Insertion Sort, Merge Sort.

### 3. [Prelim Exam: Sorting Algorithm Stress Test](PRELIM-EXAM/)

- **Description:** A comprehensive benchmarking tool designed to handle larger structured datasets (CSV).
- **Key Features:**
  - Data parsing from `generated_data.csv`.
  - Column-based sorting (ID, FirstName, LastName).
  - Performance tracking (Load time vs. Sort time).
- **Algorithms:** Bubble Sort, Insertion Sort, Merge Sort.

### 4. [Midterm Lab Work 1: Multi-Metric Shortest Path Finder](MIDTERM-LAB-WORK-1/)

- **Description:** A web-based application that finds shortest paths across all pairs of nodes using Dijkstra's algorithm, optimized for Distance, Time, and Fuel.
- **Key Features:**
  - Quick Answer panel (best source node per metric with fuel tiebreaker).
  - Interactive vis.js graph visualization with path highlighting.
  - Pill-shaped metric toggles, custom dropdown, flat 5-color dark theme.
- **Algorithm:** Dijkstra's Shortest Path ($O((V+E) \log V)$).

### 5. [Midterm Lab Work 2: GUI Route Optimizer & Analyzer](MIDTERM-LAB-WORK-2/)

- **Description:** A robust, interactive desktop application built in Tkinter that consolidates different lab logic implementations.
- **Key Features:**
  - Dynamic responsive graph view with draggable nodes.
  - "Overall Best Hub" logic (Lab 1) vs "Point-to-Point" logic (Lab 2).
  - Clean edge mapping with directional arrows for shortest paths.
- **Algorithms:** Dijkstra's Shortest Path, Procedural network-generation.

Navigate to the respective folders to find specific `README.md` files with instructions on how to run each project.

### Example: Running the Exam Project

```bash
cd PRELIM-EXAM/src
python main.py
```

### Example: Running Midterm Lab Work 2

```bash
cd MIDTERM-LAB-WORK-2/
python MidtermLab2-CARTONEROS.py
```

## 🛠️ Requirements

- Python 3.x
- Tkinter (for GUI-based Lab Works, including Midterm Lab Work 2)
  - _On Windows, Tkinter comes pre-installed with Python._
  - _On Linux, you may need to install it via `sudo apt-get install python3-tk`._
