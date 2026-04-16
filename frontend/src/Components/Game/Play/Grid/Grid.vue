<script lang="ts" setup>
import { DEFAULT_FILLER, type modifiers } from '@/types';
import { computed, ref } from 'vue';
import GridCell from './GridCell.vue';
import ModifierCell from './ModifierCell.vue';
import useUserStore from '@/Components/Stores/user';

const emit = defineEmits(['cellClicked']);

const grid = defineModel("grid", { required: true, type: Array<string | modifiers> });
const letters = defineModel("letters", { required: true, type: Array<string> });
const letterFocused = defineModel("letterFocused", { required: true, type: Number });
const blankLetter = defineModel("blankLetter", { required: true, type: String })
const activePlayer = defineModel("activePlayer", { required: true, type: Number });
const orderPlacement = defineModel("orderPlacement", { required: true, type: Array<number> });

const placed = defineModel<Map<number, [number, string, string?]>>("placed", {
	required: true,
	type: Map
});

const placedIndexes = computed(() => {
	const values = placed.value.values();
	return Array.from(values).map((value) => value[0]);
})

const OPTIONS = ["DOUBLE_WORD", "DOUBLE_LETTER", "TRIPLE_WORD", "TRIPLE_LETTER", "CENTER"];

const props = defineProps({
	filler: {
		type: String,
		required: true
	},
	showPartners: {
		type: Boolean,
		required: true
	}
})

const userStore = useUserStore();

function cellClicked(index: number) {
	console.log(index)
	if (letterFocused.value === -1) {
		// ignore...
	} else if (placedIndexes.value.includes(letterFocused.value)) {
		letterFocused.value = -1
	} else {
		if (grid.value[index] == props.filler || OPTIONS.includes(grid.value[index] || "")) {
			var letter = letters.value[letterFocused.value];
			if (letter !== undefined) {
				const arr: [number, string, string?] = [letterFocused.value, letter, undefined];
				if (blankLetter.value !== DEFAULT_FILLER) {
					arr[2] = blankLetter.value
				}
				console.log(arr);
				placed.value.set(index, arr);
				orderPlacement.value.push(index)
				blankLetter.value = DEFAULT_FILLER;
				emit('cellClicked')
			}
		} else {

		}

	}
}

</script>



<template>
	<div class="board-frame" :class="{ active: activePlayer === userStore.userData?.userID }">
		<div class="cells">
			<div class="cell" v-for="(value, i) in grid" @click="cellClicked(i)">
				<ModifierCell :modifier="(value as modifiers)" v-if="OPTIONS.includes(value) && !placed.get(i)" />
				<GridCell :cell-value="placed.get(i)?.[2] || placed.get(i)?.[1] || value" :score="''"
					:is-draft="placed.get(i) !== undefined" :x="i % 15" :y="Math.floor(i / 15)"
					:is-partners="showPartners" v-else />
			</div>
		</div>
	</div>

</template>


<style lang="css" scoped>
.board-frame {
	padding: 22px;
	background: var(--scrabble-board);
	border-radius: 20px;
	box-shadow:
		inset 0 0 15px rgba(0, 0, 0, 0.5),
		0 10px 25px rgba(0, 0, 0, 0.5);
}

.board-frame.active {
	transform: scale(1.02);
	box-shadow:
		inset 0 0 20px rgba(0, 0, 0, 0.5),
		0 20px 40px rgba(0, 0, 0, 0.6);
	transition: 0.3s;
}

.cells {
	display: grid;
	grid-template-columns: repeat(15, 40px);
	grid-template-rows: repeat(15, 40px);
	gap: 0;

	box-shadow:
		inset 0 0 25px rgba(0, 0, 0, 0.3),
		0 8px 20px rgba(0, 0, 0, 0.4);
}
</style>
