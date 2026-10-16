"""Comportamientos de patrulla y busqueda, independientes de CombatWorld."""
import math


class SearchComponent:
    def search(world, actor, dt):
        from .stealth import search_cells
        if not actor.search_started:
            actor.search_started = True
            actor.search_goal = None
            actor.search_points = search_cells(actor.last_seen, world.obstacles,
                                               actor.radius, world.width, world.height)
            actor.search_points = [p for p in actor.search_points
                                   if (round(p[0] / 35), round(p[1] / 35)) not in actor.surveyed_cells]
            actor.searched_points.clear()
            actor.search_time = 0
            actor.scan_pause = 0.3
        actor.search_time += dt
        if actor.search_time >= actor.search_duration:
            actor.alert_state = "search_ended"
            actor.reaction_remaining = actor.stealth.search_end_duration if actor.stealth else 1.0
            actor.search_goal = None
            world.events.append(CombatEvent("search_ended", actor.id, x=actor.x, y=actor.y, duration=actor.reaction_remaining))
            return
        if actor.scan_pause > 0:
            actor.scan_pause = max(0, actor.scan_pause - dt)
            angle = math.atan2(actor.facing_y, actor.facing_x) + 2 * dt
            actor.facing_x, actor.facing_y = math.cos(angle), math.sin(angle)
            return
        if actor.search_goal is None:
            if (actor.stealth.assisted_tracking if actor.stealth else world.assisted_tracking):
                from .stealth import circle_hits_rect, find_path
                while actor.trail_index < len(world.player_trail):
                    i = actor.trail_index
                    timestamp, (px, py) = world.player_trail[i]
                    if timestamp > world.elapsed - 1.25:
                        break
                    actor.trail_index += 1
                    if math.dist((px, py), actor.last_seen) > 340:
                        continue
                    hx = max(actor.radius + 4, min(world.width - actor.radius - 4, px + math.sin(i * 2.37) * 32))
                    hy = max(actor.radius + 4, min(world.height - actor.radius - 4, py + math.cos(i * 1.91) * 32))
                    if any(circle_hits_rect(hx, hy, actor.radius + 2, box) for box in world.obstacles):
                        continue
                    if find_path((actor.x, actor.y), (hx, hy), world.obstacles, actor.radius, world.width, world.height):
                        actor.search_goal = (hx, hy)
                        break
            if actor.search_goal is None and not actor.search_points:
                # Una vez agotadas las zonas desconocidas, revisa las ya
                # inspeccionadas. Nunca necesita saber donde esta el jugador.
                actor.search_points = search_cells(actor.last_seen, world.obstacles,
                                                   actor.radius, world.width, world.height)
                actor.searched_points.clear()
            if actor.search_goal is None and not actor.search_points:
                return
            if actor.search_goal is None:
                vx, vy = actor.search_direction
                norm = max(1, math.hypot(vx, vy))
                actor.search_points.sort(key=lambda point: (
                    math.dist((actor.x, actor.y), point)
                    - 90 * ((point[0] - actor.last_seen[0]) * vx +
                            (point[1] - actor.last_seen[1]) * vy) /
                           (norm * max(1, math.dist(point, actor.last_seen)))))
                actor.search_goal = actor.search_points.pop(0)
        if math.dist((actor.x, actor.y), actor.search_goal) <= actor.radius + 5:
            actor.searched_points.append(actor.search_goal)
            actor.search_goal = None
            actor.scan_pause = 0.4
        elif not world._navigate(actor, actor.search_goal, dt, actor.walk_speed):
            actor.search_goal = None


class PatrolComponent:
    def patrol(world, actor, dt):
        if not actor.patrol_points or actor.stun > 0:
            return
        if actor.patrol_pause > 0:
            actor.patrol_pause = max(0, actor.patrol_pause - dt)
            return
        x, y = actor.patrol_points[actor.patrol_index]
        dx, dy = x - actor.x, y - actor.y
        distance = math.hypot(dx, dy)
        if distance <= max(3, actor.walk_speed * dt):
            actor.patrol_index = (actor.patrol_index + 1) % len(actor.patrol_points)
            actor.patrol_pause = actor.patrol_wait
        elif distance > 0:
            # Las rutas de patrulla tambien deben rodear obstaculos.
            # El desplazamiento directo hacia un waypoint puede dejar al
            # guardia bloqueado al volver de una busqueda.
            world._navigate(actor, (x, y), dt, actor.walk_speed)
