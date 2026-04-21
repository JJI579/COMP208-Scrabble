
class ScrabbleMoveError(Exception):
	"""Base class for all move-related errors"""
	pass

class InvalidFirstWordPlacementError(ScrabbleMoveError):
	"""First move must cover the center tile"""
	pass

class CellOccupiedError(ScrabbleMoveError):
	"""The cell is already occupied"""
	pass



class InvalidMainWordError(ScrabbleMoveError):
	"""The main word formed is not valid"""
	pass

class NoWordsFormedError(ScrabbleMoveError):
	"""Move did not form any valid words on the board"""
	pass
