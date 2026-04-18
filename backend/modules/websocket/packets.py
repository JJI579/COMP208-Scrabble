
from typing import Literal, TypedDict
from modules.schema import PacketType, UserFetch

class BasePacket(TypedDict):
	t: PacketType
	d: dict

import datetime, random

class Packets:

	def __init__(self) -> None:
		pass

	def create_packet(self, t: PacketType, d: dict) -> BasePacket:
		return {
			"t": t,
			"d": d
		}
		


# These packets are sent when the game has not started yet
class StartPackets(Packets):

	def __init__(self) -> None:
		super().__init__()
	
	def confirm_leave(self, gameID: str):
		data = {
			"gameID": gameID
		}
		return self.create_packet("CONFIRM_LEAVE", data)
	
	def start_game(self, gameID: str):
		data = {
			"gameID": gameID
		}
		return self.create_packet("GAME_START", data)

	def cancel_game(self, gameID: str):
		data = {
			"gameID": gameID
		}
		return self.create_packet("GAME_CANCEL", data)
		
	def invalid_game(self, gameID: str):
		data = {
			"gameID": gameID
		}
		return self.create_packet("INVALID_GAME", data)
	
	def join_game(self, gameID: str, user: dict):
		data = {
			"gameID": gameID,
			"user": user
		}
		# returns player_join
		return self.create_packet("PLAYER_JOIN", data)

	def leave_game(self, gameID: str, user: dict):
		# returns player_leave
		data = {
			"gameID": gameID,
			"user": user
		}
		return self.create_packet("PLAYER_LEAVE", data)

	def join_group(self,user: dict, groups: list[list[int]]):
		# returns group_join
		data = {
			"user": user,
			"groups": groups
		}
		return self.create_packet("GROUP_JOIN", data)

	def leave_group(self, gameID: int, user: dict, groupID: int, groups: list[list[int]]):
		# i think groups array will be where each group is an array
		# [[uID1, uID2], [uID3, uID4]]
		data = {
			"gameID": gameID,
			"user": user,
			# this is to show what group was affected
			"focusedID": groupID,
			"groups": groups
		}
		return self.create_packet("GROUP_LEAVE", data)

	def update_group(self, gameID: int, groups: list[list[int]]):
		data = {
			"gameID": gameID,
			"groups": groups
		}
		return self.create_packet("GROUP_UPDATE", data)

	def update_game(self, gameInfo: dict, gameID: str):
		data = {
			"gameID": gameID,
			"game": gameInfo
		}
		return self.create_packet("GAME_UPDATE", data)

	def replace_shelf_game(self):
		# these are the letters that the user has!
		# need to reconsider whether this will be a packet or not or just turn_update
		pass

	def place_word(self):
		# game_place
		pass

	

# These packets are sent during the game (game has started)
class DuringPackets(Packets):

	def __init__(self) -> None:
		pass

	def turn_request(self, data: dict):
		return self.create_packet("TURN_REQUEST", data)

	def turn_confirmation(self, data: dict):
		return self.create_packet("TURN_CONFIRMATION", data)

	def turn_decline(self, data: dict):
		return self.create_packet("TURN_DECLINE", data)
	
	def draft_placed(self, data: dict):
		# {'placed': {'113': [0, 'N', None], '114': [2, 'G', None]}}
		return self.create_packet("DRAFT_PLACED", data)
	
	def game_update(self, gameinfo: dict):

		return self.create_packet("GAME_UPDATE_ONGOING", gameinfo)
	
	def chat_message(self, message: str, author: UserFetch, partner: bool = False):
		messageObject = {
			"id": random.randint(0,10000),
			"text": message, 
			"created_at": datetime.datetime.now().isoformat(),
			"partner": partner,
			"author": {
				"id": author.userID,
				"name": author.userName
			}
		}
		return self.create_packet("CHAT_MESSAGE", messageObject)
	
	
class AuthenticationPackets(Packets):
	
	def __init__(self) -> None:
		super().__init__()
	
	def identify(self, wsID: str):
		data = {
			'ID': wsID
		}
		return self.create_packet('IDENTIFY', data)

	def not_found(self):
		return self.create_packet('NOT_FOUND', {})

class EndPackets(Packets):

	def __init__(self) -> None:
		pass

	def game_end(self, gameinfo: dict):

		return self.create_packet("GAME_END", gameinfo)
	
class AllPackets:
	def __init__(self) -> None:
		self.start = StartPackets()
		self.during = DuringPackets()
		self.end = EndPackets()
		self.authentication = AuthenticationPackets()
	
	def error(self, text: str):
		return {
			"t": "ERROR",
			"d": text
		}
		
packets = AllPackets()
