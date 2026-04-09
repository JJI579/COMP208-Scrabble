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
	},
	x: {
		type: Number,
		required: true
	},
	y: {
		type: Number,
		required: true
	}

})

const score = computed(() => {
	const letter = props.cellValue.toUpperCase();
	return pointsMap[letter] || ' ';
})

// center highlight
const bgColour = computed(() => {
	return '#37a8bd';
})

</script>



<template>
	<div class="cell" :class="{ 'scrabble--placed': cellValue.length > 1, 'cell--draft': isDraft }"
		:style="{ backgroundColor: bgColour }">
		<p class="cell__letter">{{ cellValue !== '|' ? cellValue.toUpperCase() : '' }}</p>
		<p class="cell__score" v-if="cellValue !== '|'">{{ score }}</p>
	</div>
</template>


<style lang="css" scoped>
.cell {
	user-select: none;
	aspect-ratio: 1/1;
	border: 1px solid white;
	position: relative;
	font-weight: bold;
	font-size: 20px;
	color: #000;
}

.cell:hover {
	transform: scale(1.05);
}

.scrabble--placed {
	background: linear-gradient(145deg, #f3d28a, #d1a652);
	border-radius: 6px;
	box-shadow:
		inset 0 2px 2px rgba(255, 255, 255, 0.4),
		inset 0 -2px 3px rgba(0, 0, 0, 0.3),
		0 3px 5px rgba(0, 0, 0, 0.4);
	border: 1px solid #a87e3a;
}

.cell--draft {
	background-color: rgba(0, 0, 0, 0.2) !important;
}

.cell__letter {
	margin: 0;
	max-height: 90%;
	max-width: 90%;
	font-size: 24px;
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
}

.cell__score {
	position: absolute;
	bottom: 3px;
	right: 3px;
	font-size: 12px;
	margin: 0;
}
</style>