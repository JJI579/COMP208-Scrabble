<script lang="ts" setup>

import Option from './Option.vue';

const props = defineProps({
	options: {
		required: true,
		type: Array<string>,
		default: []
	}
})
const selectedOption = defineModel("current-option");

function clickOption(val: string) {
	selectedOption.value = val
}
</script>



<template>

	<div class="segmented__options">
		<Option v-for="option in options" :name="option" :selected="selectedOption == option" @click="clickOption" />
	</div>
</template>


<style lang="css" scoped>
.segmented__options {
	display: flex;
	gap: 1rem;
}
</style>