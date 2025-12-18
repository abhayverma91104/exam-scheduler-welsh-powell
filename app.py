import streamlit as st
import pandas as pd
import random
import networkx as nx
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Graph Coloring Scheduler (Welsh-Powell)", layout="wide")

def welsh_powell(adj):
    vertices = set(adj.keys())
    for v, neigh in adj.items():
        for u in neigh:
            vertices.add(u)

    full = {v: set() for v in vertices}
    for v, neigh in adj.items():
        for u in neigh:
            full[v].add(u)
            full[u].add(v)

    order = sorted(full.keys(), key=lambda x: (-len(full[x]), str(x)))

    color = {}
    current_color = 1

    for v in order:
        if v not in color:
            color[v] = current_color
            for u in order:
                if u not in color:
                    if all((nbr not in color or color[nbr] != current_color) for nbr in full[u]):
                        if v != u:
                            color[u] = current_color
            current_color += 1

    return color


def synthetic_enrollments(exams, num_students, seed=42):
    random.seed(seed)
    enroll = {}
    for i in range(1, num_students + 1):
        k = random.choices([1, 2, 3], weights=[0.65, 0.30, 0.05])[0]
        enroll[f"S{i}"] = random.sample(exams, min(k, len(exams)))
    return enroll


def build_conflicts_from_enrollments(enrollments):
    exams = sorted({e for courses in enrollments.values() for e in courses})
    conflicts = {e: set() for e in exams}

    for student, courses in enrollments.items():
        for i in range(len(courses)):
            for j in range(i + 1, len(courses)):
                a, b = courses[i], courses[j]
                conflicts[a].add(b)
                conflicts[b].add(a)

    return conflicts


def build_conflicts_from_csv_df(df):
    if df.empty:
        return {}
    df = df.dropna(subset=["student_id", "exam"])
    enroll = {}
    for sid, group in df.groupby("student_id"):
        enroll[sid] = list(group["exam"].unique())

    return build_conflicts_from_enrollments(enroll)


def draw_conflict_graph(conflicts, coloring=None):
    G = nx.Graph()
    for n in conflicts:
        G.add_node(n)
    for a, neigh in conflicts.items():
        for b in neigh:
            G.add_edge(a, b)

    pos = nx.spring_layout(G, seed=1)
    fig, ax = plt.subplots(figsize=(8, 6))

    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.4)

    node_colors = None
    if coloring:
        maxc = max(coloring.values())
        palette = plt.cm.get_cmap("tab20", maxc)
        node_colors = [palette(coloring[n] - 1) for n in G.nodes()]

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=900, ax=ax)
    labels = {n: f"{n}\n(C{coloring[n]})" for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=9, ax=ax)

    ax.set_title("Conflict Graph")
    ax.axis("off")
    st.pyplot(fig)


def schedule_from_coloring(coloring, slot_start_hour=9, slot_duration=2):
    rows = []
    for exam, c in sorted(coloring.items(), key=lambda x: (x[1], x[0])):
        start = slot_start_hour + (c - 1) * slot_duration
        rows.append({
            "Exam": exam,
            "Slot": c,
            "start": start,
            "duration": slot_duration,
            "TimeLabel": f"Slot {c} ({start:02d}:00 - {start + slot_duration:02d}:00)"
        })
    return pd.DataFrame(rows)


def gantt_plot(df):
    if df.empty:
        st.write("No schedule.")
        return

    fig, ax = plt.subplots(figsize=(10, max(4, 0.5 * len(df))))
    y = list(range(len(df)))
    ax.barh(y, df["duration"], left=df["start"], height=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(df["Exam"] + " — " + df["TimeLabel"])
    ax.invert_yaxis()
    ax.set_xlabel("Hour of day")
    st.pyplot(fig)


def schedule_csv_bytes(df):
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


st.title("Graph Coloring Scheduler — Correct Welsh-Powell Implementation")

tab1, tab2, tab3 = st.tabs(["A — Synthetic", "B — CSV Upload", "C — Manual"])

with tab1:
    exams_input = st.text_area("Exams", value="Math,Physics,Chemistry,Biology,CS,Economics,History,English")
    num_students = st.number_input("Students", 1, 5000, 200)
    seed = st.number_input("Random Seed", 0, 999999, 42)
    slot_hour = st.number_input("Start Hour", 0, 23, 9)
    slot_dur = st.number_input("Slot Duration", 1, 8, 2)

    if st.button("Generate synthetic schedule"):
        exams = [e.strip() for e in exams_input.split(",") if e.strip()]
        enroll = synthetic_enrollments(exams, num_students, seed)
        conflicts = build_conflicts_from_enrollments(enroll)
        coloring = welsh_powell(conflicts)

        draw_conflict_graph(conflicts, coloring)
        df = schedule_from_coloring(coloring, slot_hour, slot_dur)
        st.dataframe(df)
        gantt_plot(df)
        st.download_button("Download CSV", schedule_csv_bytes(df), "synthetic_schedule.csv")

with tab2:
    uploaded = st.file_uploader("Upload CSV (student_id, exam)", type=["csv"])
    slot_hour2 = st.number_input("Start Hour — CSV", 0, 23, 9)
    slot_dur2 = st.number_input("Duration — CSV", 1, 8, 2)

    if uploaded:
        df_csv = pd.read_csv(uploaded)
        conflicts = build_conflicts_from_csv_df(df_csv)
        coloring = welsh_powell(conflicts)

        draw_conflict_graph(conflicts, coloring)
        df = schedule_from_coloring(coloring, slot_hour2, slot_dur2)
        st.dataframe(df)
        gantt_plot(df)
        st.download_button("Download CSV", schedule_csv_bytes(df), "uploaded_schedule.csv")

with tab3:
    if "manual_exams" not in st.session_state:
        st.session_state.manual_exams = ["Math", "Physics", "Chemistry"]
    if "manual_edges" not in st.session_state:
        st.session_state.manual_edges = set()

    new_exam = st.text_input("Add exam")
    if st.button("Add"):
        if new_exam and new_exam not in st.session_state.manual_exams:
            st.session_state.manual_exams.append(new_exam)

    st.write("Exams:", st.session_state.manual_exams)

    ex1 = st.selectbox("Exam A", st.session_state.manual_exams)
    ex2 = st.selectbox("Exam B", st.session_state.manual_exams)
    if st.button("Add conflict"):
        if ex1 != ex2:
            st.session_state.manual_edges.add(tuple(sorted([ex1, ex2])))

    if st.button("Clear edges"):
        st.session_state.manual_edges = set()

    if st.button("Run manually"):
        exams = st.session_state.manual_exams
        conflicts = {e: set() for e in exams}
        for a, b in st.session_state.manual_edges:
            conflicts[a].add(b)
            conflicts[b].add(a)

        coloring = welsh_powell(conflicts)
        draw_conflict_graph(conflicts, coloring)

        slot_hour3 = st.number_input("Start Hour — Manual", 0, 23, 9)
        slot_dur3 = st.number_input("Duration — Manual", 1, 8, 2)

        df = schedule_from_coloring(coloring, slot_hour3, slot_dur3)
        st.dataframe(df)
        gantt_plot(df)
        st.download_button("Download CSV", schedule_csv_bytes(df), "manual_schedule.csv")
