"""
Sorting Algorithms Module for DAA Prelim Exam
==============================================
This module provides implementations of classic sorting algorithms
optimized for sorting lists of dictionaries by a specified key.

Algorithms:
    - Bubble Sort:    O(n²) time, O(1) space, Stable
    - Insertion Sort: O(n²) time, O(1) space, Stable  
    - Merge Sort:     O(n log n) time, O(n) space, Stable
"""

import math

def bubble_sort(data, key, descending=False, progress_callback=None, cancel_event=None):
    """
    Sorts a list of dictionaries using Bubble Sort.
    
    Complexity:
        Time:  O(n²) average/worst, O(n) best (already sorted)
        Space: O(1) - sorts in-place
        Stable: Yes - equal elements maintain relative order
    
    Args:
        data (list): List of dictionaries to sort.
        key (str): The key in the dictionary to sort by.
        descending (bool): Sort in descending order if True.
        progress_callback (callable): Function to call with progress percentage (0-100).
        cancel_event (threading.Event): Event to check for cancellation.
        
    Returns:
        list: The sorted list, or None if cancelled.
    """
    # Create a copy to avoid modifying original data
    data = data[:]
    n = len(data)
    
    # Pre-fetch cancellation check for performance
    is_cancelled = cancel_event.is_set if cancel_event else (lambda: False)
    
    # Total comparisons for progress calculation: n*(n-1)/2
    total_comparisons = n * (n - 1) // 2
    comparisons_done = 0
    
    # Outer loop: each pass bubbles the largest unsorted element to the end
    for i in range(n):
        if is_cancelled():
            return None
            
        swapped = False
        comparisons_in_pass = n - i - 1
        
        # Inner loop: compare adjacent elements
        for j in range(0, comparisons_in_pass):
            val1 = data[j].get(key)
            val2 = data[j+1].get(key)
            
            # Determine if swap is needed based on sort order
            should_swap = False
            if descending:
                if val1 < val2:
                    should_swap = True
            else:
                if val1 > val2:
                    should_swap = True
                    
            if should_swap:
                # Swap adjacent elements
                data[j], data[j+1] = data[j+1], data[j]
                swapped = True
            
            # Periodic cancellation check for responsiveness
            if j % 1000 == 0 and is_cancelled():
                return None
        
        # Update progress based on work completed
        comparisons_done += comparisons_in_pass
        if progress_callback:
            p = (comparisons_done / total_comparisons) * 100
            progress_callback(min(p, 99.9))
        
        # Optimization: If no swaps occurred, array is already sorted
        if not swapped:
            break
    
    if progress_callback:
        progress_callback(100)
    return data

def insertion_sort(data, key, descending=False, progress_callback=None, cancel_event=None):
    """
    Sorts a list of dictionaries using Insertion Sort.
    
    Complexity:
        Time:  O(n²) average/worst, O(n) best (already sorted)
        Space: O(1) - sorts in-place
        Stable: Yes - equal elements maintain relative order
    
    Args:
        data (list): List of dictionaries to sort.
        key (str): The key in the dictionary to sort by.
        descending (bool): Sort in descending order if True.
        progress_callback (callable): Function to call with progress percentage (0-100).
        cancel_event (threading.Event): Event to check for cancellation.
        
    Returns:
        list: The sorted list, or None if cancelled.
    """
    # Create a copy to avoid modifying original data
    data = data[:]
    n = len(data)
    
    is_cancelled = cancel_event.is_set if cancel_event else (lambda: False)
    
    # Iterate through unsorted portion (starting at index 1)
    for i in range(1, n):
        if is_cancelled():
            return None
            
        # Store the current element to be inserted
        current_record = data[i]
        current_val = current_record.get(key)
        j = i - 1
        
        # Shift elements in sorted portion to make room for current element
        while j >= 0:
            compare_val = data[j].get(key)
            should_move = False
            
            # Compare based on sort order
            if descending:
                if compare_val < current_val:
                    should_move = True
            else:
                if compare_val > current_val:
                    should_move = True
            
            if should_move:
                # Shift element right to make space
                data[j + 1] = data[j]
                j -= 1
            else:
                break
        
        # Insert current element in its correct position
        data[j + 1] = current_record
        
        # Update progress (using quadratic mapping for accurate time representation)
        if progress_callback and i % 10 == 0:
            p = (i / n) ** 2 * 100  # Quadratic progress for O(n²) algorithms
            progress_callback(p)
    
    if progress_callback:
        progress_callback(100)
    return data

def merge_sort(data, key, descending=False, progress_callback=None, cancel_event=None):
    """
    Sorts a list of dictionaries using Merge Sort.
    
    Complexity:
        Time:  O(n log n) - all cases (best, average, worst)
        Space: O(n) - requires additional space for merging
        Stable: Yes - equal elements maintain relative order
    
    Args:
        data (list): List of dictionaries to sort.
        key (str): The key in the dictionary to sort by.
        descending (bool): Sort in descending order if True.
        progress_callback (callable): Function to call with progress percentage (0-100).
        cancel_event (threading.Event): Event to check for cancellation.
        
    Returns:
        list: The sorted list, or None if cancelled.
    """
    if len(data) <= 1:
        return data
    
    is_cancelled = cancel_event.is_set if cancel_event else (lambda: False)
    
    # Tracking state for progress calculation
    total_elements = len(data)
    total_work = total_elements * math.log2(total_elements) if total_elements > 1 else 1
    state = [0]  # Mutable container for nested function access
    
    def merge_recursive(arr):
        """Recursively divide and merge the array."""
        if is_cancelled():
            return None
            
        if len(arr) <= 1:
            return arr
            
        # Divide: Split array into two halves
        mid = len(arr) // 2
        left_half = merge_recursive(arr[:mid])
        if left_half is None:
            return None
            
        right_half = merge_recursive(arr[mid:])
        if right_half is None:
            return None
        
        # Conquer: Merge the sorted halves
        merged = []
        i = j = 0
        
        while i < len(left_half) and j < len(right_half):
            if is_cancelled():
                return None
                
            val1 = left_half[i].get(key)
            val2 = right_half[j].get(key)
            
            # Select smaller/larger element based on sort order
            pick_left = False
            if descending:
                if val1 >= val2:
                    pick_left = True
            else:
                if val1 <= val2:
                    pick_left = True
            
            if pick_left:
                merged.append(left_half[i])
                i += 1
            else:
                merged.append(right_half[j])
                j += 1
        
        # Append remaining elements
        merged.extend(left_half[i:])
        merged.extend(right_half[j:])
        
        # Update progress
        state[0] += len(arr)
        if progress_callback:
            p = (state[0] / total_work) * 100
            progress_callback(min(p, 99.9))
        
        return merged
    
    result = merge_recursive(data[:])
    if result is None:
        return None
        
    if progress_callback:
        progress_callback(100)
    return result

