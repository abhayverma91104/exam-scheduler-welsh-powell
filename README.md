# 🎓 Graph Coloring Exam Scheduler

A powerful, interactive web application built with **Streamlit** that solves the "Exam Scheduling Problem" using graph theory. The app ensures that no student has two exams scheduled at the same time by utilizing the **Welsh-Powell Algorithm**.

## 🚀 Key Features

* **Automated Scheduling:** Converts complex student enrollment data into a conflict-free timetable.
* **Welsh-Powell Implementation:** Uses a degree-based heuristic to minimize the number of time slots required.
* **Interactive Visualizations:** * **Conflict Graph:** See how exams relate to one another (Colors = Slots).
    * **Gantt Chart:** A clear timeline of the generated schedule.
* **Multiple Input Modes:** * **Synthetic:** Generate test data to see the algorithm in action.
    * **CSV Upload:** Process real-world enrollment lists.
    * **Manual:** Build a custom graph node-by-node.
* **Data Export:** Download your final schedule as a CSV.

---

## 🧠 How It Works: The Welsh-Powell Algorithm

The app treats each **Exam** as a node in a graph. An **Edge** (connection) is created between two exams if at least one student is enrolled in both. The goal is to "color" the nodes so that no two connected nodes share the same color.


1.  **Degree Calculation:** The app counts how many conflicts each exam has.
2.  **Sorting:** Exams are sorted in descending order of their conflicts.
3.  **Coloring:** The algorithm iterates through the sorted list, assigning the earliest possible time slot (color) without violating conflict constraints.

---

## 📊 Visualizations
### Conflict Graph

Nodes represent exams. The lines (edges) represent shared students. Nodes of the same color are scheduled for the same time slot because they share no students.

### Schedule Timeline

A Gantt-style chart showing the chronological flow of the exam period, ensuring a clear overview of the day's events.

## 🛠️ Technologies Used
1. Python 3.x
2. Streamlit
3. NetworkX
4. Matplotlib
5. Pandas
