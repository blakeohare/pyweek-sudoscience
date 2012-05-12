class EndSceneNonStory:
	def __init__(self):
		self.next = self
		
	def process_input(self, events, pressed, axes, mouse):
		for event in events:
			if event.down:
				if event.key == 'start' or event.key == 'spray' or event.key == 'walkie':
					self.next = TransitionScene(self, MainMenuScene())
	
	def update(self, counter):
		pass
	
	def render(self, screen, counter):
		img = get_text("This is the end of the game.", 30, (255, 255, 255))
		img2 = get_text("To see the ending, play in story-mode.", 14, (255, 255, 255))
		
		screen.blit(img, (200 - img.get_width() // 2, 100))
		screen.blit(img2, (200 - img2.get_width() // 2, 150))