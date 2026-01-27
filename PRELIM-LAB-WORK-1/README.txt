PRELIM LAB WORK 1 - Sorting Algorithms
======================================

This folder contains implementations of sorting algorithms for the DAA Lab.


FILES
-----
- Alg.Sorter.py       : GUI-based sorting application with multiple algorithms
- SimpleBubbleSort.py : Simple terminal-based Bubble Sort implementation
- dataset.txt         : Sample dataset containing 10,000 integers


1. Alg.Sorter.py (GUI Application)
----------------------------------

A full-featured GUI sorting application built with Tkinter.

Features:
  - Three Sorting Algorithms: Bubble Sort, Insertion Sort, Merge Sort
  - Ascending/Descending sort order toggle
  - Real-time progress bar during sorting
  - Stop/Cancel sorting mid-operation
  - Auto-detects .txt dataset files in the folder

How to Run:
  python Alg.Sorter.py

Requirements:
  - Python 3.x
  - Tkinter (included with standard Python installation)

Usage:
  1. Run the script
  2. Select a dataset file from the dropdown
  3. Choose a sorting algorithm
  4. Select sort order (Ascending/Descending)
  5. Click "Start Sorting"
  6. View sorted results and execution time


2. SimpleBubbleSort.py (Terminal Application)
---------------------------------------------

A simple command-line Bubble Sort implementation.

Features:
  - Optimized Bubble Sort with early exit when sorted
  - Auto-detects any .txt file in the same folder
  - Formatted grid output (10 numbers per row)
  - Execution time displayed in seconds and milliseconds

How to Run:
  python SimpleBubbleSort.py

Requirements:
  - Python 3.x
  - No external packages required

Usage:
  1. Place a .txt file with integers (one per line) in the same folder
  2. Run the script
  3. The script will automatically find and sort the data

Sample Output:
  Found dataset file: dataset.txt
  Dataset loaded. 10000 integers found.
  Starting Bubble Sort...

  ==================== SORTED DATA ====================

       1     2     3     4     5     6     7     8     9    10
      11    12    13    14    15    16    17    18    19    20
      ...

  =====================================================

  Execution Time: 2.2478 seconds (2247.76 ms)


DATASET FORMAT
--------------
The dataset.txt file should contain integers, one per line:

  9999
  1234
  5678
  ...
