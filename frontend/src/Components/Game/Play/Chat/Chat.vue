<script lang="ts" setup>
import useWebsocketStore from '@/Components/Stores/websocket';
import Preset from './Preset.vue';
import { ref } from 'vue';
import Message from './Message.vue';



const websocketStore = useWebsocketStore();

function sendMessage() {
	var message = messageModel.value
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
			<button class="send__submit" @click="sendMessage"><i class="pi pi-upload"></i></button>
		</div>
	</div>
</template>


<style lang="css" scoped>
.sample {
	margin-bottom: 0.5rem;
	display: flex;
	flex-wrap: wrap;
	gap: 0.25rem;
	justify-content: center;
	max-height: 120px;
	overflow-y: auto;
	padding: 0.25rem;
}

.sample__message {
	padding: 0.1rem 0.15rem;
}

.flex-box {
	display: flex;
	flex-direction: column;
	height: calc(100% - 120px);
	min-height: 200px;
	gap: 0.5rem;
}

.messages {
	background: linear-gradient(145deg, #f8f9fa, #e9ecef);
	border: 2px solid #dee2e6;
	border-radius: 8px;
	flex: 1;
	width: 100%;
	padding: 0.5rem;
	overflow-y: auto;
	scrollbar-width: thin;
	scrollbar-color: #6c757d #f8f9fa;
	box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
	min-height: 100px;
}

.messages::-webkit-scrollbar {
	width: 6px;
}

.messages::-webkit-scrollbar-track {
	background: #f8f9fa;
	border-radius: 3px;
}

.messages::-webkit-scrollbar-thumb {
	background: #6c757d;
	border-radius: 3px;
}

.messages::-webkit-scrollbar-thumb:hover {
	background: #495057;
}

.send {
	display: flex;
	gap: 0.25rem;
	align-items: center;
	padding: 0.25rem 0;
}

.send__input {
	height: 2.5rem;
	flex: 1;
	border-radius: 6px;
	box-sizing: border-box;
	font-size: 0.9rem;
	padding: 0 0.75rem;
	border: 2px solid #dee2e6;
	transition: border-color 0.3s ease;
	background: white;
}

.send__input:focus {
	outline: none;
	border-color: var(--clr-primary-a20);
	box-shadow: 0 0 0 2px rgba(254, 178, 254, 0.1);
}

.send__submit {
	width: 2.5rem;
	height: 2.5rem;
	box-sizing: border-box;
	background: linear-gradient(145deg, var(--clr-success-a10), var(--clr-success-a0));
	border: none;
	border-radius: 6px;
	cursor: pointer;
	transition: all 0.3s ease;
	color: white;
	font-size: 1rem;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
	flex-shrink: 0;
}

.send__submit:hover {
	transform: translateY(-1px);
	box-shadow: 0 3px 6px rgba(0, 0, 0, 0.3);
}

.send__submit:active {
	transform: translateY(0);
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
</style>