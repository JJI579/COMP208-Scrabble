import { BASE_HOST, SECURE_URL, type InitType, type MessageType, type PacketType, type WebsocketPacket } from "@/types";
import { defineStore } from "pinia";
import { reactive, ref } from "vue";
import router from "@/router";
import Game from "./Game";
import useAlertStore from "./alert";


export const useWebsocketStore = defineStore('websocket-2', () => {
	const websocketURL = `ws${SECURE_URL ? 's' : ''}://${BASE_HOST}/ws`
	console.log(websocketURL);
	const websocket = ref<WebSocket | null>(null);
	const game = reactive<Game>(new Game(0, {}));

	const messages = ref<MessageType[]>([]);

	const readyToSend = ref(false)

	function connect() {
		if (websocket.value) return
		websocket.value = new WebSocket(websocketURL)

		websocket.value.onopen = async () => {
			const token = localStorage.getItem("token")
			// if session_id send resume rather than identify
			const session_id = localStorage.getItem('session_id')

			if (session_id != null) {
				websocket.value?.send(generatePacket("RESUME", { session_id: session_id }))
			} else {
				websocket.value?.send(generatePacket("IDENTIFY", { token }))
			}
			while (true) {
				// keep sending ping every 30s
				try {
					websocket.value?.send(generatePacket("PING", {}))
					await new Promise(resolve => setTimeout(resolve, 5000))
				} catch (error) {
					return
				}
			}
		}

		websocket.value.onclose = () => {
			websocket.value = null;
			setTimeout(() => {
				connect();
				console.log("connecting...")
			}, 6000);
		}

		websocket.value.onmessage = (event) => {
			const data: WebsocketPacket = JSON.parse(event.data)
			console.log("RECEIVED: ", data)
			switch (data.t) {
				case "ERROR":
					useAlertStore().alert({
						text: data.d,
						type: "error"
					})
					break
				case "IDENTIFY":
					localStorage.setItem('session_id', data.d.ID)
					readyToSend.value = true
					break
				case "NOT_FOUND":
					localStorage.removeItem("session_id")
					const token = localStorage.getItem("token")
					websocket.value?.send(generatePacket("IDENTIFY", { token }))
					break
				case "GAME_UPDATE":
					if (!game && data.d.game) {
						console.log("[GAME UPDATE] | Initialising first game")
						// it will be there.
					} else {
						if (game) {
							if (data.d.gameID != game.id) {
								// new game, sync to new content
								console.log("[GAME UPDATE] | New game, reset the dictionary")
								game.updateContent(data.d)
							} else {
								// update game content
								console.log("[GAME UPDATE] | Update current game data")
								game.updateContent(data.d)
							}
						}
					}
					break
				case "GAME_INVALID":
					useAlertStore().alert({
						text: "Invalid game",
						type: "error"
					})
					break
				case "PLAYER_JOIN":
					if (!game) {
						// we should have a game by now.
						console.log("We should have a game by now | PLAYER JOIN")
						// maybe push request for game update?
					} else {
						console.log("Added player")
						try {
							game.addPlayer(data.d.user)
						} catch (error) {
							console.log(`ADD PLAYER EXCEPTION: ${error}`)
						}
					}
					break
				case "PLAYER_LEAVE":
					break
				case "PLAYER_DISCONNECT":
					break
				case "CHAT_MESSAGE":
					messages.value = [...messages.value, data.d as MessageType];
					break
				case "GROUP_JOIN":
					if (!game) {
						// we should have a game by now.
						console.log("We should have a game by now | GROUP JOIN")
						// maybe push request for game update?
					} else {
						game.setGroups(data.d.groups);
					}
					break;
				case "CONFIRM_LEAVE":
					game.reset();
					router.replace({ name: "dashboard" })
					break
				case "GAME_START":
					// move user to game page
					if (data.d.gameID != game?.id) {
						console.log("Game ID mismatch")
						return
					} else {
						router.push({ name: "play" })
					}
					break
				case "GAME_UPDATE_ONGOING":
					game.updateOngoing(data.d)
					break
				case "GAME_END":
					router.replace({
						'name': 'finish', state: {
							finalData: data.d
						}
					})
					break
				case "DRAFT_PLACED":
					game.updatePartnerPlaced(data.d.placed);
					break
				case "TURN_CONFIRMATION":
					useAlertStore().alert({
						text: `${data.d.name} has accepted your word suggestion.`,
						type: "success",
					})
					break;
				case "TURN_REQUEST":
					useAlertStore().alert({
						text: "Your partner is suggesting a word...",
						type: "game",
						persistent: true
					})
					game.isSuggesting = true;
					break;
				case "TURN_DECLINE":
					useAlertStore().alert({
						text: `${data.d.name} has declined your word suggestion.`,
						type: "error",
					})
					break;

			}
		}
	}

	function generatePacket(type: PacketType | InitType, data: any) {
		const packet: WebsocketPacket = {
			t: type.toUpperCase() as PacketType,
			d: data
		}
		return JSON.stringify(packet)
	}

	function send(type: PacketType, data: any) {

		_send(generatePacket(type, data))
	}

	let openListenerAttached = false
	const queue: string[] = []

	function _send(packet: string) {
		if (websocket.value?.readyState === WebSocket.OPEN) {
			websocket.value.send(packet)
			return
		}

		queue.push(packet)

		if (websocket.value && !openListenerAttached) {
			console.log("waiting for open websocket")
			openListenerAttached = true

			websocket.value.addEventListener(
				"open",
				() => {
					for (const p of queue) {
						websocket.value?.send(p)
					}
					queue.length = 0
					openListenerAttached = false
				}
			)
		}
	}

	return { websocket, game, connect, generatePacket, send, readyToSend, messages }
});

export default useWebsocketStore;
