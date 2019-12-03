# ---[ Imports
from __future__ import division

import scene as sc
import numpy as np
import sound
import random

# ---[ Textures
jumping_texture = sc.Texture('plf:AlienPink_jump')
landing_texture = sc.Texture('plf:AlienPink_duck')
dead_texture = sc.Texture('plf:AlienPink_hit')


# ---[Definitions

# Define a comparison function that returns -1 if 'a' is bigger than 'b', 1 if 'b' is greater than 'a' and 0 if the two variables are equal
def cmp(a, b):
	return ((a > b) - (a < b))
	
# Define orientation of the device - to be changed later to something that makes use of the final run function	
Orientation = ['LANDSCAPE', 'PORTRAIT']

# Create classes for special in-game items	
class Block(sc.SpriteNode):
	def __init__(self, **kwargs):
		# Each coin uses the same built-in image/texture. The keyword arguments are simply passed on to the superclass's initializer, so that it's possible to pass a position, parent node etc. directly when initializing a Coin.
		sc.SpriteNode.__init__(self, 'plf:Ground_GrassHalf_mid', **kwargs)
		
class Coin(sc.SpriteNode):
	def __init__(self, **kwargs):
		# Each coin uses the same built-in image/texture. The keyword arguments are simply passed on to the superclass's initializer, so that it's possible to pass a position, parent node etc. directly when initializing a Coin.
		sc.SpriteNode.__init__(self, 'plf:Item_CoinGold', **kwargs)


# ---[The Game
class Game(sc.Scene):
	def setup(self):
		# Define the orientation of the device
		self.orientation = Orientation[0]
		
		# Set a background color for the entire scene
		self.background_color = '#00bc72'
	
		self.bottom = 32	# Height of the tile (it will correspond to the position of the player)
			
		# Create the player.
		# A SpriteNode can be initialized from a `Texture` object or simply the name of a built-in image, which is used here
		# Tip: When you put the cursor inside the name, you can see a small preview of the image -- you can also tap the preview image to select a different one.
		self.player = sc.SpriteNode('plf:AlienPink_front')
		
		# The `anchor_point` of a `SpriteNode` defines how its position/rotation is interpreted. By default, the position corresponds to the center of the sprite, but in this case, it's more convenient if the y coordinate corresponds to the bottom (feet) of the alien, so we can position it flush with the ground. The anchor point uses unit coordinates -- (0, 0) is the bottom-left corner, (1, 1) the top-right.
		self.player.anchor_point = (0.5, 0)
		# To center the player horizontally, we simply divide the width of the scene by two:
		self.player.position = (self.size.w/2, self.bottom)
		self.add_child(self.player)
		

		# The same is done for the jumped variable that will determine if the player made the first jump
		self.jumped = False
		
		# Define a jumping array which determines the vertical positions of the player during the jump
		self.jump = np.array([0])
		i = 0
		acc = 45/(200)
		self.vel = 10
		while acc*i <= self.vel:
			self.jump = np.append(self.jump, (self.vel - acc*i))
			i += 1	
		
		self.jump[i] = 0
		self.jump = np.append(self.jump, - self.jump[::-1])
		self.jump = self.jump[:-1]
		# Define a counter that will help to determine the current index of the 'jump' array
		self.count = -1
		

		# Define a new attribute to keep track of the coins and blocks that are in the game, so that we can check if any of them collides with the player:
		self.items = []
		self.blocks = []
		
		# The font of a `LabelNode` is set using a tuple of font name and size.
		score_font = ('Futura', 40)
		self.score_label = sc.LabelNode('0', score_font, parent=self)
		# The label is centered horizontally near the top of the screen:
		self.score_label.position = (self.size.w/2, self.size.h - 70)
		# The score should appear on top of everything else, so we set the `z_position` attribute here. The default `z_position` is 0.0, so using 1.0 is enough to make it appear on top of the other objects.
		self.score_label.z_position = 1
		self.score = 0
		
		# Define the high score label
		self.high_score_label = sc.LabelNode('High Score:', ('Futura', 20), parent=self)
		self.high_score_label.anchor_point = (0,0)
		self.high_score_label.position = (27, self.size.h - 70)
		
		self.high_score = sc.LabelNode('1000', ('Futura', 15), parent=self)
		self.high_score.anchor_point = (0,0)
		self.high_score.position = (27, self.size.h - 95)
		
		self.high_score_val = 1000
		
		self.high_score.text = str(self.high_score_val)
		
		# Run the new_game() to set everything to its initial state
		self.new_game()
		
		
	
	def new_game(self):
		# Create the ground node...
		# Usually, nodes are added to their parent using the 'add_child()' method, but for convenience, you can also pass
		# the node's parent as a keyword argument for the same effect
		self.ground = sc.Node(parent=self)
		ground_x = 0
		tile_width = 64
		
		# Increment ground_x until the edge of the screen is reached
		while ground_x <= self.size.w + tile_width:
			tile = sc.SpriteNode('plf:Ground_GrassMid', position=(ground_x, 0))
			self.ground.add_child(tile)
			ground_x += tile_width
		
		
		# Reset everything to its initial state...
		for item in self.items:
			item.remove_from_parent()
		self.items = []
		
		for block in self.blocks:
			block.remove_from_parent()
		self.blocks = []
		
		self.current_blocks = []
		
		# Create the first instance of a Block class. This will help with positioning of blocks later in the game
		block = Block(parent=self)
		block.position = (random.uniform(27, self.size.w-27), random.uniform(100, 200))
		block.z_position = -1
		self.blocks.append(block)
		
		self.count = -1
		self.jumped = False
		
		self.score = 0
		self.score_label.text = '0'
		self.player.position = (self.size.w/2, 32)
		self.player.texture = jumping_texture
		self.speed = 1.0
		# The game_over attribute is set to True when the alien gets hit by a meteor. We use this to stop player movement and collision checking (the update method simply does nothing when game_over is True).
		self.game_over = False
		
		# Check if the 'camera view' is moving
		self.moving = False
		self.jump_counter = 0
	
		
	# Create the update function that is called automatically 60 times per second			
	def update(self):
		if self.game_over == False:
			self.update_player()
			
			# if the camera view is moving run the modified jump function
			if self.moving == True:
				self.modified_jump()
			
			self.check_item_collisions()
			self.check_jump()
			
			# If the first jump was performed, check if the player has fallen
			if self.jumped == True:
				self.check_fall_off()
				
			# At random intervals, spawn items in the game
			if random.random() < 0.01:
				self.spawn_item()
			
			
		
	def update_player(self):
		# The gravity() function returns an (x, y, z) vector that describes the current orientation of your device.
		x,y,z = sc.gravity()
		
		# Determine player's position
		pos = self.player.position
		
		# If the camera is not moving, update player's y-coordinate
		if self.moving == False:
			self.count += 1
		
			pos.y = pos.y + self.jump[self.count % len(self.jump)]
			

		# Determine if the relevant accelerations are of significant magnitude 
		g = [x>0.01,y>0.01]
		
		max_speed = 35
		
		if any(g) and self.orientation == 'LANDSCAPE':
			# The components of the gravity vector are in the range 0.0 to 1.0, so we have to multiply it with some factor to move the player more quickly. 40 works pretty well, but feel free to experiment. 
			
			
			pos.x += -y * max_speed
			# We simply add the x component of the gravity vector to the current position, and clamp the value between 0 and the scene's width, so the alien doesn't move outside of the screen boundaries.
			pos.x = max(27, min(self.size.w-27, pos.x))
			# pos.y = max(32, min(self.size.h-70, pos.y))
			
			# Ensure that the player is facing in the direction of motion using appropriate scaling 
			self.player.x_scale = cmp(-y, 0)
			
		elif any(g) and self.orientation == 'PORTRAIT':
			
			pos.x += x*max_speed
			pos.x = max(27, min(self.size.w - 27, pos.x))
			self.player.x_scale = cmp(x, 0)
			
		self.player.position = pos
		
		
		# Create appropriate textures for more fluid motion
		if pos.y < 70:
			self.player.texture = landing_texture
			
			if pos.y < 33:
				sound.play_effect('arcade:Jump_5', 0.05)
		else:
			self.player.texture = jumping_texture
	
	
	# Create a function for spawning coins in the game
	def spawn_item(self):
		coin = Coin(parent=self)
		coin.position = (random.uniform(27, self.size.w-27), self.size.h + 30)
		# The coin's fall duration is randomly chosen somewhere between 2 and 4 seconds:
		d = random.uniform(2.0, 4.0)
		# To let the coin fall down, we use an `Action`.
		# Actions allow you to animate things without having to keep track of every frame of the animation yourself (as we did with the walking animation). Actions can be combined to groups and sequences. In this case, we create a sequence of moving the coin down, and then removing it from the scene.
		actions = [sc.Action.move_by(0, -(self.size.h + 60), d), sc.Action.remove()]
		coin.run_action(sc.Action.sequence(actions))
		# Also add the coin to the `items` list (used for checking collisions):
		self.items.append(coin)
		
	
	# Apply an analogus function to spawn_item to the blocks. A separate function is created to account for the differences in the behaviour of the two objects	
	def spawn_blocks(self):
		
		if len(list(self.blocks)) < 6:
			block = Block(parent=self)
			
			block.position = (random.uniform(27, self.size.w-27), random.uniform(list(self.blocks)[-1].position.y + 50, list(self.blocks)[-1].position.y + 200))
			block.z_position = -1
			self.blocks.append(block)	
		
		# The speed function will be modified every time a block is created to make the game more challenging with progress
		self.speed = min(3, self.speed + 0.001)
		
	
	# Define a function for item collection																						
	def collect_item(self, item, value = 10):
		sound.play_effect('digital:PowerUp7')
		
		# Ensure that the collected items are removed from the game and the record
		item.remove_from_parent()
		item.run_action(sc.Action.remove())
		self.items.remove(item)	
		
		# Add appropriate increment to the total score (and check if the high score was broken)
		self.score += value
		self.score_label.text = str(self.score)							
		self.high_score.text = str(max(self.score, self.high_score_val))
																													
	# Create a function to check for item collisions with the player			
	def check_item_collisions(self):
		
		# Define a player hitbox as a rectangle around the player
		player_hitbox = sc.Rect(self.player.position.x - 20, self.player.position.y, 40, 65)
		
		# for each item in the game check if the item intersects the hitbox. Run the collection function if appropriate
		for item in list(self.items):
			if item.frame.intersects(player_hitbox):
				self.collect_item(item)
			# When a coin has finished its animation, it is automatically removed from the scene by its Action sequence. When that's the case, also remove it from the `items` list, so it isn't checked for collisions anymore:
			elif not item.parent:
				self.items.remove(item)
				
	# Define a function to check whether a successful jump was made			
	def check_jump(self):
		# Define a player hitbox as a rectangle around the player
		player_hitbox = sc.Rect(self.player.position.x - 20, self.player.position.y, 40, 65)
		
		# Iterate over blocks in the game
		for block in list(self.blocks):
			
			# check if the block position overlaps with the player, while the player is falling 
			if self.vel+np.round(32+block.position.y,0) > self.player.position.y and np.round(32+block.position.y,0)-self.vel < self.player.position.y and block.frame.intersects(player_hitbox) and self.jump[self.count % len(self.jump)] < 0:
				
				# if the condition is satisfied, the player has performed a succesful jump. The camera view should now be shifted. This can be done by moving all in-game items and blocks by the distance of the jump
				for item in list(self.blocks):
					item.run_action(sc.Action.move_by(0, -block.position.y,0.5, sc.TIMING_SINODIAL))
				for b in list(self.blocks):
					b.run_action(sc.Action.move_by(0, -block.position.y,0.5, sc.TIMING_SINODIAL))
					
					# Additionally, if blocks have moved below the current camera view, they should be removed from the game
					if b.position.y < 0:
						b.remove_from_parent()
						b.run_action(sc.Action.remove())
						self.blocks.remove(b)
	
				# Reset the counter to 1 and the player position to 32 (corresponds to the start of a new jump)
				self.count = -1
				self.player.position.y = 32
				
				# Change the moving function to True to ensure that a correct, modified jump mechanics are applied
				self.moving = True
				
				# Make sure that the ground is removed from the game
				self.ground.run_action(sc.Action.remove())
				
				# Define the block the player is currently standing on
				self.current_block = block
				self.jumped = True
				
				# Increment the score by the normalised jump distance
				self.score += int(np.round(block.position.y/10,0))
				self.score_label.text = str(self.score)	
				self.high_score.text = str(max(self.score, self.high_score_val))
	
	def modified_jump(self):
		# 0.5 s = 30 iterations
		
		# -> total distance moved each iteration by the camera is -block.position.y/30
		
		# Here the reasoning follows the one presented in update_player() function, but the jump is modified to account for the downwards camera movement
		pos = self.player.position
		self.count += 1
		
		self.current_blocks = np.append(self.current_blocks, self.current_block.position.y)
		
		if pos.y + self.jump[self.count % len(self.jump)] > 32:
			pos.y = pos.y + self.jump[self.count % len(self.jump)] - list(self.current_blocks)[0]/30
				
		self.player.position = pos
		
		# For the case of 0.5s camera movement, this function should only run 30 times. This is enabled by the following if statement
		self.jump_counter += 1
		if self.jump_counter == 30:
			self.jump[self.count % len(self.jump)]
			self.moving = False
			self.jump_counter = 0
			self.current_blocks = []
			while len(list(self.blocks)) < 6:
				self.spawn_blocks()
							
	
	# Check if the player has fallen of the tile
	def check_fall_off(self):
		
		# If the player is at the bottom of the jump, see if the block frame intersects the player hitbox
		if self.count  % len(self.jump) == 0:
			player_hitbox = sc.Rect(self.player.position.x - 20, self.player.position.y-5, 40, 65)
			# I should in theory just have to check the bottom box
			block = self.current_block
			if block.frame.intersects(player_hitbox):
				fall = False
			else:
				fall = True
				self.run_action(sc.Action.call(self.player_dead))	
	
							
	def player_dead(self):
		# This is. alled from `check_item_collisions()` when the alien collides with a meteor. The alien simply drops off the screen, and after 2 seconds, a new game is started.
		self.game_over = True
		sound.play_effect('arcade:Explosion_1')
		self.player.texture = dead_texture
		self.player.run_action(sc.Action.move_by(0, -150))
		# Note: The duration of the `wait` action is multiplied by the current game speed, so that it always takes exactly 2 seconds, regardless of how fast the rest of the game is running.
		self.run_action(sc.Action.sequence(sc.Action.wait(2*self.speed), sc.Action.call(self.new_game)))	
			
		
	# When a touch is applied to the screen, a laser is shot from the player. This can be used for later implementation of additional obstacles in the game.
	def touch_began(self, touch):
		laser = sc.SpriteNode('spc:LaserBlue9', position=self.player.position, z_position = -1, parent = self)
		laser.run_action(sc.Action.sequence(sc.Action.move_by(0,1000), sc.Action.remove()))
		sound.play_effect('arcade:Laser_1')
		
if __name__ == '__main__':
	sc.run(Game(), sc.LANDSCAPE, show_fps = True) 
