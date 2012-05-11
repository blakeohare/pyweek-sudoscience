class TextPrinter:
	def __init__(self, text, color):
		self.text = text
		self.color = color
		self.alternator = False
		
	def get_next_char(self):
		t = ''
		if self.alternator:
			
			if len(self.text) == 0:
				return None
			t = self.text[0]
			self.text = self.text[1:]
		self.alternator = not self.alternator
		return t


class DialogPause:
	def __init__(self, amount):
		self.remaining = amount
	
	def keep_pausing(self):
		self.remaining -= 1
		return self.remaining >= 0
		
	

class DialogScene:
	def __init__(self, playscene, id):
		self.id = id
		self.next = self
		self.phase_duration = 60
		self.playscene = playscene
		self.initialize_script(id)
		self.text_printer = None
		self.prompt_for_continue = False
		self.pauser = None
		self.surfaces = {}
		self.i = 0
		self.phase = 'init'
		self.phase_counter = 0
		self.active_portrait = None
		self.buffer = []
		self.clear_on_continue = False
		self.colors = {
			'w':(255, 255, 255),
			's':(220, 180, 140),
			'j':(140, 180, 230),
			'p':(255, 120, 180)
		}
		self.buffer_clear_counter = -42
		self.frame_yielding = -42
		self.buffer_shift_offset = 0
	
	def initialize_script(self, id):
		file = read_file('data/dialog/' + id + '.txt')
		self.lines = file.split('\n')
		self.labels = {}
		i = 0
		while i < len(self.lines):
			parts = self.lines[i].split('|')
			if parts[0] == 'label' and len(parts) == 2:
				self.labels[parts[1]] = i
			i += 1
		
	def process_input(self, events, pressed, axes, mouse):
		pushed = False
		for event in events:
			if event.key in ('start', 'spray', 'walkie') and event.down:
				pushed = True
		
		if pushed and self.prompt_for_continue:
			# TODO: this can be improved so it isn't quite as jumpy
			# should also flush all text_printer queues
			self.prompt_for_continue = False
			if self.clear_on_continue:
				self.buffer = []
				
		
	
	def update(self, counter):
		self.phase_counter += 1
		self.frame_yielding -= 1
		
		if self.frame_yielding >= 0:
			for s in self.playscene.sprites:
				if s.issupervisor:
					#print 'supervisor:', s.automation.counter
					pass
			self.playscene.update(counter)
		
		keep_going = True
		while keep_going:
			if self.phase == 'init':
				if self.phase_counter == self.phase_duration:
					self.phase = 'dialog'
				keep_going = False
			elif self.phase == 'end':
				if self.phase_counter == self.phase_duration:
					self.next = self.playscene
					self.next.next = self.next
				keep_going = False
			elif self.prompt_for_continue:
				keep_going = False
			elif self.text_printer != None:
				n = self.text_printer.get_next_char()
				if n == None:
					self.text_printer = None
				else:
					self.buffer[-1][0] += n
					keep_going = False
			elif self.buffer_clear_counter > 0:
				self.buffer_clear_counter -= 1
				if self.buffer_clear_counter == 0:
					self.buffer = self.buffer[1:]
				keep_going = False
			elif self.pauser != None:
				if not self.pauser.keep_pausing():
					self.pauser = None
				keep_going = False
			else:
				if self.i < len(self.lines):
					line = trim(self.lines[self.i])
					if len(line) > 0:
						parts = line.split('|')
						command = parts[0]
						if command == 'i':
							self.change_portrait(parts[1])
						elif command == 'r':
							self.change_portrait(None)
						elif command == 'p':
							self.pauser = DialogPause(int(parts[1]))
						elif command == 's':
							if len(self.buffer) == 3:
								self.buffer_clear_counter = 10
								keep_going = False
								self.i -= 1
							else:
								color = self.colors[parts[1]]
								text = parts[2]
								self.buffer.append(['', color])
								self.text_printer = TextPrinter(text, None)
						elif command == 'c':
							self.prompt_for_continue = True
							self.clear_on_continue = False
							keep_going = False
						elif command == 'cc':
							self.prompt_for_continue = True
							self.clear_on_continue = True
						elif command == 'h':
							hack_function = get_hacks_for_level(self.playscene.level.name, 'dialog_hack')[parts[1]]
							hack_function(self.playscene, self.playscene.level)
						elif command == 'y':
							self.frame_yielding = int(parts[1])
						elif command == 'goto':
							self.do_goto(parts[1])
						elif command == 'if':
							var = parts[1]
							operator = parts[2]
							value = int(parts[3])
							label = parts[4]
							self.do_if(operator, var, value, label)
						elif command == 'end':
							self.phase_counter = 0
							self.phase = 'end'
					self.i += 1
				else:
					self.phase = 'end'
					self.phase_counter = 0
					keep_going = False
	
	def change_portrait(self, id):
		if id == None:
			self.active_portrait = None
		else:
			self.active_portrait = get_image('portraits/' + id + '.png')
		
	
	def do_goto(self, label):
		line = self.labels.get(label)
		if line != None:
			i = line
	
	def do_if(self, op, var, val, lbl):
		
		finders = [get_persisted_level_int, get_persisted_session_int, get_persisted_forever_int]
		value = 0
		for finder in finders:
			value = finder(var)
			if value != 0:
				break
		
		if op == '=':
			if value == val:
				self.do_goto(lbl)
		elif op == '<':
			if value < val:
				self.do_goto(lbl)
		elif op == '>':
			if value < val:
				self.do_goto(lbl)
		elif op == '~':
			if value != val:
				self.do_goto(lbl)
		
	
	def render_box(self, screen, phase, counter):
		
		width = 300
		height = 100
		if phase == 'end':
			counter = self.phase_duration - counter
		
		if phase == 'dialog':
			pass
		else:
			half = self.phase_duration // 2
			if counter < self.phase_duration // 2:
				height = 10
			else:
				height = 90 * (counter - self.phase_duration // 2) // (self.phase_duration // 2) + 10
			if counter < half:
				width = counter * 300 // half
			else:
				width = 300
			
		key = str(width) + '^' + str(height)
		surface = self.surfaces.get(key, None)
		if surface == None:
			surface = pygame.Surface((width, height)).convert()
			surface.fill((0, 0, 0))
			surface.set_alpha(180)
			self.surfaces[key] = surface
		
		x = screen.get_width() // 2 - width // 2
		y = 100 - height // 2
		
		screen.blit(surface, (x, y))
		pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(x, y, width, height), 1)
		
	def render(self, screen, counter):
		
		self.playscene.render(screen, counter)
		
		self.render_box(screen, self.phase, self.phase_counter)
		
		if self.phase == 'dialog':
			if self.active_portrait != None:
				screen.blit(self.active_portrait, (10, 10))
			
			font_size = 18
			line_height = 23
			last_color = (255, 255, 255)
			y = 70
			
			cursor_height = y + line_height * 3
			
			if self.buffer_clear_counter > 0:
				y -= (10 - self.buffer_clear_counter) * line_height // 10
			for line in self.buffer:
				text = line[0]
				color = line[1]
				last_color = color
				img = get_text(text, font_size, color)
				screen.blit(img, (89, y))
				y += line_height
			
			if self.prompt_for_continue and (counter // 10) % 2 == 0:
				y = cursor_height
				pygame.draw.polygon(screen, last_color, [(300, y), (308, y), (304, y + 5)])