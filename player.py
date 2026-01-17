import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import constants
from vector import Vector
import os
from pathlib import Path
import math

FLOOR = constants.SCREEN_HEIGHT - 11  # temp before map is added

script_dir = os.path.dirname(os.path.abspath(__file__))
sprite_path_l = os.path.join(script_dir, "spritesheet", "mush-l.png")
sprite_path_r = os.path.join(script_dir, "spritesheet", "mush-r.png")
print("line 16")
print(
    f"Checking sprite paths:\nLeft: {sprite_path_l} -> Exists: {os.path.exists(sprite_path_l)}\nRight: {sprite_path_r} -> Exists: {os.path.exists(sprite_path_r)}")

ROWS = 5
COLS = 6

player = {
    "x": constants.SCREEN_WIDTH // 2,
    "y": constants.SCREEN_HEIGHT - 40,
    "vx": 0,
    "vy": 0,
    "size": 20,
    "direction": "left",
}


class Spritesheet:
    def __init__(self, image, rows, cols, is_right=False):
        self.image = image
        self.rows = rows
        self.cols = cols
        self.is_right = is_right
        self.frame_width = image.get_width() // cols
        self.frame_height = image.get_height() // rows
        self.frame_count = 0
        self.current_row = 0  # 0=idle, 1=walk, 2=jump
        self.current_col = 0
        self.animation_speed = 5  # Lower=faster animation
        self.loaded = image.get_width() > 0

    def draw(self, canvas, x, y):
        if not self.loaded:
            # Fallback rectangle if image didn't load
            size = constants.TILE_SIZE
            canvas.draw_polygon([
                (x - size / 2, y - size / 2), (x + size / 2, y - size / 2),
                (x + size / 2, y + size / 2), (x - size / 2, y + size / 2)
            ], 1, "Black", "Red")
            return

        frame_x = self.current_col * self.frame_width
        frame_y = self.current_row * self.frame_height

        canvas.draw_image(
            self.image,
            (frame_x + self.frame_width // 2, frame_y + self.frame_height // 2),
            (self.frame_width, self.frame_height),
            (x, y),
            (self.frame_width * 2, self.frame_height * 2)
        )

    def next_frame(self, state):
        self.frame_count += 1

        if state == "walking":
            # Walking animation - use row 1 (second row)
            self.current_row = 1

            if self.frame_count >= self.animation_speed:
                self.frame_count = 0

                if self.is_right:
                    # Right-facing walking: loop through all columns in reverse
                    self.current_col = (self.current_col - 1) % self.cols
                    if self.current_col < 0:
                        self.current_col = self.cols - 1
                else:
                    # Left-facing walking: loop through all columns except last 2
                    self.current_col = (self.current_col + 1) % (self.cols - 2)

        elif state == "jumping":
            # Jumping animation - use row 2 (third row)
            self.current_row = 2
            # Keep same frame while jumping or implement jumping animation

        else:  # idle
            # Idle animation - use row 0 (first row)
            self.current_row = 0

            if self.frame_count >= self.animation_speed * 2:  # Slower animation
                self.frame_count = 0

                if self.is_right:
                    # Right idle: loop through columns 2-5 (skip first 2)
                    self.current_col = (self.current_col - 1) % (self.cols - 2) + 2
                    if self.current_col < 2:
                        self.current_col = self.cols - 1
                else:
                    # Left idle: loop through columns 0-3 (skip last 2)
                    self.current_col = (self.current_col + 1) % (self.cols - 2)

    def update_animation(self, is_moving):
        self.frame_count += 1

        if is_moving:
            # Walking animation
            self.current_row = 1  # Walking row
            if self.frame_count >= self.animation_speed:
                self.frame_count = 0

                if self.is_right_sheet:
                    # Right-facing animation (reverse order)
                    self.current_col = (self.current_col - 1) % self.cols
                else:
                    # Left-facing animation (skip last 2 columns)
                    self.current_col += 1
                    if self.current_col >= self.cols - 2:
                        self.current_col = 0
                    print(f"Left walk frame: {self.current_col}")  # Debug output
        else:
            # Idle animation
            self.current_row = 0  # Idle row
            if self.frame_count >= self.animation_speed * 2:
                self.frame_count = 0

                if self.is_right_sheet:
                    # Right idle (use columns 2-5)
                    self.current_col -= 1
                    if self.current_col < 2:
                        self.current_col = 5  # Loop back within 2-5 range
                else:
                    # Left idle (normal loop)
                    self.current_col = (self.current_col + 1) % self.cols

    def load_image_reliable(path):
        """Try multiple methods to load an image"""
        try:
            abs_path = Path(path).absolute()
            uri = abs_path.as_uri()

            # Try different loading methods
            for load_method in [
                lambda: simplegui.load_image(path),
                lambda: simplegui.load_image(uri),
                lambda: simplegui.load_image(f"file://{path}")
            ]:
                try:
                    img = load_method()
                    if img.get_width() > 0:
                        print(f"Successfully loaded: {path}")
                        return img
                except:
                    continue
        except Exception as e:
            print(f"Error loading {path}: {str(e)}")
        return None


# class Clock:
#     def __init__(self):
#         self.time = 0
#         self.walk_frame_duration = 5  # Faster animation for walking
#         self.idle_frame_duration = 10  # Slower animation for idle
#
#     def tick(self):
#         self.time += 1
#
#     def should_animate_walk(self):
#         return self.time % self.walk_frame_duration == 0
#
#     def should_animate_idle(self):
#         return self.time % self.idle_frame_duration == 0


class Health:
    def __init__(self, max_health):
        self.max_health = constants.LIVES
        self.current_health = max_health

        # Load heart image directly in the Health class
        self.heart_image = simplegui.load_image(constants.HEART_IMAGE_URL)

        # loading the image dirctly
        base_dir = os.path.abspath("assets")
        base_uri = f"file:///{base_dir.replace('\\', '/')}"
        life_uri = f"{base_uri}/ui/life.png"

        self.heart_image = simplegui.load_image(life_uri)

    def life_lost(self):
        # Current health decreases by 1
        if self.current_health > 0:
            self.current_health -= 1

    def reset(self):
        self.current_health = self.max_health

    def draw(self, canvas):
        if self.heart_image.get_width() > 0:  # Right now the heart lives dont load
            for i in range(self.current_health):
                x = constants.SCREEN_WIDTH - (constants.HEART_IMAGE_SIZE[0] + constants.HEART_IMAGE_SPACING) * (i + 1)
                y = constants.HEART_IMAGE_SPACING + constants.HEART_IMAGE_SIZE[1] / 2
                canvas.draw_image(self.heart_image,
                                  (self.heart_image.get_width() / 2, self.heart_image.get_height() / 2),
                                  (self.heart_image.get_width(), self.heart_image.get_height()),
                                  (x, y),
                                  constants.HEART_IMAGE_SIZE)
        else:
            # Image doesnt work so for now lives are rectangles
            for i in range(self.current_health):
                x = constants.SCREEN_WIDTH - (constants.HEART_IMAGE_SIZE[0] + constants.HEART_IMAGE_SPACING) * (i + 1)
                y = constants.HEART_IMAGE_SPACING
                canvas.draw_polygon([
                    (x, y),
                    (x + constants.HEART_IMAGE_SIZE[0], y),
                    (x + constants.HEART_IMAGE_SIZE[0], y + constants.HEART_IMAGE_SIZE[1]),
                    (x, y + constants.HEART_IMAGE_SIZE[1])
                ], 1, "Red", "Red")


class Player:
    def __init__(self, pos):
        self.pos = pos
        self.size = (constants.TILE_SIZE,
                     constants.TILE_SIZE)  # Size of the character (width and height) same as tile for consistency
        self.speed = constants.PLAYER_SPEED  # current speed
        self.on_ground = False
        self.on_block = False
        self.vel = Vector(0, 0)
        self.default_speed = constants.DEFAULT_PLAYER_SPEED  # Save default speed
        self.health = Health(constants.LIVES)  # Initialize health with 3 hearts
        self.on_moss = False
        self.direction = "left"

        self.animation_counter = 0
        self.animation_speed = 5

        script_dir = os.path.dirname(os.path.abspath(__file__))
        sprite_path_l = os.path.join(script_dir, "spritesheet", "mush-l.png")
        sprite_path_r = os.path.join(script_dir, "spritesheet", "mush-r.png")

        player_image_l = Spritesheet.load_image_reliable(sprite_path_l)
        player_image_r = Spritesheet.load_image_reliable(sprite_path_r)

        # Initialize spritesheets with proper parameters
        self.sprite_left = Spritesheet(player_image_l, ROWS, COLS, is_right=False)
        self.sprite_right = Spritesheet(player_image_r, ROWS, COLS, is_right=True)

        self.current_sprite = self.sprite_left
        self.animation_state = "idle"
        self.animation_speed = 5  # Adjust this value to control animation speed

        print(f"Loading left sprite from: {sprite_path_l}")
        print(f"Loading right sprite from: {sprite_path_r}")

        print("Sprite Right Path:", sprite_path_r)
        print("Sprite Left Path:", sprite_path_l)
        print("Heart Image Path:", constants.HEART_IMAGE_URL)

    def draw(self, canvas):

        if not (self.on_ground or self.on_block):
            self.animation_state = "jumping"
        elif abs(self.vel.x) > 0.1:  # If player is moving horizontally
            self.animation_state = "walking"
        else:
            self.animation_state = "idle"

            # Set the correct sprite based on direction
        if self.direction == "left":
            self.current_sprite = self.sprite_left
        else:
            self.current_sprite = self.sprite_right

            # Update animation frame
        self.current_sprite.next_frame(self.animation_state)

        # Draw the player
        self.current_sprite.draw(canvas, self.pos.x, self.pos.y)

        # Draw health (keep this as is)
        self.health.draw(canvas)
        #
        # # Draw
        # self.current_sprite.draw(canvas, self.pos.x, self.pos.y)
        # self.health.draw(canvas)
        # Draw a rectangle representing the character
        # canvas.draw_polygon([
        #     # drawing a polygon with the character's position and size
        #     (self.pos.x - self.size[0] / 2, self.pos.y - self.size[1] / 2),
        #     (self.pos.x + self.size[0] / 2, self.pos.y - self.size[1] / 2),
        #     (self.pos.x + self.size[0] / 2, self.pos.y + self.size[1] / 2),
        #     (self.pos.x - self.size[0] / 2, self.pos.y + self.size[1] / 2)
        # ], 1, "Black", "Red")

        # self.animation_counter += 1
        #
        # # Choose sprite based on direction
        # if self.direction == "left":
        #     sprite = self.sprite_left
        # else:
        #     sprite = self.sprite_right
        #
        # # Set animation row based on state
        # if not self.on_ground and not self.on_block:
        #     sprite.row = 2  # Jumping
        # elif abs(self.vel.x) > 0.1:  # Moving
        #     sprite.row = 1  # Walking
        #     if self.animation_counter % self.animation_speed == 0:
        #         sprite.next_frame(state=self.direction == "right")
        # else:
        #     sprite.row = 0  # Idle
        #     if self.animation_counter % (self.animation_speed * 2) == 0:
        #         sprite.next_frame(state=self.direction == "right")
        #
        # sprite.draw(canvas, self.pos.x, self.pos.y)
        #
        # # Draw the sprite
        # # current_sprite.draw(canvas, self.pos.x, self.pos.y)
        #
        #
        # # Draws the player's health
        # self.health.draw(canvas)

    def move(self, left, right, jump):
        screen_scroll = [0, 0]
        # self.is_walking = False
        self.vel.x = 0  # Reset horizontal velocity each frame

        if left:
            self.vel.x = -self.speed
            self.direction = "left"  # This is crucial for animation
        elif right:
            self.vel.x = self.speed
            self.direction = "right"

        # self.vel.x = 0
        #     if left:
        #         self.vel.x = -self.speed
        #         self.direction = "left"
        #         # self.is_walking = True
        #     elif right:
        #         self.vel.x = self.speed
        #         self.direction = "right"
        # self.is_walking = True

        if (self.on_ground or self.on_block) == False:
            self.vel.y += constants.GRAVITY
        elif jump and (self.on_ground or self.on_block):  # only when on ground can character jump
            self.vel.y = constants.JUMP_POWER
        else:
            self.vel.y = 0

        # preventing character from falling forever
        if self.pos.y >= FLOOR:
            self.pos.y = FLOOR
            # check if character is on the ground
            self.on_ground = True
        else:
            self.on_ground = False

        if self.vel.y > constants.TERMINAL_VELOCITY:
            self.vel.y = constants.TERMINAL_VELOCITY
        self.pos.add(self.vel)

        # updating character x coords based on player inputs

        vel_x = 0
        if right:
            vel_x = constants.PLAYER_SPEED
        if left:
            vel_x = -constants.PLAYER_SPEED
        self.vel.x = vel_x

        # reducing the height
        # not working right now
        # if jump and (self.on_ground or self.on_block):
        #     #print(f"jumping{self.on_moss}")
        #     if self.on_moss:
        #         # print (self.vel.y)
        #         self.vel.y = constants.JUMP_POWER * 0.1
        #         # print(self.vel.y)
        #     else:
        #         self.vel.y = constants.JUMP_POWER

        # adjusting screen scroll based on player's position
        if self.pos.x > (constants.SCREEN_WIDTH - constants.SCROLL_THRESH):  # check right side
            screen_scroll[0] = (constants.SCREEN_WIDTH - constants.SCROLL_THRESH) - self.pos.x
            self.pos.x = constants.SCREEN_WIDTH - constants.SCROLL_THRESH  # stop player moving when near right edge

        if self.pos.x < constants.SCROLL_THRESH:  # check left side
            screen_scroll[0] = constants.SCROLL_THRESH - self.pos.x
            self.pos.x = constants.SCROLL_THRESH  # stop player moving when near left edge

        # if self.pos.y > (constants.SCREEN_HEIGHT - constants.SCROLL_THRESH):  # check bottom # temp removed to stop player endless falling
        #     screen_scroll[1] = (constants.SCREEN_HEIGHT - constants.SCROLL_THRESH) - self.pos.y
        #     self.pos.y = constants.SCREEN_HEIGHT - constants.SCROLL_THRESH  # stop player moving when near bottom

        if self.pos.y < constants.SCROLL_THRESH:  # check top
            screen_scroll[1] = constants.SCROLL_THRESH - self.pos.y
            self.pos.y = constants.SCROLL_THRESH  # stop player moving when near top

        return screen_scroll

    def is_on_block(self, block):
        # player's bottom edge
        player_bottom = self.pos.y + self.size[1] / 2

        # block's top edge
        block_top = block.center[1] - block.size[1] / 2

        # check if the players bottom is close to the blocks top
        if abs(player_bottom - block_top) < 5:  # tolerance for inaccuracies

            player_left = self.pos.x - self.size[0] / 2
            player_right = self.pos.x + self.size[0] / 2
            block_left = block.center[0] - block.size[0] / 2
            block_right = block.center[0] + block.size[0] / 2

            if (player_right > block_left and player_left < block_right):
                return True
        return False

    def reset_speed(self):
        # reset the player's speed to the default value
        self.speed = self.default_speed

# example usage
# player = Player(Vector(100, 100))