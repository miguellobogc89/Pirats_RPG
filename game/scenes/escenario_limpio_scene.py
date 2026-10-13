"""Arena blanca independiente para probar movimiento y combate sin tiles."""
import pygame
from game.scenes.farm_scene import FarmScene

WORLD_W, WORLD_H = 640, 512
WHITE = (255, 255, 255)
GRAY = (165, 165, 165)
DARK = (95, 95, 95)


def clamp_position(point, radius=16):
    point.x = max(radius, min(WORLD_W - radius, point.x))
    point.y = max(radius, min(WORLD_H - radius, point.y))


class EscenarioLimpioScene(FarmScene):
    def enter(self):
        self.boss = pygame.Vector2(505, 165)
        self.boss_home = self.boss.copy()
        self.boss_hp = 100
        self.boss_state = "idle"
        self.boss_timer = 0.8
        self.boss_flash = 0.0
        self.boss_stun = 0.0
        self.boss_charge_dir = pygame.Vector2()
        self.player_invulnerable = 0.0
        self.player_flash = 0.0
        self.attack_cooldown = 0.0
        self.attack_flash = 0.0
        self.facing = pygame.Vector2(0, -1)
        self.knockback = pygame.Vector2()
        self.player_stun = 0.0
        self.player = self.app.state["player"]
        self.player["x"], self.player["y"] = 320, 256
        self.app.state["health"]["current"] = self.app.state["health"]["max"]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_f):
            self.attack()
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.attack()
            return True
        return super().handle_event(event)

    def attack(self):
        if self.attack_cooldown > 0 or self.player_stun > 0:
            return
        self.attack_cooldown = 0.38
        self.attack_flash = 0.14
        delta = self.boss - pygame.Vector2(self.player["x"], self.player["y"])
        if delta.length_squared() and delta.length() < 92 and self.facing.dot(delta.normalize()) > 0.25:
            self.boss_hp = max(0, self.boss_hp - 20)
            self.boss_flash = 0.18
            self.boss_stun = 0.55
            self.boss_state = "stunned"
            self.boss += delta.normalize() * 25
            clamp_position(self.boss, 26)

    def update(self, dt):
        dt = min(dt, 0.05)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.attack_flash = max(0, self.attack_flash - dt)
        self.player_invulnerable = max(0, self.player_invulnerable - dt)
        self.player_flash = max(0, self.player_flash - dt)
        self.player_stun = max(0, self.player_stun - dt)
        self.boss_flash = max(0, self.boss_flash - dt)
        self.boss_stun = max(0, self.boss_stun - dt)
        self.boss_timer -= dt
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(
            int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
            int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP]),
        )
        if direction.length_squared():
            direction = direction.normalize()
            self.facing = direction
        pos = pygame.Vector2(self.player["x"], self.player["y"])
        if self.player_stun <= 0:
            pos += direction * 185 * dt
        if self.knockback.length_squared() > 0.1:
            pos += self.knockback * dt
            self.knockback *= max(0, 1 - 9 * dt)
        clamp_position(pos)
        self.player["x"], self.player["y"] = pos.x, pos.y

        if self.boss_hp <= 0:
            return
        delta = pos - self.boss
        distance = delta.length()
        if self.boss_stun > 0:
            self.boss_state = "stunned"
        elif self.boss_state == "stunned":
            self.boss_state = "idle"
            self.boss_timer = 0.5
        elif self.boss_state == "idle":
            if distance > 80 and distance < 360 and distance:
                self.boss += delta.normalize() * 45 * dt
            if self.boss_timer <= 0 and distance < 340 and distance:
                self.boss_state = "windup"
                self.boss_timer = 0.85
                self.boss_charge_dir = delta.normalize()
        elif self.boss_state == "windup" and self.boss_timer <= 0:
            self.boss_state = "charge"
            self.boss_timer = 0.38
        elif self.boss_state == "charge":
            self.boss += self.boss_charge_dir * 440 * dt
            clamp_position(self.boss, 26)
            if self.boss_timer <= 0:
                self.boss_state = "recovery"
                self.boss_timer = 1.0
        elif self.boss_state == "recovery" and self.boss_timer <= 0:
            self.boss_state = "idle"
            self.boss_timer = 0.45
        if self.boss_state == "charge" and self.boss.distance_to(pos) < 36 and self.player_invulnerable <= 0:
            self.app.state["health"]["current"] = max(0, self.app.state["health"]["current"] - 3)
            self.player_invulnerable = 1.0
            self.player_flash = 0.7
            self.player_stun = 0.45
            self.knockback = self.boss_charge_dir * 330
        if self.app.state["health"]["current"] <= 0:
            # Cambiar primero de escena; guardar solo el estado ya situado en la posada.
            self.app.state["health"]["current"] = self.app.state["health"]["max"]
            self.app.state.setdefault("brumazul", {})["beach_completed"] = True
            changed = self.app.scene_manager.change_scene(
                "brumazul_posada", payload={"target_spawn_id": "despertar"}
            )
            if changed:
                from core.save_manager import save_state
                try:
                    save_state(self.app.state)
                except (OSError, RuntimeError, TypeError, ValueError) as error:
                    self.app.add_log("No se pudo guardar: " + str(error))
                self.app.dispatch_scene_entered_event()

    def draw(self):
        screen = self.app.screen
        sw, sh = screen.get_size()
        ox, oy = (sw - WORLD_W) // 2, (sh - WORLD_H) // 2
        screen.fill(WHITE)
        pygame.draw.rect(screen, (210, 210, 210), (ox, oy, WORLD_W, WORLD_H), 1)
        if self.boss_hp > 0:
            bx, by = round(ox + self.boss.x), round(oy + self.boss.y)
            if self.boss_state == "windup":
                endpoint = self.boss + self.boss_charge_dir * 170
                pygame.draw.line(screen, (195, 195, 195), (bx, by), (round(ox + endpoint.x), round(oy + endpoint.y)), 1)
                pygame.draw.circle(screen, (180, 180, 180), (bx, by), 32, 1)
            if not (self.boss_flash > 0 and int(self.boss_flash * 22) % 2):
                pygame.draw.circle(screen, DARK, (bx, by), 24, 1)
                pygame.draw.circle(screen, DARK, (bx - 8, by - 5), 3, 1)
                pygame.draw.circle(screen, DARK, (bx + 8, by - 5), 3, 1)
            if self.boss_state == "stunned":
                pygame.draw.circle(screen, (160, 160, 160), (bx, by), 31, 1)
            pygame.draw.rect(screen, (185, 185, 185), (bx - 26, by - 40, 52, 4), 1)
            pygame.draw.rect(screen, (130, 130, 130), (bx - 25, by - 39, round(50 * self.boss_hp / 100), 2))
        pos = pygame.Vector2(self.player["x"], self.player["y"])
        center = pygame.Vector2(ox, oy) + pos
        front = center + self.facing * 16
        side = pygame.Vector2(-self.facing.y, self.facing.x)
        corners = [front, center - self.facing * 12 + side * 10, center - self.facing * 12 - side * 10]
        if not (self.player_flash > 0 and int(self.player_flash * 16) % 2):
            pygame.draw.polygon(screen, DARK, [(round(p.x), round(p.y)) for p in corners], 1)
        if self.attack_flash > 0:
            pygame.draw.circle(screen, (170, 170, 170), (round(front.x), round(front.y)), 30, 1)
        health = self.app.state["health"]
        pygame.draw.rect(screen, GRAY, (18, 20, 155, 7), 1)
        pygame.draw.rect(screen, (205, 205, 205), (19, 21, round(153 * health["current"] / max(1, health["max"])), 5))
        if self.app.menu_open:
            from game.hud.menu_overlay import draw_menu
            draw_menu(self.app)
