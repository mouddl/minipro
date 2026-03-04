import numpy as np
from astar import astar, ucs, greedy, manhattan
from markov import build_transition_matrix, run_simulations

# --- Créer une grille simple ---
grid = np.zeros((5, 5), dtype=object)
grid[1:4, 2] = 1  # Obstacles verticaux
start = (0, 0)
goal = (4, 4)
grid[start] = 'S'
grid[goal] = 'G'

# --- Trouver un chemin avec A* ---
path = astar(grid, start, goal, manhattan)
print("Chemin A*:", path)

# --- Construire P et simuler ---
P, state_index = build_transition_matrix(grid, path, epsilon=0.2)
results = run_simulations(P, state_index, start, n_simulations=1000)
print("Probabilité d'atteindre le but:", results['goal_probability'])
