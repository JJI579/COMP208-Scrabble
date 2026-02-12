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
</script>



<template>

	<div class="join">
		<input type="text" v-model="codeModel" placeholder="enter code...">
		<button @click="joinGame">Join</button>
	</div>
	<div class="players">
		{{ websocket.sessionID }}
		{{ websocket.game?.players }}
		<div class="player" v-for="player in websocket.game?.players">
			{{ player.userName }}
		</div>

	</div>
</template>


<style lang="css" scoped></style>