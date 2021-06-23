"""
Slime Adventure Game
"""
import arcade
from tkinter import messagebox

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Slime Adventure"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 0.5
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 7
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 200
RIGHT_VIEWPORT_MARGIN = 200
BOTTOM_VIEWPORT_MARGIN = 150
TOP_VIEWPORT_MARGIN = 100

PLAYER_START_X = 64
PLAYER_START_Y = 225

#levels
level = 1



class InstructionView(arcade.View):
    def on_show(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.DARK_GREEN)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        img = arcade.load_texture('background.jpg')
        arcade.draw_lrwh_rectangle_textured(0, 0, 1000, 650, img)

        arcade.draw_text("Slime Adventure", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.BLACK, font_size=80, anchor_x="center")
        arcade.draw_text("Click to Play", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")


    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        game_view = GameView()
        game_view.setup(level)
        self.window.show_view(game_view)

class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):

        # Background Music
        arcade.Window.music.play(0.1)

        # Call the parent class and set up the window
        super().__init__()

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.flags_list = None
        self.coin_list = None
        self.wall_list = None
        self.foreground_list = None
        self.background_list = None
        self.player_list = None

        # Timer for the GAMERS and SPEEDRUNERS lol
        self.total_time = 0.0

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player_list,
            platforms=self.wall_list,
            gravity_constant=GRAVITY,
        )

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Keep track of the score
        self.score = 0
        self.level = 1

        self.upheld = False


        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound("slime.ogg")
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav")


    def setup(self, level):
        """ Set up the game here. Call this function to restart the game. """

        self.background = arcade.load_texture("backgroundold.jpg")



        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # More time stuff
        self.total_time = 0.0

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.foreground_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.flags_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Set up the player, specifically placing it at these coordinates.
        image_source = "player.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_list.append(self.player_sprite)

        # --- Load in a map from the tiled editor ---

        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Platforms'
        # Name of the layer that has items for pick-up
        coins_layer_name = 'Coins'
        # Name of the layer that has items for foreground
        foreground_layer_name = 'Foreground'
        # Name of the layer that has items for background
        background_layer_name = 'Background'

        flags_layer_name = 'Flags'

        # Map name
        map_name = f"map_{level}.tmx"

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)


        # -- Background
        self.background_list = arcade.tilemap.process_layer(my_map,
                                                            background_layer_name,
                                                            TILE_SCALING)

        # -- Foreground
        self.foreground_list = arcade.tilemap.process_layer(my_map,
                                                            foreground_layer_name,
                                                            TILE_SCALING)

        self.flags_list = arcade.tilemap.process_layer(my_map, flags_layer_name , TILE_SCALING)

        # -- PlatformsCoins
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platforms_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        # -- Coins
        self.coin_list = arcade.tilemap.process_layer(my_map,
                                                      coins_layer_name,
                                                      TILE_SCALING,
                                                      use_spatial_hash=True)

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             GRAVITY)

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen to the background color
        arcade.start_render()

        # Calculate minutes
        minutes = int(self.total_time) // 6

        # Calculate seconds by using a modulus (remainder)
        seconds = int(self.total_time) % 60
        # Figure out our output
        output = f"Time: {minutes:02d}:{seconds:02d}"

        # Draw the background texture
        arcade.draw_lrwh_rectangle_textured(self.view_left, self.view_bottom,
        SCREEN_WIDTH, SCREEN_HEIGHT,
        self.background)


        # Draw our sprites
        self.wall_list.draw()
        self.background_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()
        self.player_list.draw()
        self.flags_list.draw()
        self.foreground_list.draw()


        # Output the timer text.
        # First a dark green background for a shadow effect
        arcade.draw_text(
            output,
            start_x=10 + self.view_left,
            start_y=60 + self.view_bottom,
            color=arcade.csscolor.DARK_GREEN,
            font_size=40,
        )
        # Now in lime green, slightly shifted
        arcade.draw_text(
            output,
            start_x=15 + self.view_left,
            start_y=65 + self.view_bottom,
            color=arcade.csscolor.LIME_GREEN,
            font_size=40,
        )

        # Draw the score in the lower left
        score_text = f"Score: {self.score}"

        # First a dark green background for a shadow effect
        arcade.draw_text(
            score_text,
            start_x=10 + self.view_left,
            start_y=10 + self.view_bottom,
            color=arcade.csscolor.DARK_GREEN,
            font_size=40,
        )
        # Now in lime green, slightly shifted
        arcade.draw_text(
            score_text,
            start_x=15 + self.view_left,
            start_y=15 + self.view_bottom,
            color=arcade.csscolor.LIME_GREEN,
            font_size=40,
        )

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.upheld = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

         # Cheats
        if key == arcade.key.KEY_6:
            self.level = self.level + 1
            self.setup(self.level)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0
        elif key == arcade.key.UP or key == arcade.key.W:
            self.upheld = False

    def update(self, delta_time):
        """ Movement and game logic """



        # Move the player with the physics engine
        self.physics_engine.update()

        # fucking magic or some shit idk
        self.total_time += delta_time

        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list)
        flags_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.flags_list)

        if self.physics_engine.can_jump() and self.upheld == True:
            self.player_sprite.change_y = PLAYER_JUMP_SPEED
            arcade.play_sound(self.jump_sound)

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Add one to the score
            self.score += 1

        for flags in flags_hit_list:
            flags.remove_from_sprite_lists()
            try:
                self.level = self.level + 1
                self.setup(self.level)
            except:
                print("debuginfo: no more levels, game exiting")
                exit()

            print(self.level)
            if self.level == 3:
                self.background = arcade.load_texture("backgroundcave.jpg")
                arcade.draw_lrwh_rectangle_textured(self.view_left, self.view_bottom,
                                                    SCREEN_WIDTH, SCREEN_HEIGHT,
                                                    self.background)
            else:
                print("debuginfo: level is not a cave")
        # Track if we need to change the viewport
        changed_viewport = False

        # Did the player fall off the map?
        if self.player_sprite.center_y < -100:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True
            arcade.play_sound(self.game_over)



        # --- Manage Scrolling ---

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed_viewport = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed_viewport = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed_viewport = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed_viewport = True

        if changed_viewport:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


def main():
    """ Main method """

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.Window.music = arcade.Sound("backgroundmusic.mp3", streaming=True)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()



if __name__ == "__main__":
    main()