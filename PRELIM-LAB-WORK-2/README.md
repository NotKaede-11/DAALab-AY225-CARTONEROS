# Sorting Algorithms Visualizer (GUI Application)

A full-featured GUI sorting application built with Tkinter, featuring multiple algorithms with real-time progress tracking and visual feedback.

## Files

- `Alg.Sorter.py`: The main GUI application script.
- `dataset.txt`: Sample dataset containing integers.

## Algorithm Analysis

### Comparison of Implemented Algorithms

| Algorithm          | Best Case  | Average Case | Worst Case | Space | Stable |
| ------------------ | ---------- | ------------ | ---------- | ----- | ------ |
| **Bubble Sort**    | O(n)       | O(n²)        | O(n²)      | O(1)  | ✓ Yes  |
| **Insertion Sort** | O(n)       | O(n²)        | O(n²)      | O(1)  | ✓ Yes  |
| **Merge Sort**     | O(n log n) | O(n log n)   | O(n log n) | O(n)  | ✓ Yes  |

### When to Use Each Algorithm

| Algorithm          | Best Use Case                                                                |
| ------------------ | ---------------------------------------------------------------------------- |
| **Bubble Sort**    | Educational purposes, very small datasets (N < 100), nearly sorted data      |
| **Insertion Sort** | Small datasets, online sorting (data arriving in stream), nearly sorted data |
| **Merge Sort**     | Large datasets, when stability is required, predictable performance needed   |

### Visual Comparison

```
Time Complexity Growth (log scale):

O(n²)      │                    ╱
           │                  ╱
           │                ╱
           │             ╱
           │          ╱
O(n log n) │       ╱ ─ ─ ─ ─ ─ ─
           │     ╱
           │   ╱
O(n)       │ ╱
           └─────────────────────
             N → 100  1K   10K  100K

── Bubble/Insertion (O(n²))
─ ─ Merge Sort (O(n log n))
```

## Features

- **Graphical User Interface:** Built using Python's `tkinter` with a modern "Latte" theme.
- **Three Sorting Algorithms:**
  - Bubble Sort (with early exit optimization)
  - Insertion Sort
  - Merge Sort (divide and conquer)
- **Controls:**
  - Algorithm selection via sidebar buttons
  - Sort order toggle (Ascending/Descending)
  - Real-time progress bar
  - Cancel button for long operations
- **Dataset Management:** Auto-detects `.txt` files, supports dataset switching.

## How to Run

1. Ensure you have Python 3.x installed.
2. Run the application:
   ```bash
   python Alg.Sorter.py
   ```
3. Select a dataset from the dropdown (if multiple `.txt` files exist).
4. Choose Ascending or Descending order.
5. Click on an algorithm button to start sorting.

## Sample Output

After sorting, results are displayed in a formatted grid showing the sorted integers with execution time metrics.

## Requirements

- Python 3.x
- `tkinter` (included with standard Python installations)
