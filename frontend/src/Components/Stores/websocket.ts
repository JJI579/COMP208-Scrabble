import api from "@/api";
import type { InitType, PacketType, SelfReturn, UserReturn, WebsocketPacket } from "@/types";
import { defineStore } from "pinia";
import { ref } from "vue";
import useUserStore from "./user";

function generatePacket(type: PacketType | InitType, data: any) {
	const packet: WebsocketPacket = {
		t: type.toUpperCase() as PacketType,
		d: data
	}

	return JSON.stringify(packet)
}


type GAME_TYPE = "NORMAL" | "GROUP" | "BOT"

type GAME = {
	id: number,
	type: GAME_TYPE,
	players: Map<Number, UserReturn>,
	leader: Number,
	groups: Number[][],
	hasStarted: boolean,
	timeLimit: number,
	dictionaryAllowed: boolean
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
	leader: number
}


class Game implements GAME {
	id: number;
	leader: number;
	type: GAME_TYPE;
	players: Map<Number, UserReturn>;
	groups: Number[][] = []
	hasStarted: boolean;
	timeLimit: number;
	dictionaryAllowed: boolean;

	constructor(gameCode: number, dictionary: initData) {
		this.id = gameCode;
		this.type = dictionary.game_type;
		this.players = new Map<Number, UserReturn>();
		this.leader = dictionary.leader;

		for (let i = 0; i < dictionary.players.length; i++) {
			var player = dictionary.players[i];
			if (player !== undefined) {
				this.players.set(Number(player.userID), player);
			}
		}

		if (dictionary.groups) {
			this.groups = dictionary.groups;
		}
		this.hasStarted = dictionary.has_started;
		console.log(dictionary.options.time_limit)
		// TODO: convert time_limit to actual time limit
		this.timeLimit = 999999999999999999;
		this.dictionaryAllowed = dictionary.options.dictionary;
	}

	isLeader(userID: number): boolean {

		return userID == this.leader;

	}
	getId(): number {
		return this.id;
	}

	getType(): GAME_TYPE {
		return this.type;
	}

	getPlayers(): UserReturn[] {
		return Array.from(this.players.values());
	}

	getPlayer(userID: number) {
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
		this.players = new Map();
		for (let i = 0; i < players.length; i++) {
			var player = players[i];
			if (player !== undefined) {
				this.players.set(player.userID, player);
			}
		}
	}

	addPlayer(player: UserReturn): void {
		if (this.hasStarted) {
			throw new Error("Game has already started");
		}
		const hasPlayer = this.players.get(player.userID);

		if (hasPlayer !== undefined) {
			throw new Error("Player already in game");
		} else {
			this.players.set(player.userID, player);
		}

	}

	removePlayer(player: UserReturn) {
		// returns if removed or not
		return this.players.delete(player.userID);
	}

	setGroups(groups: Number[][]): void {
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


export const useWebsocketStore = defineStore('websocket-2', () => {
	const websocketURL = 'ws://localhost:8000/ws1'
	const websocket = ref<WebSocket | null>(null);
	const game = ref<Game | null>(null);
	const userStore = useUserStore();

	const readyToSend = ref(false)




	function connect() {
		if (websocket.value) return
		websocket.value = new WebSocket(websocketURL)

		websocket.value.onopen = async () => {
			const token = localStorage.getItem("token")
			websocket.value?.send(generatePacket("IDENTIFY", { token }))
			while (true) {
				// keep sending ping every 30s
				websocket.value?.send(generatePacket("PING", {}))
				await new Promise(resolve => setTimeout(resolve, 30000))
			}
		}

		websocket.value.onclose = () => {
			console.log("it has closzed")
		}

		websocket.value.onmessage = (event) => {
			const data: WebsocketPacket = JSON.parse(event.data)
			console.log(data)
			switch (data.t) {
				case "IDENTIFY":
					readyToSend.value = true
				case "GAME_UPDATE":
					if (!game.value && data.d.game) {
						console.log("[GAME UPDATE] | Initialising first game")
						game.value = new Game(data.d.gameID, data.d.game)
					} else {
						if (game.value) {
							if (data.d.gameID != game.value.getId()) {
								// new game, sync to new content
								console.log("[GAME UPDATE] | New game, reset the dictionary")
								game.value = new Game(data.d.gameID, data.d.game)
							} else {
								// update game content
								console.log("[GAME UPDATE] | Update current game data")
							}
						}
					}
					break
				case "GAME_INVALID":
					// TODO: implement into alert
					break
				case "PLAYER_JOIN":
					if (!game.value) {
						// we should have a game by now.
						console.log("We should have a game by now | PLAYER JOIN")
						// maybe push request for game update?
					} else {
						console.log("Added player")
						try {
							game.value.addPlayer(data.d.user)
						} catch (error) {
							console.log(`ADD PLAYER EXCEPTION: ${error}`)
						}
					}
					break
				case "PLAYER_LEAVE":
					break

				case "PLAYER_DISCONNECT":
					break
			}
		}
	}

	function join(code: string) {
		send(generatePacket("PLAYER_JOIN", { code }))
	}

	function leave() {
		if (game.value) {
			console.log(game.value)
			send(generatePacket("PLAYER_LEAVE", { code: game.value.getId() }))
			console.log("sent")
		}
	}

	function isLeader() {
		if (game.value && userStore.userData) {
			return game.value.isLeader(Number(userStore.userData.userID));
		} else {
			return false;

		}
	}

	function send(packet: string) {
		if (websocket.value?.readyState === WebSocket.OPEN) {
			// TODO: make this wait until authenticated
			websocket.value.send(packet)
		} else {
			console.log("waiting till websocket is open..")
			websocket.value?.addEventListener(
				"open",
				() => websocket.value?.send(packet),
				{ once: true }
			)
		}
	}



	return { websocket, game, connect, join, leave, isLeader }


});

// export const xuseWebsocketStore = defineStore("websocket", () => {
// 	const userStore = useUserStore();
// 	const websocketURL = 'ws://localhost:8000/ws'
// 	const sessionID = ref<string | null>(null)
// 	const websocket = ref<WebSocket | null>(null)
// 	const game = ref<Game | null>(null)
// 	let reconnectTimeout: number | null = null

// 	function connect() {
// 		if (websocket.value) return

// 		websocket.value = new WebSocket(websocketURL)

// 		websocket.value.onopen = () => {
// 			console.log("WebSocket opened")
// 			if (sessionID.value !== null) {
// 				websocket.value?.send(generatePacket("RESUME", { sessionID: sessionID.value, userID: userStore.userData?.userID }));
// 			} else {
// 				// identify for first time
// 				const token = localStorage.getItem("token")
// 				websocket.value?.send(generatePacket("IDENTIFY", { token }))
// 			}

// 		}

// 		websocket.value.onmessage = (event) => {
// 			const data: WebsocketPacket = JSON.parse(event.data)
// 			console.log(data)
// 			console.log(data.t == "GAME_UPDATE")
// 			switch (data.t) {
// 				// case "NOT_FOUND":
// 				// 	const token = localStorage.getItem("token")
// 				// 	websocket.value?.send(generatePacket("IDENTIFY", { token }))
// 				// 	break
// 				case "GAME_UPDATE":
// 					console.log("game update")
// 					break
// 				case "PLAYER_JOIN":
// 					if (!game.value && data.d.game) {
// 						game.value = new Game(data.d.gameID, data.d.game)
// 					} else {
// 						if (game.value?.players.includes(data.d.user)) return
// 						console.log("appending new player")
// 						console.log(data.d.user)

// 						game.value?.getPlayer(data.d.user.userID)
// 					}
// 					break
// 				case "PLAYER_LEAVE":
// 					game.value?.removePlayer(data.d.user)
// 					break
// 				case "IDENTIFY":
// 					sessionID.value = data.d.ID
// 					break
// 			}
// 		}

// 		websocket.value.onclose = (event) => {
// 			console.log("WebSocket closed, retrying in 1s", event)
// 			websocket.value = null
// 			if (reconnectTimeout) clearTimeout(reconnectTimeout)
// 			reconnectTimeout = window.setTimeout(connect, 1000)
// 		}
// 	}

// 	function disconnect() {
// 		if (websocket.value?.readyState === WebSocket.OPEN) {
// 			websocket.value.send(generatePacket("DISCONNECT", {}))
// 			websocket.value.close()
// 		}
// 	}

// 	function send(packet: string) {
// 		if (websocket.value?.readyState === WebSocket.OPEN) {
// 			websocket.value.send(packet)
// 		} else {
// 			websocket.value?.addEventListener(
// 				"open",
// 				() => websocket.value?.send(packet),
// 				{ once: true }
// 			)
// 		}
// 	}

// 	function join(code: string) {
// 		send(generatePacket("PLAYER_JOIN", { code }))
// 	}

// 	return { websocket, game, connect, disconnect, join, sessionID }
// })

export default useWebsocketStore;
