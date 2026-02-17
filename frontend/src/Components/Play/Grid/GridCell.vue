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
	if (props.x === 7 && props.y === 7) {
		return '#FFD700';
	}
	return '#8ED6FF';
})

</script>



<template>
	<div class="cell" :class="{ 'cell--draft': isDraft }" :style="{ backgroundColor: bgColour }">
		<p class="letter">{{ cellValue !== '|' ? cellValue.toUpperCase() : '' }}</p>
    	<p class="score" v-if="cellValue !== '|'">{{ score }}</p>
	</div>
</template>


<style lang="css" scoped>
.cell {
user-select: none;
aspect-ratio: 1/1;
border: 1px solid white;
display: flex;
justify-content: center;
align-items: center;
position: relative;
font-weight: bold;
font-size: 20px;
color: #000; 
}

.cell:hover {
  transform: scale(1.05);
}

.cell--draft {
	opacity: .5;
}

.letter {
	font-size: 24px;
	max-width: 90%;
	max-height: 90%;
	display: flex;
	justify-content: center;
	align-items: center;
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
}

.score {
  position: absolute;
  right: 4px;
  bottom: 2px;
  font-size: 12px;
}
</style>