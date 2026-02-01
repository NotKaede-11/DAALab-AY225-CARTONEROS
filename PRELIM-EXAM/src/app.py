import os
import time
import csv
import sys

# Add the current directory to sys.path to ensure local imports work if run from different locations
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sorting_algorithms

DATA_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'generated_data.csv')

def load_data(filepath, limit=None):
    """Loads data from CSV file."""
    data = []
    try:
        start_time = time.perf_counter()
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # The CSV has headers: ID, FirstName, LastName
            # We need to ensure ID is treated as int for proper sorting
            for row in reader:
                try:
                    row['ID'] = int(row['ID'])
                except ValueError:
                    pass # Keep as string if not int (though specs say ID is int)
                data.append(row)
                if limit and len(data) >= limit:
                    break
        end_time = time.perf_counter()
        return data, (end_time - start_time)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return [], 0
    except Exception as e:
        print(f"Error loading file: {e}")
        return [], 0

def print_header(title):
    print(f"\n{'='*20} {title} {'='*20}")

def print_results(data, execution_time):
    print(f"\n{'-'*60}")
    print(f"{'ID':<15} {'FirstName':<20} {'LastName':<20}")
    print(f"{'-'*60}")
    
    # Print first 10 records
    for i, row in enumerate(data[:10]):
        print(f"{row['ID']:<15} {row['FirstName']:<20} {row['LastName']:<20}")
        
    print(f"{'-'*60}")
    print(f"Total Execution Time: {execution_time:.6f} seconds")
    print(f"Total Records Displayed: {min(len(data), 10)} of {len(data)}")
    print(f"{'-'*60}\n")

def get_user_choice(prompt, valid_options):
    while True:
        try:
            choice = input(prompt).strip()
            if choice in valid_options:
                return choice
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input.")

def main():
    print_header("SORTING ALGORITHM STRESS TEST (PRELIM EXAM)")
    
    # Load all data first or load on demand? 
    # The requirement says "Performance Tracking: Measure the time taken to load the file vs. the time taken to sort."
    # So we should probably load it per run to demonstrate the difference if N changes, 
    # or load all once and slice it. Loading 100k isn't too heavy.
    # Let's load all once to check validity, but for the benchmark we might reload or slice.
    # Actually, slicing a list is very fast (O(k)) compared to I/O. 
    # For accurate "load time" benchmarking for specific N, we should probably simulate loading or just measure the list slice time which is negligible,
    # OR honestly just measure the load of the full file as "Load Time" and then sort N rows.
    
    print("Loading dataset...")
    full_data, load_time = load_data(DATA_FILE_PATH)
    if not full_data:
        print("Failed to load data. Exiting.")
        return
        
    print(f"Dataset loaded successfully. {len(full_data)} records found.")
    print(f"Load Time: {load_time:.6f} seconds")
    
    while True:
        print_header("MAIN MENU")
        print("1. Sort by ID")
        print("2. Sort by FirstName")
        print("3. Sort by LastName")
        print("4. Exit")
        
        choice = get_user_choice("Enter choice (1-4): ", ['1', '2', '3', '4'])
        
        if choice == '4':
            print("Exiting...")
            break
            
        sort_key_map = {'1': 'ID', '2': 'FirstName', '3': 'LastName'}
        sort_key = sort_key_map[choice]
        
        print_header("SELECT ALGORITHM")
        print("1. Bubble Sort")
        print("2. Insertion Sort")
        print("3. Merge Sort")
        
        algo_choice = get_user_choice("Enter choice (1-3): ", ['1', '2', '3'])
        
        print_header("SELECT N (Number of rows)")
        print("1. 1,000")
        print("2. 10,000")
        print("3. 100,000")
        print("4. Custom")
        
        n_choice = get_user_choice("Enter choice (1-4): ", ['1', '2', '3', '4'])
        
        if n_choice == '1':
            n = 1000
        elif n_choice == '2':
            n = 10000
        elif n_choice == '3':
            n = 100000
        else:
            while True:
                try:
                    custom_n = int(input("Enter custom N: "))
                    if 0 < custom_n <= len(full_data):
                        n = custom_n
                        break
                    print(f"Please enter a value between 1 and {len(full_data)}.")
                except ValueError:
                    print("Invalid integer.")
        
        # Slicing the data for the test
        test_data = full_data[:n]
        
        # Copy data to avoid sorting the original list reference if we were to loop (though we reload slice each time)
        # Deep copy is safer if mutable objects, but here we have dicts. Shallow copy of list of dicts is fine if we don't mutate dict content.
        # But sorting algorithms might move items.
        # Bubble/Insertion allow in-place. Merge returns new.
        # To be safe for repeated tests, we use a fresh slice.
        current_data = list(test_data) 
        
        print(f"\nSelected: Sort by {sort_key}, N={n}")
        
        # Warning for O(n^2)
        if n > 10000 and algo_choice in ['1', '2']:
            print("\n" + "!"*60)
            print("WARNING: You selected an O(n^2) algorithm for a large dataset.")
            print("This computation may take a significant amount of time.")
            print("!"*60 + "\n")
            confirm = get_user_choice("Do you want to proceed? (y/n): ", ['y', 'n', 'Y', 'N'])
            if confirm.lower() == 'n':
                continue
        
        print("\nSorting... Please wait.")
        start_sort = time.perf_counter()
        
        if algo_choice == '1':
            sorted_data = sorting_algorithms.bubble_sort(current_data, sort_key)
        elif algo_choice == '2':
            sorted_data = sorting_algorithms.insertion_sort(current_data, sort_key)
        elif algo_choice == '3':
            sorted_data = sorting_algorithms.merge_sort(current_data, sort_key)
            
        end_sort = time.perf_counter()
        sort_time = end_sort - start_sort
        
        print_header("RESULTS")
        print_results(sorted_data, sort_time)
        input("Press Enter to continue...")

if __name__ == "__main__":
    main()
