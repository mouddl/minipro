import heapq
import time
import numpy as np
from collections import defaultdict


def manhattan(p, goal):
    return abs(p[0] - goal[0]) + abs(p[1] - goal[1])


def get_neighbors(grid, pos):
    x, y = pos
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1] and grid[nx, ny] != 1:
            neighbors.append((nx, ny))
    return neighbors


def astar(grid, start, goal, heuristic=manhattan):
    start_time = time.time()
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = defaultdict(lambda: float('inf'))
    g_score[start] = 0
    f_score = defaultdict(lambda: float('inf'))
    f_score[start] = heuristic(start, goal)


    nodes_explored = 0
    nodes_tested = 0

    while open_set:
        _, current = heapq.heappop(open_set)
        nodes_explored += 1
        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return {
                'path': path,
                'cost': g_score[goal],
                'nodes_explored': nodes_explored,
                'nodes_tested': nodes_tested,
                'runtime': time.time() - start_time
            }
        for neighbor in get_neighbors(grid, current):
            tentative_g = g_score[current] + 1
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
                nodes_tested += 1
    return None


def ucs(grid, start, goal):
    return astar(grid, start, goal, heuristic=lambda p, goal: 0)


def greedy(grid, start, goal):
    open_set = []
    heapq.heappush(open_set, (manhattan(start, goal), start))
    came_from = {}
    visited = set()

    nodes_explored = 0
    nodes_tested = 0

    while open_set:
        _, current = heapq.heappop(open_set)
        nodes_explored += 1
        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return {
                'path': path,
                'cost': len(path) - 1,
                'nodes_explored': nodes_explored,
                'nodes_tested': nodes_tested
            }
        if current in visited:
            continue
        visited.add(current)
        for neighbor in get_neighbors(grid, current):
            if neighbor not in visited:
                came_from[neighbor] = current
                heapq.heappush(open_set, (manhattan(neighbor, goal), neighbor))
                nodes_tested += 1
    return None
