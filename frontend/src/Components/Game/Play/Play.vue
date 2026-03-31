<script lang="ts" setup>
import { computed, onActivated, onMounted, onUnmounted, ref, watch, type Ref } from 'vue';
import { DEFAULT_FILLER, type modifiers } from '@/types';
import Player from './Player.vue';
import Grid from './Grid/Grid.vue';
import Chat from './Chat/Chat.vue';
import useWebsocketStore from '@/Components/Stores/websocket';
import router from '@/router';
import useUserStore from '@/Components/Stores/user';
import type { GameUser } from '@/game_types';

// Stores
const websocketStore = useWebsocketStore();
const userStore = useUserStore();



const letterFocused = ref<number>(-1);

watch(() => websocketStore.game.letters, () => {
	letters.value = websocketStore.game.letters;
})

watch(() => websocketStore.game.grid, () => {
	grid.value = websocketStore.game.grid;
})

const letters = ref<string[]>([]);
const grid = ref<(string | modifiers)[]>([]);
const placed = ref<Map<number, [number, string]>>(new Map());
const orderPlacement = ref<number[]>([]);

onMounted(() => {
	grid.value = websocketStore.game.grid;
})




// Game Active
function submitTurn() {
	const toSend: [number[], string][] = [];

	placed.value.forEach((value, key) => {
		var letter = value[1] as string;
		var cellID = key;
		const x = cellID % 15;
		const y = Math.floor(cellID / 15);
		toSend.push([[x, y], letter])
	})

	websocketStore.send("GAME_TURN", {letters: toSend});
}

const activePlayer = computed(() => {
	console.log(activePlayer)
	if (websocketStore.game === null) {
		return -1
	}
	return websocketStore.game.gameTurn
})

const chatOpen = ref(false);


onMounted(() => {
	if (websocketStore.game === null) {
		router.replace({ name: "dashboard" })
		return
	}
	console.log(websocketStore.game.players)
	console.log(websocketStore.game.gameTurn)
})


function undo() {
	const last = orderPlacement.value.pop();
	console.log(last)
	if (last !== undefined) {
		placed.value.delete(last);
	}
}

function handleKeyboardPress(event: KeyboardEvent) {
	switch (event.key) {
		case "1":
		case "2":
		case "3":
		case "4":
		case "5":
		case "6":
		case "7":
			letterFocused.value = parseInt(event.key) - 1
			break;
		case "Backspace":
			undo();
			break;
	}
}

function handleTileClick(index: number) {
	if (placedIndexes.value.includes(index)) {
		return
	}
	letterFocused.value = index;
}
onMounted(() => {
	window.addEventListener("keyup", handleKeyboardPress)
})

onUnmounted(() => {
	window.removeEventListener("keyup", handleKeyboardPress)
});

const placedIndexes = computed(() => {
	const values = placed.value.values();
	return Array.from(values).map((value) => value[0]);
});

const players = computed(() => {
	const tempPlayers = Array.from(websocketStore.game?.players.values() ?? [])
	const ret: GameUser[][] = []
	if (tempPlayers !== undefined) {
		var count = 0;
		var temp = [];

		while (count != 4) {
			var player = tempPlayers[count]
			if (player !== undefined) {
				temp.push(player)
				count++;
			} else {
				ret.push(temp)
				break
			}
			if (count % 2 == 0 && count != 0) {
				ret.push(temp)
				temp = []
			}
		}
	}
	return ret
})
</script>

<!--<div v-if="players.length > 0" class="player-card"></div>
		this eventually will show  players in  game, but for now its a placeholder.  -->

<template>

	<!-- This is the page where you play the game, this will need to be live with the websocket we plan to use.  -->
	<div class="wrapper">
		<div class="wrapper__flex">
			<div class="player__column left">
				<Player :active-player="activePlayer" :user-game-data="player"
					v-for="player in (players.length > 0 ? players[0] : [])" />
			</div>

			{{ activePlayer }}
			<div class="center__wrapper">
				<Grid :filler="DEFAULT_FILLER" :active-player="activePlayer" :grid="grid"
					:order-placement="orderPlacement" :letter-focused="letterFocused" :letters="letters"
					@cell-clicked="letterFocused = -1" :placed="placed" />

				<div class="actions">
					<button class="action" @click="undo()"><i class="pi pi-undo"></i></button>
					<button class="action" :disabled="activePlayer !== userStore.userData?.userID"
						:class="{ 'action--disabled': activePlayer !== userStore.userData?.userID }"><i
							class="pi pi-arrow-right-arrow-left"></i></button>
					<div class="rack">
						<div class="rack__tile" v-for="(letter, ind) in letters" @click="handleTileClick(ind)"
							:class="{ 'tile--selected': letterFocused == ind, 'tile--used': placedIndexes.includes(ind) }">
							{{ letter.toUpperCase() }}
						</div>
					</div>
					<button @click="submitTurn" class="action" :disabled="activePlayer !== userStore.userData?.userID"
						:class="{ 'action--disabled': activePlayer !== userStore.userData?.userID }" ><i
							class="pi pi-check "></i></button>
					<button class="action" :disabled="activePlayer !== userStore.userData?.userID"
						:class="{ 'action--disabled': activePlayer !== userStore.userData?.userID }"><i
							class="pi pi-flag"></i></button>
				</div>
			</div>
			<div class="player__column right">
				<Player :active-player="activePlayer" :user-game-data="player"
					v-for="player in (players.length > 1 ? players[1] : [])" />
			</div>
			<div class="chat__panel" :class="{ open: chatOpen }">
				<button class="panel__close" @click="chatOpen = false">✕</button>
				<Chat />
			</div>
		</div>
	</div>

</template>


<style lang="css" scoped>
.wrapper {
	display: flex;
	justify-content: center;
	height: 100%;
	width: 100%;
}

.wrapper__flex {
	margin-top: 1rem;
	height: fit-content;
	display: flex;
	gap: 2rem;
	align-items: center;
}

.player__column {
	display: flex;
	flex-direction: column;
	gap: 2rem;
	width: fit-content;
}


.center__wrapper {
	display: flex;
	/* background-color: blue; */
	flex: 1;
	flex-direction: column;
	align-items: center;
	gap: 1.5rem;
}


.rack {
	display: flex;
	gap: 10px;
	padding: 15px;
	border-radius: 12px;
	background: linear-gradient(145deg, #b88a44, #d9a955);
	box-shadow: inset 0 4px 6px rgba(0, 0, 0, 0.4);
}

.rack__tile {
	width: 50px;
	height: 50px;
	background: #f1bc4c;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 22px;
	font-weight: bold;
	border-radius: 8px;
	cursor: pointer;
	box-shadow: 0 3px 6px rgba(0, 0, 0, 0.4);
	transition: 0.2s;
}

.rack__tile:hover {
	transform: translateY(-3px);
}

.tile--selected {
	transform: translateY(-3px);
}

.tile--used {
	opacity: 0.5;
}

.actions {
	display: flex;
	gap: 1rem;
	align-items: center;
	margin: auto;
}

.action {
	padding: 12px 20px;
	font-size: large;
	height: fit-content;
	border: none;
	border-radius: 8px;
	background: #f1bc4c;

	cursor: pointer;
	box-shadow: 0 3px 6px rgba(0, 0, 0, 0.4);
	transition: 0.5s ease-in all;

}

.action--disabled {
	opacity: 0.5;
	cursor: not-allowed;
}

.chat__panel {
	position: fixed;
	right: -320px;
	top: 0;
	width: 320px;
	height: 100%;
	background: #2c8595;
	transition: 0.3s;
	padding: 1rem;
	color: white;
	z-index: 100;
	box-shadow: -5px 0 15px rgba(0, 0, 0, 0.4);
}

.chat__panel.open {
	right: 0;
}

.panel__close {
	background: none;
	border: none;
	color: white;
	font-size: 20px;
	cursor: pointer;
}
</style>