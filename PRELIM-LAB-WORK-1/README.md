# Simple Bubble Sort (Console Application)

A command-line implementation of the Bubble Sort algorithm with performance benchmarking.

## Algorithm Analysis: Bubble Sort

### How It Works

Bubble Sort is a simple comparison-based sorting algorithm that repeatedly steps through the list, compares adjacent elements, and swaps them if they are in the wrong order. The algorithm gets its name because smaller elements "bubble" to the top of the list.

```
Pass 1: [5, 3, 8, 1] → [3, 5, 1, 8]  (largest element bubbles to end)
Pass 2: [3, 5, 1, 8] → [3, 1, 5, 8]
Pass 3: [3, 1, 5, 8] → [1, 3, 5, 8]  (sorted!)
```

### Complexity Analysis

| Case        | Time Complexity | When It Occurs                                         |
| ----------- | --------------- | ------------------------------------------------------ |
| **Best**    | O(n)            | Array is already sorted (with early exit optimization) |
| **Average** | O(n²)           | Random order                                           |
| **Worst**   | O(n²)           | Array is reverse sorted                                |

| Property             | Value                                    |
| -------------------- | ---------------------------------------- |
| **Space Complexity** | O(1) - sorts in-place                    |
| **Stable**           | Yes - equal elements keep relative order |
| **Adaptive**         | Yes - faster on nearly sorted data       |

### Optimization Implemented

This implementation includes an **early exit optimization**: if no swaps occur during a pass, the array is already sorted and the algorithm terminates early. This improves best-case performance from O(n²) to O(n).

## Features

- Optimized Bubble Sort with early exit when sorted.
- Auto-detects any `.txt` file in the same folder.
- Formatted grid output (10 numbers per row).
- Execution time displayed in seconds and milliseconds.

## How to Run

1. Ensure you have Python 3.x installed.
2. Place a `.txt` file with integers (one per line) in the same folder (e.g., `dataset.txt`).
3. Run the script:
   ```bash
   python SimpleBubbleSort.py
   ```

## Sample Output

```
Dataset loaded: 1000 integers

Sorting... Done!

Execution Time: 0.0423 seconds (42.3 ms)

Sorted Data (First 50):
┌──────────────────────────────────────────────────┐
│   1    2    3    4    5    6    7    8    9   10 │
│  11   12   13   14   15   16   17   18   19   20 │
│ ...                                              │
└──────────────────────────────────────────────────┘
```

## Requirements

- Python 3.x
- No external packages required.
