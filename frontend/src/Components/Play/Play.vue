<script lang="ts" setup>
import { onMounted, ref } from 'vue';
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

const options = ["DOUBLE_WORD", "DOUBLE_LETTER", "TRIPLE_WORD", "TRIPLE_LETTER"]
const letterFocused = ref<number>(-1);
const letters = ref<string[]>(['a', 'b', 'c', 'd', 'e']);
const placed = ref<Map<number, string>>(new Map());

function cellClicked(index: number) {
	console.log(index)
	if (letterFocused.value === -1) {
		// ignore...
	} else {
		if (grid.value[index] == DEFAULT_FILLER) {
			var temp = letters.value[letterFocused.value];
			if (temp !== undefined) {
				console.log("placed")
				placed.value.set(index, temp);
			}
		} else {
			console.log("not placed")
		}

	}
}
</script>



<template>

	<!-- This is the page where you play the game, this will need to be live with the websocket we plan to use.  -->
	<div class="board">
		<div class="cells">
			<div class="cell" v-for="(value, i) in grid" @click="cellClicked(i)">
				<ModifierCell :modifier="value as modifiers" v-if="options.includes(value)" />
				<GridCell :cell-value="placed.get(i) || value" :score="''" :is-draft="placed.get(i) !== undefined"
					v-else />
			</div>

		</div>
	</div>

	<div class="tileset">
		<div class="tileset__tile" v-for="(letter, ind) in letters" @click="letterFocused = ind"
			:class="{ 'tileset__tile--selected': letterFocused == ind }">
			{{ letter }}
		</div>
	</div>

</template>


<style lang="css" scoped>
.board {
	display: flex;
	justify-content: center;

}

.cells {
	/* background-color: pink; */
	width: 70%;
	display: grid;
	grid-template-columns: repeat(15, 1fr);
	gap: 0px;
	background-color: var(--scrabble-board);
	padding: .25rem;
}

.tileset {
	display: flex;
	gap: 1rem;
	justify-content: center;
	align-items: center;
	margin-top: 1rem;
}

.tileset__tile {
	display: flex;
	justify-content: center;
	align-items: center;
	background-color: var(--tile-background-colour);
	color: var(--tile-text-colour);
	padding: 1.5rem;
	height: 2rem;
	width: 2rem;
	font-weight: bold;
	font-size: larger;
	border-radius: 8px;
}

.tileset__tile--selected {
	border: 2px solid black;
}
</style>