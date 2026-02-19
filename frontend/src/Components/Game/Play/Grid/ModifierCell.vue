<script lang="ts" setup>
import { computed, type PropType } from 'vue';
import type { modifiers } from "@/types";

const props = defineProps({
	modifier: {
		type: String as PropType<modifiers>,
		required: true
	}
})

const convertedLabel = computed(() => {
	switch (props.modifier) {
		case 'DOUBLE_LETTER':
			return 'Double Letter';
		case 'TRIPLE_LETTER':
			return 'Triple Letter';
		case 'DOUBLE_WORD':
			return 'Double Word';
		case 'TRIPLE_WORD':
			return 'Triple Word';
		case 'CENTER':
			return '★';
		default:
			return '';
	}
})

const bgColour = computed(() => {
	switch (props.modifier) {
		case 'DOUBLE_LETTER':
			return '#242050';
		case 'TRIPLE_LETTER':
			return '#db005a';
		case 'DOUBLE_WORD':
			return '#ebc728';
		case 'TRIPLE_WORD':
			return '#c5d14a';
		case 'CENTER':
			return '#f1bc4c';
		default:
			return '#2c8595';
	}
})

</script>



<template>
	<div class="modifier_cell" :style="{ backgroundColor: bgColour }">
		<p class="letter" :class="{ star: modifier === 'CENTER' }">
			{{ convertedLabel }}
		</p>

	</div>

</template>


<style lang="css" scoped>
.modifier_cell {
	user-select: none;
	aspect-ratio: 1/1;
	border: 2px solid white;
	display: flex;
	justify-content: center;
	align-items: center;
	text-align: center;
	height: 100%;
	width: 100%;
	position: relative;
	font-weight: bold;
	font-size: 12px;
	line-height: 1;
	color: white;
	box-shadow: 1px 1px 3px rbga(0, 0, 0, 0.3);
	transition: transform 0.2s;
}

.modifier_cell:hover {
	transform: scale(1.05);
}

.letter {
	margin: 0;
	padding: 0;
}

.score {
	position: absolute;
	bottom: 2px;
	right: 2px;
	font-size: 10px;
	color: white;
}

.star {
	font-size: 24px;
	color: black;
}
</style>