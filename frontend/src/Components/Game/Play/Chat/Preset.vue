<script lang="ts" setup>
import useWebsocketStore from '@/Components/Stores/websocket';


const props = defineProps({
	message: {
		type: String,
		required: true
	}
})

const websocketStore = useWebsocketStore();

function sendMessage() {
	websocketStore.send("CHAT_MESSAGE", { message: props.message })
}
</script>



<template>
	<div class="preset" @click="sendMessage()">
		{{ props.message }}
	</div>

</template>


<style lang="css" scoped>
.preset {
	padding: .25rem;
	padding-inline: .5rem;
	width: fit-content;
	cursor: pointer;
	background-color: var(--tile-background-colour);
	color: var(--tile-text-colour);
	font-weight: 500;
	border-radius: 8px;
}
</style>