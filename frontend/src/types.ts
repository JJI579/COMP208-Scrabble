const debug = true;

type LoginReturn = {
	type: string
	id: string
	token: string
	refresh_token: string
	expires_at: string
}

type UserReturn = {
	userID: number
	userName: string
	userCreatedAt: string
	wins: number
	loses: number
	totalScore: number
	bestScore: number
	rank?: number
}

type Item = {
	itemID: number,
	name: string,
	description: string,
	xpRequired: number,
	unlocked: boolean
}

type UnlockedItemType = Item & {
	equipped: boolean
}

type SelfReturn = UserReturn & {
	friends: UserReturn[];
	// itemID, selfconfig
	config: Record<number, boolean>
}

type InitType = "IDENTIFY" | "DISCONNECT"

type PacketType =
	| "ERROR"
	| "GAME_INVALID"
	| "CONFIRM_LEAVE"
	| "GAME_START"
	| "RESUME"
	| "PING"
	| "GAME_CANCEL"
	| "PLAYER_JOIN"
	| "PLAYER_LEAVE"
	| "PLAYER_DISCONNECT"
	| "GROUP_UPDATE"
	| "GROUP_JOIN"
	| "GROUP_LEAVE"
	| "GAME_PLACE"
	| "GAME_REPLACE"
	| "GAME_UPDATE"
	| "GAME_UPDATE_ONGOING"
	| "NOT_FOUND"
	| "GAME_TURN"
	| "CHAT_MESSAGE"
	| "GAME_END"
	| "DRAFT_PLACED"
	| "TURN_CONFIRMATION"
	| "TURN_DECLINE"
	| "TURN_REQUEST"
	| "SKIP_TURN"
	| "SWITCH_TURN"

type WebsocketPacket = {
	t: PacketType | InitType
	d: any
}

type modifiers =
	"DOUBLE_WORD" |
	"TRIPLE_WORD" |
	"DOUBLE_LETTER" |
	"TRIPLE_LETTER" |
	"CENTER"

const pointsMap: Record<string, number> = {
	"A": 1,
	"B": 3,
	"C": 3,
	"D": 2,
	"E": 1,
	"F": 4,
	"G": 2,
	"H": 4,
	"I": 1,
	"J": 8,
	"K": 5,
	"L": 1,
	"M": 3,
	"N": 1,
	"O": 1,
	"P": 3,
	"Q": 10,
	"R": 1,
	"S": 1,
	"T": 1,
	"U": 1,
	"V": 4,
	"W": 4,
	"X": 8,
	"Y": 4,
	"Z": 10
}

const DEFAULT_FILLER = "|";

type MessageType = {
	id: number,
	text: string
	created_at: Date,
	partner: boolean,
	author: {
		id: number,
		name: string
	}
}

// const BASE_HOST = 'w11-desktop.tail57640.ts.net';
const BASE_HOST = 'localhost:8000';
var SECURE_URL = false;
var BASE_URL = `http://${BASE_HOST}`
if (BASE_HOST.includes('w11-desktop')) {
	SECURE_URL = true;
	var BASE_URL = `${SECURE_URL ? 'https' : 'http'}://${BASE_HOST}/api`
}


export type { LoginReturn, UserReturn, SelfReturn, WebsocketPacket, PacketType, InitType, modifiers, Item, UnlockedItemType, MessageType };
export { debug, pointsMap, DEFAULT_FILLER, BASE_URL, BASE_HOST, SECURE_URL };
