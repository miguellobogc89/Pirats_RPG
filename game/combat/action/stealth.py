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
