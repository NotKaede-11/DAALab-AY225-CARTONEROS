# Sorting Algorithm Stress Test (Prelim Exam)

This project contains a comprehensive benchmarking tool for sorting algorithms, designed to test performance on large structured datasets.

## Structure

- `data/`: Contains the `generated_data.csv` dataset (100,000 records).
- `src/`: Source code for the application.
  - `app.py`: Main CLI application runner.
  - `sorting_algorithms.py`: Implementation of Bubble, Insertion, and Merge Sorts.

## Algorithms Implemented

1. **Bubble Sort** - O(n²)
2. **Insertion Sort** - O(n²)
3. **Merge Sort** - O(n log n)

## How to Run

1. Navigate to the `src` directory:
   ```bash
   cd src
   ```
2. Run the application:
   ```bash
   python app.py
   ```
3. Follow the on-screen menu to select the sorting column, algorithm, and dataset size.

## Benchmark Results

_Run the application to populate this table with your machine's performance metrics._

| Algorithm          | N = 1,000 (Time) | N = 10,000 (Time) | N = 100,000 (Time) |
| ------------------ | ---------------- | ----------------- | ------------------ |
| **Bubble Sort**    | TBD              | TBD               | TBD                |
| **Insertion Sort** | TBD              | TBD               | TBD                |
| **Merge Sort**     | TBD              | TBD               | TBD                |

### Observations

- **Bubble Sort & Insertion Sort**: Expected to perform well on small N, but execution time will grow exponentially as N increases.
- **Merge Sort**: Expected to maintain efficient performance even at N=100,000 due to its logarithmic complexity.

## Requirements

- Python 3.x
