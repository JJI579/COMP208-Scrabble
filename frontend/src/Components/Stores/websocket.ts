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
	players: UserReturn[],
	groups: UserReturn[][],
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
	groups?: UserReturn[][]
}


class Game implements GAME {
	id: number;
	type: GAME_TYPE;
	players: UserReturn[]
	groups: UserReturn[][] = []
	hasStarted: boolean;
	timeLimit: number;
	dictionaryAllowed: boolean;

	constructor(gameCode: number, dictionary: initData) {
		this.id = gameCode;
		this.type = dictionary.game_type;
		this.players = dictionary.players;
		if (dictionary.groups) {
			this.groups = dictionary.groups;
		}
		this.hasStarted = dictionary.has_started;
		console.log(dictionary.options.time_limit)
		// TODO: convert time_limit to actual time limit
		this.timeLimit = 999999999999999999;
		this.dictionaryAllowed = dictionary.options.dictionary;
	}

	getId(): number {
		return this.id;
	}

	getType(): GAME_TYPE {
		return this.type;
	}

	getPlayers(): UserReturn[] {
		return this.players;
	}

	getPlayer(userID: number) {
		if (this.players !== undefined) {
			for (let i = 0; i < this.players.length; i++) {
				console.log(this.players[i])
				if (this.players[i]['userID'] == userID) {
					return this.players[i];
				}
			}
		}


	}

	getGroups(): UserReturn[][] {
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
		this.players = players;
	}

	addPlayer(player: UserReturn): void {
		if (this.hasStarted) {
			throw new Error("Game has already started");
		}
		this.players.push(player);
	}

	removePlayer(player: UserReturn) {
		this.players = this.players.filter(p => p.userID !== player.userID);
		this.groups.map(element => {
			if (element.includes(player)) {
				return element.filter(p => p.userID !== player.userID);
			}
			return element
		});
	}

	setGroups(groups: UserReturn[][]): void {
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

export const useWebsocketStore = defineStore("websocket", () => {
	const userStore = useUserStore();
	const websocketURL = 'ws://localhost:8000/ws'
	const sessionID = ref<string | null>(null)
	const websocket = ref<WebSocket | null>(null)
	const game = ref<Game | null>(null)
	let reconnectTimeout: number | null = null

	function connect() {
		if (websocket.value) return

		websocket.value = new WebSocket(websocketURL)

		websocket.value.onopen = () => {
			console.log("WebSocket opened")
			if (sessionID.value !== null) {
				websocket.value?.send(generatePacket("RESUME", { sessionID: sessionID.value, userID: userStore.userData?.userID }));
			} else {
				// identify for first time
				const token = localStorage.getItem("token")
				websocket.value?.send(generatePacket("IDENTIFY", { token }))
			}

		}

		websocket.value.onmessage = (event) => {
			const data: WebsocketPacket = JSON.parse(event.data)
			console.log(data)

			switch (data.t) {
				// case "NOT_FOUND":
				// 	const token = localStorage.getItem("token")
				// 	websocket.value?.send(generatePacket("IDENTIFY", { token }))
				// 	break
				case "PLAYER_JOIN":
					if (!game.value && data.d.game) {
						game.value = new Game(data.d.gameID, data.d.game)
					} else {
						if (game.value?.players.includes(data.d.user)) return
						console.log("appending new player")
						console.log(data.d.user)

						game.value?.getPlayer(data.d.user.userID)
					}
					break
				case "PLAYER_LEAVE":
					game.value?.removePlayer(data.d.user)
					break
				case "IDENTIFY":
					sessionID.value = data.d.ID
					break
			}
		}

		websocket.value.onclose = (event) => {
			console.log("WebSocket closed, retrying in 1s", event)
			websocket.value = null
			if (reconnectTimeout) clearTimeout(reconnectTimeout)
			reconnectTimeout = window.setTimeout(connect, 1000)
		}
	}

	function disconnect() {
		if (websocket.value?.readyState === WebSocket.OPEN) {
			websocket.value.send(generatePacket("DISCONNECT", {}))
			websocket.value.close()
		}
	}

	function send(packet: string) {
		if (websocket.value?.readyState === WebSocket.OPEN) {
			websocket.value.send(packet)
		} else {
			websocket.value?.addEventListener(
				"open",
				() => websocket.value?.send(packet),
				{ once: true }
			)
		}
	}

	function join(code: string) {
		send(generatePacket("PLAYER_JOIN", { code }))
	}

	return { websocket, game, connect, disconnect, join, sessionID }
})

export default useWebsocketStore;
