"""
Platformer Game
"""
import arcade

# Constants
SCREEN_WIDTH = 1000 * 2
SCREEN_HEIGHT = 650 * 2 
SCREEN_TITLE = "Platformer"

CHARACTER_SCALING = 3
TILE_SCALING = 1
COIN_SCALING = 0.5
TILE_WIDTH = 70
TILE_SPACING = TILE_WIDTH * TILE_SCALING

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 15

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = SCREEN_WIDTH * 0.4
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 100

AUTO_RUN_SPEED = 5



class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        self.score = 0

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        self.player_list = arcade.SpriteList()

        self.player_sprite = arcade.Sprite("police.png", CHARACTER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 120
        self.player_list.append(self.player_sprite)


        # Name of map file to load
        map_name = "level1.tmx"
        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Platforms'
        # Name of the layer that has items for pick-up
        coins_layer_name = 'Bonus'

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # -- Platforms
        self.wall_list = arcade.tilemap.process_layer(my_map, platforms_layer_name, TILE_SCALING)

        # -- Coins
        self.coin_list = arcade.tilemap.process_layer(my_map, coins_layer_name, TILE_SCALING)


        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             GRAVITY)

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        # Code to draw the screen goes here

        self.wall_list.draw()
        self.coin_list.draw()
        self.player_list.draw()

        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.RED, 28)

    # def on_key_press(self, key, modifiers):
    #     """Called whenever a key is pressed. """

    #     if key == arcade.key.UP or key == arcade.key.Z:
    #         if self.physics_engine.can_jump():
    #             self.player_sprite.change_y = PLAYER_JUMP_SPEED
    #     elif key == arcade.key.LEFT or key == arcade.key.Q:
    #         self.player_sprite.change_x = AUTO_RUN_SPEED // 2
    #     elif key == arcade.key.RIGHT or key == arcade.key.D:
    #         self.player_sprite.change_x = AUTO_RUN_SPEED + PLAYER_MOVEMENT_SPEED

    # def on_key_release(self, key, modifiers):
    #     """Called when the user releases a key. """

    #     if key == arcade.key.LEFT or key == arcade.key.Q:
    #         self.player_sprite.change_x = AUTO_RUN_SPEED
    #     elif key == arcade.key.RIGHT or key == arcade.key.D:
    #         self.player_sprite.change_x = AUTO_RUN_SPEED

    def process_keychange(self):
        """
        Called when we change a key up/down or we move on/off a ladder.
        """

        # Process left/right
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = AUTO_RUN_SPEED + PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = AUTO_RUN_SPEED // 2

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.Z:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.Q:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.LEFT or key == arcade.key.Q:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def on_update(self, delta_time):
        """ Movement and game logic """
        self.physics_engine.update()

        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False
        else:
            self.player_sprite.can_jump = True

         # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list)

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.kill()
            # Add one to the score
            self.score += int(coin.properties['score'])

        changed = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True

        if changed:
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
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()