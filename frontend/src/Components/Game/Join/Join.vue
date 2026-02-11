<script lang="ts" setup>
import { ref, type PropType } from 'vue';
import CustomSelect from './CustomSelect.vue';



type options = "team" | "friend" | "bot"
const props = defineProps({
	type: {
		required: true,
		type: String as PropType<options>,
	}
})




const gameOwner = false;

function startGame() {

}

const timeLimit = ref();

const options = [['none', "None"], ['45', "45 Minutes"], ['1', "1 Hour"], ['2', "2 Hours"]]

const botOptions = [['easy', "Easy"], ['medium', "Medium"], ['hard', "Hard"]]
</script>



<template>

	<!-- This is where you input the code to join a game -->
	<div class="content">



		<div class="label__container">
			<CustomSelect :options="options" :label="'Time Limit'" v-model:selected="timeLimit" />
		</div>

		<div class="container__bot" v-if="props.type == 'bot'">
			<div class="label__container">
				<CustomSelect :options="botOptions" :label="'Bot Difficulty'" />
			</div>
		</div>
		<div class="container__friends" v-if="props.type == 'friend'">
			<div class="label__container">
				<label for="friend__input" class="label"></label>
				<input type="text" name="friend__input" id="friend__input" placeholder="Username" class="input">
			</div>
			{{ 'players here...' }}
		</div>
		<div class="container__team" v-else>

		</div>
		<!-- if game owner show start game else show "waiting for leader to start" -->
		<div class="submit" v-if="gameOwner">
			<button @click="startGame()">Start</button>
		</div>
		<div class="waitfor" v-else>
			<p>Waiting for Leader to start game...</p>
		</div>
	</div>

</template>


<style lang="css" scoped>
.content {}


.label__container {
	display: flex;
	flex-direction: column;
	gap: .5rem;
}

.label {}

.select {
	padding: .5rem .75rem;
	font-size: medium;
	font-weight: 500;

}

.input {}
</style>