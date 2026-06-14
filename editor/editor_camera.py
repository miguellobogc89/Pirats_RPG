from game.world.grid_manager import TILE_SIZE


class EditorCamera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.is_panning = False
        self.last_mouse_pos = None

        self.min_zoom = 0.5
        self.max_zoom = 1.5
        self.zoom_step = 0.1

    def get_tile_size(self):
        return int(TILE_SIZE * self.zoom)

    def screen_to_cell(self, pos):
        tile_size = self.get_tile_size()

        return [
            int((pos[0] + self.x) // tile_size),
            int((pos[1] + self.y) // tile_size),
        ]

    def zoom_in(self):
        self.zoom += self.zoom_step

        if self.zoom > self.max_zoom:
            self.zoom = self.max_zoom

    def zoom_out(self):
        self.zoom -= self.zoom_step

        if self.zoom < self.min_zoom:
            self.zoom = self.min_zoom

    def panel_zoom_in(self):
        self.zoom += 0.25

        if self.zoom > self.max_zoom:
            self.zoom = self.max_zoom

    def panel_zoom_out(self):
        self.zoom -= 0.25

        if self.zoom < self.min_zoom:
            self.zoom = self.min_zoom

    def start_pan(self, mouse_pos):
        self.is_panning = True
        self.last_mouse_pos = mouse_pos

    def stop_pan(self):
        self.is_panning = False
        self.last_mouse_pos = None

    def update_pan(self, mouse_pos):
        if not self.is_panning:
            return

        if self.last_mouse_pos is None:
            self.last_mouse_pos = mouse_pos
            return

        dx = mouse_pos[0] - self.last_mouse_pos[0]
        dy = mouse_pos[1] - self.last_mouse_pos[1]

        self.x -= dx
        self.y -= dy

        if self.x < 0:
            self.x = 0

        if self.y < 0:
            self.y = 0

        self.last_mouse_pos = mouse_pos