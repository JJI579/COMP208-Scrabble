<script lang="ts" setup>
import useWebsocketStore from '@/Components/Stores/websocket';
import Preset from './Preset.vue';
import { ref } from 'vue';
import Message from './Message.vue';



const websocketStore = useWebsocketStore();

function sendMessage(sample: String | undefined) {
	var message;
	if (sample == undefined) {
		message = sample;
	} else {
		// send input content
		message = messageModel.value
	}

	websocketStore.send("CHAT_MESSAGE", {
		message: message
	});
}

const sampleSends = [
	'Crushing it!',
	'On a roll!',
	'Great job!',
	'Keep going!',
	'Not much time left!',
	'Youre doing fantastic!',
	'Youre a Scrabble mastermind!',
	'Wow, not many points...'
]

function sampleClick(sample: String) {
	messageModel.value = sample.toString();
}
const messageModel = ref("");

const messages = websocketStore.messages;
</script>


<template>

	<div class="sample">
		<div class="sample__message" v-for="message in sampleSends">
			<Preset :message="message" @click="sampleClick"  />
		</div>
	</div>
	<div class="flex-box">
		
		<div class="messages">
			<Message v-for="message in messages" :message="message"/>
		</div>
		<div class="send">
			<input type="text" v-model="messageModel" class="send__input">
			<button class="send__submit"><i class="pi pi-upload"></i></button>
		</div>
	</div>
</template>


<style lang="css" scoped>
.sample {
	margin-top: 1rem;
	display: flex;
	flex-wrap: wrap;
}

.sample__message {
	padding: .175rem .25rem;
}

.flex-box {
	display: flex;
	flex-direction: column;
	justify-content: space-between;
	height: 70%;
}

.messages {
	background-color: pink;
	flex: 1;
	width: 100%;
}

.send {
	padding-block: 1rem;
	height: 2rem;
	display: flex;
	gap: .5rem;
	
	justify-content: center;
}

.send__input {
	height: 3rem;
	width: 100%;
	border-radius: 8px;
	box-sizing: border-box;
	font-size: large;
	padding-left: 1rem;
}

.send__submit {
	width: 3rem;
	box-sizing: border-box;
	height: 3rem;
	background-color: var(--clr-success-a10);
	border: none;
	border-radius: 8px;
	cursor: pointer;
}
</style>