"""
Platformer Game mit dynamischem Schwierigkeitsgrad
"""
import arcade
import random

# Constants
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 500
SCREEN_TITLE = "Dino Runner"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 5
OBSTACLE_SCALING = 2.5
TILE_SCALING = 0.5

# Konstanten für die Bewegung
BACKGROUND_SCALING = 1.0
BASE_SPEED = 10  # Grundgeschwindigkeit

# Animationseinstellungen
UPDATES_PER_FRAME = 8

class Player(arcade.Sprite):
    def __init__(self):
        self.run_textures = []
        for i in range(1, 7):
            texture = arcade.load_texture(f"Sprites/Dino/Dino {i}.png")
            self.run_textures.append(texture)

        super().__init__(self.run_textures[0], CHARACTER_SCALING)

        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        self.is_jumping = False

    def update_animation(self, delta_time: float = 1/60):
        if not self.is_jumping:
            self.cur_texture += 1
            if self.cur_texture // UPDATES_PER_FRAME >= len(self.run_textures):
                self.cur_texture = 0
            self.texture = self.run_textures[self.cur_texture // UPDATES_PER_FRAME]

class Obstacle(arcade.Sprite):
    def __init__(self, texture_path):
        super().__init__(texture_path, OBSTACLE_SCALING)
        self.bottom = 70
        self.left = SCREEN_WIDTH

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.scene = None
        self.player_sprite = None
        self.physics_engine = None
        self.gui_camera = None
        self.score = 0
        self.game_speed = BASE_SPEED
        self.spawn_timer = 0
        self.difficulty_level = 1
        self.max_difficulty = 20

        # Hintergrundvariablen
        self.background_list = None
        self.background_sprite = []
        self.midground_list = None
        self.midground_sprite = []
        self.ground_list = None
        self.ground_sprite = []

    def setup(self):
        self.gui_camera = arcade.camera.Camera2D()
        self.score = 0
        self.game_speed = BASE_SPEED
        self.difficulty_level = 1
        self.scene = arcade.Scene()
        self.obstacle_list = arcade.SpriteList()

        # Spieler erstellen
        self.player_sprite = Player()
        self.player_sprite.center_x = 120
        self.player_sprite.center_y = 112
        self.scene.add_sprite("Player", self.player_sprite)

        # Boden-SpriteList erstellen
        self.ground_list = arcade.SpriteList()
        self.scene.add_sprite_list("Walls", sprite_list=self.ground_list)

        # Bodensegmente erstellen
        for i in range(35):
            ground = arcade.Sprite("Sprites/Sand.jpg", 0.33)
            ground.left = ground.width * i
            ground.bottom = 0
            self.ground_sprite.append(ground)
            self.ground_list.append(ground)

        # Hintergrund-System
        self.background_list = arcade.SpriteList()
        self.midground_list = arcade.SpriteList()

        # Hintergrundebenen
        for i in range(2):
            bg = arcade.Sprite("Sprites/Hintergrund Nacht.png", BACKGROUND_SCALING)
            bg.center_x = bg.width * i
            bg.center_y = SCREEN_HEIGHT // 2
            self.background_sprite.append(bg)
            self.background_list.append(bg)

            mg = arcade.Sprite("Sprites/Mittelgrund Nacht.png", BACKGROUND_SCALING)
            mg.center_x = mg.width * i
            mg.center_y = 144
            self.midground_sprite.append(mg)
            self.midground_list.append(mg)

        # Physik-Engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            gravity_constant=1,
            walls=self.ground_list
        )

    def spawn_obstacle(self):
        """Erstellt ein neues Hindernis mit Schwierigkeitsanpassung"""
        # Schwierigkeitsabhängige Parameter
        obstacle_types = [
            ("Sprites/Cactus1.png", 70, 0.5),  # (Pfad, Höhe, Wahrscheinlichkeit)
            ("Sprites/Cactus2.png", 70, 0.3),
            ("Sprites/Bird.png", 150, 0.2)
        ]

        # Schwierigkeitsabhängige Anpassungen
        if self.difficulty_level > 3:
            obstacle_types.append(("Sprites/Cactus3.png", 70, 0.4))
        if self.difficulty_level > 5:
            obstacle_types[2] = ("Sprites/Bird.png", 170, 0.3)  # Höhere Vögel
        if self.difficulty_level > 7:
            obstacle_types.append(("Sprites/Bird2.png", 300, 0.2))

        # Normalisierung der Wahrscheinlichkeiten
        total_weight = sum(w for _, _, w in obstacle_types)
        normalized_types = [
            (path, height, weight / total_weight)
            for path, height, weight in obstacle_types
        ]
        texture_path, height, _ = random.choices(
            normalized_types,
            weights=[w for _, _, w in normalized_types],

            k=1
        )[0]

        obstacle = Obstacle(texture_path)
        obstacle.bottom = height
        self.obstacle_list.append(obstacle)

    def update_difficulty(self):
        """Passt den Schwierigkeitsgrad basierend auf dem Score an"""
        self.difficulty_level = min(
            self.max_difficulty,
            1 + int(self.score / 300)  # Alle 1000 Punkte +1 Level
        )

        # Geschwindigkeitssteigerung
        self.game_speed = BASE_SPEED * (1 + 0.2 * self.difficulty_level)

        # Sprungphysik anpassen
        self.physics_engine.gravity_constant = 1 + 0.1 * self.difficulty_level

    def on_draw(self):
        self.clear()
        self.background_list.draw()
        self.midground_list.draw()
        self.ground_list.draw()
        self.obstacle_list.draw(pixelated=True)
        self.scene.draw(pixelated=True)

        self.gui_camera.use()
        arcade.draw_text(
            f"Score: {int(self.score)}",
            1300, 465,
            arcade.csscolor.BLACK,
            24,
            font_name="Consolas"
        )

        # Schwierigkeitsgrad anzeigen
        arcade.draw_text(
            f"Level: {self.difficulty_level}",
            10, 465,
            arcade.csscolor.RED,
            24,
            font_name="Consolas"
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = 20 + 2 * self.difficulty_level  # Höhere Sprünge
                self.player_sprite.is_jumping = True

    def on_update(self, delta_time):
        # Schwierigkeit updaten
        self.update_difficulty()

        # Hindernis-Spawn-System
        self.spawn_timer += delta_time
        spawn_interval = max(0.5, 3 - 0.2 * self.difficulty_level)  # Schnelleres Spawning
        if self.spawn_timer > random.uniform(spawn_interval*0.5, spawn_interval*1.5):
            self.spawn_obstacle()
            self.spawn_timer = 0

        # Bewegungssystem
        speed_factor = self.game_speed / BASE_SPEED

        # Hintergrundbewegung
        for bg in self.background_sprite:
            bg.center_x -= BASE_SPEED * 0.2 * speed_factor
            if bg.right <= 0:
                bg.left = max(s.right for s in self.background_sprite)

        # Mittelgrundbewegung
        for mg in self.midground_sprite:
            mg.center_x -= BASE_SPEED * 0.5 * speed_factor
            if mg.right <= 0:
                mg.left = max(s.right for s in self.midground_sprite)

        # Bodenbewegung
        for ground in self.ground_sprite:
            ground.center_x -= self.game_speed
            if ground.right <= 0:
                ground.left = max(s.right for s in self.ground_sprite)

        # Hindernisse bewegen
        for obstacle in self.obstacle_list:
            obstacle.center_x -= self.game_speed
            if obstacle.right < 0:
                obstacle.remove_from_sprite_lists()

        # Kollisionsabfrage
        if arcade.check_for_collision_with_list(self.player_sprite, self.obstacle_list):
            arcade.exit()

        # Physik und Animation
        self.physics_engine.update()
        self.player_sprite.is_jumping = not self.physics_engine.can_jump()
        self.player_sprite.update_animation(delta_time)
        self.score += delta_time * 10 * speed_factor  # Schnellerer Score-Anstieg

def main():
    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
