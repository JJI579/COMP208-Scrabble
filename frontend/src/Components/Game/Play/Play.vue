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

// Stores
const websocketStore = useWebsocketStore();
const userStore = useUserStore();

const letterFocused = ref<number>(-1);

watch(() => websocketStore.game.letters, (newLetters, oldLetters) => {
	letters.value = [...newLetters];

	const previousLetters = oldLetters ?? [];
	const rackChanged =
		newLetters.length !== previousLetters.length ||
		newLetters.some((letter, index) => letter !== previousLetters[index]);

	if (rackChanged) {
		// Only clear drafted placements when the rack genuinely changes.
		placed.value = new Map();
		orderPlacement.value = [];
	}
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
const unreadChatCount = ref(0);

watch(() => websocketStore.messages.length, (newLength, oldLength = 0) => {
	if (newLength <= oldLength) {
		return;
	}
	const latestMessage = websocketStore.messages[newLength - 1];
	if (!chatOpen.value && latestMessage?.author?.id !== userStore.userData?.userID) {
		unreadChatCount.value += newLength - oldLength;
	}
});

function toggleChat() {
	chatOpen.value = !chatOpen.value;
	if (chatOpen.value) {
		unreadChatCount.value = 0;
	}
}

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

function leaveGame() {
	websocketStore.send("PLAYER_LEAVE", {});
}

function skipTurn() {
	websocketStore.send("SKIP_TURN", {});

}
function switchTurn() {
	websocketStore.send("SWITCH_TURN", {});
}
</script>

<!--<div v-if="players.length > 0" class="player-card"></div>
		this eventually will show  players in  game, but for now its a placeholder.  -->

<template>

	<!-- This is the page where you play the game, this will need to be live with the websocket we plan to use.  -->
	<div v-if="selectBlank !== -1" class="letter-selection-overlay" @click="selectBlank = -1"></div>
	<div class="letter-selection" :class="{ 'letter-selection--visible': selectBlank !== -1 }">
		<div class="letter-selection__header">
			<h3>Choose a letter</h3>
			<p>Your blank tile will act as this letter.</p>
		</div>
		<div class="letter-selection__grid">
			<button class="letter-selection__letter" v-for="letter, ind in alphabetArray" :key="letter"
				@click="selectedBlankTile(Number(ind))">
				<span>{{ letter }}</span>
			</button>
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

				<div class="actions-wrap">
					<div class="actions">
						<button class="action tooltip-btn" @click="showPartners = !showPartners" data-tooltip="Toggle Partners"><i class="pi"
								:class="{ 'pi-eye': showPartners, 'pi-eye-slash': !showPartners }"
								></i></button>
						<button class="action tooltip-btn" @click="undo()" data-tooltip="Undo Last Move"><i class="pi pi-undo"></i></button>
						<button class="action tooltip-btn" @click="skipTurn()" :disabled="activePlayer !== userStore.userData?.userID"
							:class="{ 'action--disabled': activePlayer !== userStore.userData?.userID }" data-tooltip="Skip Turn"><i
								class="pi pi-angle-double-right"></i></button>
						<div class="rack">
							<div class="rack__tile" v-for="(letter, ind) in letters" @click="handleTileClick(ind)"
								:class="{ 'tile--selected': letterFocused == ind, 'tile--used': placedIndexes.includes(ind) }">
								<span class="tile__letter">{{ letter.toUpperCase() }}</span>
								<span class="tile__score">{{ pointsMap[letter.toUpperCase()] || ' ' }}</span>
							</div>
						</div>
						<button @click="submitTurn()" class="action tooltip-btn" :disabled="activePlayer !== userStore.userData?.userID"
							:class="{ 'action--disabled': activePlayer !== userStore.userData?.userID }" data-tooltip="Submit Turn">
								<i class="pi pi-check "></i></button>
						<button class="action tooltip-btn chat-toggle" @click="toggleChat" data-tooltip="Chat"><i class="pi pi-comments"></i>
							<span v-if="unreadChatCount > 0" class="chat__badge">{{ unreadChatCount > 99 ? '99+' : unreadChatCount }}</span>
						</button>
						<button class="action tooltip-btn" @click="switchTurn" :disabled="activePlayer !== userStore.userData?.userID"
							:class="{ 'action--disabled': activePlayer !== userStore.userData?.userID }" data-tooltip="Swap Tiles"><i class="pi pi-arrow-right-arrow-left"></i></button>
					</div>
					<button class="leave-game-btn" @click="leaveGame">Leave Game</button>
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

.tooltip-btn {
	position: relative;
	overflow: visible;
}
.tooltip-btn::after {
	content: attr(data-tooltip);
	position: absolute;
	bottom: calc(100% + 10px);
	left: 50%;
	transform: translateX(-50%) translateY(6px);
	background: rgba(20, 20, 20, 0.95);
	color: white;
	padding: 7px 10px;
	border-radius: 10px;
	font-size: 13px;
	font-weight: 600;
	white-space: nowrap;
	pointer-events: none;
	opacity: 0;
	transition: all 0.18s ease;
	box-shadow: 0 8px 18px rgba(0,0,0,.35);
	z-index: 9999;
	letter-spacing: .2px;
}

.tooltip-btn::before {
	content: "";
	position: absolute;
	bottom: calc(100% + 4px);
	left: 50%;
	transform: translateX(-50%);
	border-left: 6px solid transparent;
	border-right: 6px solid transparent;
	border-top: 6px solid rgba(20,20,20,.95);
	opacity: 0;
	transition: all 0.18s ease;
	z-index: 9999;
}

.tooltip-btn:hover::after,
.tooltip-btn:hover::before {
	opacity: 1;
	transform: translateX(-50%) translateY(0);
}

/* PERFECTLY CENTERED CONTROLS */
.actions-wrap {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 0.85rem;
	width: 100%;
}

.actions {
	display: grid;
	grid-template-columns: 56px 56px 56px auto 56px 56px 56px;
	gap: 0.75rem;
	align-items: center;
	justify-content: center;
	width: fit-content;
	max-width: 100%;
}

.leave-game-btn {
	border: none;
	border-radius: 12px;
	padding: 0.8rem 1.2rem;
	background: linear-gradient(135deg, #8f2a2a, #c94a4a);
	color: white;
	font-weight: 700;
	cursor: pointer;
	box-shadow: 0 4px 10px rgba(0, 0, 0, .3);
	transition: .18s ease;
}

.leave-game-btn:hover {
	transform: translateY(-2px);
	filter: brightness(1.05);
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

.chat-toggle {
	position: relative;
	z-index: 10001;
}

.chat__badge {
	position: absolute;
	top: -6px;
	right: -6px;
	min-width: 20px;
	height: 20px;
	padding: 0 5px;
	border-radius: 999px;
	background: #ff3b30;
	color: white;
	font-size: 11px;
	font-weight: 700;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 2px 8px rgba(0, 0, 0, .35);
}

.chat__panel {
	position: fixed;
	right: -420px;
	top: 0;
	width: min(380px, 92vw);
	height: 100%;
	background: rgba(35, 52, 90, 0.96);
	transition: .3s ease;
	padding: 1rem;
	color: white;
	z-index: 9999;
	box-shadow: -5px 0 15px rgba(0, 0, 0, .4);
	padding-bottom: 3rem;
	display: flex;
	flex-direction: column;
	gap: 0.75rem;
	backdrop-filter: blur(10px);
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
	align-self: flex-end;
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

.letter-selection-overlay {
	position: fixed;
	inset: 0;
	background: rgba(7, 16, 30, 0.6);
	backdrop-filter: blur(5px);
	z-index: 9998;
}

.letter-selection {
	display: none;
	visibility: hidden;
	position: fixed;
	left: 50%;
	top: 50%;
	transform: translate(-50%, -50%);
	background: linear-gradient(180deg, rgba(20, 35, 58, 0.98), rgba(14, 24, 40, 0.98));
	border: 1px solid rgba(255, 255, 255, 0.12);
	box-shadow: 0 24px 60px rgba(0, 0, 0, 0.45);
	border-radius: 20px;
	z-index: 9999;
	width: min(92vw, 560px);
	padding: 1.2rem;
	flex-direction: column;
	gap: 1rem;
}

.letter-selection--visible {
	display: flex;
	visibility: visible;
}

.letter-selection__header {
	text-align: center;
	color: white;
}

.letter-selection__header h3 {
	margin: 0;
	font-size: 1.35rem;
	color: #ffd86a;
}

.letter-selection__header p {
	margin: 0.35rem 0 0;
	font-size: 0.95rem;
	color: rgba(255, 255, 255, 0.78);
}

.letter-selection__grid {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(52px, 1fr));
	gap: 0.7rem;
}

.letter-selection__letter {
	height: 52px;
	width: 100%;
	color: white;
	display: flex;
	justify-content: center;
	align-items: center;
	border: 1px solid rgba(255, 255, 255, 0.14);
	background: linear-gradient(145deg, #d9a955, #f1bc4c);
	border-radius: 12px;
	cursor: pointer;
	font-size: 1.1rem;
	font-weight: 800;
	color: #1a1a1a;
	transition: transform 0.16s ease, box-shadow 0.16s ease, filter 0.16s ease;
	box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
}

.letter-selection__letter:hover {
	transform: translateY(-2px) scale(1.03);
	filter: brightness(1.04);
	box-shadow: 0 8px 18px rgba(0, 0, 0, 0.3);
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