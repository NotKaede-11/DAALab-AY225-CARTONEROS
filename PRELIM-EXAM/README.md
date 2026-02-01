# Sorting Algorithm Stress Test (Prelim Exam)

This project contains a comprehensive benchmarking tool for sorting algorithms, designed to test performance on large structured datasets with a modern GUI interface.

## Structure

- `data/`: Contains the `generated_data.csv` dataset (100,000 records).
- `src/`: Source code for the application.
  - `main.py`: Main GUI application with benchmarking interface.
  - `sorting_algorithms.py`: Implementation of Bubble, Insertion, and Merge Sorts with full documentation.

## Algorithms Implemented

### 1. Bubble Sort

| Property                      | Value                      |
| ----------------------------- | -------------------------- |
| **Time Complexity (Best)**    | O(n) - when already sorted |
| **Time Complexity (Average)** | O(n²)                      |
| **Time Complexity (Worst)**   | O(n²)                      |
| **Space Complexity**          | O(1) - in-place            |
| **Stable**                    | Yes                        |

**How it works:** Repeatedly steps through the list, compares adjacent elements, and swaps them if they are in the wrong order. The pass through the list is repeated until the list is sorted.

### 2. Insertion Sort

| Property                      | Value                      |
| ----------------------------- | -------------------------- |
| **Time Complexity (Best)**    | O(n) - when already sorted |
| **Time Complexity (Average)** | O(n²)                      |
| **Time Complexity (Worst)**   | O(n²)                      |
| **Space Complexity**          | O(1) - in-place            |
| **Stable**                    | Yes                        |

**How it works:** Builds the final sorted array one item at a time. It picks elements from the unsorted portion and inserts them into their correct position in the sorted portion.

### 3. Merge Sort

| Property                      | Value                           |
| ----------------------------- | ------------------------------- |
| **Time Complexity (Best)**    | O(n log n)                      |
| **Time Complexity (Average)** | O(n log n)                      |
| **Time Complexity (Worst)**   | O(n log n)                      |
| **Space Complexity**          | O(n) - requires auxiliary space |
| **Stable**                    | Yes                             |

**How it works:** Divide-and-conquer algorithm that divides the input array into two halves, recursively sorts them, and then merges the two sorted halves.

## How to Run

1. Navigate to the `src` directory:
   ```bash
   cd src
   ```
2. Run the application:
   ```bash
   python main.py
   ```
3. Use the GUI to select the sorting algorithm, sort key, and dataset size.

## Features

- **Data Validation:** Validates CSV schema before processing.
- **Progress Tracking:** Real-time progress bar during sorting operations.
- **Cancellation Support:** Stop long-running sorts at any time.
- **Data Preview:** View first 5 records before sorting.
- **Performance Metrics:** Precise timing measurements in seconds.

## Benchmark Results

_Sample results from testing (your results may vary based on hardware):_

| Algorithm          | N = 1,000 | N = 10,000 | N = 100,000   |
| ------------------ | --------- | ---------- | ------------- |
| **Bubble Sort**    | ~0.05s    | ~5s        | ~500s+ (est.) |
| **Insertion Sort** | ~0.03s    | ~3s        | ~300s+ (est.) |
| **Merge Sort**     | ~0.005s   | ~0.06s     | ~0.8s         |

### Observations

- **Bubble Sort & Insertion Sort**: Perform acceptably on small datasets (N ≤ 1,000), but execution time grows quadratically. At N = 10,000, noticeable delays occur. At N = 100,000, these algorithms become impractical.
- **Merge Sort**: Maintains consistent O(n log n) performance across all dataset sizes. Even at N = 100,000, completes in under a second, demonstrating the importance of algorithm selection for large-scale data processing.

- **Stability**: All three algorithms are stable, meaning equal elements maintain their relative order after sorting—important for multi-key sorting scenarios.

## Requirements

- Python 3.x
- Tkinter (included with standard Python installations)
