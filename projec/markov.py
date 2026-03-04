import numpy as np
from astar import get_neighbors

# --- Construire la matrice P (CORRIGÉ + COMPLÉTÉ) ---
def build_transition_matrix(grid, path, epsilon=0.1):
    """
    Construit la matrice de transition P à partir du chemin A* (politique).
    - Les états sur le chemin suivent exactement la direction du chemin suivant.
    - Les autres états utilisent une direction par défaut (droite).
    - GOAL et FAIL sont absorbants.
    """
    # 1. Créer la liste des états (cellules libres + GOAL/FAIL)
    states = []
    state_index = {}
    index = 0
    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            if grid[x, y] != 1:
                states.append((x, y))
                state_index[(x, y)] = index
                index += 1
    state_index['GOAL'] = index
    state_index['FAIL'] = index + 1
    states.append('GOAL')
    states.append('FAIL')

    P = np.zeros((len(states), len(states)))

    # === POLITIQUE : dictionnaire "où aller" à partir du chemin A* ===
    intended_next = {}
    if path and len(path) > 1:
        for i in range(len(path) - 1):
            intended_next[path[i]] = path[i + 1]

    # 2. Remplir P
    for state, i in state_index.items():
        if state == 'GOAL' or state == 'FAIL':
            P[i, i] = 1.0  # États absorbants
            continue

        x, y = state

        # Détection du but (comme dans le code original)
        if grid[x, y] == 'G':
            P[i, state_index['GOAL']] = 1.0
            continue

        neighbors = get_neighbors(grid, (x, y))
        if not neighbors:  # Bloqué
            P[i, state_index['FAIL']] = 1.0
            continue

        # === ACTION INTENTIONNELLE ===
        if state in intended_next:
            next_pos = intended_next[state]
            intended_direction = (next_pos[0] - x, next_pos[1] - y)
        else:
            intended_direction = (0, 1)  # défaut : droite

        # Vérifier si la direction intentionnelle est valide (dans les voisins)
        intended_neighbor_valid = any(
            (neighbor[0] - x, neighbor[1] - y) == intended_direction
            for neighbor in neighbors
        )

        # 4. Remplir les probabilités (modèle glissement ε)
        if intended_neighbor_valid:
            for neighbor in neighbors:
                j = state_index[neighbor]
                dx, dy = (neighbor[0] - x, neighbor[1] - y)
                if (dx, dy) == intended_direction:
                    P[i, j] = 1 - epsilon
                else:
                    P[i, j] = epsilon / len(neighbors)
        else:
            # Direction intentionnelle invalide : distribution uniforme
            for neighbor in neighbors:
                j = state_index[neighbor]
                P[i, j] = 1.0 / len(neighbors)

        # Normaliser la ligne
        row_sum = P[i, :].sum()
        if row_sum > 0:
            P[i, :] /= row_sum

    return P, state_index


# --- Vérification que P est stochastique (bonus utile) ---
def is_stochastic(P, tol=1e-8):
    """Vérifie que chaque ligne somme à 1 (requis par le sujet)."""
    return np.allclose(P.sum(axis=1), 1.0, atol=tol)


# --- Calcul de la distribution π^(n) = π^(0) P^n (MANQUANT dans l'original) ---
def compute_distribution(P, state_index, start, n_steps=20):
    """
    Calcule l'évolution de la distribution de probabilité sur n_steps étapes.
    Retourne un tableau (n_steps+1, n_states) avec π(0), π(1), ..., π(n).
    C'est exactement ce que demande le squelette #4 du sujet.
    """
    n_states = len(P)
    pi = np.zeros(n_states)
    pi[state_index[start]] = 1.0

    distributions = [pi.copy()]
    current_pi = pi.copy()

    for _ in range(n_steps):
        current_pi = current_pi @ P
        distributions.append(current_pi.copy())

    return np.array(distributions)


# --- Simulation d'une trajectoire ---
def simulate_trajectory(P, state_index, start, max_steps=100):
    current = state_index[start]
    trajectory = [current]
    for _ in range(max_steps):
        if current in [state_index['GOAL'], state_index['FAIL']]:
            break
        next_state = np.random.choice(len(P), p=P[current])
        trajectory.append(next_state)
        current = next_state
    return trajectory


# --- Exécuter N simulations ---
def run_simulations(P, state_index, start, n_simulations=1000):
    goal_count = 0
    fail_count = 0
    for _ in range(n_simulations):
        traj = simulate_trajectory(P, state_index, start)
        if traj[-1] == state_index['GOAL']:
            goal_count += 1
        elif traj[-1] == state_index['FAIL']:
            fail_count += 1
    return {
        'goal_probability': goal_count / n_simulations,
        'fail_probability': fail_count / n_simulations
    }


# --- Analyse d'absorption (déjà présente et conforme) ---
def absorption_analysis(P, state_index):
    absorbing = ['GOAL', 'FAIL']
    absorbing_indices = [state_index[state] for state in absorbing]
    transient_indices = [i for i in range(len(P)) if i not in absorbing_indices]

    # Décomposition P = [I 0 ; R Q]
    Q = P[np.ix_(transient_indices, transient_indices)]
    R = P[np.ix_(transient_indices, absorbing_indices)]

    I = np.eye(len(Q))
    N = np.linalg.inv(I - Q)               # Matrice fondamentale

    absorption_probs = N @ R
    expected_time = N.sum(axis=1)

    # Mapping pour lisibilité
    transient_states = [state for state, idx in state_index.items() if idx in transient_indices]
    absorption_labels = [state for state, idx in state_index.items() if idx in absorbing_indices]

    return {
        'absorption_probs': absorption_probs,
        'expected_time': expected_time,
        'transient_states': transient_states,
        'absorption_labels': absorption_labels
    }