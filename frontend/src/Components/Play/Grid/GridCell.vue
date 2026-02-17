<script lang="ts" setup>
import { pointsMap } from '@/types';
import { computed } from 'vue';

const props = defineProps({
	cellValue: {
		type: String,
		required: true
	},
	score: {
		type: String,
		required: true
	},
	isDraft: {
		type: Boolean,
		required: true
	}
})

const score = computed(() => {
	const letter = props.cellValue.toUpperCase();
	return pointsMap[letter] || ' ';
})


</script>



<template>
	<div class="cell" :class="{ 'cell--draft': props.isDraft }">
		<p class="letter">{{ props.cellValue.toUpperCase() }}</p>
		<p class="score">{{ score }}</p>
	</div>
</template>


<style lang="css" scoped>
.cell {
	user-select: none;
	background-color: var(--tile-background-colour);
	color: var(--tile-text-colour);
	aspect-ratio: 1/1;
	border: 2px solid var(--scrabble-board);
	display: flex;
	height: 100%;
	width: 100%;
	position: relative;
	/* border-radius: 8px; */
}

.cell--draft {
	color: grey;
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