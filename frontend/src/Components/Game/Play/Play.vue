<script lang="ts" setup>
import { computed, onActivated, onMounted, onUnmounted, ref, watch, type Ref } from 'vue';
import { DEFAULT_FILLER, type modifiers, pointsMap } from '@/types';
import Player from './Player.vue';
import Grid from './Grid/Grid.vue';
import Chat from './Chat/Chat.vue';
import useWebsocketStore from '@/Components/Stores/websocket';
import router from '@/router';
import useUserStore from '@/Components/Stores/user';
import type { GameUser } from '@/game_types';
import useAlertStore from '@/Components/Stores/alert';
import GroupPlayer from './GroupPlayer.vue';
import { skip } from 'node:test';

// Stores
const websocketStore = useWebsocketStore();
const userStore = useUserStore();

const letterFocused = ref<number>(-1);

watch(() => websocketStore.game.letters, () => {
	letters.value = websocketStore.game.letters;
	// if letters change that mean they have been handed a new deck.
	placed.value = new Map();
})

watch(() => websocketStore.game.grid, () => {
	grid.value = websocketStore.game.grid;
})



const letters = ref<string[]>([]);
const grid = ref<(string | modifiers)[]>([]);
const placed = ref<Map<number, [number, string, string?]>>(new Map());

// Groups implementation
const showPartners = ref(false);

watch(() => websocketStore.game.isSuggesting, () => {
	if (websocketStore.game.isSuggesting) {
		// show partners letters.
		showPartners.value = true;
	}
})

const orderPlacement = ref<number[]>([]);
const blankLetter = ref<string>(DEFAULT_FILLER);
onMounted(() => {
	grid.value = websocketStore.game.grid;
})



// Game Active
function submitTurn() {
	const toSend: [number[], string, string?][] = [];

	placed.value.forEach((value, key) => {
		var letter = value[1] as string;
		var cellID = key;
		const x = cellID % 15;
		const y = Math.floor(cellID / 15);
		toSend.push([[x, y], letter, value[2]])
	})

	if (websocketStore.game.type == "GROUP") {
		websocketStore.send("TURN_REQUEST", { letters: toSend });
	} else {
		websocketStore.send("GAME_TURN", { letters: toSend });
	}
}

const activePlayer = computed(() => {
	if (websocketStore.game === null) {
		return -1
	}
	return websocketStore.game.gameTurn
})

const chatOpen = ref(false);


function undo() {
	const last = orderPlacement.value.pop();
	if (last !== undefined) {
		placed.value.delete(last);
		websocketStore.send("DRAFT_PLACED", { placed: Object.fromEntries(placed.value) });
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
			handleTileClick(parseInt(event.key) - 1);
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
	if (letters.value[index] === " ") {
		selectBlank.value = index;
		return;
	}
	blankLetter.value = DEFAULT_FILLER;
	letterFocused.value = index;
}


const playerGroups = ref<GameUser[][]>([]);


onMounted(() => {
	const websocket = useWebsocketStore();
	setTimeout(() => {
		console.log("Checking Game Turn has been set")
		if (websocket.game.gameTurn == -1) {
			router.replace({ name: "dashboard" })
		}
		if (websocketStore.game.type == "GROUP") {
			var groups = [];
			for (const [key, value] of Object.entries(websocket.game.groups)) {
				var group: GameUser[] = [];
				for (const user of value) {
					var userObject = websocket.game.players.get(Number(user))
					if (userObject !== undefined) {
						group.push(userObject)
					}
				}
				groups.push(group)
			}
			playerGroups.value = groups.sort((a, b) => b.length - a.length);

			playerGroups.value = groups;
		}

	}, 2000);
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


onMounted(() => {
	if (websocketStore.game.type == "GROUP") {
		console.log("players")
		console.log(websocketStore.game.players);
	}
})


const alphabetArray = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"];
const selectBlank = ref(-1);

function selectedBlankTile(index: number) {
	var letter = alphabetArray[index];
	if (letter !== undefined) {
		// will never be.
		letter.toLowerCase();
		blankLetter.value = letter;
		letterFocused.value = selectBlank.value;
		selectBlank.value = -1;
	}
}



function handleCellClicked() {
	if (websocketStore.game.type == "GROUP") {
		websocketStore.send("DRAFT_PLACED", { placed: Object.fromEntries(placed.value) });
	}
	letterFocused.value = -1
}

const isLaptop = ref(false);

onMounted(() => {
	window.addEventListener("resize", () => {
		if (window.innerWidth <= 1024) {
			isLaptop.value = true;
		} else {
			isLaptop.value = false;
		}
	});
	if (window.innerWidth <= 1024) {
		isLaptop.value = true;
	} else {
		isLaptop.value = false;
	}
});

onUnmounted(() => {
	window.removeEventListener("resize", () => { });
});

function endGame() {
	websocketStore.send("GAME_END", {});
}

function skipTurn() {
	websocketStore.send("SKIP_TURN", {});

}
function switchTurn() {
	// TODO: look at how i done skip turn, you add the name of the packet to PacketType in types.ts, then send it like above, then go to backend ->  websocket.py
	// look at big switch case, then add the packet type to PacketType in types.py i think
	// Then make a static method in gamehandler
	// then do all your working in that
	// copy paste that boiler plate in all other static methods to make sure user in game and etc etc 
	// HARI
}
</script>

<!--<div v-if="players.length > 0" class="player-card"></div>
		this eventually will show  players in  game, but for now its a placeholder.  -->

<template>

	<!-- This is the page where you play the game, this will need to be live with the websocket we plan to use.  -->
	<div class="letter-selection" :class="{ 'letter-selection--visible': selectBlank !== -1 }">
		<div class="letter-selection__letter" v-for="letter, ind in alphabetArray"
			@click="selectedBlankTile(Number(ind))">
			{{ letter }}
		</div>
	</div>
	<div class="wrapper">
		<div class="wrapper__flex">
			<div class="player__column left">
				<GroupPlayer :users="group" :active-player="1"
					v-for="group in (playerGroups.length > 0 ? playerGroups.slice(0, isLaptop ? 4 : 2) : [])"
					v-if="websocketStore.game.type == 'GROUP'" />
				<Player :active-player="activePlayer" :user-game-data="player"
					v-for="player in (players.length > 0 ? players[0] : [])" v-else />
			</div>
			<div class="center__wrapper">
				<Grid :filler="DEFAULT_FILLER" :active-player="activePlayer" :grid="grid"
					:order-placement="orderPlacement" :letter-focused="letterFocused" :letters="letters"
					@cell-clicked="handleCellClicked()"
					:placed="!showPartners ? placed : (new Map(Object.entries(websocketStore.game.partnerPlaced).map(([k, v]) => [Number(k), v])))"
					:blank-letter="blankLetter" :show-partners="showPartners" />

				<div class="actions">
					<button class="action" @click="showPartners = !showPartners"><i class="pi"
							:class="{ 'pi-eye': showPartners, 'pi-eye-slash': !showPartners }"
							v-if="websocketStore.game.type == 'GROUP'"></i></button>
					<button class="action" @click="undo()"><i class="pi pi-undo"></i></button>
					<button class="action" @click="skipTurn()" :disabled="activePlayer !== userStore.userData?.userID"
						:class="{ 'action--disabled': activePlayer !== userStore.userData?.userID }"><i
							class="pi pi-arrow-right-arrow-left"></i></button>
					<div class="rack">
						<div class="rack__tile" v-for="(letter, ind) in letters" @click="handleTileClick(ind)"
							:class="{ 'tile--selected': letterFocused == ind, 'tile--used': placedIndexes.includes(ind) }">
							<span class="tile__letter">{{ letter.toUpperCase() }}</span>
							<span class="tile__score">{{ pointsMap[letter.toUpperCase()] || ' ' }}</span>
						</div>
					</div>
					<button @click="submitTurn()" class="action" :disabled="activePlayer !== userStore.userData?.userID"
						:class="{ 'action--disabled': activePlayer !== userStore.userData?.userID }"><i
							class="pi pi-check "></i></button>
					<button class="action" :disabled="activePlayer !== userStore.userData?.userID" @click="endGame"
						:class="{ 'action--disabled': activePlayer !== userStore.userData?.userID }"><i
							class="pi pi-flag"></i></button>
					<button class="action" @click="() => chatOpen = true"><i class="pi pi-comments"></i></button>
					<button class="action" @click="switchTurn"><i class="pi pi-comments">switch</i></button>

				</div>
			</div>
			<div class="player__column right">
				<GroupPlayer :users="group" :active-player="1"
					v-for="group in (playerGroups.length > 2 && !isLaptop ? playerGroups.slice(2, 4) : [])"
					v-if="websocketStore.game.type == 'GROUP'" />
				<Player :active-player="activePlayer" :user-game-data="player"
					v-for="player in (players.length > 1 ? players[1] : [])" v-else />
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
	align-items: center;
	width: 100%;
	margin: auto;
	padding: 0.5rem 1rem;
	overflow: hidden;
	box-sizing: border-box;
}

.wrapper__flex {
	display: flex;
	justify-content: center;
	align-items: center;
	gap: clamp(1rem, 2vw, 2rem);
	width: 80%;
	height: 100%;
}

.player__column {
	display: flex;
	flex-direction: column;
	gap: 8rem;
	min-width: 250px;
	justify-content: center;
}

.center__wrapper {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 0.85rem;
	flex: 1;
	height: 100%;
	min-width: 0;
}

.center__wrapper :deep(.grid),
.center__wrapper :deep(.board),
.center__wrapper :deep(.scrabble-grid) {
	width: min(80vmin, 700px);
	height: min(80vmin, 700px);
	aspect-ratio: 1 / 1;

	display: grid;
}

/* PERFECTLY CENTERED CONTROLS */
.actions {
	display: grid;
	grid-template-columns: 56px 56px 56px auto 56px 56px 56px;
	gap: 0.75rem;
	align-items: center;
	justify-content: center;
	width: fit-content;
	max-width: 100%;
}

/* rack now hugs tiles properly */
.rack {
	display: grid;
	grid-auto-flow: column;
	grid-auto-columns: clamp(44px, 3vw, 54px);
	gap: 0.45rem;
	padding: 0.65rem;
	border-radius: 14px;
	background: linear-gradient(145deg, #b88a44, #d9a955);
	box-shadow:
		inset 0 4px 8px rgba(0, 0, 0, 0.35),
		0 6px 14px rgba(0, 0, 0, 0.35);
	width: fit-content;
}

.rack__tile {
	width: clamp(44px, 3vw, 54px);
	height: clamp(44px, 3vw, 54px);
	background: #f1bc4c;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: clamp(1.15rem, 1.2vw, 1.55rem);
	font-weight: 800;
	border-radius: 8px;
	cursor: pointer;
	box-shadow: 0 3px 6px rgba(0, 0, 0, .35);
	transition: .18s ease;
	position: relative;
}

.tile__letter {
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
	font-size: 22px;
}

.tile__score {
	position: absolute;
	bottom: 6px;
	right: 8px;
	font-size: 12px;
	color: #000;
}

.rack__tile:hover,
.tile--selected {
	transform: translateY(-3px);
}

.tile--used {
	opacity: .45;
}

.action {
	width: 56px;
	height: 56px;
	border: none;
	border-radius: 12px;
	background: #f1bc4c;
	cursor: pointer;
	font-size: 1.25rem;
	box-shadow: 0 4px 10px rgba(0, 0, 0, .35);
	transition: .18s ease;
}

.action:hover {
	transform: translateY(-2px);
}

.action--disabled {
	opacity: .45;
	cursor: not-allowed;
}

/* hidden spacer button */
.action--blank {
	visibility: hidden;
	pointer-events: none;
}

.chat__panel {
	position: fixed;
	right: -420px;
	top: 0;
	width: min(380px, 92vw);
	height: 100%;
	background: #23345a;
	transition: .3s ease;
	padding: 1rem;
	color: white;
	z-index: 9999;
	box-shadow: -5px 0 15px rgba(0, 0, 0, .4);
	padding-bottom: 3rem;
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

/* laptops */
@media (max-height: 900px) {
	.wrapper {
		height: calc(100vh - 64px);
	}

	.center__wrapper {
		gap: 0.55rem;
	}

	.action {
		width: 50px;
		height: 50px;
	}

	.actions {
		grid-template-columns: 50px 50px 50px auto 50px 50px 50px;
		gap: .55rem;
	}

	.rack__tile {
		width: 46px;
		height: 46px;
		font-size: 1.1rem;
	}
}

/* mobile/tablet */
@media (max-width: 1100px) {
	.wrapper {
		height: auto;
		min-height: 100vh;
		overflow-y: auto;
	}

	.wrapper__flex {
		flex-wrap: wrap;
		padding-bottom: 1rem;
	}

	.player__column {
		flex-direction: row;
		width: 100%;
		justify-content: center;
		min-width: 0;
	}

	.actions {
		grid-template-columns: repeat(4, auto);
	}

	.rack {
		grid-column: 1 / -1;
		order: 20;
		justify-self: center;
	}
}

.letter-selection {
	display: none;
	visibility: hidden;
	position: fixed;
	left: 50%;
	top: 50%;
	transform: translate(-50%, -50%);
	background: var(--scrabble-board);
	border-radius: 10px;
	z-index: 9999;
	max-width: 50vh;
	width: auto;
	gap: 1rem;
	flex-wrap: wrap;
	max-width: 520px;
}

.letter-selection--visible {
	display: flex;
	visibility: visible;
}

.letter-selection__letter {
	height: 46px;
	width: 46px;
	color: white;
	display: flex;
	justify-content: center;
	align-items: center;
	border: 1px solid white;
	border-radius: 8px;
	cursor: pointer;
}

@media (min-width: 900px) and (max-width: 1200px) {
	.player__column {
		flex-direction: row;
	}

	.left {
		margin-top: 10rem;
	}
}
</style>