<script lang="ts" setup>


type potential = {
	letter: string,
	score: number
}


type websocketReturn = {
	board: Map<string, potential>
	players: Map<string, string>
}

const props = defineProps({
	gridData: {
		required: true
	}
})
</script>



<template>
	<div class="cell">
		<p class="letter">J</p>
		<p class="score">8</p>
	</div>

</template>


<style lang="css" scoped>
.cell {
	background-color: black;
	aspect-ratio: 1/1;
	border: 2px solid var(--scrabble-board);
	background-color: #fff0cf;
	display: flex;
	height: 100%;
	width: 100%;
	position: relative;
	/* border-radius: 8px; */
}

.letter {
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
	margin: 0;
	font-size: 24px;
	font-weight: bolder;
}

.score {
	position: absolute;
	right: 0;
	bottom: 0;
	margin: 0;
	transform: translate(-15%, -5%);
}
</style>