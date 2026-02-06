<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import GridCell from './Grid/GridCell.vue';



const DEFAULT_FILLER = "";
const grid = ref<string[]>([]);

onMounted(() => {
	var initGrid = [];

	for (let i = 0; i < 225; i++) {
		initGrid.push(DEFAULT_FILLER)
	}
	grid.value = initGrid;
})
</script>



<template>

	<!-- This is the page where you play the game, this will need to be live with the websocket we plan to use.  -->
	<div class="board">
		<div class="cells">
			<GridCell :key="i" v-for="(value, i) in grid" :grid-data="value" />
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
</style>