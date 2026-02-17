<script lang="ts" setup>
import useUserStore from '@/Components/Stores/user';
import useWebsocketStore from '@/Components/Stores/websocket';
import { isPartiallyEmittedExpression } from 'typescript';
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import Group from './Group.vue';


const route = useRoute();


const websocket = useWebsocketStore()
const user = useUserStore();

onMounted(() => {

	const code = route.query.code;

	if (code !== undefined) {
		// if not null, join game.
		console.log("joining")
		
		websocket.send("PLAYER_JOIN", {code: code})
	} else {

		console.log("undeifned")
	}
})

const codeModel = ref('');
function joinGame() {
	websocket.send("PLAYER_JOIN", {code: codeModel.value})
}

function leaveGame() {
	if (websocket.game) {
		websocket.send("PLAYER_LEAVE", {code: websocket.game.getId()})
	} else {
		// TODO: alert to say you are not in a game.
	}
}
function startGame() {
	if (websocket.game) {
		websocket.send("GAME_START", {})
	} else {
		// TODO: alert to say you are not in a game.
	}
}
</script>



<template>

	<div class="join">
		<input type="text" v-model="codeModel" placeholder="enter code...">
		<button @click="joinGame">Join</button>
		<button @click="leaveGame">Leave</button>
	</div>
	<div class="players" >

		<div class="player" v-for="player in websocket.game?.players.values()" v-if="websocket.game?.type == 'NORMAL'">
			{{ player.userName }}
		</div>
		<div class="group" v-else-if="websocket.game?.type == 'GROUP'">
			<div class="player">
				{{ user.userData?.userName  }}
			</div>
			<div class="groups">
				<Group v-for="(group, ind) in websocket.game?.groups" :group="group" :max-size="Number(websocket.game.maxGroupSize)" :id="ind" :key="ind" />
			</div>
		</div>

	</div>

	<div class="start" v-if="websocket.isLeader()">
		<button @click="startGame">Start Game</button>
	</div>
</template>


<style lang="css" scoped>

.groups {
	display: flex;
	gap: 1rem;
	justify-content: space-between;
	
}</style>