<script lang="ts" setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import GridCell from './Grid/GridCell.vue';
import ModifierCell from './Grid/ModifierCell.vue';
import type { modifiers } from '@/types';



const DEFAULT_FILLER = "";
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

const options = ["DOUBLE_WORD", "DOUBLE_LETTER", "TRIPLE_WORD", "TRIPLE_LETTER", "CENTER"];
const letterFocused = ref<number>(-1);
const letters = ref<string[]>(['a', 'b', 'c', 'd', 'e']);
const placed = ref<Map<number, [number, string]>>(new Map());
const placedIndexes = computed(() => {
	const values = placed.value.values();
	return Array.from(values).map((value) => value[0]);
})


const chatOpen = ref(false);
const activePlayer = ref(0);

const orderPlacement = ref<number[]>([]);


function cellClicked(index: number) {
	console.log(index)
	if (letterFocused.value === -1) {
		// ignore...
	} else if (placedIndexes.value.includes(index)) {
		letterFocused.value = -1
	} else {
		if (grid.value[index] == DEFAULT_FILLER) {
			var letter = letters.value[letterFocused.value];
			if (letter !== undefined) {
				placed.value.set(index, [letterFocused.value, letter]);
				orderPlacement.value.push(index)
				letterFocused.value = -1
			}
		} else {
			console.log("not placed")
		}

	}
}

function undo() {
	const last = orderPlacement.value.pop();
	console.log(last)
	if (last !== undefined) {
		const x = placed.value.delete(last);
	}
}

function handleKeyboardPress(event: KeyboardEvent) {
	switch (event.key) {
		case "1":
		case "2":
		case "3":
		case "4":
		case "5":
			letterFocused.value = Number(event.key) - 1
			break;
		case "Backspace":
			event.preventDefault();
			undo(); 1
			break;
	}
}

onMounted(() => {
	window.addEventListener("keyup", handleKeyboardPress)
})

onUnmounted(() => {
	window.removeEventListener("keyup", handleKeyboardPress)
});
</script>

		<!--<div v-if="players.length > 0" class="player-card"></div>
		this eventually will show  players in  game, but for now its a placeholder.  -->


<template>

	<!-- This is the page where you play the game, this will need to be live with the websocket we plan to use.  -->
<div class="game-wrapper">
	<div class="layout">
		<div class="player-column left">
			<div class="player-card" :class="{ active: activePlayer === 0 }">
				<img class="pfp" src="https://i.pravatar.cc/40?img=2" />
				<div class="player-info">
					<p class="name">Player 1</p>
					<p class="score">Score: 42</p>
					<p class="timer">02:15</p>
				</div>
			</div>

			<div class="player-card" :class="{ active: activePlayer === 1 }">
				<img class="pfp" src="https://i.pravatar.cc/40?img=4" />
				<div class="player-info">
					<p class="name">Player 2</p>
					<p class="score">Score: 31</p>
					<p class="timer">01:48</p>
				</div>
			</div>
		</div>
		<div class="center-area">
			<div class="board-frame" :class="{ active: activePlayer === 0 }">
				<div class="cells">
					<div class="cell" v-for="(value, i) in grid" @click="cellClicked(i)">
						<ModifierCell :modifier="value as modifiers" v-if="options.includes(value)" />
						<GridCell
							:cell-value="placed.get(i)?.[1] || value"
							:score="''"
							:is-draft="placed.get(i) !== undefined"
							:x="i % 15"
							:y="Math.floor(i / 15)"
							v-else />
					</div>
				</div>
			</div>
			<div class="rack">
				<div
					class="tile"
					v-for="(letter, ind) in letters"
					@click="letterFocused = ind"
					:class="{ selected: letterFocused == ind }">
					{{ letter }}
				</div>
			</div>
			<div class="actions">
				<button @click="undo()">Undo</button>
				<button>Swap</button>
				<button>Submit</button>
				<button @click="chatOpen = true">Chat</button>
				<button>Forfeit</button>
			</div>

		</div>
		<div class="player-column right">
			<div class="player-card" :class="{ active: activePlayer === 2 }">
				<img class="pfp" src="https://i.pravatar.cc/40?img=1" />
				<div class="player-info">
					<p class="name">Player 1</p>
					<p class="score">Score: 42</p>
					<p class="timer">02:15</p>
				</div>
			</div>
			<div class="player-card" :class="{ active: activePlayer === 3 }">
				<img class="pfp" src="https://i.pravatar.cc/40?img=3" />
				<div class="player-info">
					<p class="name">Player 1</p>
					<p class="score">Score: 42</p>
					<p class="timer">02:15</p>
				</div>
			</div>
		</div>
		<div class="chat-panel" :class="{ open: chatOpen }">
			<button class="close" @click="chatOpen=false">✕</button>
			<p>Chat here</p>
		</div>
	</div>
</div>

</template>


<style lang="css" scoped>
.game-wrapper {
min-height:80vh;
display:flex;
align-items:center;
justify-content:center;
}
.layout {
display:grid;
grid-template-columns: auto auto auto;
justify-content:center;
align-items:center;
gap:2rem;
}
.player-column {
display:flex;
flex-direction:column;
gap:2rem;
width:fit-content;
}

.player-card {
height:150px;
width:200px;
background:#2c8595;
border-radius:14px;
box-shadow:0 6px 12px rgba(0,0,0,0.4);
display:flex;
align-items:center;
gap:1rem;
padding:1rem;
align-self: flex-start;
transform: translateY(-5.3rem);
animation: floatCard 4s ease-in-out infinite;
}

@keyframes floatCard {
	0%, 100% {
		transform: translateY(-5.3rem);
	}
	50% {
		transform: translateY(-6rem);
	}
}

.player-card.active {
  transform: translateY(-5.3rem) scale(1);
  box-shadow:
    0 0 25px rgba(241,188,76,0.8),
    0 0 60px rgba(241,188,76,0.4),
    0 0 40px rgba(241,188,76,0.6) inset;
  animation: glowCard 4s ease-in-out infinite;
  transition: transform 0.3s, box-shadow 0.3s;
}

@keyframes glowCard {
	0% {
		transform: translateY(-5.3rem) scale(1);
		box-shadow:
			0 0 20px rgba(241,188,76,0.6),
			0 0 50px rgba(241,188,76,0.3),
			0 0 30px rgba(241,188,76,0.4) inset;
	}
	25% {
		transform: translateY(-5.5rem) scale(1.02);
		box-shadow:
			0 0 30px rgba(241,188,76,0.8),
			0 0 60px rgba(241,188,76,0.4),
			0 0 40px rgba(241,188,76,0.5) inset;
	}
	50% {
		transform: translateY(-5.8rem) scale(1.04);
		box-shadow:
			0 0 40px rgba(241,188,76,1),
			0 0 80px rgba(241,188,76,0.5),
			0 0 50px rgba(241,188,76,0.6) inset;
	}
	75% {
		transform: translateY(-5.5rem) scale(1.02);
		box-shadow:
			0 0 30px rgba(241,188,76,0.8),
			0 0 60px rgba(241,188,76,0.4),
			0 0 40px rgba(241,188,76,0.5) inset;
	}
	100% {
		transform: translateY(-5.3rem) scale(1);
		box-shadow:
			0 0 20px rgba(241,188,76,0.6),
			0 0 50px rgba(241,188,76,0.3),
			0 0 30px rgba(241,188,76,0.4) inset;
	}	
}

.player-card.active .timer {
	animation: pulseTimer 1s infinite;
}

@keyframes pulseTimer {
	0%, 100% { opacity: 1; }
	50% { opacity: 0.3; }
}


.pfp {
width:55px;
height:55px;
border-radius:50%;
object-fit:cover;
border:3px solid #f1bc4c;
}

.player-info {
display:flex;
flex-direction:column;
gap:3px;
}

.name {
font-weight:bold;
color:white;
}

.score {
color:#f1bc4c;
font-weight:bold;
}

.timer {
color:white;
font-size:14px;
position: relative;
}


.center-area {
display:flex;
flex-direction:column;
align-items:center;
gap:1.5rem;
}

.board-frame {
padding:22px;
background: var(--scrabble-board);
border-radius:20px;
box-shadow:
	inset 0 0 15px rgba(0,0,0,0.5),
	0 10px 25px rgba(0,0,0,0.5);
}

.board-frame.active{
transform: scale(1.02);
box-shadow:
inset 0 0 20px rgba(0,0,0,0.5),
0 20px 40px rgba(0,0,0,0.6);
transition: 0.3s;
}

.cells {
display:grid;
grid-template-columns: repeat(15, 40px);
grid-template-rows: repeat(15, 40px);
gap:0;
box-shadow:
inset 0 0 25px rgba(0,0,0,0.3),
0 8px 20px rgba(0,0,0,0.4);
}
.rack {
display:flex;
gap:10px;
padding:15px;
border-radius:12px;
background:linear-gradient(145deg,#b88a44,#d9a955);
box-shadow: inset 0 4px 6px rgba(0,0,0,0.4);
}

.tile {
width:50px;
height:50px;
background:#f1bc4c;
display:flex;
align-items:center;
justify-content:center;
font-size:22px;
font-weight:bold;
border-radius:8px;
cursor:pointer;
box-shadow:0 3px 6px rgba(0,0,0,0.4);
transition:0.2s;
}

.tile:hover {
transform:translateY(-3px);
}

.actions {
display:flex;
gap:1rem;
}

.actions button {
padding:12px 20px;
border:none;
border-radius:8px;
background:#f1bc4c;
font-weight:bold;
cursor:pointer;
box-shadow:0 3px 6px rgba(0,0,0,0.4);
}
.chat-panel {
position:fixed;
right:-320px;
top:0;
width:320px;
height:100%;
background:#2c8595;
transition:0.3s;
padding:1rem;
color:white;
z-index:100;
box-shadow:-5px 0 15px rgba(0,0,0,0.4);
}

.chat-panel.open {
right:0;
}

.close {
background:none;
border:none;
color:white;
font-size:20px;
cursor:pointer;
}

</style>