import numpy as np
import heapq
from collections import defaultdict

# =============================================
# 1. Création de la grille et des obstacles
# =============================================

def create_grid(rows, cols, obstacles, start, goal):
    """
    Crée une grille 2D avec des obstacles, un point de départ et un but.
    :param rows: Nombre de lignes
    :param cols: Nombre de colonnes
    :param obstacles: Liste de tuples (x, y) représentant les obstacles
    :param start: Tuple (x, y) du point de départ
    :param goal: Tuple (x, y) du but
    :return: Grille sous forme de matrice numpy
    """
    grid = np.zeros((rows, cols), dtype=object)
    for (x, y) in obstacles:
        grid[x, y] = 1
    grid[start] = 'S'
    grid[goal] = 'G'
    return grid

# =============================================
# 2. Heuristiques pour A*
# =============================================

def manhattan(p, goal):
    """
    Heuristique de Manhattan .
    """
    return abs(p[0] - goal[0]) + abs(p[1] - goal[1])

# =============================================
# 3. Algorithmes de recherche (A*, UCS, Greedy)
# =============================================

def get_neighbors(grid, current):
    """
    Retourne les voisins accessibles  d'une cellule.
    """
    rows, cols = grid.shape
    x, y = current
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < rows and 0 <= ny < cols and grid[nx, ny] not in [1]:
            neighbors.append((nx, ny))
    return neighbors

def astar(grid, start, goal, heuristic):
    """
    Implémentation de l'algorithme A*.
    """
    open_set = []
    heapq.heappush(open_set, (0, start) )
    came_from = {}
    g_score = defaultdict(lambda: float('inf'))
    g_score[start] = 0
    f_score = defaultdict(lambda: float('inf'))
    f_score[start] = heuristic(start, goal)

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            return reconstruct_path(came_from, current)
        for neighbor in get_neighbors(grid, current):
            tentative_g = g_score[current] + 1
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return None

def ucs(grid, start, goal):
    """
    Implémentation de l'algorithme UCS
    """
    return astar(grid, start, goal, lambda p, goal: 0)

def greedy(grid, start, goal, heuristic):
    open_set = []
    heapq.heappush(open_set, ( heuristic(start, goal), start ))
    came_from = {}
    visited = set()

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            return reconstruct_path(came_from, current)
        if current in visited:
            continue
        visited.add(current)
        for neighbor in get_neighbors(grid, current):
            if neighbor not in visited:
                came_from[neighbor] = current
                heapq.heappush(open_set, (heuristic(neighbor, goal), neighbor))
    return None

def reconstruct_path(came_from, current):
    """
    Reconstruit le chemin à partir du dictionnaire came_from.
    """
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

# =============================================
# 4. Construction de la matrice de transition P (Chaîne de Markov)
# =============================================

def build_transition_matrix(grid, epsilon=0.1):
    """
    Construit la matrice de transition P pour la chaîne de Markov.
    :param grid: Grille 2D
    :param epsilon: Probabilité de déviation
    :return: Matrice P et dictionnaire d'index des états
    """
    rows, cols = grid.shape
    states = []
    state_index = {}
    index = 0

    # Créer une liste des états
    for x in range(rows):
        for y in range(cols):
            if grid[x, y] not in [1, 'S', 'G']:
                states.append((x, y))
                state_index[(x, y)] = index
                index += 1

    # Ajouter les états absorbants GOAL et FAIL
    state_index['GOAL'] = index
    state_index['FAIL'] = index + 1
    states.append('GOAL')
    states.append('FAIL')
    num_states = len(states)
    P = np.zeros((num_states, num_states))

    # Remplir la matrice P
    for (x, y), i in state_index.items():
        if (x, y) == 'GOAL' or (x, y) == 'FAIL':
            P[i, i] = 1  # États absorbants
        else:
            neighbors = get_neighbors(grid, (x, y))
            if not neighbors:  # Si pas de voisins (bloqué)
                P[i, state_index['FAIL']] = 1
            else:
                # Probabilité de transition vers chaque voisin
                for nx, ny in neighbors:
                    j = state_index.get((nx, ny), state_index['FAIL'])
                    if (nx, ny) == 'G':
                        P[i, state_index['GOAL']] += (1 - epsilon)
                    else:
                        P[i, j] += (1 - epsilon) / len(neighbors)
                # Probabilité de déviation (epsilon)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < rows and 0 <= ny < cols and grid[nx, ny] not in [1]:
                        j = state_index.get((nx, ny), state_index['FAIL'])
                        P[i, j] += epsilon / 4
                # Normalisation pour s'assurer que la somme des probabilités = 1
                P[i, :] /= P[i, :].sum()

    return P, state_index

# =============================================
# 5. Calculs Markov : π(n) = π(0) * P^n
# =============================================

def markov_evolution(P, pi0, n_steps):
    """
    Calcule l'évolution de la distribution π après n étapes.
    """
    pi = pi0.copy()
    for _ in range(n_steps):
        pi = pi @ P
    return pi

# =============================================
# 6. Simulation Monte-Carlo
# =============================================

def simulate_trajectory(P, state_index, start, max_steps=100):
    """
    Simule une trajectoire Markov à partir de l'état initial.
    """
    current = state_index[start]
    trajectory = [current]
    for _ in range(max_steps):
        if current == state_index['GOAL'] or current == state_index['FAIL']:
            break
        next_state = np.random.choice(len(P), p=P[current])
        trajectory.append(next_state)
        current = next_state
    return trajectory
