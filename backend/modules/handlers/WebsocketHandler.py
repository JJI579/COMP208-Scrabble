from websocket.WebsocketWrapper import WebsocketWrapper
from modules.schema import UserFetch
from modules.scrabble.newgame import BaseGame


class WebsocketHandler:
	
	def __init__(self):
		pass
	
	async def verify_websocket(self, websocket: WebsocketWrapper):
		if not websocket.get_authenticated():
			raise Exception("Unauthenticated")
		
	async def get_game_and_connection(self, websocket: WebsocketWrapper, verified: bool=False):
		if not verified:
			try:
				await self.verify_websocket(websocket)
			except Exception as e:
				print("Websocket verification failed:", e)
				raise e
		try:
			game = await self.get_game(websocket, True)
			conn = await self.get_connection(websocket, True)
			return game, conn
		except Exception as e:
			print("Error occurred while fetching game and connection:", e)
			raise e
		
	async def get_game(self, websocket: WebsocketWrapper, verified: bool=False) -> BaseGame:
		if not verified:
			try:
				await self.verify_websocket(websocket)
			except Exception as e:
				print("Websocket verification failed:", e)
				raise e
	
	async def get_connection(self, websocket: WebsocketWrapper, verified: bool=False) -> Connection:
		if not verified:
			try:
				await self.verify_websocket(websocket)
			except Exception as e:
				print("Websocket verification failed:", e)
				raise e

		