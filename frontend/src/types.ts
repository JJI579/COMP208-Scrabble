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

type modifiers =
	"DOUBLE_WORD" |
	"TRIPLE_WORD" |
	"DOUBLE_LETTER" |
	"TRIPLE_LETTER"


export type { LoginReturn, UserReturn, SelfReturn, modifiers };
export default debug;