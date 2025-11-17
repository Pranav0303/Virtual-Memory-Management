# app.py
import streamlit as st
from utils import generate_page_sequence, hit_ratio
from algorithms import fifo, lru, mru
from ml_model import train_multi_algo_model
from data_generation import extract_features_for_step
from visualization import visualize_steps, plot_faults_graph, plot_summary_bar
import pandas as pd

st.set_page_config(page_title="Virtual Memory ML Visualizer", layout="wide")
st.title("Virtual Memory Page Fault Predictor (FIFO + LRU + MRU)")

# --- Sidebar Config ---
st.sidebar.header("Configuration")
frames = st.sidebar.slider("Number of Frames", 2, 7, 3)
seq_len = st.sidebar.slider("Sequence Length", 5, 25, 10)
max_page = st.sidebar.slider("Max Page Number", 3, 12, 5)

# --- Sequence Generation ---
col1, col2 = st.columns(2)
with col1:
    if st.button("Generate Random Sequence"):
        seq = generate_page_sequence(seq_len, max_page)
        st.session_state["seq"] = seq
with col2:
    manual = st.text_input("Enter custom sequence (comma separated):")
    if st.button("Use Custom Sequence"):
        try:
            seq = [int(x.strip()) for x in manual.split(",") if x.strip() != ""]
            if len(seq) == 0:
                st.error("Sequence cannot be empty")
            else:
                st.session_state["seq"] = seq
        except Exception:
            st.error("Invalid sequence input")

if "seq" in st.session_state:
    seq = st.session_state["seq"]
    st.success(f"Current Sequence: {seq}")
else:
    st.info("No sequence generated yet.")

# --- ML Model ---
st.sidebar.markdown("---")
st.sidebar.write("### ML Model (Multi-Algorithm Fault Predictor)")
if "multi_model" not in st.session_state:
    st.session_state["multi_model"] = None
    st.session_state["multi_acc"] = None

if st.sidebar.button("Train / Retrain ML Model"):
    with st.spinner("Training page fault predictor (FIFO + LRU + MRU)..."):
        model, acc = train_multi_algo_model()
        st.session_state["multi_model"] = model
        st.session_state["multi_acc"] = acc
        st.sidebar.success(f"Trained successfully (Accuracy: {acc*100:.1f}%)")

if st.session_state["multi_model"] is not None:
    st.sidebar.info(f"Model Accuracy: {st.session_state['multi_acc']*100:.1f}%")

# --- ML Prediction Section ---
if "seq" in st.session_state and st.session_state["multi_model"] is not None:
    model = st.session_state["multi_model"]
    algos = ["FIFO", "LRU", "MRU"]
    st.markdown("###  ML Predicted Page Faults for Each Algorithm")
    for algo in algos:
        st.markdown(f"#### {algo}")
        memory = []
        recent = {}
        preds = []
        for step in range(len(seq)):
            features = extract_features_for_step(seq, frames, step, memory)
            feat_df = pd.DataFrame([features + [algo]], columns=["Page","SeqLen","Frames","InMemory","Recency","FutureFreq","Algorithm"])
            feat_df = pd.get_dummies(feat_df)
            for col in model.feature_names_in_:
                if col not in feat_df.columns:
                    feat_df[col] = 0
            feat_df = feat_df[model.feature_names_in_]
            y_pred = model.predict(feat_df)[0]
            preds.append(y_pred)
            # Memory update
            if seq[step] not in memory:
                if len(memory) < frames:
                    memory.append(seq[step])
                else:
                    if algo == "FIFO":
                        memory.pop(0)
                        memory.append(seq[step])
                    elif algo == "LRU":
                        candidates = {pg: recent.get(pg, -1) for pg in memory}
                        if any(v >= 0 for v in candidates.values()):
                            lru_page = min(candidates, key=candidates.get)
                            memory[memory.index(lru_page)] = seq[step]
                        else:
                            memory.pop(0)
                            memory.append(seq[step])
                    elif algo == "MRU":
                        candidates = {pg: recent.get(pg, -1) for pg in memory}
                        if any(v >= 0 for v in candidates.values()):
                            mru_page = max(candidates, key=candidates.get)
                            memory[memory.index(mru_page)] = seq[step]
                        else:
                            memory.pop(0)
                            memory.append(seq[step])
            recent[seq[step]] = step
        readable = [f"{p}→{'Fault' if preds[i]==1 else 'Hit'}" for i,p in enumerate(seq)]
        st.write(readable)

# --- Simulation + Graphs ---
if st.button("Run Simulation (All Algorithms)"):
    if "seq" not in st.session_state:
        st.error("Generate or input a sequence first.")
    else:
        seq = st.session_state["seq"]
        results = []
        for func, name in [(fifo, "FIFO"), (lru, "LRU"), (mru, "MRU")]:
            faults, hist = func(seq, frames)
            st.subheader(f"{name} Simulation Result")
            st.metric("Total Page Faults", faults)
            st.metric("Hit Ratio (%)", hit_ratio(faults, len(seq)))

            visualize_steps(hist, frames)
            plot_faults_graph(hist, f"{name} - Step-wise Page Fault Timeline")

            results.append({"Algorithm": name, "Page Faults": faults, "Hit Ratio (%)": hit_ratio(faults, len(seq))})

        plot_summary_bar(pd.DataFrame(results))
