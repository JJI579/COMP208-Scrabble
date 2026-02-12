import api from "@/api";
import type { InitType, PacketType, SelfReturn, UserReturn, WebsocketPacket } from "@/types";
import { defineStore } from "pinia";
import { ref } from "vue";

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



class Game implements GAME {
	constructor(public id: number, public type: GAME_TYPE, public players: UserReturn[], public groups: UserReturn[][], public hasStarted: boolean, public timeLimit: number, public dictionaryAllowed: boolean) {
		this.id = id;
		this.type = type;
		this.players = players;
		this.groups = groups;
		this.hasStarted = hasStarted;
		this.timeLimit = timeLimit;
		this.dictionaryAllowed = dictionaryAllowed;
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


const useWebsocketStore = defineStore("websocket", () => {
	const debug = true;
	const websocketURL = debug ? 'ws://localhost:8000/ws' : 'wss://pibble.pics/api/ws';
	const websocket = new WebSocket(websocketURL);
	const game = ref<Game | null>(null);

	websocket.onopen = () => {
		console.log('Websocket connection opened');
		const token = localStorage.getItem('token')
		websocket.send(generatePacket('IDENTIFY', { token: token }))
	};


	websocket.onmessage = (message) => {
		const data: WebsocketPacket = JSON.parse(message.data)
		console.log(data)
		switch (data.t) {

		}
	};

	function disconnect() {
		websocket.send(generatePacket('DISCONNECT', {}))
		websocket.close()
	}

	function join(code: string) {
		const packet = generatePacket("PLAYER_JOIN", { code: code })
		if (websocket.readyState === websocket.OPEN) {
			websocket.send(packet)
		} else {
			websocket.addEventListener("open", () => {
				websocket.send(packet)
			}, {
				once: true
			})
		}

	}

	return { websocket, disconnect, join };
})

export default useWebsocketStore;
