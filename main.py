import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import os
import csv
import math

from vector import Vector
from player import Player
from level import Block
from moss import Moss

import constants


class Game:
    def __init__(self):
        self.running = True
        self.state = "menu"
        self.mouse_pos = [0, 0]
        self.level = 1
        self.right = False
        self.left = False
        self.jump = False
        self.damaged_cooldown = 0  # prevents continuous damage
        self.blocks = []
        self.moss = []

        # declaring player object
        self.player = Player(Vector(15, 150))

        self.interaction = Interaction(self)

        # declaring several moss objects
        self.moss = [
            # position (x, y) , height , width
            Moss(Vector(200, 600), 10, 200),
            Moss(Vector(50, 600), 10, 100),
            Moss(Vector(500, 600), 10, 50)
        ]

        self.blocks = [
            Block((500, 500)),
            Block((200, 400)),
            Block((300, 300)),
        ]

        # Initialize tile_list and world_data
        self.tile_list = []
        self.world_data = []

        # Initialize screen_scroll
        self.screen_scroll = 0

        # Load images and level data
        self.loadImages()
        self.loadLevel()

    def mouse_handler(self, pos):
        # handles mouse click
        self.mouse_pos = pos
        if self.state == "menu":
            self.state = "game"
            self.player.health.current_health = self.player.health.max_health

    def draw(self, canvas):
        # according to state (menu, game, game over) it draws the specific canvas
        if self.state == "menu":
            self.draw_menu(canvas)
        elif self.state == "game":
            self.draw_game(canvas)
        else:
            self.draw_game_over(canvas)

    def draw_menu(self, canvas):
        # draws main menu screen
        canvas.draw_text("MUSHROOM DUNGEON",
                         (constants.SCREEN_WIDTH // 2 - 200, constants.SCREEN_HEIGHT // 3 + 50),
                         50, "White", "monospace")

        # making "click to play" a clickable text
        text = "CLICK TO PLAY"
        text_width = frame.get_canvas_textwidth(text, 30, 'monospace')
        text_x = constants.SCREEN_WIDTH // 2 - text_width // 2 + 20
        text_y = constants.SCREEN_HEIGHT // 2
        canvas.draw_text(text, (text_x, text_y), 30, "White", "monospace")

    def draw_game(self, canvas):
        if self.player.health.current_health > 0:
            self.interaction.check_and_handle_collisions()

            self.player.draw(canvas)

            # drawing the moss objects
            for moss in self.moss:
                moss.draw(canvas)

            for block in self.blocks:
                block.draw(canvas)

            self.update()
        else:
            self.state = "game_over"

    def draw_game_over(self, canvas):
        # draws the game over screen
        canvas.draw_text("GAME OVER", (constants.SCREEN_WIDTH // 2 - 200, constants.SCREEN_HEIGHT // 3 + 30),
                         70, "Red", "monospace")
        canvas.draw_text("Press R to restart", (constants.SCREEN_WIDTH // 2 - 175, constants.SCREEN_HEIGHT // 2 - 25),
                         30, "White", "monospace")

    def update(self):
        # call move method for player based on player inputs
        self.screen_scroll = self.player.move(self.left, self.right, self.jump)  # takes output for moving screen

        # checking if the player is in contact with the moss
        on_moss = False
        for moss in self.moss:
            if moss.is_player_on_moss(self.player):
                on_moss = True

                break
        self.player.on_moss = on_moss

        if on_moss:

            self.player.vel.x *= constants.SLOW_FACTOR  # Reduce horizontal velocity
            self.player.vel.y *= constants.SLOW_FACTOR  # Reduce vertical velocity (optional)

            if self.damaged_cooldown == 0:  # Prevents immediate life loss
                self.damaged_player()
                self.damaged_cooldown = 180  # A delay before next damage

        # Decrease cooldown timer
        if self.damaged_cooldown > 0:
            self.damaged_cooldown -= 1

    def keyDown(self, key):  # taking inputs from the player
        if self.state == "game":
            if key == simplegui.KEY_MAP['d']:
                self.right = True
            elif key == simplegui.KEY_MAP['a']:
                self.left = True
            elif key == simplegui.KEY_MAP['w']:
                self.jump = True
        elif self.state == "game_over" and key == simplegui.KEY_MAP['r']:
            self.state = "game"
            # restarts the game fully
            global game
            game = Game()
            frame.set_draw_handler(game.draw)
            frame.set_keydown_handler(game.keyDown)
            frame.set_keyup_handler(game.keyUp)
            frame.set_mouseclick_handler(game.mouse_handler)

    def keyUp(self, key):  # ending inputs from the player
        if self.state == "game":
            if key == simplegui.KEY_MAP['d']:
                self.right = False
            elif key == simplegui.KEY_MAP['a']:
                self.left = False
            elif key == simplegui.KEY_MAP['w']:
                self.jump = False

    def damaged_player(self):
        self.player.health.life_lost()

    def loadImages(self):
        # Load tilemap images
        for x in range(constants.TILE_TYPES):
            absolute_path = os.path.abspath(f"assets/tiles/{x}.png")
            image = simplegui.load_image(absolute_path)
            self.tile_list.append(image)

    def loadLevel(self):
        for row in range(150):  # creating empty 150x150 world_data list
            r = [-1] * 150
            self.world_data.append(r)
        # loading level data from csv file into world_data
        with open("levels/level0_data.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    self.world_data[x][y] = int(tile)


class Interaction:
    def __init__(self, game):
        self.game = game

    def check_and_handle_collisions(self):

        self.handle_block_collisions()
        # self.handle_moss_collisions()

    def handle_block_collisions(self):

        self.game.player.on_block = False  # assume the player is not on the block
        for block in self.game.blocks:
            if self.is_colliding_with_block(self.game.player, block):
                self.resolve_block_collision(self.game.player, block)
                if self.game.player.is_on_block(block):
                    self.game.player.on_block = True  # player is on top of the block

    def handle_moss_collisions(self):

        for moss in self.game.moss:
            if moss.is_player_on_moss(self.game.player):
                self.game.player.on_moss = True

    def is_colliding_with_block(self, player, block):

        player_left = player.pos.x - player.size[0] / 2
        player_right = player.pos.x + player.size[0] / 2
        player_top = player.pos.y - player.size[1] / 2
        player_bottom = player.pos.y + player.size[1] / 2

        block_left = block.center[0] - block.size[0] / 2
        block_right = block.center[0] + block.size[0] / 2
        block_top = block.center[1] - block.size[1] / 2
        block_bottom = block.center[1] + block.size[1] / 2

        # check for collision
        return (player_right > block_left and player_left < block_right and player_bottom > (
            block_top) and player_top < block_bottom)

    def resolve_block_collision(self, player, block):

        # calculate overlap in x and y
        overlap_x = min(
            abs(player.pos.x + player.size[0] / 2 - (block.center[0] - block.size[0] / 2)),
            abs(player.pos.x - player.size[0] / 2 - (block.center[0] + block.size[0] / 2))
        )
        overlap_y = min(
            abs(player.pos.y + player.size[1] / 2 - (block.center[1] - block.size[1] / 2)),
            abs(player.pos.y - player.size[1] / 2 - (block.center[1] + block.size[1] / 2))
        )

        # resolve collision based on overlap
        if overlap_x < overlap_y:
            # horizontal collision
            if player.pos.x < block.center[0]:
                player.pos.x = block.center[0] - block.size[0] / 2 - player.size[0] / 2
            else:
                player.pos.x = block.center[0] + block.size[0] / 2 + player.size[0] / 2
            player.vel.x = 0
        else:
            # vertical collision
            if player.pos.y < block.center[1]:
                player.pos.y = block.center[1] - block.size[1] / 2 - player.size[1] / 2
            else:
                player.pos.y = block.center[1] + block.size[1] / 2 + player.size[1] / 2
                player.vel.y = 0


frame = simplegui.create_frame("Mushroom Guy", constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
game = Game()
frame.set_draw_handler(game.draw)
frame.set_keydown_handler(game.keyDown)
frame.set_keyup_handler(game.keyUp)
frame.set_mouseclick_handler(game.mouse_handler)

frame.start()