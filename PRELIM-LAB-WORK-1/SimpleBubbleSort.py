import time
import os

def load_dataset(filepath):
    """Reads integers from a file."""
    try:
        with open(filepath, 'r') as f:
            # Read all lines, strip whitespace, and convert to int
            # Filters out empty lines
            data = [int(line.strip()) for line in f if line.strip()]
        return data
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return []
    except ValueError:
        print(f"Error: File '{filepath}' contains non-integer values.")
        return []

def bubble_sort(arr):
    """
    Sorts a list of integers using the optimized Bubble Sort algorithm.
    Returns the sorted list.
    """
    n = len(arr)
    # Traverse through all array elements
    for i in range(n):
        swapped = False

        # Last i elements are already in place
        for j in range(0, n - i - 1):
            # Traverse the array from 0 to n-i-1
            # Swap if the element found is greater than the next element
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True

        # If no two elements were swapped by inner loop, then break
        if not swapped:
            break
    
    return arr

def print_organized(arr, items_per_line=10):
    """
    Prints the array in an organized grid format.
    """
    print(f"\n{'='*20} SORTED DATA {'='*20}\n")
    
    # Calculate padding for consistently aligned columns
    if not arr:
        print("No data.")
        return

    # Find max width for padding
    max_val = max(arr)
    min_val = min(arr)
    # Length of string representation of largest/smallest number
    max_width = max(len(str(max_val)), len(str(min_val))) + 2 
    
    for i, num in enumerate(arr):
        # Print number with padding
        print(f"{num:>{max_width}}", end="")
        
        # Newline after every 'items_per_line' elements
        if (i + 1) % items_per_line == 0:
            print()
    
    # Final newline if the list didn't end exactly at the line break
    if len(arr) % items_per_line != 0:
        print()
    
    print(f"\n{'='*53}\n")

if __name__ == "__main__":
    # Determine the path to dataset.txt relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Auto-detect any .txt file in the directory
    txt_files = [f for f in os.listdir(script_dir) if f.lower().endswith('.txt')]

    if not txt_files:
        print("No .txt file found in the script directory.")
        data = []
    else:
        file_path = os.path.join(script_dir, txt_files[0])
        print(f"Found dataset file: {txt_files[0]}")
        data = load_dataset(file_path)

    if data:
        print(f"Dataset loaded. {len(data)} integers found.")
        print("Starting Bubble Sort...")

        start_time = time.time()
        sorted_data = bubble_sort(data)
        end_time = time.time()

        elapsed_time = end_time - start_time
        
        print_organized(sorted_data)
        print(f"Execution Time: {elapsed_time:.4f} seconds ({elapsed_time*1000:.2f} ms)")
