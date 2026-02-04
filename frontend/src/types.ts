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

export type { LoginReturn, UserReturn, SelfReturn };
export default debug;