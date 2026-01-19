import constants
import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
from constants import SCROLL_THRESH_Y
from vector import Vector
import os
from pathlib import Path


class Spritesheet:
    def __init__(self, image, rows, cols, is_right):
        self.image = image
        self.rows = rows
        self.cols = cols
        # self.is_right = False
        self.is_right = is_right

        self.frame_width = image.get_width() // cols
        self.frame_height = image.get_height() // rows

        self.frame_count = 0
        #  row 0 = idle, 1 = walk ,2 = jump
        self.current_row = 0
        self.current_col = 0

        self.animation_speed = 100
        #  checking that the image is there
        self.loaded = image.get_width() > 0

    def draw(self, canvas, x, y):
        if not self.loaded:
            # Fallback rectangle if image didn't load
            size = constants.TILE_SIZE
            canvas.draw_polygon(
                [
                    (x - size / 2, y - size / 2),
                    (x + size / 2, y - size / 2),
                    (x + size / 2, y + size / 2),
                    (x - size / 2, y + size / 2),
                ],
                1,
                "Black",
                "Red",
            )
            # return "image not loaded"
        else:
            #  load the image
            frame_x = self.current_col * self.frame_width
            frame_y = self.current_row * self.frame_height

            canvas.draw_image(
                self.image,
                (frame_x + self.frame_width // 2, frame_y + self.frame_height // 2),
                (self.frame_width, self.frame_height),
                (x, y),
                (self.frame_width * 1.5, self.frame_height * 1.1),
            )

    def next_frame(self, state):

        self.animation_speed = 5

        if state == "walking":
            # Walking animation - use row 1 (second row)
            if self.frame_count >= self.animation_speed:
                self.current_row = 1
                if self.is_right:
                    self.current_col = (self.current_col - 1) % (self.cols - 2)
                else:
                    self.current_col = (self.current_col + 1) % (self.cols - 2)

                self.frame_count = 0
            self.frame_count += 1

        else:  # idle
            self.current_row = 2
            if self.is_right:
                self.current_col = 2
            else:
                self.current_col = 0

    def load_image_reliable(path):
        """Try multiple methods to load an image"""
        try:
            abs_path = Path(path).absolute()
            uri = abs_path.as_uri()

            # Try different loading methods
            for load_method in [
                lambda: simplegui.load_image(path),
                lambda: simplegui.load_image(uri),
                lambda: simplegui.load_image(f"file://{path}"),
            ]:
                try:
                    img = load_method()
                    if img.get_width() > 0:
                        print(f"Successfully loaded: {path}")
                        return img
                except (FileNotFoundError, OSError):
                    continue
        except Exception as e:
            print(f"Error loading {path}: {str(e)}")
        return None


class Health:
    def __init__(self, max_health, game):
        self.game = game
        self.max_health = constants.LIVES
        self.current_health = max_health

        # Load heart image directly in the Health class
        base_dir = os.path.abspath("assets")
        base_uri = f"file:///{base_dir.replace('\\', '/')}"
        life_uri = f"{base_uri}/ui/life.png"

        self.heart_image = simplegui.load_image(life_uri)

    def life_lost(self):
        # Current health decreases by 1
        if self.current_health > 0:
            self.current_health -= 1

    def life_gained(self, amount):
        # current health increases by {amount}
        if self.current_health + amount <= self.max_health:
            self.current_health += amount
        else:
            self.current_health = self.max_health

    def reset(self):
        self.current_health = self.max_health

    def draw(self, canvas):
        if self.heart_image.get_width() > 0:
            for i in range(self.current_health):
                x = constants.SCREEN_WIDTH - (
                    constants.HEART_IMAGE_SIZE[0] + constants.HEART_IMAGE_SPACING
                ) * (i + 1)
                y = constants.HEART_IMAGE_SPACING + constants.HEART_IMAGE_SIZE[1] / 2
                canvas.draw_image(
                    self.heart_image,
                    (
                        self.heart_image.get_width() / 2,
                        self.heart_image.get_height() / 2,
                    ),
                    (self.heart_image.get_width(), self.heart_image.get_height()),
                    (x, y),
                    constants.HEART_IMAGE_SIZE,
                )


class Player:
    def __init__(self, pos, game):
        self.game = game
        self.pos = pos
        self.size = (
            constants.TILE_SIZE,
            constants.TILE_SIZE,
        )  # Size of the character (width and height) same as tile for consistancy
        self.speed = constants.PLAYER_SPEED
        self.on_ground = False
        self.vel = Vector(0, 0)
        self.on_block = False
        self.health = Health(
            constants.LIVES, self.game
        )  # Initialize health with 3 hearts
        self.gravity = constants.GRAVITY
        self.speed_time = 0
        self.gravity_time = 0
        self.checkpoint = Vector(0, 0)
        self.uptime = 0
        self.direction = "left"

        self.animation_speed = 0

        # loading the sprite image directly
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sprite_path_l = os.path.join(script_dir, "sprite_sheet", "sheet", "mush-l.png")
        sprite_path_r = os.path.join(script_dir, "sprite_sheet", "sheet", "mush-r.png")

        player_image_l = Spritesheet.load_image_reliable(sprite_path_l)
        player_image_r = Spritesheet.load_image_reliable(sprite_path_r)

        self.sprite_left = Spritesheet(
            player_image_l, constants.ROWS, constants.COLS, is_right=False
        )
        self.sprite_right = Spritesheet(
            player_image_r, constants.ROWS, constants.COLS, is_right=True
        )

        self.current_sprite = self.sprite_left
        self.animation_state = "idle"
        self.animation_speed = 15  # Adjust this value to control animation speed

        self.on_block_counter = 0

    def draw(self, canvas):

        if abs(self.vel.x) > 0.1:

            self.animation_state = "walking"
        else:
            self.animation_state = "idle"

        if self.direction == "right":
            self.current_sprite = self.sprite_right
        else:
            self.current_sprite = self.sprite_left

        # Update and draw
        self.current_sprite.next_frame(self.animation_state)
        self.current_sprite.draw(canvas, self.pos.x, self.pos.y)

        self.update_powerups()

        self.health.draw(canvas)

        self.uptime += 1

    def return_to_checkpoint(self):
        self.game.return_to_checkpoint()
        self.uptime = 0

    def collect_powerup(self, type):
        if type == "health":
            self.health.life_gained(1)
        elif type == "speed":
            self.speed_time += 600
        elif type == "gravity":
            self.gravity_time += 600
        elif type == "damage":
            self.health.life_lost()
            self.return_to_checkpoint()
        elif type == "ladder":
            if self.game.current_level < 3:
                self.game.current_level += 1
                self.return_to_checkpoint()

    def update_powerups(self):

        if self.speed_time > 0:
            self.speed_time -= 1
            self.speed = constants.PLAYER_SPEED * 1.2
            if self.speed_time == 0:
                self.speed = constants.PLAYER_SPEED
        if self.gravity_time > 0:
            self.gravity_time -= 1
            self.gravity = constants.GRAVITY * 0.8
            if self.gravity_time == 0:
                self.gravity = constants.GRAVITY

    def move(self, left, right, jump):
        screen_scroll = [0, 0]

        self.vel.x = 0  # Reset horizontal velocity each frame
        if left:
            self.vel.x = -self.speed
            self.direction = "left"  # This is crucial for animation
        elif right:
            self.vel.x = self.speed
            self.direction = "right"

        if not self.on_ground:
            self.vel.y += self.gravity
        elif jump and (self.on_ground):  # only when on ground can character jump
            self.vel.y = constants.JUMP_POWER
        else:
            self.vel.y = 0

        if self.vel.y > constants.TERMINAL_VELOCITY:
            self.vel.y = constants.TERMINAL_VELOCITY

        if self.uptime >= 60:
            self.pos.add(self.vel)

        # updating character x coords based on player inputs
        vel_x = 0
        if right:
            vel_x = self.speed
        if left:
            vel_x = -self.speed
        self.vel.x = vel_x

        # adjusting screen scroll based on players position
        if self.pos.x > (
            constants.SCREEN_WIDTH - constants.SCROLL_THRESH_X
        ):  # check right side
            screen_scroll[0] = (
                constants.SCREEN_WIDTH - constants.SCROLL_THRESH_X
            ) - self.pos.x
            self.pos.x = (
                constants.SCREEN_WIDTH - constants.SCROLL_THRESH_X
            )  # stop player moving when near right edge

        if self.pos.x < constants.SCROLL_THRESH_X:  # check left side
            screen_scroll[0] = constants.SCROLL_THRESH_X - self.pos.x
            self.pos.x = (
                constants.SCROLL_THRESH_X
            )  # stop player movinf when near left edge

        if self.pos.y > (constants.SCREEN_HEIGHT - SCROLL_THRESH_Y):  # check bottom
            screen_scroll[1] = (constants.SCREEN_HEIGHT - SCROLL_THRESH_Y) - self.pos.y
            self.pos.y = (
                constants.SCREEN_HEIGHT - SCROLL_THRESH_Y
            )  # stop player moving when near bottom

        if self.pos.y < constants.SCROLL_THRESH_Y:  # check top
            screen_scroll[1] = constants.SCROLL_THRESH_Y - self.pos.y
            self.pos.y = constants.SCROLL_THRESH_Y  # stop player moving when near top

        if self.on_ground or self.on_block:
            self.vel.x *= 0.8  # Friction factor

            # Cap minimum velocity to prevent micro-movements
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        if abs(self.vel.y) < 0.1:
            self.vel.y = 0

        return screen_scroll

    def is_on_tile(self, tile):
        # players bottom edge
        player_bottom = self.pos.y + self.size[1] / 2
        # tiles top edge
        tile_top = tile[2]

        # check if the players bottom is close to the tiles top
        if abs(player_bottom - tile_top) < 15:  # tolerance for inaccuracies
            player_left = self.pos.x - self.size[0] / 2
            player_right = self.pos.x + self.size[0] / 2
            tile_left = tile[1]
            tile_right = tile[1] + constants.TILE_SIZE

            if player_right > tile_left and player_left < tile_right:
                self.pos.y = tile_top - self.size[1] / 2
                self.vel.y = 0
                return True
        return False

    def reset_speed(self):
        # reset the player's speed to the default value
        self.speed = self.default_speed
