from modules.websocket.WebsocketWrapper import WebsocketWrapper

class PacketHandler:

	def __init__(self):
		pass

	async def player_join(self, data: dict, websocket: WebsocketWrapper):
		# Handle generic then pass off
		gameObject = websocket.get_game()
		if gameObject == None:
			# TODO: No game exists
			return
		if not websocket.get_authenticated():
			# TODO: not authenticated
			return
		if gameObject.fetch_player(websocket.get_user()):
			# TODO: user already in game
			return
		gameObject.create_player(websocket.get_user())
		# TODO: inform user they are in game.
		if gameObject.get_type() == 'GROUP':
			await self._group_player_join(data, websocket)
		else:
			# TODO: return the data that player has joined
			pass

	# Make user join first group available
	async def _group_player_join(self, data: dict, websocket: WebsocketWrapper):
		pass

	async def player_leave(self, data: dict, websocket: WebsocketWrapper):
		pass


	async def game_update(self, data: dict, websocket: WebsocketWrapper):
		pass

	async def group_join(self, data: dict, websocket: WebsocketWrapper):
		pass

	async def game_start(self, data: dict, websocket: WebsocketWrapper):
		pass
	async def game_turn(self, data: dict, websocket: WebsocketWrapper):
		pass
	async def chat_message(self, data: dict, websocket: WebsocketWrapper):
		pass
	async def draft_placed(self, data: dict, websocket: WebsocketWrapper):
		pass
	async def turn_confirmation(self, data: dict, websocket: WebsocketWrapper):
		pass
	async def turn_decline(self, data: dict, websocket: WebsocketWrapper):
		pass
	async def turn_request(self, data: dict, websocket: WebsocketWrapper):
		pass
	async def finish_game(self, data: dict, websocket: WebsocketWrapper):
		pass
	async def skip_turn(self, data: dict, websocket: WebsocketWrapper):
		pass
	async def switch_turn(self, data: dict, websocket: WebsocketWrapper):
		pass