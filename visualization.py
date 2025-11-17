# visualization.py
import streamlit as st
import pandas as pd
import plotly.express as px
import time

def visualize_steps(history, frames):
    st.markdown("### Step-by-Step Visualization")
    progress = st.progress(0.0)
    total = len(history)

    for i, h in enumerate(history):
        cols = st.columns(frames)
        mem_state = h["Frames"]
        for j in range(frames):
            color = "#a3e635" if j < len(mem_state) else "#e5e7eb"
            box = mem_state[j] if j < len(mem_state) else ""
            cols[j].markdown(
                f"<div style='background-color:{color};padding:15px;text-align:center;"
                f"border-radius:10px;font-size:20px;border:1px solid #333'>{box}</div>",
                unsafe_allow_html=True,
            )
        fault_color = "red" if h["Page Fault"] == 1 else "green"
        st.markdown(f"<b style='color:{fault_color}'>Step {h['Step']} | Page: {h['Page']} | Page Fault: {h['Page Fault']}</b>", unsafe_allow_html=True)
        progress.progress((i + 1) / total)
        time.sleep(0.18)

def plot_faults_graph(history, title):
    df_hist = pd.DataFrame(history)
    fig2 = px.line(
        df_hist,
        x="Step",
        y="Page Fault",
        title=title,
        markers=True,
    )
    fig2.update_layout(yaxis=dict(tickvals=[0, 1], ticktext=["Hit", "Fault"]))
    st.plotly_chart(fig2, use_container_width=True)

def plot_summary_bar(results_df):
    fig = px.bar(
        results_df,
        x="Algorithm",
        y="Page Faults",
        color="Algorithm",
        text="Page Faults",
        title="Total Page Faults by Algorithm",
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)
