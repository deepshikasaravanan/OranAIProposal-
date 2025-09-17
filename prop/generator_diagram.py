import os
from typing import List, Tuple
import matplotlib
# Use a non-interactive backend suitable for servers/CI
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

def render_flowchart(steps: List[Tuple[str,str]], out_path: str):
    G = nx.DiGraph()
    for a,b in steps:
        G.add_edge(a,b)
    try:
        from networkx.drawing.nx_agraph import graphviz_layout
        pos = graphviz_layout(G, prog="dot")
    except Exception:
        pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, node_size=2000, node_shape="o", arrows=True)
    plt.tight_layout()
    d = os.path.dirname(out_path)
    if d:
        os.makedirs(d, exist_ok=True)
    plt.savefig(out_path, dpi=200)
    plt.close()

def render_gantt(tasks: List[Tuple[str, int, int]], out_path: str):
    labels = [t[0] for t in tasks]
    starts = [t[1] for t in tasks]
    durations = [t[2] for t in tasks]
    yticks = range(len(labels))
    plt.figure(figsize=(10, 4))
    for i,(s,d) in enumerate(zip(starts, durations)):
        plt.barh(i, d, left=s)
    plt.yticks(list(yticks), labels)
    plt.xlabel("Days")
    plt.tight_layout()
    d = os.path.dirname(out_path)
    if d:
        os.makedirs(d, exist_ok=True)
    plt.savefig(out_path, dpi=200)
    plt.close()
