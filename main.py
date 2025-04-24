"""
Platformer Game mit Laufanimation
"""
import arcade
import random
import os

# Constants
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 500
SCREEN_TITLE = "Dino Runner"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 5
TILE_SCALING = 0.5

# Konstanten für die Hintergrundbewegung
BACKGROUND_SCALING = 1.0
BACKGROUND_SPEED = 0.5

# Animationseinstellungen
UPDATES_PER_FRAME = 8  # Geschwindigkeit der Animation

class Player(arcade.Sprite):
    def __init__(self):
        # Lade die Animationstexturen
        self.run_textures = []
        for i in range(1, 7):
            texture = arcade.load_texture(f"Sprites/Dino/Dino {i}.png")
            self.run_textures.append(texture)

        super().__init__(self.run_textures[0], CHARACTER_SCALING)

        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        self.is_jumping = False

    def update_animation(self, delta_time: float = 1/60):
        # Nur animieren wenn am Boden
        if not self.is_jumping:
            self.cur_texture += 1
            if self.cur_texture // UPDATES_PER_FRAME >= len(self.run_textures):
                self.cur_texture = 0

            self.texture = self.run_textures[self.cur_texture // UPDATES_PER_FRAME]

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.scene = None
        self.player_sprite = None
        self.physics_engine = None
        self.gui_camera = None
        self.score = 0

        # Variable für Hintergrund
        self.background_list = None
        self.background_sprite = []
        self.background_list2 = None
        self.background_sprite2 = []

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        # Setup the GUI Camera
        self.gui_camera = arcade.camera.Camera2D()

        # Keep track of the score
        self.score = 0

        # Player Scene
        self.scene = arcade.Scene()

        # Create the Sprite lists
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls")

        # Spieler erstellen
        self.player_sprite = Player()
        self.player_sprite.center_x = 120
        self.player_sprite.center_y = 112
        self.scene.add_sprite("Player", self.player_sprite)

        # Boden erstellen
        for x in range(0, 1600, 64):
            wall = arcade.Sprite("Sprites/Sand.jpg", 0.33)
            wall.center_x = x
            wall.center_y = 0
            self.scene.add_sprite("Walls", wall)

        # Physik-Engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            gravity_constant=1,
            walls=self.scene["Walls"]
        )

        # Hintergrund
        self.background_list = arcade.SpriteList()
        self.background_list2 = arcade.SpriteList()

        # Zwei Hintergrund sprites
        for i in range(2):
            background = arcade.Sprite(
                "Sprites/Hintergrund.png",
                BACKGROUND_SCALING
            )
            background.center_x = background.width * i
            background.center_y = SCREEN_HEIGHT // 2
            self.background_sprite.append(background)
            self.background_list.append(background)

        for i in range(2):
            background2 = arcade.Sprite(
                "Sprites/Mittelgrund.png",
                BACKGROUND_SCALING
            )
            background2.center_x = background2.width * i
            background2.center_y = 144
            self.background_sprite2.append(background2)
            self.background_list.append(background2)

    def on_draw(self):
        """Render the screen."""
        self.clear()

        # Hintergrund zuerst zeichnen
        self.background_list.draw()

        # Scene zeichnen
        self.scene.draw(pixelated=True)

        # GUI
        self.gui_camera.use()
        score_text = f"Score: {int(self.score)}"
        arcade.draw_text(
            score_text,
            1320, 480,
            arcade.csscolor.BLACK,
            18,
            font_name="Consolas"
        )

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if key == arcade.key.UP or key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = 20
                self.player_sprite.is_jumping = True

    def on_update(self, delta_time):
        """Bewegungslogik und Spielphysik"""
        # Hintergrund bewegen
        for background in self.background_sprite:
            background.center_x -= BACKGROUND_SPEED
            if background.right <= 0:
                background.left = max(sprite.right for sprite in self.background_sprite)

        for background2 in self.background_sprite2:
            background2.center_x -= BACKGROUND_SPEED * 4
            if background2.right <= 0:
                background2.left = max(sprite.right for sprite in self.background_sprite2)

        # Physik-Engine und Animation aktualisieren
        self.physics_engine.update()

        # Springstatus überprüfen
        self.player_sprite.is_jumping = not self.physics_engine.can_jump()

        # Animation aktualisieren
        self.player_sprite.update_animation(delta_time)

        # Score erhöhen
        self.score += delta_time * 10

def main():
    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
