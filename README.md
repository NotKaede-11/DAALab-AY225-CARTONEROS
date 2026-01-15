# Data Sorting Algorithm Visualizer 📊

A modern, minimalist Python application designed to visualize and benchmark standard sorting algorithms on large integer datasets. Built with `tkinter`, it features a clean "Latte Series" UI, real-time progress tracking, and robust dataset handling.

![Python](https://img.shields.io/badge/Python-3.x-blue.svg?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-success.svg?style=flat-square)

---

## ✨ Features

- **Modern Minimalist GUI**: A soothing "Latte Theme" interface with rounded aesthetic cards, custom toggle switches, and an intuitive layout.
- **Robust Dataset Parsing**: Intelligently reads and parses parsing `.txt` dataset files.
  - Automatically handles newline, comma, and space-separated values.
  - **Smart Parsing**: Detects and splits "concatenated" number errors based on statistical digit length analysis.
- **Core Algorithms**:
  - **Bubble Sort**: Best for educational purposes on smaller datasets.
  - **Insertion Sort**: Efficient for small or partially sorted datasets.
  - **Merge Sort**: A highly efficient, stable sorting algorithm for large datasets (O(n log n)).
- **Real-Time Visualization**:
  - Smooth progress status bar.
  - Live sorting stats (Item count, Elapsed time).
  - Responsive UI that doesn't freeze during processing (Multi-threaded).
- **Control**:
  - **Sort Order**: Toggle between Ascending and Descending order.
  - **Cancellation**: Stop any running sort operation instantly.

---

## 🚀 Getting Started

### Prerequisites

Ensure you have Python installed on your system. This application uses the standard library `tkinter`, which typically comes pre-installed with Python.

```bash
python --version
```

### Installation

1.  Clone this repository or download the source code.
2.  Navigate to the project directory:
    ```bash
    cd DAALab-AY225-CARTONEROS
    ```

### Usage

1.  **Prepare your dataset**:
    - Ensure your data text files (e.g., `dataset.txt`) are in the same folder as the script.
    - Format: One integer per line OR space/comma-separated numbers.
2.  **Run the application**:
    ```bash
    python RENAME.py
    ```
3.  **In the App**:
    - **Select Dataset**: Choose a file from the dropdown menu (top-left).
    - **Toggle Order**: Click "Asc" or "Desc" to set the sorting direction.
    - **Choose Algorithm**: Click on _Bubble Sort_, _Insertion Sort_, or _Merge Sort_ to start.
    - **View Results**: The sorted output will appear in the main text area, along with the time taken.

---

## 📂 Project Structure

```
DAALab-AY225-CARTONEROS/
├── RENAME.py          # Main application source code
├── dataset.txt        # Sample dataset file
└── README.md          # Project documentation
```

## 🛠️ Technical Details

- **Language**: Python 3
- **GUI Framework**: Tkinter (Native)
- **Concurrency**: `threading` module used to prevent UI blocking during heavy computations.
- **Parsing Logic**: Uses `collections.Counter` to determine the mode of digit lengths, allowing the parser to intelligently split numbers that may have been accidentally concatenated in raw data files.

## 📝 License

This project is part of the **DAA-Lab** (Design and Analysis of Algorithms) coursework.

---

_Created for DAALab AY225_
