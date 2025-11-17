# utils.py
import random

def generate_page_sequence(length=10, max_page=5):
    return [random.randint(0, max_page) for _ in range(length)]

def repetition_ratio(seq):
    if len(seq) == 0:
        return 0.0
    unique = len(set(seq))
    return round(1 - unique / len(seq), 2)

def unique_count(seq):
    return len(set(seq))

def hit_ratio(faults, total):
    if total == 0:
        return 0.0
    return round((1 - faults / total) * 100, 2)
