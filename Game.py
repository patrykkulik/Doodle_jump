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

Monster_textures = {'bee' : [sc.Texture('plf:Enemy_Bee'), sc.Texture('plf:Enemy_Bee_move'), sc.Texture('plf:Enemy_Bee_dead')], 'fly'	: [sc.Texture('plf:Enemy_Fly'), sc.Texture('plf:Enemy_Fly_move'), sc.Texture('plf:Enemy_Fly_dead')],
'frog'  : [sc.Texture('plf:Enemy_Frog'), sc.Texture('plf:Enemy_Frog_move'), sc.Texture('plf:Enemy_Frog_dead')],
'fish' 	: [sc.Texture('plf:Enemy_FishPink'), sc.Texture('plf:Enemy_FishPink_move'), sc.Texture('plf:Enemy_FishPink_dead')],
'saw'	: [sc.Texture('plf:Enemy_Saw'), sc.Texture('plf:Enemy_Saw_move'), sc.Texture('plf:Enemy_Saw_dead')],
'mouse' : [sc.Texture('plf:Enemy_Mouse'), sc.Texture('plf:Enemy_Mouse_move'), sc.Texture('plf:Enemy_Mouse_dead')],
'bug'	: [sc.Texture('plf:Enemy_Ladybug'), sc.Texture('plf:Enemy_Ladybug_move'), sc.Texture('plf:Enemy_Ladybug_fly')],
'blob'	: [sc.Texture('plf:Enemy_SlimePurple'), sc.Texture('plf:Enemy_SlimePurple_move'), sc.Texture('plf:Enemy_SlimePurple_dead')],
'snail' : [sc.Texture('plf:Enemy_Snail'), sc.Texture('plf:Enemy_Snail_move'), sc.Texture('plf:Enemy_Snail_shell')],
'worm'	: [sc.Texture('plf:Enemy_WormPink'), sc.Texture('plf:Enemy_WormPink_move'), sc.Texture('plf:Enemy_WormPink_dead')],
}

Monster_types = list(Monster_textures.keys())

# ---[Definitions

# Define a comparison function that returns -1 if 'a' is bigger than 'b', 1 if 'b' is greater than 'a' and 0 if the two variables are equal
def cmp(a, b):
	return ((a > b) - (a < b))
	
# Define orientation of the device - to be changed later to something that makes use of the final run function	
Orientation = ['LANDSCAPE', 'PORTRAIT']

# Create classes for special in-game items	
class Block(sc.SpriteNode):
	def __init__(self, **kwargs):
		# Each block uses the same built-in image/texture. The keyword arguments are simply passed on to the superclass's initializer, so that it's possible to pass a position, parent node etc. directly when initializing a Block.
		sc.SpriteNode.__init__(self, 'plf:Ground_GrassHalf_mid', **kwargs)
		
class Coin(sc.SpriteNode):
	def __init__(self, **kwargs):
		# Each coin uses the same built-in image/texture. The keyword arguments are simply passed on to the superclass's initializer, so that it's possible to pass a position, parent node etc. directly when initializing a Coin.
		sc.SpriteNode.__init__(self, 'plf:Item_CoinGold', **kwargs)

class Cloud(sc.SpriteNode):
	def __init__(self, **kwargs):
		# Each cloud uses the same built-in image/texture. The keyword arguments are simply passed on to the superclass's initializer, so that it's possible to pass a position, parent node etc. directly when initializing a Cloud.
		sc.SpriteNode.__init__(self, 'emj:Cloud', **kwargs)
		
class Monster(sc.SpriteNode):
	def __init__(self, **kwargs):
		# The Monster class randomply chooses an enemy from Monster_types defined earlier. In addition, an enemy_type method is created to make sure correct textures are chosen later.
		
		r = random.uniform(0,1)
		r = int(np.floor(10*r))
		
		self.enemy_type = Monster_types[r]
		sc.SpriteNode.__init__(self, Monster_textures[self.enemy_type][0], **kwargs)
			
# ---[The Game
class Game(sc.Scene):
	def setup(self):
		# Define the orientation of the device
		self.orientation = Orientation[1]
		
		# Set a background color for the entire scene
		self.background_color = '#00b1d1'
	
		self.bottom = 32	# Height of the tile (it will correspond to the lowest allowed position of the player)
			
		# Create the player.
		# A SpriteNode can be initialized from a `Texture` object or simply the name of a built-in image, which is used here
		self.player = sc.SpriteNode('plf:AlienPink_front')
		
		# The `anchor_point` of a `SpriteNode` defines how its position/rotation is interpreted. By default, the position corresponds to the center of the sprite, but in this case, it's more convenient if the y coordinate corresponds to the bottom (feet) of the alien, so we can position it flush with the ground. The anchor point uses unit coordinates -- (0, 0) is the bottom-left corner, (1, 1) the top-right.
		self.player.anchor_point = (0.5, 0)
		# To center the player horizontally, we simply divide the width of the scene by two:
		self.player.position = (self.size.w/2, self.bottom)
		self.add_child(self.player)
		
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
		
		self.max_jump = self.bottom + np.sum(self.jump[0:len(self.jump)/2])
		
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
		
		# Define the high score and current score labels
		self.high_score_label = sc.LabelNode('High Score:', ('Futura', 20), parent=self)
		self.high_score_label.anchor_point = (0,0)
		self.high_score_label.position = (27, self.size.h - 70)
		
		self.high_score = sc.LabelNode('0', ('Futura', 15), parent=self)
		self.high_score.anchor_point = (0,0)
		self.high_score.position = (27, self.size.h - 95)
		
		self.high_score_val = 6793
		
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
		
		self.current_blocks = np.array([])
		
		self.lasers = []
		
		# Create the first instance of a Block class. This will help with positioning of blocks later in the game
		block = Block(parent=self)
		block.position = (random.uniform(27, self.size.w-27), random.uniform(100, 200))
		block.z_position = -1
		self.blocks.append(block)
		
		# Initialise jump counter and the jumped method to determine if the player has performed the first jump
		self.count = -1
		self.jumped = False
		
		# Set the current score to zero, and the player position to the default starting position
		self.score = 0
		self.score_label.text = '0'
		self.player.position = (self.size.w/2, 32)
		self.player.texture = jumping_texture
		
		# Set the difficulty of the game back to its initial state
		self.speed = 1.0
		
		# The game_over attribute is set to True when the alien dies. We use this to stop player movement and collision checking (the update method simply does nothing when game_over is True).
		self.game_over = False
		
		# Check if the 'camera view' is moving
		self.moving = False
		self.jump_counter = 0
		
		# Reset velocity scale and step of the enemies in the game
		self.vel_scale = 1
		self.step = 0
	
		
	# Create the update function that is called automatically ~60 times per second			
	def update(self):
		if self.game_over == False:
			self.update_player()
			
			# if the camera view is moving run the modified jump function
			if self.moving == True:
				self.modified_jump()
			
			self.check_item_collisions()
			self.check_jump()
			self.update_items()
			self.check_laser_collisions()
			
			# If the first jump was performed, check if the player has fallen and start spawning items
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
		g = [abs(x)>0.01,abs(y)>0.01]
		
		# The components of the gravity vector are in the range 0.0 to 1.0, so we have to multiply it with some factor to move the player more quickly. 35 works pretty well, but feel free to experiment. 
		max_speed = 35
		
		# Check the orientation. In Ladnscape orientation, the x direction of movement corresponds to the y coordinate of the accelerometer
		if any(g) and self.orientation == 'LANDSCAPE':
			
			# change position x depending on the accelerometer data and the speed of the game (higher as the game progresses)
			pos.x += -y * max_speed
			
			# We simply add the x component of the gravity vector to the current position, and clamp the value between 27 and the scene's width, so the alien doesn't move outside of the screen boundaries.
			pos.x = max(27, min(self.size.w-27, pos.x))
			
			# Ensure that the player is facing in the direction of motion using appropriate scaling 
			self.player.x_scale = cmp(-y, 0)
			
		elif any(g) and self.orientation == 'PORTRAIT':
			
			# apply similar equations in the Portrait case
			pos.x += x*max_speed
			pos.x = max(27, min(self.size.w - 27, pos.x))
			self.player.x_scale = cmp(x, 0)
		
		# Update the final player position	
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
		
		# Create an instance of the Coin class, ensuring that its position is within the x-bounds and above the camera window in the y direction
		coin = Coin(parent=self)
		coin.position = (random.uniform(27, self.size.w-27), self.size.h + 30)
		
		# Also add the coin to the `items` list (used for checking collisions):
		self.items.append(coin)
		
		# Spawn clouds
		# make clouds rarer than coins
		if random.random() < 2:
			cloud = Cloud(parent=self)
			cloud.position = (random.uniform(-50, self.size.w - 100), random.uniform(self.size.h+200, self.size.h + 600))
			
			# Ensure that Clouds appear below everything else in the game
			cloud.z_position = -2

			# Also add the cloud to the `items` list (used for checking collisions):
			self.items.append(cloud)
			
		# Spawn enemies:
		if random.random() < 0.09 * self.speed:
			monster = Monster(parent = self)
			monster.position = (random.uniform(50, self.size.w-50), random.uniform(self.size.h+100, self.size.h + 400))
			# create a new method for the monster class and set it to false. This will help with checking if the player has destroyed the enemy
			monster.destroyed = False
			self.items.append(monster)
			
			
	
	# Apply an analogus function to spawn_item to create new blocks in the game. A separate function is created to account for the differences in the behaviour of the two objects	
	def spawn_blocks(self):
			
		# Make sure that a finite number of blocks is present in the game at any given time
		if len(list(self.blocks)) < 10:
			block = Block(parent=self)
			
			# Define the block position in terms of the position of the previously created block. This ensures that blocks are a reasonable distance apart and the game is not impossible
			block.position = (random.uniform(27, self.size.w-27), random.uniform(list(self.blocks)[-1].position.y + 50, list(self.blocks)[-1].position.y + 220))
			block.z_position = -1
			
			# Append the block to the blocks list to help check for jump and fall-offs
			self.blocks.append(block)	
		
		# The speed function will be modified every time a block is created to make the game more challenging with progress
		self.speed = min(3, self.speed + 0.01)
	
		
	def update_items(self):
		
		for item in list(self.items):
			
			# if current_block exists, the player is in the process of jumping. In that case, move all items by the size of the jump downwards
			if self.current_blocks.size:
				
				pos = item.position
				pos.y = pos.y - self.current_blocks[0]/30
				item.position = pos
			
				
			# If an item is below the camera window, remove it from the game and from the item list	
			if item.position.y < 0:
				item.remove_from_parent()
				item.run_action(sc.Action.remove())
				self.items.remove(item)	
			
			# If the item is a coin, assign it a velocity and move it by that amount in the y-direction	
			if isinstance(item, Coin):
				# The coin's velocity is randomly chosen to create a fall duration of between 2 and 4 seconds:
				v = random.uniform(self.size.w/(2.0*60), self.size.w/(4.0*60))
				
				
				pos = item.position
				pos.y = pos.y - v
				item.position = pos
			
			# If the item is a cloud, assign it a velocity and move it by that amount in the x-direction			
			if isinstance(item, Cloud):
				v = random.uniform(self.size.w/(25*60), self.size.w/(40*60))
				
				pos = item.position
				pos.x = pos.x + v
				item.position = pos
				
				# in case a cloud moves outside the camera window, remove it from the game and from the item list
					
				if item.position.x > self.size.w + 30:
					item.remove_from_parent()
					item.run_action(sc.Action.remove())
					self.items.remove(item)	
			
			# if the item is a Monster, assign it a velocity and move it left and right in a periodic fashion	
			if isinstance(item, Monster):
				v = random.uniform(self.size.w/(5*60), self.size.w/(10*60))
					
				# If the monster is close to the right-hand edge of the screen, change the velocity scale to negtive to reverse its motion. The equivalent operation is done when the Monster moves to the left hand side of the screen		
				if item.position.x > self.size.w - 40:
					self.vel_scale = -1
				elif item.position.x < 40:
					self.vel_scale = 1
		  
		  		# Update Monster position
				pos = item.position	
				pos.x = pos.x + v * self.speed * self.vel_scale
				
				item.position = pos
				
				# Scale the monster so that it faces the direction of motion. Additionally, make the monsters bigger with the speed of the game (it is incremented in the block spawning function)
				item.x_scale = -self.vel_scale*self.speed
				item.y_scale = self.speed
				
				# The step is defined so that it changes after the monster moves 20 pixels. This will help generate the appropriate texture and fluid motion
				step = int(pos.x / 20) % 2
				
				# Change the Monster's texture depending on the current step
				item.texture = Monster_textures[item.enemy_type][step]
				
				
				
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
		self.high_score_val = max(self.score, self.high_score_val)						
		self.high_score.text = str(self.high_score_val)
	
	
	# Define a function for checking laser collisions. 
	def check_laser_collisions(self):
		for laser in list(self.lasers):
			
			# If the laser does not belong to the game (i.e. it was removed), remove it from the laser list
			if not laser.parent:
				self.lasers.remove(laser)
				continue
			
			# iterate over all Monsters in the items list
			for item in self.items:
				if not isinstance(item, Monster):
					continue
				if item.destroyed:
					continue
				
				# if the laster overlaps with the monster, destroy the monster and remove the laser from the game
				if laser.position in item.frame:
					self.destroy_monster(item)
					laser.run_action(sc.Action.remove())
					self.lasers.remove(laser)
					laser.remove_from_parent()
					break
					
	# Define a function for destroying monsters						
	def destroy_monster(self, monster):
		sound.play_effect('arcade:Explosion_2', 0.2)
		
		# Change the monster texture to dead
		monster.texture = Monster_textures[monster.enemy_type][2]
		
		# Modify the opacity of the texture to make it clear that the monster is dead
		monster.alpha = 0.5
		
		# Modify the destroyed method
		monster.destroyed = True
		
		# Run action sequence to freeze the destroyed monster for one second. Afterwards, remove it from the game
		monster.run_action(sc.Action.sequence(sc.Action.wait(1),sc.Action.remove()))
		self.items.remove(monster)
		monster.remove_from_parent
		
		# Create some left over pieces:
		#for i in range(5):
		#	m = SpriteNode('spc:MeteorBrownMed1', parent=self)
		#	m.position = meteor.position + (random.uniform(-20, 20), random.uniform(-20, 20))
		#	angle = random.uniform(0, pi*2)
		#	dx, dy = cos(angle) * 80, sin(angle) * 80
		#	m.run_action(A.move_by(dx, dy, 0.6, TIMING_EASE_OUT))
		#	m.run_action(A.sequence(A.scale_to(0, 0.6), A.remove()))																																																																																																		
	# Create a function to check for item collisions with the player			
	def check_item_collisions(self):
		
		# Define a player hitbox as a rectangle around the player
		player_hitbox = sc.Rect(self.player.position.x - 20, self.player.position.y, 40, 65)
		
		# for each item in the game check if the item intersects the hitbox. Run the collection function if appropriate
		for item in list(self.items):
			if isinstance(item, Coin):
				if item.frame.intersects(player_hitbox):
					self.collect_item(item)
				#	 When a coin has finished its animation, it is automatically removed from the scene by its Action sequence. When that's the case, also remove it from the `items` list, so it isn't checked for collisions anymore:
				elif not item.parent:
					self.items.remove(item)
			if isinstance(item, Monster):
				if item.frame.intersects(player_hitbox):
					self.player_dead()
				
	# Define a function to check whether a successful jump was made			
	def check_jump(self):
		# Define a player hitbox as a rectangle around the player
		player_hitbox = sc.Rect(self.player.position.x - 20, self.player.position.y, 40, 65)
		
		# Iterate over blocks in the game
		for block in list(self.blocks):
			
			# check if the block position overlaps with the player, while the player is falling 
			if self.vel+np.round(32+block.position.y,0) > self.player.position.y and np.round(32+block.position.y,0)-self.vel < self.player.position.y and block.frame.intersects(player_hitbox) and self.jump[self.count % len(self.jump)] < 0:
				
				# if the condition is satisfied, the player has performed a succesful jump. The camera view should now be shifted. This can be done by moving all in-game blocks by the distance of the jump
				
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
				
				self.player.texture = landing_texture
				
				# Increment the score by the normalised jump distance
				self.score += int(np.round(block.position.y/10,0))
				self.score_label.text = str(self.score)	
				self.high_score_val = max(self.score, self.high_score_val)
				self.high_score.text = str(self.high_score_val)
	
	def modified_jump(self):
		# 0.5 s = 30 iterations
		
		# -> total distance moved each iteration by the camera is -block.position.y/30
		
		# Here the reasoning follows the one presented in update_player() function, but the jump is modified to account for the downwards camera movement
		pos = self.player.position
		self.count += 1
		
		self.current_blocks = np.append(self.current_blocks, self.current_block.position.y)
		
		# Not sure if this if statement does anything
		if pos.y + self.jump[self.count % len(self.jump)] > 32:
			pos.y = pos.y + self.jump[self.count % len(self.jump)] - list(self.current_blocks)[0]/30
				
		self.player.position = pos
		
		if self.count > 1:
			self.player.texture = jumping_texture
		
		# For the case of 0.5s camera movement, this function should only run 30 times. This is enabled by the following if statement
		self.jump_counter += 1
		if self.jump_counter == 30:
			self.jump[self.count % len(self.jump)]
			self.moving = False
			self.jump_counter = 0
			self.current_blocks = np.array([])
			while len(list(self.blocks)) < 6:
				self.spawn_blocks()
							
	
	# Check if the player has fallen of the tile
	def check_fall_off(self):
		
		# If the player is at the bottom of the jump, see if the block frame intersects the player hitbox
		if self.count  % len(self.jump) == 0:
			player_hitbox = sc.Rect(self.player.position.x - 20, self.player.position.y-5, 40, 65)
			
			block = self.current_block
			if block.frame.intersects(player_hitbox):
				fall = False
			else:
				fall = True
				self.run_action(sc.Action.call(self.player_dead))	
	
							
	def player_dead(self):
		# If any of the conditions for the end of the game are satisfied, the player simply drops off the screen, and after 2 seconds, a new game is started.
		self.game_over = True
		sound.play_effect('arcade:Explosion_1')
		self.player.texture = dead_texture
		self.player.run_action(sc.Action.move_by(0, -self.size.h))
		# Note: The duration of the `wait` action is multiplied by the current game speed, so that it always takes exactly 2 seconds, regardless of how fast the rest of the game is running.
		self.run_action(sc.Action.sequence(sc.Action.wait(2*self.speed), sc.Action.call(self.new_game)))	
			
		
	# When a touch is applied to the screen, a laser is shot from the player. 
	def touch_began(self, touch):
		laser = sc.SpriteNode('spc:LaserBlue9', position=self.player.position, z_position = -1, parent = self)
		laser.run_action(sc.Action.sequence(sc.Action.move_by(0,1000), sc.Action.remove()))
		self.lasers.append(laser)
		sound.play_effect('arcade:Laser_1')
		
		
if __name__ == '__main__':
	sc.run(Game(), sc.PORTRAIT, show_fps = True) 
