# Pathfinding & Markov Chain Simulation Project

This project implements pathfinding algorithms (A*, UCS, Greedy) combined with Markov chain analysis for robot navigation with uncertainty.

## Prerequisites

- Python 3.x
- Required packages: `numpy`, `pandas`, `matplotlib`, `seaborn`

## Installation

1. Activate the virtual environment:
   ```bash
   source ../.venv/bin/activate
   ```

2. Install dependencies (if not already installed):
   ```bash
   pip install numpy pandas matplotlib seaborn
   ```

## Running the Project

Execute the main script from the `projec` directory:

```bash
python main.py
```

## Output

Results are saved in the `results/` directory:
- **Grid visualizations**: `grid_*_plain.png`, `grid_*_all_algorithms.png`
- **Comparison charts**: `bar_nodes_explored.png`, `bar_execution_time.png`
- **ε impact analysis**: `graph_prob_vs_epsilon.png`, `graph_expected_time_vs_epsilon.png`
- **CSV data**: `experiment1_comparaison_algos.csv`, `experiment2_impact_epsilon.csv`

## Project Structure

```
projec/
├── main.py          # Main entry point - runs experiments
├── astar.py         # A*, UCS, and Greedy pathfinding algorithms
├── markov.py        # Markov chain transition matrix & simulation
└── results/         # Generated outputs (created on first run)
```

## Experiments

1. **Experiment 1**: Compares UCS, Greedy, and A* algorithms on different grid sizes
2. **Experiment 2**: Analyzes the impact of execution uncertainty (ε) on goal probability
