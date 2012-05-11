"""

on_circuits:
	pick 1 circuit PER CIRCUIT GROUP to indicate that that group should
	always remain on.
	A power input or output pad counts as a circuit so something like...
		---wire---[pad]---wire---
	...is 1 group, not 2.
	
	Format is a list of tuples that are (x, y, and z) coordinates. 
	You can get these from the map editor title bar

moving_platforms:
	directions map to platforms in tile parser order.
	lowest y first, then lowest x, then lowest z
	
	P is pause
"""

def make_sprite(type, col, row, layer):
	return Sprite(col * 16 + 8, row * 16 + 8, layer * 8, type)

def _hack_introduce_sprites_intro(level, counter):
	
	if counter == 120:
		s = make_sprite('supervisor', 14, 0, 1)
		s.set_automation(Automation(level, 'intro_supervisor'))
		return [s]
	elif counter == 150:
		s = make_sprite('janitor', 14, 0, 1)
		s.set_automation(Automation(level, 'intro_janitor'))
		return [s]
	return []

def _hack_do_stuff_intro(playscene, level, counter):
	if counter == -1:
		playscene.player.set_automation(Automation(level, 'intro_protagonist'))
	
	if counter == 329 + 14:
		playscene.next = DialogScene(playscene, 'intro')
	
	if counter == 1000:
		playscene.next = TransitionScene(playscene, PlayScene(get_level_manager().get_next_level('intro')))
	
def _hack_dialog_intro_transition_level_one(playscene, level):
	dialog_scene = playscene.next
	dialog_scene.next = TransitionScene(dialog_scene, PlayScene('1-1'))


_level_specific_hacks = {
	'intro': {
		'introduce_sprites': _hack_introduce_sprites_intro,
		'do_stuff': _hack_do_stuff_intro,
		'dialog': { 'transition_level_one': _hack_dialog_intro_transition_level_one }
	},
	
	'9-0': {
		'on_circuits': [
			(1, 2, 0)
		]
	},
	
	'15-0': {
		'moving_platforms': [
			'NW P P SE SE SE P P NW NW', 
			'SW P P NE NE NE P P SW SW'
		]
	},
	
	'16-0': {
		'moving_platforms': [
			'NW NW P P SE SE P P',
			'NE NE NE NE P P SW SW SW SW P P',
			'NW NW NW NW P P SE SE SE SE P P'
		]
	},
	
	'17-3': {
		'moving_platforms': [
			'SW SW SW SW SW P P NE NE NE NE NE P P'
		]
	},
	
	'18-0': {
		'moving_platforms': [
			'SE SE NW NW NW NW NW NW NW NW NW NW SE SE SE SE SE SE SE SE',
			'NW NW SE SE SE SE SE SE SE SE SE SE NW NW NW NW NW NW NW NW',
			'NW NW NW NW NW NW NW NW NW SE SE SE SE SE SE SE SE SE SE NW',
			'NW NW NW NW SE SE SE SE SE SE SE SE SE SE NW NW NW NW NW NW',
			'SE SE SE NW NW NW NW NW NW NW NW NW NW SE SE SE SE SE SE SE',
			'NW SE SE SE SE SE SE SE SE SE SE NW NW NW NW NW NW NW NW NW',
			'SE SE SE SE NW NW NW NW NW NW NW NW NW NW SE SE SE SE SE SE',
			'NW NW NW NW NW NW NW SE SE SE SE SE SE SE SE SE SE NW NW NW',
			'SE SE SE SE SE SE SE SE SE SE NW NW NW NW NW NW NW NW NW NW',
			'SE SE SE SE SE SE SE SE NW NW NW NW NW NW NW NW NW NW SE SE',
			'NW NW NW NW NW NW NW NW NW NW SE SE SE SE SE SE SE SE SE SE'
		]
	},
	
	'21-0': {
		'moving_platforms': [
			'NW NW P P SE SE SE SE P P NW NW'
		]
	},
	
	'25-0': {
		'moving_platforms': [
			'SE SE NW NW NW NW NW SE SE SE',
			'SE SE SE SE NW NW NW NW NW SE',
			'NW NW NW NW NW SE SE SE SE SE',
			'SE SE NW NW NW NW NW SE SE SE',
			'SE SE SE SE SE NW NW NW NW NW',
			'SE NW NW NW NW NW SE SE SE SE',
			'SE SE SE SE NW NW NW NW NW SE',
			'SE SE SE NW NW NW NW NW SE SE',
			'NW NW NW NW NW SE SE SE SE SE'
		]
	},
	
	'24-0': {
		'moving_platforms': [
			'P P SE SE SE SE SE SE P P NW NW NW NW NW NW',
			'NE P P SW SW P P NE',
			'NE NE NE NE NE NE NE NE P P SW SW SW SW SW SW SW SW P P',
			'P SW SW P P NE NE P'
		]
	},
	
	'90-0': {
		'moving_platforms': [
			'SW SW SW P P NE NE NE P P'
		]
	}
}

def get_hacks_for_level(name, category):
	global _level_specific_hacks
	dict = _level_specific_hacks.get(name)
	if dict != None:
		return dict.get(category)
	return None