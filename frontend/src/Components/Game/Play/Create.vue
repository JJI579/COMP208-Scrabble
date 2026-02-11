<script lang="ts" setup>
import { ref } from 'vue';
import SegmentedControl from './SegmentedControl/SegmentedControl.vue';


const gamemodeOptions = ['Solo', 'Duos']
const gamemodeRef = ref('Solo');

const dictionaryOptions = ['Yes', "No"]
const dictionaryRef = ref('Yes');

function createGame() {
	// TODO: implement.
}
</script>



<template>

	<div class="options">
		<div class="opt">
			<p>Gamemode Options</p>
			<SegmentedControl :options="gamemodeOptions" v-model:current-option="gamemodeRef" />
		</div>
		<div class="opt">
			<p>Dictionary Enabled</p>
			<SegmentedControl :options="dictionaryOptions" v-model:current-option="dictionaryRef" />
		</div>
	</div>
	<button class="button" @click="createGame">
		Create Game
	</button>
</template>


<style lang="css" scoped>
.options {
	display: flex;
	flex-direction: column;
	gap: 1rem;
	width: 100%;
	margin-bottom: 1rem;
}

.opt {
	/* display: flex; */
}
</style>