"""
Platformer Game
"""
import arcade

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 5
TILE_SCALING = 0.5

# Konstanten für die Hintergrundbewegung
BACKGROUND_SCALING = 1.0
BACKGROUND_SPEED = 2


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        # Our physics engine
        self.physics_engine = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        # Keep track of the score
        self.score = 0

        #Variable für Hintergund
        self.background_list = None
        self.background_sprite = []

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Setup the GUI Camera
        self.gui_camera = arcade.camera.Camera2D()

        # Keep track of the score
        self.score = 0

        #Player Scene
        self.scene = arcade.Scene()

        # Create the Sprite lists
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls")

        # Set up the player, specifically placing it at these coordinates.
        image_source = "Sprites/Dino/Dino 1.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 120
        self.player_sprite.center_y = 112
        self.scene.add_sprite("Player", self.player_sprite)

        # Create the ground
        # This shows using a loop to place multiple sprites horizontally
        for x in range(0, 1250, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.scene.add_sprite("Walls", wall)

        # Put some crates on the ground
        # This shows using a coordinate list to place sprites
        coordinate_list = [[512, 96], [256, 96], [768, 96]]

        for coordinate in coordinate_list:
            # Add a crate on the ground
            wall = arcade.Sprite(
                ":resources:images/tiles/boxCrate_double.png", TILE_SCALING
            )
            wall.position = coordinate
            self.scene.add_sprite("Walls", wall)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=1, walls=self.scene["Walls"]
        )

        #Hintergrund
        self.background_list = arcade.SpriteList()

        #Zwei Hintergrund sprites
        for i in range (2):
            background = arcade.Sprite(
                "Sprites/Background.png",
                BACKGROUND_SCALING
            )
            background.center_x = background.width * i
            background.center_y = SCREEN_HEIGHT // 2
            self.background_sprite.append(background)
            self.background_list.append(background)

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        #Hintergrund zuerst zeichnen
        self.background_list.draw()

        # Draw our Scene
        self.scene.draw(pixelated = True)

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(
            score_text,
            10,
            10,
            arcade.csscolor.WHITE,
            18,
            font_name="Consolas",
        )

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = 20

    def on_update(self, delta_time):
        """Movement and game logic"""
        #Hintergrund bewegen
        for background in self.background_sprite:
            background.center_x -= BACKGROUND_SPEED

        if background.right <= 0:
            background.left = max(sprite.right for sprite in self.background_sprite)

        # Move the player with the physics engine
        self.physics_engine.update()

def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()