class MovingPlatformManager:
	
	def __init__(self, level):
		self.level = level
		self.ticker = 0
		directions = get_hacks_for_level(level.name, 'moving_platforms')
		if directions == None:
			directions = []
		else:
			directions = safe_map(lambda x:x.split(), directions)
		self.platforms = self.level.get_moving_platforms()
		self.num_platforms = len(self.platforms)
		while len(directions) < self.num_platforms:
			directions.append(['P'])
		self.directions = directions
			
	def update(self):
		self.ticker += 1
		if self.ticker % 60 == 0:
			level = self.level
			i = 0
			while i < self.num_platforms:
				platform = self.platforms[i]
				directions = self.directions[i]
				direction = directions[0]
				if direction == 'P':
					directions.pop(0)
					directions.append('P')
				else:
					target = [platform[0], platform[1], platform[2]]
					if direction == 'NW':
						target[0] -= 1
					elif direction == 'NE':
						target[1] -= 1
					elif direction == 'SW':
						target[1] += 1
					else:
						target[0] += 1
					t_lower = level.get_tile_at(target[0], target[1], target[2])
					t_upper = level.get_tile_at(target[0], target[1], target[2] + 1)
					if t_lower == None and t_upper == None:
						mp = level.modify_block(platform[0], platform[1], platform[2], None)
						level.modify_block(target[0], target[1], target[2], mp)
						directions.append(directions.pop(0))
						self.platforms[i] = target
				i += 1
