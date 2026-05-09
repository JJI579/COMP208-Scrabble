from backend.modules.handlers import ConnectionsHandler
from modules.handlers import LobbyHandler, GameHandler, CreationHandler, WebsocketHandler

class BaseHandler:
	def __init__(self):
		self.connections = ConnectionsHandler.ConnectionHandler()
		self.create = CreationHandler.CreationHandler()
		self.game = GameHandler.GameHandler()
		self.lobby = LobbyHandler.LobbyHandler()
		self.websocket = WebsocketHandler.WebsocketHandler()

handler = BaseHandler()

