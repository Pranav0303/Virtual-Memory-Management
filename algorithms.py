
# algorithms.py
def fifo(pages, frames):
    memory, faults = [], 0
    history = []
    for step, p in enumerate(pages):
        page_fault = 0
        if p not in memory:
            page_fault = 1
            faults += 1
            if len(memory) < frames:
                memory.append(p)
            else:
                memory.pop(0)
                memory.append(p)
        history.append({"Step": step + 1, "Page": p, "Frames": memory.copy(), "Page Fault": page_fault})
    return faults, history

def lru(pages, frames):
    memory, faults = [], 0
    history = []
    recent = {}
    for step, p in enumerate(pages):
        page_fault = 0
        if p not in memory:
            page_fault = 1
            faults += 1
            if len(memory) < frames:
                memory.append(p)
            else:
                candidates = {pg: recent.get(pg, -1) for pg in memory}
                lru_page = min(candidates, key=candidates.get)
                memory[memory.index(lru_page)] = p
        recent[p] = step
        history.append({"Step": step + 1, "Page": p, "Frames": memory.copy(), "Page Fault": page_fault})
    return faults, history

def mru(pages, frames):
    memory, faults = [], 0
    history = []
    recent = {}
    for step, p in enumerate(pages):
        page_fault = 0
        if p not in memory:
            page_fault = 1
            faults += 1
            if len(memory) < frames:
                memory.append(p)
            else:
                candidates = {pg: recent.get(pg, -1) for pg in memory}
                if any(v >= 0 for v in candidates.values()):
                    mru_page = max(candidates, key=candidates.get)
                    memory[memory.index(mru_page)] = p
                else:
                    memory.pop(0)
                    memory.append(p)
        recent[p] = step
        history.append({"Step": step + 1, "Page": p, "Frames": memory.copy(), "Page Fault": page_fault})
    return faults, history
