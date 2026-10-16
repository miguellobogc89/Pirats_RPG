"""Navegacion reutilizable: la IA solicita destinos, este componente mueve."""
import math


class MovementComponent:
    @staticmethod
    def navigate(world, actor, destination, dt, speed=None):
        from .stealth import find_path
        path = find_path((actor.x, actor.y), destination, world.obstacles,
                         actor.radius, world.width, world.height)
        if not path:
            return False
        x, y = path[0]
        dx, dy = x - actor.x, y - actor.y
        distance = math.hypot(dx, dy)
        velocity = actor.speed if speed is None else speed
        if distance > 0 and velocity > 0:
            world.move(actor.id, dx, dy, min(dt, distance / velocity), speed=velocity)
        return True

