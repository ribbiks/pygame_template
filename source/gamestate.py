
class GameState:
	def __init__(self, game_runner):
		self.accepting_inputs = True
		self.is_updating      = True
		self.is_drawing       = True
		# pointer to GameRunner object so each GameState object has access to everything
		self.game_runner = game_runner

	def update(self):
		raise NotImplementedError()

	def draw(self):
		raise NotImplementedError()

	def reset(self):
		raise NotImplementedError()
	