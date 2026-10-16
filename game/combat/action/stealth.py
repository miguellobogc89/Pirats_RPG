"""Percepcion, cobertura y patrulla para la microfase 3.1. Sin Pygame."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Obstacle:
    x: float
    y: float
    width: float
    height: float


def segment_hits_rect(x1, y1, x2, y2, rect, padding=0):
    """Interseccion segmento/AABB por intervalos, incluyendo contacto."""
    left, right = rect.x - padding, rect.x + rect.width + padding
    top, bottom = rect.y - padding, rect.y + rect.height + padding
    lo, hi = 0.0, 1.0
    for origin, delta, minimum, maximum in (
        (x1, x2 - x1, left, right), (y1, y2 - y1, top, bottom)
    ):
        if abs(delta) < 1e-10:
            if origin < minimum or origin > maximum:
                return False
            continue
        t1, t2 = (minimum - origin) / delta, (maximum - origin) / delta
        lo, hi = max(lo, min(t1, t2)), min(hi, max(t1, t2))
        if lo > hi:
            return False
    return True


def line_of_sight(x1, y1, x2, y2, obstacles):
    return not any(segment_hits_rect(x1, y1, x2, y2, box) for box in obstacles)


def can_see(observer, target, obstacles):
    if not observer.alive or not target.alive:
        return False
    dx, dy = target.x - observer.x, target.y - observer.y
    distance = math.hypot(dx, dy)
    if distance > observer.vision_range:
        return False
    if distance > 1e-8:
        dot = (dx * observer.facing_x + dy * observer.facing_y) / distance
        if dot < math.cos(math.radians(observer.vision_angle) / 2):
            return False
    return line_of_sight(observer.x, observer.y, target.x, target.y, obstacles)


def circle_hits_rect(x, y, radius, rect):
    cx = min(max(x, rect.x), rect.x + rect.width)
    cy = min(max(y, rect.y), rect.y + rect.height)
    return (x - cx) ** 2 + (y - cy) ** 2 < radius ** 2

def find_path(start, goal, obstacles, radius, width, height):
    """Camino corto por grafo de visibilidad de esquinas, con margen del actor."""
    import heapq
    margin = radius + 3
    nodes = [tuple(start), tuple(goal)]
    for box in obstacles:
        for x in (box.x - margin, box.x + box.width + margin):
            for y in (box.y - margin, box.y + box.height + margin):
                if margin <= x <= width - margin and margin <= y <= height - margin:
                    if not any(circle_hits_rect(x, y, radius, other) for other in obstacles):
                        nodes.append((x, y))
    def clear(a, b):
        return not any(segment_hits_rect(*a, *b, box, padding=radius + 0.5) for box in obstacles)
    # Los vertices se situan a radius+3, evitando contactos tangentes.
    if clear(nodes[0], nodes[1]):
        return [nodes[1]]
    graph = [[] for _ in nodes]
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if clear(nodes[i], nodes[j]):
                cost = math.dist(nodes[i], nodes[j])
                graph[i].append((j, cost))
                graph[j].append((i, cost))
    distances = [float("inf")] * len(nodes)
    parents = {}
    distances[0] = 0
    queue = [(0, 0)]
    while queue:
        cost, index = heapq.heappop(queue)
        if cost > distances[index]:
            continue
        if index == 1:
            route = []
            while index != 0:
                route.append(nodes[index])
                index = parents[index]
            return list(reversed(route))
        for neighbor, edge in graph[index]:
            candidate = cost + edge
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                parents[neighbor] = index
                heapq.heappush(queue, (candidate, neighbor))
    return []

def search_cells(origin, obstacles, radius, width, height, search_radius=230, spacing=70):
    """Puntos transitables alrededor del ultimo avistamiento; no consulta al jugador."""
    ox, oy = origin
    points = []
    x = max(radius + 4, ox - search_radius)
    while x <= min(width - radius - 4, ox + search_radius):
        y = max(radius + 4, oy - search_radius)
        while y <= min(height - radius - 4, oy + search_radius):
            if math.hypot(x - ox, y - oy) <= search_radius:
                if not any(circle_hits_rect(x, y, radius + 2, box) for box in obstacles):
                    if find_path(origin, (x, y), obstacles, radius, width, height):
                        points.append((x, y))
            y += spacing
        x += spacing
    return points

def visible_cells(observer, obstacles, width, height, spacing=35):
    """Celdas realmente visibles durante la persecucion, en una rejilla estable."""
    cells = set()
    ox, oy = observer.x, observer.y
    radius = observer.vision_range
    for ix in range(max(0, int((ox - radius) // spacing)),
                    min(int(width // spacing), int((ox + radius) // spacing)) + 1):
        for iy in range(max(0, int((oy - radius) // spacing)),
                        min(int(height // spacing), int((oy + radius) // spacing)) + 1):
            x, y = ix * spacing, iy * spacing
            dx, dy = x - ox, y - oy
            dist = math.hypot(dx, dy)
            if dist > radius:
                continue
            if dist > 0 and (dx * observer.facing_x + dy * observer.facing_y) / dist < math.cos(math.radians(observer.vision_angle) / 2):
                continue
            if line_of_sight(ox, oy, x, y, obstacles):
                cells.add((ix, iy))
    return cells
