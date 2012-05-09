_debug_message = None
def set_user_debug_message(text):
	global _debug_message
	_debug_message = text

def get_user_debug_message():
	global _debug_message
	return _debug_message

"""def get_inputs(event_list, pressed, isometric):
	global _key_mapping
	pg_pressed = pygame.key.get_pressed()
	for event in pygame.event.get():
		if event.type in (pygame.KEYDOWN, pygame.KEYUP):
			down = event.type == pygame.KEYDOWN
			if down and event.key == pygame.K_F4:
				if pg_pressed[pygame.K_LALT] or pg_pressed[pygame.K_RALT]:
					return True
			elif down and event.key == pygame.K_ESCAPE:
				return True
			
			my_key = _key_mapping.get(event.key)
			if my_key != None:
				my_event = MyEvent(my_key, down)
				event_list.append(my_event)
				pressed[my_key] = down
		elif event.type == pygame.QUIT:
			return True
	
	x_axis = 0
	y_axis = 0
	
	if pressed['left']:
		x_axis = -2
	elif pressed['right']:
		x_axis = 2
	if pressed['up']:
		y_axis = -2
	elif pressed['down']:
		y_axis = 2
	
	do_one_off_fix = x_axis != 0 and y_axis != 0
	if isometric:
		fx_axis = x_axis
		fy_axis = -x_axis
		fx_axis += y_axis
		fy_axis += y_axis
		x_axis = fx_axis
		y_axis = fy_axis
	
	# BUG: one off fix
	if do_one_off_fix:
		x_axis = x_axis // 2
		y_axis = y_axis // 2
		
	pressed['x-axis'] = x_axis
	pressed['y-axis'] = y_axis
	return False
	"""
			

def main():

	pygame.init()
	real_screen = pygame.display.set_mode((800, 600))
	fake_screen = pygame.Surface((400, 300))
	fps = 60

	pressed = {
		'start': False,
		'left': False,
		'right': False,
		'down': False,
		'up': False,
		'action': False,
		'x-axis': 0,
		'y-axis': 0
	}
	
	load_persistent_state()
	
	if os.path.exists('start.txt'):
		lines = trim(read_file('start.txt').split('\n'))
		
		if lines[0] == 'normal':
			active_scene = MainMenuScene()
		else:
			active_scene = PlayScene(lines[0])
			coords = safe_map(int, lines[1].split(','))
			active_scene.player.x = coords[0] * 16 + 8
			active_scene.player.y = coords[1] * 16 + 8
	else:
		active_scene = PlayScene('7-0')
	counter = 0
	
	input_manager = get_input_manager()
	
	while active_scene != None:
		start = time.time()
		
		counter += 1
		
		event_list = input_manager.get_events()
		pressed = input_manager.my_pressed
		try_quit = input_manager.quitAttempt
		axes = input_manager.axes
		
		active_scene.process_input(event_list, pressed, axes)
		active_scene.update(counter)
		
		fake_screen.fill((0, 0, 0))
		active_scene.render(fake_screen, counter)
		
		debug_message = get_user_debug_message()
		if debug_message != None:
			fake_screen.blit(get_text(debug_message, 20, (255, 0, 0)), (10, 10))
		
		pygame.transform.scale(fake_screen, (real_screen.get_width(), real_screen.get_height()), real_screen)
		
		active_scene = active_scene.next
		
		if try_quit:
			active_scene = None
			
		pygame.display.flip()
		
		end = time.time()
		
		diff = end - start
		delay = 1.0 / fps - diff
		if delay > 0:
			time.sleep(delay)
		# TODO: print FPS when in debug mode
