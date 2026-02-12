const debug = true;

type LoginReturn = {
	type: string
	id: string
	token: string
	refresh_token: string
	expires_at: string
}

type UserReturn = {
	userID: string
	userName: string
	userCreatedAt: string
}

type SelfReturn = UserReturn & {
	friends: UserReturn[];
}

type InitType = "IDENTIFY" | "DISCONNECT"

type PacketType =
	| "GAME_START"
	| "RESUME"
	| "GAME_CANCEL"
	| "PLAYER_JOIN"
	| "PLAYER_LEAVE"
	| "GROUP_UPDATE"
	| "GROUP_JOIN"
	| "GROUP_LEAVE"
	| "GAME_PLACE"
	| "GAME_REPLACE"
	| "GAME_UPDATE"
	| "NOT_FOUND"
	| "GAME_TURN";

type WebsocketPacket = {
	t: PacketType | InitType
	d: any
}


export type { LoginReturn, UserReturn, SelfReturn, WebsocketPacket, PacketType, InitType };
export default debug;