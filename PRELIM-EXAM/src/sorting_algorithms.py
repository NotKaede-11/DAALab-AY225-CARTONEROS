def bubble_sort(data, key, descending=False):
    """
    Sorts a list of dictionaries in-place using Bubble Sort.
    
    Args:
        data (list): List of dictionaries to sort.
        key (str): The key in the dictionary to sort by.
        descending (bool): Sort in descending order if True.
    """
    n = len(data)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            val1 = data[j].get(key)
            val2 = data[j+1].get(key)
            
            should_swap = False
            if descending:
                if val1 < val2:
                    should_swap = True
            else:
                if val1 > val2:
                    should_swap = True
                    
            if should_swap:
                data[j], data[j+1] = data[j+1], data[j]
                swapped = True
        
        # Optimization: If no two elements were swapped by inner loop, then break
        if not swapped:
            break
    return data

def insertion_sort(data, key, descending=False):
    """
    Sorts a list of dictionaries in-place using Insertion Sort.
    
    Args:
        data (list): List of dictionaries to sort.
        key (str): The key in the dictionary to sort by.
        descending (bool): Sort in descending order if True.
    """
    for i in range(1, len(data)):
        current_record = data[i]
        current_val = current_record.get(key)
        j = i - 1
        
        while j >= 0:
            compare_val = data[j].get(key)
            should_move = False
            
            if descending:
                if compare_val < current_val:
                    should_move = True
            else:
                if compare_val > current_val:
                    should_move = True
            
            if should_move:
                data[j + 1] = data[j]
                j -= 1
            else:
                break
        
        data[j + 1] = current_record
    return data

def merge_sort(data, key, descending=False):
    """
    Sorts a list of dictionaries using Merge Sort.
    Note: Merge Sort is typically not in-place. This implementation returns a new sorted list.
    
    Args:
        data (list): List of dictionaries to sort.
        key (str): The key in the dictionary to sort by.
        descending (bool): Sort in descending order if True.
    """
    if len(data) <= 1:
        return data

    mid = len(data) // 2
    left_half = merge_sort(data[:mid], key, descending)
    right_half = merge_sort(data[mid:], key, descending)

    return _merge(left_half, right_half, key, descending)

def _merge(left, right, key, descending):
    sorted_list = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        val1 = left[i].get(key)
        val2 = right[j].get(key)
        
        pick_left = False
        if descending:
            if val1 >= val2:
                pick_left = True
        else:
            if val1 <= val2:
                pick_left = True
                
        if pick_left:
            sorted_list.append(left[i])
            i += 1
        else:
            sorted_list.append(right[j])
            j += 1
            
    # Append remaining elements
    sorted_list.extend(left[i:])
    sorted_list.extend(right[j:])
    
    return sorted_list
