import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import os
from matplotlib.colors import ListedColormap
from astar import astar, ucs, greedy
from markov import (
    build_transition_matrix,
    run_simulations,
    absorption_analysis,
    compute_distribution,
    is_stochastic
)

sns.set_theme(style="ticks", palette="deep", font_scale=1.1)
os.makedirs("results", exist_ok=True)

N_SIMULATIONS = 1000
EPSILONS = [0.0, 0.1, 0.2, 0.3]
MAX_STEPS_DISTRIB = 30

def create_grids():
    grids = {}
    starts = {}
    goals = {}

    grid_easy = np.zeros((6, 6), dtype=object)
    grid_easy[4, 4] = 'G'
    grids['easy'] = grid_easy
    starts['easy'] = (0, 0)
    goals['easy'] = (4, 4)

    grid_med = np.zeros((8, 8), dtype=object)

    grid_med[3, 2:5] = 1
    grid_med[5, 1:3] = 1
    grid_med[2, 5] = 1

    grid_med[6, 3] = 1
    grid_med[5, 6] = 1


    grid_med[6, 6] = 'G'
    grids['medium'] = grid_med
    starts['medium'] = (0, 0)
    goals['medium'] = (6, 6)

    grid_hard = np.zeros((10, 10), dtype=object)

    walls = [
        (7, 8),
        (7, 9),
        (4,8),
        (4,7),
        (4,6),
        (2, 3),
        (4, 5),
        (6, 4),
        (7, 8),
        (9, 3),
        (9, 6)
    ]

    for x,y in walls:
        grid_hard[x,y] = 1
    grid_hard[8, 8] = 'G'
    grids['hard'] = grid_hard
    starts['hard'] = (0, 0)
    goals['hard'] = (8, 8)

    return grids, starts, goals


def plot_plain_grid(grid, start, goal, title, filename):
    plt.figure(figsize=(7.5, 7.5))
    grid_vis = np.zeros(grid.shape, dtype=int)

    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if grid[i,j] == 1:
                grid_vis[i,j] = 1
            elif grid[i,j] == 'G':
                grid_vis[i,j] = 2

    cmap = ListedColormap(['white', 'black', '#90EE90'])
    plt.imshow(grid_vis, cmap=cmap, origin='upper', vmin=0, vmax=2)

    ax = plt.gca()
    ax.set_xticks(np.arange(-0.5, grid.shape[1], 1))
    ax.set_yticks(np.arange(-0.5, grid.shape[0], 1))
    ax.grid(color='white', linewidth=2)
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    plt.text(start[1], start[0], 'START', color='darkblue', fontsize=16, fontweight='bold',
             ha='center', va='center', bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.95))
    plt.text(goal[1], goal[0], 'GOAL', color='darkgreen', fontsize=16, fontweight='bold',
             ha='center', va='center', bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.95))

    plt.title(title, fontsize=16, pad=20)
    plt.axis('off')
    plt.savefig(f"results/{filename}", dpi=300, bbox_inches='tight')
    plt.close()


def plot_all_paths(grid, paths_dict, start, goal, title, filename):
    plt.figure(figsize=(8.5, 8.5))
    grid_vis = np.zeros(grid.shape, dtype=int)

    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if grid[i,j] == 1:
                grid_vis[i,j] = 1
            elif grid[i,j] == 'G':
                grid_vis[i,j] = 2

    cmap = ListedColormap(['white', 'black', '#90EE90'])
    plt.imshow(grid_vis, cmap=cmap, origin='upper', vmin=0, vmax=2)

    ax = plt.gca()
    ax.set_xticks(np.arange(-0.5, grid.shape[1], 1))
    ax.set_yticks(np.arange(-0.5, grid.shape[0], 1))
    ax.grid(color='black', linewidth=2)
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    plt.text(start[1], start[0], 'START', color='darkblue', fontsize=16, fontweight='bold',
             ha='center', va='center', bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.95))
    plt.text(goal[1], goal[0], 'GOAL', color='darkgreen', fontsize=16, fontweight='bold',
             ha='center', va='center', bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.95))

    colors = {'UCS': 'blue', 'Greedy': 'orange', 'A*': 'red'}
    linestyles = {'UCS': '-', 'Greedy': '-', 'A*': '-'}
    linewidths = {'UCS': 5, 'Greedy': 4.5, 'A*': 6}

    offsets = {'UCS': (-0.15, -0.15), 'Greedy': (0, 0), 'A*': (0.15, 0.15)}

    for algo in ['UCS', 'Greedy', 'A*']:
        if algo in paths_dict and paths_dict[algo] is not None:
            path = paths_dict[algo]
            offset_x, offset_y = offsets[algo]
            px = [p[0] + offset_x for p in path]
            py = [p[1] + offset_y for p in path]
            plt.plot(py, px,
                     color=colors[algo],
                     linestyle=linestyles[algo],
                     linewidth=linewidths[algo],
                     marker='o',
                     markersize=7,
                     alpha=0.95,
                     label=f'{algo} (coût = {len(path)-1})')

    plt.legend(fontsize=12, loc='upper right', frameon=True, shadow=True)
    plt.title(title, fontsize=16, pad=20)
    plt.axis('off')
    plt.savefig(f"results/{filename}", dpi=350, bbox_inches='tight')
    plt.close()


def experiment_1(grids, starts, goals):
    print("=== Expérience 1 : Comparaison UCS / Greedy / A* ===")
    rows = []

    for name in ['easy', 'medium', 'hard']:
        grid = grids[name]
        start = starts[name]
        goal = goals[name]

        plot_plain_grid(grid, start, goal,
                        f"Grille {name.upper()}",
                        f"grid_{name}_plain.png")

        paths_dict = {}
        for algo_name, func in [("UCS", ucs), ("Greedy", greedy), ("A*", astar)]:
            t0 = time.time()
            result = func(grid, start, goal)
            runtime = time.time() - t0

            if result is None:
                paths_dict[algo_name] = None
                rows.append([name, algo_name, np.nan, np.nan, np.nan, np.nan, np.nan])
                continue

            if isinstance(result, dict):
                path = result.get('path')
                nodes_exp = result.get('nodes_explored', np.nan)
                nodes_test = result.get('nodes_tested', np.nan)
            else:
                path = result
                nodes_exp = nodes_test = np.nan

            cost = len(path) - 1 if path else np.nan
            paths_dict[algo_name] = path

            rows.append([name, algo_name, cost, nodes_exp, nodes_test, round(runtime, 5), len(path)])

        plot_all_paths(grid, paths_dict, start, goal,
                       f"Grille {name.upper()} — UCS / Greedy / A* (chemins superposés)",
                       f"grid_{name}_all_algorithms.png")

    df = pd.DataFrame(rows, columns=["Grille", "Algorithme", "Coût", "Nœuds développés", "Nœuds testés", "Temps (s)", "Longueur chemin"])
    df.to_csv("results/experiment1_comparaison_algos.csv", index=False)

    plt.figure(figsize=(10,6))
    sns.barplot(data=df, x="Grille", y="Nœuds développés", hue="Algorithme")
    plt.title("Nœuds développés par algorithme")
    plt.savefig("results/bar_nodes_explored.png", dpi=300, bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(10,6))
    sns.barplot(data=df, x="Grille", y="Temps (s)", hue="Algorithme")
    plt.title("Temps d'exécution par algorithme")
    plt.savefig("results/bar_execution_time.png", dpi=300, bbox_inches='tight')
    plt.close()

    print("   → grid_xxx_plain.png + grid_xxx_all_algorithms.png (3 chemins visibles grâce aux styles)")
    return df


def experiment_2(grids, starts, goals):
    print("=== Expérience 2 : Impact de ε ===")
    rows = []
    prob_data = []

    for eps in EPSILONS:
        for name in ['easy', 'medium', 'hard']:
            grid = grids[name]
            start = starts[name]
            goal = goals[name]

            t0 = time.time()
            res = astar(grid, start, goal)
            plan_time = time.time() - t0
            path = res['path']
            cost = len(path) - 1

            P, state_index = build_transition_matrix(grid, path, epsilon=eps)
            assert is_stochastic(P)

            t0 = time.time()
            stats = run_simulations(P, state_index, start, N_SIMULATIONS)
            sim_time = time.time() - t0

            abs_analysis = absorption_analysis(P, state_index)
            goal_prob_abs = abs_analysis['absorption_probs'][0, 0]
            expected_time = abs_analysis['expected_time'][0] if len(abs_analysis['expected_time']) > 0 else np.nan

            rows.append([eps, name, cost, round(goal_prob_abs, 4), round(stats['goal_probability'], 4),
                         round(expected_time, 2), round(plan_time, 5), round(sim_time, 5)])

            prob_data.append([eps, name, stats['goal_probability'], round(expected_time, 2)])

            if name == 'medium' and eps == 0.1:
                dist = compute_distribution(P, state_index, start, MAX_STEPS_DISTRIB)
                goal_idx = state_index['GOAL']
                plt.figure(figsize=(9,5))
                sns.lineplot(x=range(len(dist)), y=dist[:, goal_idx], marker='o', linewidth=3)
                plt.title(f"Évolution π(n) — Grille medium, ε={eps}")
                plt.xlabel("Nombre d'étapes")
                plt.ylabel("P(être dans GOAL)")
                plt.grid(True)
                plt.savefig("results/distribution_pi_medium_eps01.png", dpi=300)
                plt.close()

    df = pd.DataFrame(rows, columns=["ε", "Grille", "Coût A*", "Proba absorption GOAL", "Proba MC GOAL",
                                     "Temps moyen absorption", "Temps planification (s)", "Temps simulation (s)"])
    df.to_csv("results/experiment2_impact_epsilon.csv", index=False)

    dfp = pd.DataFrame(prob_data, columns=["ε", "Grille", "Probabilité GOAL", "Temps moyen absorption"])

    plt.figure(figsize=(10,6))
    sns.lineplot(data=dfp, x="ε", y="Probabilité GOAL", hue="Grille", marker="o", linewidth=3)
    plt.title("Impact de ε sur la probabilité d'atteindre GOAL")
    plt.ylim(0.6, 1.02)
    plt.savefig("results/graph_prob_vs_epsilon.png", dpi=300, bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(10,6))
    sns.lineplot(data=dfp, x="ε", y="Temps moyen absorption", hue="Grille", marker="o", linewidth=3)
    plt.title("Temps moyen avant absorption vs ε")
    plt.savefig("results/graph_expected_time_vs_epsilon.png", dpi=300, bbox_inches='tight')
    plt.close()

    print("   → experiment2 terminé")
    return df


if __name__ == "__main__":
    grids, starts, goals = create_grids()

    df1 = experiment_1(grids, starts, goals)
    df2 = experiment_2(grids, starts, goals)
    print ("voir resultats  !")