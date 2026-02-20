<script lang="ts" setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import type { modifiers } from '@/types';
import Player from './Player.vue';
import Grid from './Grid/Grid.vue';
import Chat from './Chat/Chat.vue';

const DEFAULT_FILLER = "";

const letterFocused = ref<number>(-1);
const letters = ref<string[]>(['a', 'b', 'c', 'd', 'e']);
const placed = ref<Map<number, [number, string]>>(new Map());
const orderPlacement = ref<number[]>([]);
const grid = ref<(string | modifiers)[]>([]);

onMounted(() => {
	var initGrid: (string | modifiers)[] = [];

	const doubleWord = [16, 32, 48, 64, 112, 160, 176, 192, 208, 28, 42, 56, 70, 154, 168, 182, 196];
	const doubleLetter = [3, 11, 36, 38, 45, 52, 59, 92, 96, 98, 102, 108, 116, 122, 126, 128, 132, 165, 172, 179, 186, 188, 213, 221];
	const tripleWord = [0, 7, 14, 105, 119, 210, 217, 224];
	const tripleLetter = [20, 24, 76, 80, 84, 88, 136, 140, 144, 148, 200, 204];

	for (let i = 0; i < 225; i++) {
		if (i === 112) {
			initGrid.push("CENTER");
			continue;
		}
		if (doubleWord.includes(i)) {
			initGrid.push("DOUBLE_WORD");
			continue;
		} else if (doubleLetter.includes(i)) {
			initGrid.push("DOUBLE_LETTER");
		} else if (tripleWord.includes(i)) {
			initGrid.push("TRIPLE_WORD");
		} else if (tripleLetter.includes(i)) {
			initGrid.push("TRIPLE_LETTER");
		} else {
			initGrid.push(DEFAULT_FILLER)
		}
	}
	grid.value = initGrid;
})


const chatOpen = ref(false);
const activePlayer = ref(0);

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
</script>

<!--<div v-if="players.length > 0" class="player-card"></div>
		this eventually will show  players in  game, but for now its a placeholder.  -->

<template>

	<!-- This is the page where you play the game, this will need to be live with the websocket we plan to use.  -->
	<div class="wrapper">
		<div class="wrapper__flex">
			<div class="player__column left">
				<Player :active-player="activePlayer" :user-game-data="{ name: 'Jeremy', score: 10, timer: '05:53' }" />
				<Player :active-player="activePlayer" :user-game-data="{ name: 'Jeremy', score: 10, timer: '05:53' }" />
			</div>
			<div class="center__wrapper">
				<Grid :filler="DEFAULT_FILLER" :active-player="activePlayer" :grid="grid"
					:order-placement="orderPlacement" :letter-focused="letterFocused" :letters="letters"
					@cell-clicked="letterFocused = -1" :placed="placed" />

				<div class="actions">
					<button class="action" @click="undo()"><i class="pi pi-undo"></i></button>
					<button class="action" :disabled="activePlayer == 0"
						:class="{ 'action--disabled': activePlayer == 0 }"><i
							class="pi pi-arrow-right-arrow-left"></i></button>
					<div class="rack">
						<div class="rack__tile" v-for="(letter, ind) in letters" @click="handleTileClick(ind)"
							:class="{ 'tile--selected': letterFocused == ind, 'tile--used': placedIndexes.includes(ind) }">
							{{ letter.toUpperCase() }}
						</div>
					</div>
					<button class="action" :disabled="activePlayer == 0"
						:class="{ 'action--disabled': activePlayer == 0 }"><i class="pi pi-check "></i></button>
					<button class="action" :disabled="activePlayer == 0"
						:class="{ 'action--disabled': activePlayer == 0 }"><i class="pi pi-flag"></i></button>
				</div>
				<!-- <div class="actions">

					<button class="action" :disabled="activePlayer == 0"
						:class="{ 'action--disabled': activePlayer == 0 }">Swap</button>
					<button class="action" :disabled="activePlayer == 0"
						:class="{ 'action--disabled': activePlayer == 0 }">Submit</button>
					<button class="action" @click="chatOpen = !chatOpen">Chat</button>
					<button class="action" :disabled="activePlayer == 0"
						:class="{ 'action--disabled': activePlayer == 0 }">Forfeit</button>
				</div> -->

			</div>
			<div class="player__column right">
				<Player :active-player="activePlayer" :user-game-data="{ name: 'Jeremy', score: 10, timer: '05:53' }" />
				<Player :active-player="activePlayer" :user-game-data="{ name: 'Jeremy', score: 10, timer: '05:53' }" />
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