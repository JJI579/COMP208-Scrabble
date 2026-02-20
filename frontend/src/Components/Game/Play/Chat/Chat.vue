<script lang="ts" setup>
import useWebsocketStore from '@/Components/Stores/websocket';
import Preset from './Preset.vue';



const websocketStore = useWebsocketStore();


const messages = [
	'Crushing it!',
	'On a roll!',
	'Great job!',
	'Keep going!',
	'Not much time left!',
	'Youre doing fantastic!',
	'Youre a Scrabble mastermind!',
	'Wow, not many points...'
]

</script>



<template>

	<div class="sample">
		<div class="sample__message" v-for="message in messages">
			<Preset :message="message" />
		</div>
	</div>
</template>


<style lang="css" scoped>
.sample {
	margin-top: 1rem;
	display: flex;
	gap: 5px;
	flex-wrap: wrap;
}

.sample__message {
	padding: .175rem .5rem;
}
</style>