
from typing import Literal, TypedDict
from modules.schema import PacketType


class BasePacket(TypedDict):
	t: PacketType
	d: dict

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
	
	def start_game(self, gameInfo):
		gameInfo = False
		data = {
			"game": gameInfo
		}
		return self.create_packet("GAME_START", data)

	def cancel_game(self, gameID: int):
		data = {
			"gameID": gameID
		}
		return self.create_packet("GAME_CANCEL", data)
		

	def join_game(self, gameID: int, user: dict):
		data = {
			"gameID": gameID,
			"user": user
		}
		# returns player_join
		return self.create_packet("PLAYER_JOIN", data)

	def leave_game(self, gameID: int, user: dict):
		# returns player_leave
		data = {
			"gameID": gameID,
			"user": user
		}
		return self.create_packet("PLAYER_LEAVE", data)

	def join_group(self, gameID: int, user: dict, groupID: int, groups: list[list[int]]):
		# returns group_join
		data = {
			"gameID": gameID,
			"user": user,
			# this is to show what group was affected
			"focusedID": groupID,
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

	def update_game(self):
		pass

	def replace_shelf_game(self):
		# these are the letters that the user has!
		# need to reconsider whether this will be a packet or not or just turn_update
		pass

	def place_word(self):
		# game_place
		pass

	

# These packets are sent during the game (game has started)
class DuringPackets:

	def __init__(self) -> None:
		pass



class AllPackets:
	def __init__(self) -> None:
		self.start = StartPackets()
		self.during = DuringPackets()

packets = AllPackets()
