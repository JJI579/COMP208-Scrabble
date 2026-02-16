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
}

export type { LoginReturn, UserReturn, SelfReturn, Item, UnlockedItemType };
export default debug;