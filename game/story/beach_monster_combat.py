"""Adaptador de la mision inicial de playa al motor de combate reutilizable.

La escena mantiene la narrativa y el guardado. El motor controla la
persecucion, el aviso de ataque y el impacto del monstruo.
"""
from game.combat.action.engine import CombatWorld, Fighter


class BeachMonsterCombat:
    def __init__(self, player_x, player_y, monster_x=490, monster_y=560):
        self.world = CombatWorld(width=704, height=704)
        self.player = self.world.add(Fighter(
            "beach_player", "player", player_x, player_y,
            hp=1, max_hp=1, radius=14, brain_enabled=False,
        ))
        self.monster = self.world.add(Fighter(
            "beach_monster", "monster", monster_x, monster_y,
            hp=999, max_hp=999, radius=40, speed=42,
            damage=1, reach=62, aggro_radius=160,
            attack_cooldown=1.2, brain_enabled=True,
        ))

    def update(self, dt, player_x, player_y):
        # El desplazamiento del jugador pertenece a la escena.
        self.player.x, self.player.y = player_x, player_y
        self.world.update(dt)
        events = self.world.consume_events()
        return events, not self.player.alive

    def hit_monster(self, damage=25):
        if not self.monster.alive:
            return False
        # La criatura del prologo es invencible a efectos narrativos.
        # Conserva la respuesta al golpe sin poder morir en esta mision.
        self.monster.hp = max(1, self.monster.hp - damage)
        return True
