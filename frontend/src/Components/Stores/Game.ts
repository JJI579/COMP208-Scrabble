import type { GameUser } from "@/game_types"
import type { UserReturn } from "@/types"
import { ref, type Ref } from "vue"

type GAME_TYPE = "NORMAL" | "GROUP" | "BOT"



function toGameUser(user: UserReturn): GameUser {
	return { ...user, placed: [], points: 0 }
}

type GAME = {
	id: Ref<number>,
	type: Ref<GAME_TYPE>,
	players: Ref<Map<Number, GameUser>>,
	leader: Ref<number>,
	groups: Ref<Number[][]>,
	hasStarted: Ref<boolean>,
	timeLimit: Ref<number>,
	dictionaryAllowed: Ref<boolean>,
	gameTurn: Ref<number>
}


type gameOptions = {
	game_type: GAME_TYPE,
	group_size: number,
	time_limit: string,
	dictionary: boolean
}
type initData = {
	game_type: GAME_TYPE,
	players: UserReturn[],
	has_started: boolean,
	options: gameOptions,
	groups?: Number[][]
	leader: number,
	turn?: number
}


class Game implements GAME {
	gameTurn = ref<number>(-1);
	id = ref<number>(0);
	leader = ref<number>(0);
	type = ref<GAME_TYPE>("NORMAL");
	players = ref<Map<Number, GameUser>>(new Map());
	groups = ref<Number[][]>([]);
	maxGroupSize = ref<number>(2);
	hasStarted = ref<boolean>(false);
	timeLimit = ref<number>(0);
	dictionaryAllowed = ref<boolean>(false);



	constructor(gameCode: number, dictionary: initData) {
		console.log(dictionary)
		if (dictionary.turn !== undefined && dictionary.turn != -1) {
			console.log("here")
			console.log(dictionary.turn)
			this.gameTurn.value = dictionary.turn
		}
		this.id.value = gameCode;
		this.type.value = dictionary.game_type;
		this.players.value = new Map<Number, GameUser>();
		this.leader.value = dictionary.leader;
		for (let i = 0; i < dictionary.players.length; i++) {
			var player = dictionary.players[i];
			if (player !== undefined) {
				this.players.value.set(Number(player.userID), toGameUser(player));
			}
		}
		if (dictionary.groups) {
			this.groups.value = dictionary.groups;
		}
		this.hasStarted.value = dictionary.has_started;
		// TODO: convert time_limit to actual time limit
		this.timeLimit.value = 999999999999999999;
		this.dictionaryAllowed.value = dictionary.options.dictionary;
	}



	updateContent(dictionary: initData) {
		if (dictionary.turn !== undefined) {
			this.gameTurn.value = dictionary.turn
		}
		this.leader.value = dictionary.leader
		this.hasStarted.value = dictionary.has_started

		console.log("new game turn" + this.gameTurn)

	}
	isLeader(userID: number): boolean {
		return userID == this.leader.value;
	}
	getId(): number {
		return this.id.value;
	}

	getTurn(): number {
		return this.gameTurn.value;
	}

	getType(): GAME_TYPE {
		return this.type.value;
	}

	getPlayers(): GameUser[] {
		return Array.from(this.players.value.values());
	}

	getPlayer(userID: number): GameUser | false {
		const user = this.players.value.get(userID)
		if (user !== undefined) {
			return user
		}
		return false;
	}

	getGroups(): Number[][] {
		return this.groups.value;
	}

	getHasStarted(): boolean {
		return this.hasStarted.value;
	}

	getTimeLimit(): number {
		return this.timeLimit.value;
	}

	getDictionaryAllowed(): boolean {
		return this.dictionaryAllowed.value;
	}

	setId(id: number): void {
		this.id.value = id;
	}

	setType(type: GAME_TYPE): void {
		this.type.value = type;
	}

	setPlayers(players: UserReturn[]): void {
		var x = new Map();
		for (let i = 0; i < players.length; i++) {
			var player = players[i];
			if (player !== undefined) {
				x.set(player.userID, toGameUser(player));
			}
		}
		// set all at once rather than reactive response per player add.
		this.players.value = x;
	}

	addPlayer(player: UserReturn): void {
		if (this.hasStarted) {
			throw new Error("Game has already started");
		}
		const hasPlayer = this.players.value.get(player.userID);

		if (hasPlayer !== undefined) {
			throw new Error("Player already in game");
		} else {
			this.players.value.set(player.userID, toGameUser(player));
		}

	}

	removePlayer(player: UserReturn) {
		// returns if removed or not
		return this.players.value.delete(player.userID);
	}

	setGroups(groups: Number[][]): void {
		this.groups.value = groups;
	}

	setHasStarted(hasStarted: boolean): void {
		this.hasStarted.value = hasStarted;
	}

	setTimeLimit(timeLimit: number): void {
		this.timeLimit.value = timeLimit;
	}

	setDictionaryAllowed(dictionaryAllowed: boolean): void {
		this.dictionaryAllowed.value = dictionaryAllowed;
	}

}


export default Game;
