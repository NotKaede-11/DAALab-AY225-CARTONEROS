# Multi-Metric Shortest Path Finder 🗺️

An aesthetic web-based application that finds the shortest paths between all pairs of nodes in a graph using Dijkstra's algorithm, optimized for three different metrics: **Distance**, **Time**, and **Fuel**.

![Algorithm](https://img.shields.io/badge/Algorithm-Dijkstra's-blue)
![Complexity](<https://img.shields.io/badge/Complexity-O((V%2BE)logV)-green>)
![Language](https://img.shields.io/badge/Language-JavaScript-yellow)

## 📋 Features

- **Multi-Metric Optimization**: Computes shortest paths for three different metrics
  - 📏 Distance (shortest physical path)
  - ⏱️ Time (fastest route)
  - ⛽ Fuel (most fuel-efficient)

- **All-Pairs Shortest Paths**: Calculates optimal paths from every node to every other node

- **Interactive UI**:
  - Filter results by source node
  - Toggle metrics on/off
  - Color-coded visualization for each metric
  - Expandable path details

- **Modern Design**:
  - Gradient backgrounds and animations
  - Responsive layout (mobile-friendly)
  - Dark theme with vibrant accents
  - Smooth transitions and hover effects

## 🚀 Quick Start

1. **Open the Application**:

   ```
   Simply open index.html in your web browser
   ```

2. **View Results**:
   - The application automatically loads data from `data/data.json`
   - Computes shortest paths for all node pairs
   - Displays results in an organized, card-based layout

3. **Interact**:
   - Use the node filter dropdown to focus on a specific source node
   - Click metric toggle buttons to show/hide distance, time, or fuel results
   - Switch between metrics using the tabs within each node card

## 📁 Project Structure

```
MIDTERM-LAB-WORK-1/
│
├── index.html                 # Main HTML file
├── styles.css                 # Aesthetic styling
├── README.md                  # This file
│
├── data/
│   ├── dataset.xlsx          # Original Excel data
│   └── data.json             # Converted JSON data (graph edges)
│
├── js/
│   ├── graph.js              # Graph data structure & Dijkstra's algorithm
│   └── main.js               # Application logic & UI interactions
│
└── convert_excel_to_json.py  # Python script for data conversion
```

## 📊 Data Format

### Input (Excel/JSON)

The graph data consists of edges with the following structure:

| Column    | Description                 | Example |
| --------- | --------------------------- | ------- |
| node_from | Source node identifier      | 1       |
| node_to   | Destination node identifier | 2       |
| distance  | Physical distance           | 10      |
| time      | Travel time                 | 15      |
| fuel      | Fuel consumption            | 1.2     |

### Example JSON:

```json
[
  {
    "node_from": 1,
    "node_to": 2,
    "distance": 10,
    "time": 15,
    "fuel": 1.2
  },
  ...
]
```

## 🧮 Algorithm

### Dijkstra's Shortest Path Algorithm

- **Time Complexity**: O((V + E) log V) with min-heap priority queue
- **Space Complexity**: O(V) for distance array and visited set

The algorithm is executed:

- 3 times per source node (once for each metric: distance, time, fuel)
- For N nodes: **3N total Dijkstra executions**

### Implementation Highlights

1. **MinHeap Priority Queue**: Efficient O(log V) insertions and deletions
2. **Adjacency List**: Space-efficient graph representation
3. **Path Reconstruction**: Tracks previous nodes for full path recovery
4. **Generic Weight Function**: Easily adaptable to different metrics

## 🎨 Color Scheme

- **Distance**: Blue (`#3b82f6`) - Represents spatial measurement
- **Time**: Green (`#10b981`) - Represents temporal efficiency
- **Fuel**: Orange (`#f59e0b`) - Represents resource consumption
- **Background**: Dark theme with gradient accents

## 🔧 Data Conversion

If you need to update the graph data:

1. **Edit the Excel file**: `data/dataset.xlsx`
2. **Run the conversion script**:
   ```bash
   python convert_excel_to_json.py
   ```
3. **Refresh the browser** to see updated results

### Requirements for Conversion:

```bash
pip install openpyxl
```

## 📈 Statistics Displayed

The application shows:

- **Total Nodes**: Number of unique nodes in the graph
- **Total Edges**: Number of connections between nodes
- **Paths Computed**: Total shortest paths calculated (N × (N-1) × 3)

## 🌐 Browser Compatibility

Tested and working on:

- ✅ Google Chrome (recommended)
- ✅ Mozilla Firefox
- ✅ Microsoft Edge
- ✅ Safari

## 📱 Responsive Design

The application adapts to different screen sizes:

- **Desktop**: Full layout with side-by-side comparisons
- **Tablet**: Stacked cards with optimized spacing
- **Mobile**: Single-column layout with touch-friendly controls

## 🎓 Academic Context

**Course**: Design and Analysis of Algorithms (DAA)  
**Assignment**: Midterm Lab Work 1  
**Topic**: Graph Algorithms - Shortest Path Problem  
**Year**: AY 2025

## 🔍 Usage Examples

### Finding the Shortest Distance Path

1. Open the application
2. Locate the source node card (e.g., "Source Node 1")
3. Ensure the "Distance" tab is selected (blue)
4. View the table showing all destinations with their shortest distance paths

### Comparing Metrics

1. Select a single source node using the filter dropdown
2. Switch between Distance, Time, and Fuel tabs
3. Compare how optimal paths differ based on the optimization metric

### Filtering Results

1. Use the "Filter by Source Node" dropdown
2. Select a specific node to view only its paths
3. Or keep "All Nodes" to see the complete graph analysis

## 💡 Key Insights

- **Different Metrics, Different Paths**: The shortest distance path may not be the fastest or most fuel-efficient
- **All-Pairs Analysis**: Computing paths from every node provides comprehensive graph understanding
- **Visualization Matters**: Color-coding and interactive UI make complex data accessible

## 🚦 Status

✅ **Complete and Functional**

All features implemented:

- [x] Excel to JSON data conversion
- [x] Graph data structure with adjacency list
- [x] Dijkstra's algorithm implementation
- [x] All-pairs shortest path computation
- [x] Interactive web interface
- [x] Responsive design
- [x] Multi-metric support
- [x] Path visualization

## 📝 License

Educational use only - DAA Lab Assignment

## 👥 Credits

**Team**: CARTONEROS  
**Lab**: DAA Lab AY225  
**Algorithm**: Edsger W. Dijkstra (1956)

---

**Enjoy exploring optimal paths! 🎉**
