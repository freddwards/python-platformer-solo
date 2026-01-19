import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import os
import csv
import math
import time

from vector import Vector
from player import Player
from level import Level
from level import Powerup
import constants


class Game:
    def __init__(self):
        self.state = "menu"
        self.running = True
        self.level = 1
        self.right = False
        self.left = False
        self.jump = False
        self.current_level = 0
        self.blocks = []
        self.powerups = []
        self.powerup_images = []
        self.moss = []
        self.tile_list = []

        # Declare player
        self.player = Player(Vector(200, 150), self)

        # Define world data
        self.loadImages()
        self.world_data = world_data = []
        self.loadLevel(self.current_level)
        self.screen_scroll = [0, 0]

        self.interaction = Interaction(self)
        # Declare level
        self.level = Level(self)
        # Process level data
        self.level.process_data(self.world_data, self.tile_list)

    def mouse_handler(self, pos):
        # handles mouse click
        self.mouse_pos = pos
        if self.state == "menu":
            self.state = "instruct"
        elif self.state == "instruct":
            self.state = "game"
            self.player.health.current_health = self.player.health.max_health

    def draw(self, canvas):
        # according to state (menu, game, game over) it draws the specific canvas
        if self.state == "menu":
            self.draw_menu(canvas)
        elif self.state == "game":
            self.draw_game(canvas)
        elif self.state == "instruct":
            self.draw_instructions(canvas)
        else:
            self.draw_game_over(canvas)

    def draw_menu(self, canvas):
        # draws main menu screen
        canvas.draw_text(
            "MUSHROOM DUNGEON",
            (constants.SCREEN_WIDTH // 2 - 275, constants.SCREEN_HEIGHT // 3 - 100),
            65,
            "White",
            "monospace",
        )

        # making "click to play" a clickable text
        text = "CLICK TO PLAY"
        text_width = frame.get_canvas_textwidth(text, 30, "monospace")
        text_x = constants.SCREEN_WIDTH // 2 - text_width // 2 - 25
        text_y = constants.SCREEN_HEIGHT // 2 + 100
        canvas.draw_text(text, (text_x, text_y), 35, "White", "monospace")

    def draw_instructions(self, canvas):
        # draws main menu screen
        canvas.draw_text(
            "INSTRUCTIONS",
            (constants.SCREEN_WIDTH // 2 - 275, constants.SCREEN_HEIGHT // 3 - 100),
            65,
            "White",
            "monospace",
        )

        # draw the instructions
        instructions = [
            "Instructions:",
            "• Use A to move left",
            "• Use D to move right",
            "• Space to jump",
            "• Collect powerups to gain abilities",
            "• Goal is to navigate the cave till the end",
            "Good luck!",
        ]

        # position of instructions below title
        start_y = constants.SCREEN_HEIGHT // 3 - 50
        line_height = 30

        for i, instruction in enumerate(instructions):
            y_pos = start_y + (i * line_height)
            canvas.draw_text(
                instruction,
                (constants.SCREEN_WIDTH // 2 - 215, y_pos),
                24,
                "White",
                "monospace",
            )

        # making "click to play" a clickable text
        text = "CLICK TO PLAY"
        text_width = frame.get_canvas_textwidth(text, 30, "monospace")
        text_x = constants.SCREEN_WIDTH // 2 - text_width // 2 - 25
        text_y = constants.SCREEN_HEIGHT // 2 + 100
        canvas.draw_text(text, (text_x, text_y), 35, "White", "monospace")

    def draw_game_over(self, canvas):
        # draws the game over screen
        canvas.draw_text(
            "GAME OVER",
            (constants.SCREEN_WIDTH // 2 - 200, constants.SCREEN_HEIGHT // 3 + 30),
            70,
            "Red",
            "monospace",
        )
        canvas.draw_text(
            "Press R to restart",
            (constants.SCREEN_WIDTH // 2 - 175, constants.SCREEN_HEIGHT // 2 - 25),
            30,
            "White",
            "monospace",
        )

    def draw_game(self, canvas):

        if self.player.health.current_health > 0:
            self.level.update(self.screen_scroll)
            self.level.draw(canvas)
            self.player.draw(canvas)
            self.update()
            for block in self.blocks:
                block.draw(canvas)
            for powerup in self.powerups:
                powerup.draw(canvas)
        else:
            self.state = "game_over"

    def update(self):
        # Call move method for player based on player inputs
        self.screen_scroll = self.player.move(
            self.left, self.right, self.jump
        )  # takes output for moving screen
        self.interaction.check_and_handle_collisions()

    def keyDown(self, key):  # Handle key presses
        if self.state == "game":
            if key == simplegui.KEY_MAP["d"]:
                self.right = True
            elif key == simplegui.KEY_MAP["a"]:
                self.left = True
            elif key == simplegui.KEY_MAP["space"]:
                self.jump = True
        elif self.state == "game_over" and key == simplegui.KEY_MAP["r"]:
            self.state = "game"
            # restarts the game fully
            global game
            game = Game()
            frame.set_draw_handler(game.draw)
            frame.set_keydown_handler(game.keyDown)
            frame.set_keyup_handler(game.keyUp)
            frame.set_mouseclick_handler(game.mouse_handler)

    def keyUp(self, key):  # Handle key releases
        if self.state == "game":
            if key == simplegui.KEY_MAP["d"]:
                self.right = False
            elif key == simplegui.KEY_MAP["a"]:
                self.left = False
            elif key == simplegui.KEY_MAP["space"]:
                self.jump = False

    def return_to_checkpoint(self):
        self.world_data = []
        self.loadLevel(self.current_level)
        self.screen_scroll = [0, 0]
        self.level = Level(self)
        self.level.process_data(self.world_data, self.tile_list)

    def loadImages(self):
        self.tile_list = []
        self.powerup_images = []

        # get the absolute path and convert to proper format (fix for images not loading)
        base_dir = os.path.abspath("assets")
        base_uri = f"file:///{base_dir.replace('\\', '/')}"

        for x in range(constants.TILE_TYPES):

            tile_uri = f"{base_uri}/tiles/{x}.png"
            print(f"Loading image: {tile_uri}")

            # load the image
            img = simplegui.load_image(tile_uri)

            self.tile_list.append(img)
            print(f"Loaded tile {x} - Dimensions: {img.get_width()}x{img.get_height()}")

        for x in range(constants.POWERUP_TYPES):

            powerup_uri = f"{base_uri}/powerups/{x}.png"
            print(f"Loading image: {powerup_uri}")

            # load the image
            img = simplegui.load_image(powerup_uri)

            # check if the image loaded properly
            if img.get_width() == 0:
                print(f"Image {x}.png didn't load properly - using placeholder")
                # create a placeholder blank image
                img = simplegui._create_blank_image(
                    constants.POWERUP_SIZE, constants.POWERUP_SIZE
                )
                img.fill((255, 255, 255))

            self.powerup_images.append(img)
            print(
                f"Loaded powerup {x} - Dimensions: {img.get_width()}x{img.get_height()}"
            )

    def loadLevel(self, level):
        self.world_data = []
        self.powerups = []
        for row in range(150):  # creating empty 150x150 world_data list
            r = [-1] * 150
            self.world_data.append(r)
        # loading level data from csv file into world_data
        with open(f"levels/level{level}_data.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    if tile == "H":
                        self.powerups.append(
                            Powerup(
                                self,
                                Vector(
                                    y * constants.TILE_SIZE, x * constants.TILE_SIZE
                                ),
                                0,
                            )
                        )
                    elif tile == "S":
                        self.powerups.append(
                            Powerup(
                                self,
                                Vector(
                                    y * constants.TILE_SIZE, x * constants.TILE_SIZE
                                ),
                                1,
                            )
                        )
                    elif tile == "G":
                        self.powerups.append(
                            Powerup(
                                self,
                                Vector(
                                    y * constants.TILE_SIZE, x * constants.TILE_SIZE
                                ),
                                2,
                            )
                        )
                    elif tile == "P":
                        self.player.pos.x = y * constants.TILE_SIZE
                        self.player.pos.y = x * constants.TILE_SIZE
                    elif tile == "20":
                        self.powerups.append(
                            Powerup(
                                self,
                                Vector(
                                    y * constants.TILE_SIZE, x * constants.TILE_SIZE
                                ),
                                3,
                            )
                        )
                    elif tile == "22":
                        self.powerups.append(
                            Powerup(
                                self,
                                Vector(
                                    y * constants.TILE_SIZE, x * constants.TILE_SIZE
                                ),
                                4,
                            )
                        )
                    else:
                        self.world_data[x][y] = int(tile)


class Interaction:
    def __init__(self, game):
        self.game = game
        self.collision_tolerance = 0.1  # small threshold to prevent jittering

    def check_and_handle_collisions(self):
        self.handle_tile_collisions()
        self.handle_powerup_collisions()

    def handle_tile_collisions(self):
        self.game.player.on_ground = False

        for tile in self.game.level.map_tiles:
            if self.is_colliding_with_tile(self.game.player, tile):
                self.resolve_tile_collision(self.game.player, tile)
                self.check_on_ground(self.game.player, tile)

    def handle_powerup_collisions(self):
        # collect the powerup and remove it from the list when colliding
        for powerup in self.game.powerups[:]:
            if self.is_colliding_with_powerup(self.game.player, powerup):
                self.game.player.collect_powerup(powerup.type)
                if powerup.type != "damage" and powerup.type != "ladder":
                    self.game.powerups.remove(powerup)

    def is_colliding_with_tile(self, player, tile):
        # find player bounds
        player_left = player.pos.x - player.size[0] / 2
        player_right = player.pos.x + player.size[0] / 2
        player_top = player.pos.y - player.size[1] / 2
        player_bottom = player.pos.y + player.size[1] / 2

        # find tile bounds
        tile_left = tile[1] - constants.TILE_SIZE / 2
        tile_right = tile[1] + constants.TILE_SIZE / 2
        tile_top = tile[2] - constants.TILE_SIZE / 2
        tile_bottom = tile[2] + constants.TILE_SIZE / 2

        return (
            player_right > tile_left
            and player_left < tile_right
            and player_bottom > tile_top
            and player_top < tile_bottom
        )

    def is_colliding_with_powerup(self, player, powerup):
        # find player bounds
        player_left = player.pos.x - player.size[0] / 2
        player_right = player.pos.x + player.size[0] / 2
        player_top = player.pos.y - player.size[1] / 2
        player_bottom = player.pos.y + player.size[1] / 2

        # find powerup bounds
        powerup_centre = (
            (powerup.pos.x + constants.POWERUP_SIZE / 2),
            (powerup.pos.y + constants.POWERUP_SIZE / 2),
        )
        powerup_left = powerup.pos.x - constants.POWERUP_SIZE / 2
        powerup_right = powerup.pos.x + constants.POWERUP_SIZE / 2
        powerup_top = powerup.pos.y - constants.POWERUP_SIZE / 2
        powerup_bottom = powerup.pos.y + constants.POWERUP_SIZE / 2

        return (
            player_right > powerup_left
            and player_left < powerup_right
            and player_bottom > powerup_top
            and player_top < powerup_bottom
        )

    def resolve_tile_collision(self, player, tile):
        # find bounds with threshold
        tile_left = tile[1] - constants.TILE_SIZE / 2 + self.collision_tolerance
        tile_right = tile[1] + constants.TILE_SIZE / 2 - self.collision_tolerance
        tile_top = tile[2] - constants.TILE_SIZE / 2 + self.collision_tolerance
        tile_bottom = tile[2] + constants.TILE_SIZE / 2 - self.collision_tolerance

        # find penetration distances
        penetration_left = (player.pos.x + player.size[0] / 2) - tile_left
        penetration_right = tile_right - (player.pos.x - player.size[0] / 2)
        penetration_top = (player.pos.y + player.size[1] / 2) - tile_top
        penetration_bottom = tile_bottom - (player.pos.y - player.size[1] / 2)

        # find smallest penetration
        min_penetration = min(
            penetration_left, penetration_right, penetration_top, penetration_bottom
        )

        # resolve collision based on smallest penetration
        if min_penetration == penetration_left:
            # collision from left side
            player.pos.x = tile_left - player.size[0] / 2 - self.collision_tolerance
            player.vel.x = 0

        elif min_penetration == penetration_right:
            # collision from right side
            player.pos.x = tile_right + player.size[0] / 2 + self.collision_tolerance
            player.vel.x = 0

        elif min_penetration == penetration_top:
            # collision from top
            player.pos.y = tile_top - player.size[1] / 2 - self.collision_tolerance
            player.vel.y = 0

        else:  # penetration_bottom
            # collision from bottom
            player.pos.y = tile_bottom + player.size[1] / 2 + self.collision_tolerance
            player.vel.y = 0

    def check_on_ground(self, player, tile):
        # check if the player is on the ground
        player_bottom = player.pos.y + player.size[1] / 2
        tile_top = tile[2] - constants.TILE_SIZE / 2

        if (
            abs(player_bottom - tile_top) < 5  # Small tolerance
            and player.pos.x + player.size[0] / 2 > tile[1] - constants.TILE_SIZE / 2
            and player.pos.x - player.size[0] / 2 < tile[1] + constants.TILE_SIZE / 2
        ):
            player.on_ground = True


# Create frame and start game
frame = simplegui.create_frame(
    "Mushroom Guy", constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT
)
game = Game()
frame.set_draw_handler(game.draw)
frame.set_keydown_handler(game.keyDown)
frame.set_keyup_handler(game.keyUp)
frame.set_mouseclick_handler(game.mouse_handler)
frame.start()
