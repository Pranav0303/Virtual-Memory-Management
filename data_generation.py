# data_generation.py
import random
import pandas as pd

from algorithms import fifo, lru, mru

def extract_features_for_step(seq, frames, step, memory):
    page = seq[step]
    past = seq[:step]
    future = seq[step+1:]
    recency = 0
    if page in past:
        last_idx = max(i for i, x in enumerate(past) if x == page)
        recency = step - last_idx
    freq_future = future.count(page)
    in_memory = 1 if page in memory else 0
    return [page, len(seq), frames, in_memory, recency, freq_future]

def generate_training_data(samples=500, rng_seed=42):
    rnd = random.Random(rng_seed)
    data = []
    for _ in range(samples):
        frames = rnd.randint(2, 6)
        seq_len = rnd.randint(5, 20)
        max_page = rnd.randint(3, 10)
        seq = [rnd.randint(0, max_page) for _ in range(seq_len)]

        for algo_func, algo_name in [(fifo, "FIFO"), (lru, "LRU"), (mru, "MRU")]:
            mem = []
            recent = {}
            for step, page in enumerate(seq):
                features = extract_features_for_step(seq, frames, step, mem)
                page_fault = 0
                if page not in mem:
                    page_fault = 1
                    if len(mem) < frames:
                        mem.append(page)
                    else:
                        if algo_name == "FIFO":
                            mem.pop(0)
                            mem.append(page)
                        elif algo_name == "LRU":
                            candidates = {pg: recent.get(pg, -1) for pg in mem}
                            if any(v >= 0 for v in candidates.values()):
                                lru_page = min(candidates, key=candidates.get)
                                mem[mem.index(lru_page)] = page
                            else:
                                mem.pop(0)
                                mem.append(page)
                        elif algo_name == "MRU":
                            candidates = {pg: recent.get(pg, -1) for pg in mem}
                            if any(v >= 0 for v in candidates.values()):
                                mru_page = max(candidates, key=candidates.get)
                                mem[mem.index(mru_page)] = page
                            else:
                                mem.pop(0)
                                mem.append(page)
                recent[page] = step
                data.append(features + [algo_name, page_fault])

    df = pd.DataFrame(data, columns=["Page", "SeqLen", "Frames", "InMemory", "Recency", "FutureFreq", "Algorithm", "PageFault"])
    return df
