<script lang="ts" setup>
import useWebsocketStore from '@/Components/Stores/websocket';
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';


const route = useRoute();


const websocket = useWebsocketStore()

onMounted(() => {

	const code = route.query.code;

	if (code !== undefined) {
		// if not null, join game.
		console.log("joining")
		websocket.join(code as string)
	} else {

		console.log("undeifned")
	}
})

const codeModel = ref('');
function joinGame() {
	websocket.join(codeModel.value)
}

function leaveGame() {
	websocket.leave()
}
</script>



<template>

	<div class="join">
		<input type="text" v-model="codeModel" placeholder="enter code...">
		<button @click="joinGame">Join</button>
		<button @click="leaveGame">Leave</button>
	</div>
	<div class="players">

		<div class="player" v-for="player in websocket.game?.players.values()">
			{{ player.userName }}
		</div>

	</div>

	<div class="start" v-if="websocket.isLeader()">
		<button>Start Game</button>
	</div>
</template>


<style lang="css" scoped></style>