
class MyEvent:
	def __init__(self, key, down):
		self.key = key
		self.down = down
		self.up = not down

_input_manager = None

def get_input_manager():
	global _input_manager
	if _input_manager == None:
		_input_manager = InputManager()
	return _input_manager

class InputManager:
	def __init__(self):
		self.cursor = (0, 0)
		self.mouse_pressed = False
		self.mouse_events = []
		self.joysticks = []
		self.active_joystick = -1
		self.raw_keyups = []
		self.read_config_save()
		self.active_actual_joystick = -1
		self.activate_joysticks()
		self.events = []
		self.quitAttempt = False
		self.init_default_key_config()
		self.my_pressed = {
			'start': False,
			'left': False,
			'right': False,
			'up': False,
			'down': False,
			'spray': False,
			'walkie': False
		}
		
		self.axes = [0.0, 0.0]
	
	def init_default_key_config(self):
		self._key_mapping = {
			Game.KeyboardKey.ENTER: 'start',
			Game.KeyboardKey.LEFT: 'left',
			Game.KeyboardKey.RIGHT: 'right',
			Game.KeyboardKey.UP: 'up',
			Game.KeyboardKey.DOWN: 'down',
			Game.KeyboardKey.SPACE: 'spray',
			Game.KeyboardKey.W: 'walkie'
		}
		t = read_file('data/key_config.txt')
		
		things = 'start left right up down spray walkie'.split()
		if t != None:
			for line in t.split('\n'):
				parts = line.split(':')
				if len(parts) == 2:
					action = parts[0]
					value = parseInt(parts[1])
					
					if value > 0 and action in things:
						for k in self._key_mapping.keys():
							if self._key_mapping[k] == action:
								self._key_mapping.pop(k)
								break
						self._key_mapping[value] = action
		
	
	def save_key_config(self):
		output = []
		for key in self._key_mapping.keys():
			action = self._key_mapping[key]
			output.append(action + ':' + str(key))
		output = '\r\n'.join(output)
		write_file('data/key_config.txt', output)
	
	def set_key_config(self, action, key):
		for k in self._key_mapping.keys():
			if self._key_mapping[k] == action:
				self._key_mapping.pop(k)
				break
		self._key_mapping[key] = action
	
	def set_active_actual_joystick(self, id):
		if id == -1:
			self.active_actual_joystick = -1
			self.active_joystick = -1
		elif len(self.actual_joysticks) > id:
			self.active_actual_joystick = id
			name = self.actual_joysticks[self.active_actual_joystick].get_name().strip()
			found = False
			i = 0
			for js in self.joysticks:
				if js.get('name', '').lower() == name.lower():
					found = True
					self.active_joystick = i
				i += 1
			if not found:
				self.active_joystick = len(self.joysticks)
				self.joysticks.append({'name': name})
	
	def get_config_label_for_key_for_keyboard(self, key):
		for k in self._key_mapping.keys():
			if self._key_mapping[k] == key:
				output = pygame.key.name(k)
				return output[0].upper() + output[1:]
		return "Not configured!"
	
	def get_config_label_for_key_for_active(self, key):
		if self.active_joystick != -1:
			js = self.joysticks[self.active_joystick]
			value = js.get(key, None)
			if value == None:
				return "Not configured!"
			if value[0] == 'axis':
				output = "Axis " + str(value[1])
				if value[2].endswith('+'):
					output = "Positive " + output
				else:
					output = "Negative " + output
				
			elif value[0] == 'hat':
				output = "Hat " + str(value[1])
				if value[2].startswith('x'):
					output = "X " + output
				else:
					output = "Y " + output
				if value[2].endswith('-'):
					output = "Negative " + output
				else:
					output = "Positive " + output
			else:
				output = "Button " + str(value[1])
				
			return output
		return "---"
	
	def get_cursor_position(self):
		return self.cursor
	
	def get_mouse_status(self):
		return self.mouse_pressed
	
	def get_events(self, window):
		events = []
		self.raw_keyups = []
		keyboard_only = True
		self.axes = [0.0, 0.0]
		for event in window.pumpEvents():
			if event.type == Game.EventType.QUIT:
				self.quitAttempt = True
				return []
			elif event.type == Game.EventType.MOUSE_LEFT_DOWN or event.type == Game.EventType.MOUSE_LEFT_UP:
				self.mouse_events.append((event.x, event.y, False, event.down))
				self.cursor = (event.x, event.y)
				self.mouse_pressed = event.down
			elif event.type == Game.EventType.MOUSE_MOVE:
				self.mouse_events.append((event.x, event.y, True, False))
				self.cursor = (event.x, event.y)
			elif event.type == Game.EventType.KEY_DOWN or event.type == Game.EventType.KEY_UP:
				if not event.down:
					self.raw_keyups.append(event.key)
				action = self._key_mapping.get(event.key)
				
				if action != None:
					self.my_pressed[action] = event.down
					events.append(MyEvent(action, event.down))
		self.axes[0] = 2.0 if self.my_pressed['right'] else 0.0
		self.axes[0] = -2.0 if self.my_pressed['left'] else self.axes[0]
		self.axes[1] = 2.0 if self.my_pressed['down'] else 0.0
		self.axes[1] = -2.0 if self.my_pressed['up'] else self.axes[1]

		joystick = None
		config = None
		any_axes_found = False
		if self.active_joystick != -1:
			config = self.joysticks[self.active_joystick]
			name = config.get('name', '')
			for js in self.actual_joysticks:
				name2 = js.get_name()
				if name.lower() == name2.lower():
					joystick = js
					break
		
		if joystick != None and config != None:
			cached_poll = {}
			for action in ('right', 'left', 'up', 'down', 'start', 'spray', 'walkie'):
				direction = False
				c = config.get(action, None)
				x = False
				if c != None:
					n = c[1]
					if c[0] == 'axis':
						direction = True
						x = cached_poll.get('a' + str(n))
						if x == None:
							x = joystick.get_axis(n)
							if abs(x) < 0.01:
								x = 0
							cached_poll['a' + str(n)] = x
						
						if c[2][1] == '+':
							if x < 0:
								x = 0
						else:
							if x > 0:
								x = 0
							else:
								x *= -1
						x = abs(x)
						
						if x > 0.01:
							keyboard_only = False
							if not any_axes_found:
								any_axes_found = True
								self.axes = [0.0, 0.0]
						
					elif c[0] == 'hat':
						direction = True
						x = cached_poll.get('h' + str(n))
						if x == None:
							x = joystick.get_hat(n)
							cached_poll['h' + str(n)] = x
						if c[2][0] == 'x':
							x = x[0]
						else:
							x = x[1]
						
						if c[2][1] == '+':
							if x < 0:
								x = 0
						else:
							if x > 0:
								x = 0
							else:
								x *= -1
						x = abs(x)
					elif c[0] == 'button':
						x = cached_poll.get('b' + str(n))
						if x == None:
							x = joystick.get_button(n)
							cached_poll['b' + str(n)] = x
						
					
					if action in ('start', 'spray', 'walkie'):
						pushed = x
						if direction:
							pushed = x >= .5
						if self.my_pressed[action] != pushed:
							self.my_pressed[action] = pushed
							events.append(MyEvent(action, pushed))
					elif action in ('left', 'right', 'down', 'up'):
						
						toggled = False
						if direction:
							pushed = x + 0.0
						else:
							pushed = 0.0 if (pushed < .5) else 1.0
						toggled = pushed > .2
						if pushed < 0.01:
							pushed = 0
						
						if toggled != self.my_pressed[action]:
							self.my_pressed[action] = toggled
							events.append(MyEvent(action, toggled))
						
						if action == 'left':
							if abs(self.axes[0]) < 0.01 and pushed > 0.01:
								self.axes[0] = -2 * pushed
						
						elif action == 'right':
							if abs(self.axes[0]) < 0.01 and pushed > 0.01:
								self.axes[0] = 2 * pushed
								
						elif action == 'up':
							if abs(self.axes[1]) < 0.01 and pushed > 0.01:
								self.axes[1] = -2 * pushed
								
						elif action == 'down':
							if abs(self.axes[1]) < 0.01 and pushed > 0.01:
								self.axes[1] = 2 * pushed
		
		self.axes[0] = self.axes[0] / 1.8
		
		x = self.axes[0]
		y = self.axes[1]
		
		if not any_axes_found and x != 0 and y != 0:
			xsign = 1 if (x > 0) else -1
			ysign = 1 if (y > 0) else -1
			x = 1.2 * xsign
			y = 1.2 * ysign
			
		if abs(x) < 0.05 and abs(y) < 0.05:
			rx = 0.0
			ry = 0.0
			
		else:
			ang = 3.14159265 / 4.0
			c = math.cos(ang)
			s = math.sin(ang)
			rx = x * c + y * s
			ry = -x * s + y * c
		
		self.axes[0] = rx / 1.8
		self.axes[1] = ry / 1.8
		
		return events
			
	def activate_joysticks(self):
		self.actual_joysticks = []
		active_joystick_name = None
		if self.active_joystick != -1:
			active_joystick_name = self.joysticks[self.active_joystick].get('name', '').strip().lower()
		for i in range(pygame.joystick.get_count()):
			js = pygame.joystick.Joystick(i)
			js.init()
			self.actual_joysticks.append(js)
			name = js.get_name().strip().lower()
			if name == active_joystick_name:
				self.active_actual_joystick = i
		
		if self.active_actual_joystick == -1:
			self.active_joystick = -1
			
	def verify_axis_value(self, x):
		return len(x) == 2 and x[0] in 'xy' and x[1] in '-+'
	
	def save_config(self):
		output = []
		if self.active_joystick != -1 and self.active_joystick < len(self.joysticks):
			output.append('#active: ' + self.joysticks[self.active_joystick].get('name', ''))
		else:
			output.append('#active: ')
		for joystick in self.joysticks:
			output.append(self._save_joystick(joystick))
		output = '$'.join(output)
		write_file('data/input_config.txt', output)
	
	
	def _save_joystick(self, config):
		output = []
		for key in config.keys():
			if key == 'name':
				value = config[key]
			else:
				value = ' '.join(safe_map(str, config[key]))
			
			row = '#' + key + ': ' + value
			
			output.append(row)
			
		return '\r\n'.join(output)
	
	def read_config_save(self):
		prev = read_file('data/input_config.txt')
		if prev != None:
			data = prev.strip().split('$')
			if len(data) > 0:
				active = data[0].strip()
				parts = active.split(':')
				active_joystick_name = None
				if len(parts) >= 2 and parts[0].strip() == '#active':
					active_joystick_name = ':'.join(parts[1:]).strip()
				for config in data[1:]:
					lines = config.split('\n')
					data = {}
					for line in lines:
						line = line.strip()
						if len(line) > 0 and line[0] == '#':
							parts = line[1:].split(':')
							if len(parts) == 2:
								key = parts[0].strip()
								value = parts[1].strip().split(' ')
								if value[0] == 'axis':
									if len(value) == 3:
										n = parseInt(value[1])
										if self.verify_axis_value(value[2]):
											data[key] = ('axis', n, value[2])
								elif value[0] == 'button':
									if len(value) == 2:
										n = parseInt(value[1])
										data[key] = ('button', n)
								elif value[0] == 'hat':
									if len(value) == 3:
										n = parseInt(value[1])
										if self.verify_axis_value(value[2]):
											data[key] = ('hat', n, value[2])
								elif key == 'name':
									data[key] = ' '.join(value).strip()
					name = data.get('name', None)
					if name != None and len(name) > 0:
						if active_joystick_name != None and active_joystick_name.lower() == name.lower():
							self.active_joystick = len(self.joysticks)
						self.joysticks.append(data)
	
	def get_mouse_events(self):
		output = self.mouse_events
		self.mouse_events = []
		return output