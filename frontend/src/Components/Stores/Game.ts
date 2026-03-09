import type { GameUser } from "@/game_types"
import type { UserReturn } from "@/types"
import { ref, type Ref } from "vue"

type GAME_TYPE = "NORMAL" | "GROUP" | "BOT"



function toGameUser(user: UserReturn): GameUser {
	return { ...user, placed: [], points: 0 }
}

type GAME = {
	id: number,
	type: GAME_TYPE,
	players: Map<Number, GameUser>,
	leader: number,
	groups: number[][],
	hasStarted: boolean,
	timeLimit: number,
	dictionaryAllowed: boolean,
	gameTurn: number
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
	groups?: number[][]
	leader: number,
	turn?: number
	letters?: []
}

type ongoingData = {
	letters: [],
	players: [],
	turn: number
}

class Game implements GAME {
	gameTurn: number = -1;
	id: number = 0;
	leader: number = 0;
	type: GAME_TYPE = "NORMAL";
	players: Map<number, GameUser> = new Map();
	groups: number[][] = [];
	maxGroupSize: number = 2;
	hasStarted: boolean = false;
	timeLimit: number = 0;
	dictionaryAllowed: boolean = false;
	letters: string[] = [];

	constructor(gameCode: number, dictionary: any | initData) {
		if (gameCode == 0) {
			return
		}
		console.log(dictionary)
		if (dictionary.turn !== undefined && dictionary.turn != -1) {
			console.log("here")
			console.log(dictionary.turn)
			this.gameTurn = dictionary.turn
		}
		this.id = gameCode;
		this.type = dictionary.game_type;
		this.players = new Map<number, GameUser>();
		this.leader = dictionary.leader;
		for (let i = 0; i < dictionary.players.length; i++) {
			var player = dictionary.players[i];
			if (player !== undefined) {
				this.players.set(Number(player.userID), toGameUser(player));
			}
		}
		if (dictionary.groups) {
			this.groups = dictionary.groups;
		}
		this.hasStarted = dictionary.has_started;
		// TODO: convert time_limit to actual time limit
		this.timeLimit = 999999999999999999;
		this.dictionaryAllowed = dictionary.options.dictionary;
	}

	updateOngoing(allData: ongoingData) {
		this.letters = allData.letters;
		console.log("myletters");
		console.log(this.letters);

	}

	updateContent(allData: any) {

		var dictionary: initData = allData.game
		var gameID = allData.gameID

		if (dictionary.turn !== undefined) {
			this.gameTurn = dictionary.turn
		}
		this.id = gameID;
		this.type = dictionary.game_type;
		this.leader = dictionary.leader;
		this.letters = [];
		this.players.clear();
		for (let i = 0; i < dictionary.players.length; i++) {
			var player = dictionary.players[i];
			if (player !== undefined) {
				this.players.set(Number(player.userID), toGameUser(player));
			}
		}
		if (dictionary.groups) {
			this.groups = dictionary.groups;
		}
		if (dictionary.letters) {
			this.letters = dictionary.letters
		} else {
			this.letters = []
		}
		this.hasStarted = dictionary.has_started;
		this.dictionaryAllowed = dictionary.options.dictionary;
	}
	isLeader(userID: number): boolean {
		return userID == this.leader;
	}
	getId(): number {
		return this.id;
	}

	getTurn(): number {
		return this.gameTurn;
	}

	getType(): GAME_TYPE {
		return this.type;
	}

	getPlayers(): GameUser[] {
		return Array.from(this.players.values());
	}

	getPlayer(userID: number): GameUser | false {
		const user = this.players.get(userID)
		if (user !== undefined) {
			return user
		}
		return false;
	}

	getGroups(): Number[][] {
		return this.groups;
	}

	getHasStarted(): boolean {
		return this.hasStarted;
	}

	getTimeLimit(): number {
		return this.timeLimit;
	}

	getDictionaryAllowed(): boolean {
		return this.dictionaryAllowed;
	}

	setId(id: number): void {
		this.id = id;
	}

	setType(type: GAME_TYPE): void {
		this.type = type;
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
		this.players = x;
	}

	addPlayer(player: UserReturn): void {
		if (this.hasStarted) {
			throw new Error("Game has already started");
		}
		const hasPlayer = this.players.get(player.userID);

		if (hasPlayer !== undefined) {
			throw new Error("Player already in game");
		} else {
			this.players.set(player.userID, toGameUser(player));
		}

	}

	removePlayer(player: UserReturn) {
		// returns if removed or not
		return this.players.delete(player.userID);
	}

	setGroups(groups: number[][]): void {
		this.groups = groups;
	}

	setHasStarted(hasStarted: boolean): void {
		this.hasStarted = hasStarted;
	}

	setTimeLimit(timeLimit: number): void {
		this.timeLimit = timeLimit;
	}

	setDictionaryAllowed(dictionaryAllowed: boolean): void {
		this.dictionaryAllowed = dictionaryAllowed;
	}

}


export default Game;
