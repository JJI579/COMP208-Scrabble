from newscrab import Scrabble

class BaseGame:

	def __init__(self) -> None:
		pass

	def get_next_turn(self) -> Player:
		pass


class GroupGame(BaseGame):

	def __init__(self, group) -> None:
		super().__init__()
		self.group = group


class BotGame(BaseGame):

	def __init__(self, user) -> None:
		super().__init__()
		self.user = user

class NormalGame(BaseGame):

	def __init__(self) -> None:
		super().__init__()