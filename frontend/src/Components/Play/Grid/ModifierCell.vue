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
	if (props.modifier == "DOUBLE_LETTER") {
		return "DL"
	} else if (props.modifier == "TRIPLE_LETTER") {
		return "TL"
	} else if (props.modifier == "DOUBLE_WORD") {
		return "DW"
	} else if (props.modifier == "TRIPLE_WORD") {
		return "TW"
	}
})


</script>



<template>
	<div class="modifier_cell">
		<p class="letter">{{ convertedLabel }}</p>
	</div>

</template>


<style lang="css" scoped>
.modifier_cell {
	user-select: none;
	background-color: black;
	aspect-ratio: 1/1;
	border: 2px solid var(--scrabble-board);
	background-color: #fff0cf;
	display: flex;
	justify-content: center;
	align-items: center;
	height: 100%;
	width: 100%;
	position: relative;
	/* border-radius: 8px; */
}

.letter {
	margin: 0;
	padding: 0;
	font-weight: bold;
}

.score {
	position: absolute;
	right: 0;
	bottom: 0;
	margin: 0;
	transform: translate(-15%, -5%);
}
</style>