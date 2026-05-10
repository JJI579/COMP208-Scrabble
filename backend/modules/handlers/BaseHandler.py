from backend.modules.handlers import ConnectionsHandler
from modules.handlers import LobbyHandler, GameHandler, CreationHandler

class BaseHandler:
	def __init__(self):
		self.connections = ConnectionsHandler.ConnectionHandler()
		self.create = CreationHandler.CreationHandler()
		self.game = GameHandler.GameHandler()
		self.lobby = LobbyHandler.LobbyHandler()

handler = BaseHandler()

