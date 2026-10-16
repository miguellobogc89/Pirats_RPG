"""Coordinador de estados de IA. No dibuja ni controla el motor de movimiento.

Las capacidades de sigilo se activan por enemigo mediante StealthConfig.
"""
import math


class EnemyBrain:
    @staticmethod
    def tick(world, actor, target, dt):
        from .engine import CombatEvent
        stealth_enabled = actor.stealth is not None or world.perception_enabled
        dx, dy = target.x - actor.x, target.y - actor.y
        distance = math.hypot(dx, dy)
        if stealth_enabled and actor.alert_state == "search_ended":
            from .stealth import line_of_sight
            if (distance <= actor.vision_range and
                    line_of_sight(actor.x, actor.y, target.x, target.y, world.obstacles)):
                actor.alert_state = "alert"
                actor.reaction_remaining = 0
                actor.last_seen = (target.x, target.y)
                actor.search_started = False
                actor.search_time = 0
            else:
                actor.reaction_remaining = max(0, actor.reaction_remaining - dt)
                if actor.reaction_remaining == 0:
                    actor.awake = False
                    actor.alert_state = "patrol"
                    actor.detection = 0
                    actor.last_seen = None
                    actor.search_goal = None
                    actor.search_points.clear()
                    actor.searched_points.clear()
                    actor.search_started = False
                    actor.search_direction = (0, 0)
                    actor.trail_index = len(world.player_trail)
                    actor.scan_pause = 0
                    actor.patrol_pause = 0
                return
        if stealth_enabled and not actor.awake:
            from .stealth import can_see
            visible = can_see(actor, target, world.obstacles)
            actor.detection = min(actor.detection_time, actor.detection + dt) if visible else max(0, actor.detection - dt * 1.5)
            if actor.detection >= actor.detection_time:
                actor.awake = True
                actor.alert_state = "surprised"
                actor.surprise_remaining = actor.stealth.surprise_duration if actor.stealth else 0.32
                actor.last_seen = (target.x, target.y)
                actor.search_direction = (target.x - actor.x, target.y - actor.y)
                world.events.append(CombatEvent("aggro", actor.id, target.id, x=actor.x, y=actor.y, duration=actor.surprise_remaining))
            else:
                world._patrol(actor, dt)
            return
        if not stealth_enabled and distance <= actor.aggro_radius and not actor.awake:
            actor.awake = True
            world.events.append(CombatEvent("aggro", actor.id, target.id,
                                           x=actor.x, y=actor.y))
        if not actor.awake:
            return
        if stealth_enabled and actor.surprise_remaining > 0:
            actor.surprise_remaining = max(0, actor.surprise_remaining - dt)
            # Durante el sobresalto no se mueve, pero recuerda al jugador
            # mientras siga a la vista. No lee posiciones ocultas.
            from .stealth import line_of_sight
            if (distance <= actor.vision_range and
                    line_of_sight(actor.x, actor.y, target.x, target.y, world.obstacles)):
                actor.last_seen = (target.x, target.y)
                actor.search_direction = (dx, dy)
            if actor.surprise_remaining == 0:
                actor.alert_state = "alert"
            return
        if stealth_enabled:
            from .stealth import can_see, line_of_sight
            # Una vez alertado no conoce la posicion del jugador tras las cajas.
            # En combate se permite una vision periferica mayor que en patrulla.
            # Tras la deteccion, mantener contacto visual sin depender de
            # la orientacion que adopta al esquivar una caja.
            seen = (distance <= actor.vision_range and
                    line_of_sight(actor.x, actor.y, target.x, target.y, world.obstacles))
            if seen:
                actor.last_seen = (target.x, target.y)
                actor.alert_state = "alert"
                actor.search_goal = None
                actor.search_started = False
                actor.search_time = 0
                actor.search_points.clear()
                actor.searched_points.clear()
                actor.trail_index = len(world.player_trail)
            else:
                actor.windup = 0
                if actor.alert_state == "confused":
                    actor.reaction_remaining = max(0, actor.reaction_remaining - dt)
                    if actor.reaction_remaining == 0:
                        actor.alert_state = "search"
                        world._search(actor, dt)
                    return
                if actor.last_seen is None:
                    return
                if not actor.search_started and actor.search_direction == (0, 0):
                    actor.search_direction = (actor.last_seen[0] - actor.x,
                                              actor.last_seen[1] - actor.y)
                # Corre hasta el ultimo avistamiento, incluso sin vision.
                if not actor.search_started and math.dist((actor.x, actor.y), actor.last_seen) > actor.radius + 5:
                    actor.alert_state = "pursuit"
                    world._navigate(actor, actor.last_seen, dt, actor.chase_speed)
                else:
                    if not actor.search_started and actor.alert_state != "confused":
                        actor.alert_state = "confused"
                        actor.reaction_remaining = actor.stealth.confusion_duration if actor.stealth else 1.0
                        world.events.append(CombatEvent("confused", actor.id, x=actor.x, y=actor.y, duration=actor.reaction_remaining))
                    else:
                        actor.alert_state = "search"
                        world._search(actor, dt)
                return
            # Recuerda las zonas realmente observadas, no las que simplemente
            # ha atravesado; se actualiza con cadencia para ahorrar CPU.
            actor.survey_timer -= dt
            if actor.survey_timer <= 0:
                from .stealth import visible_cells
                actor.surveyed_cells.update(visible_cells(actor, world.obstacles,
                                                          world.width, world.height))
                actor.survey_timer = 0.15
        if actor.windup > 0:
            actor.windup = max(0, actor.windup - dt)
            if actor.windup == 0 and target.alive:
                if math.hypot(target.x - actor.x, target.y - actor.y) <= actor.reach + target.radius:
                    if not world.damage(actor.id, target.id, actor.damage):
                        world.events.append(CombatEvent("blocked", actor.id, target.id,
                                                       x=target.x, y=target.y,
                                                       duration=0.22))
                else:
                    world.events.append(CombatEvent("miss", actor.id,
                                                   x=actor.x + actor.facing_x * actor.reach,
                                                   y=actor.y + actor.facing_y * actor.reach,
                                                   duration=0.18))
            return
        if actor.stun > 0 or actor.dash_remaining > 0:
            return
        if distance > 0:
            actor.facing_x, actor.facing_y = dx / distance, dy / distance
        if distance <= actor.reach + target.radius:
            if actor.cooldown == 0:
                actor.cooldown = actor.attack_cooldown
                actor.windup = 0.22
                world.events.append(CombatEvent("telegraph", actor.id, target.id,
                                               x=actor.x, y=actor.y, duration=0.22))
        elif distance > 0:
            if stealth_enabled:
                world._navigate(actor, (target.x, target.y), dt, actor.chase_speed)
            else:
                world.move(actor.id, dx, dy, dt)

