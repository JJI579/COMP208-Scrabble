<script lang="ts" setup>
import useUserStore from '@/Components/Stores/user';
import useWebsocketStore from '@/Components/Stores/websocket';
import { isPartiallyEmittedExpression } from 'typescript';
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import Group from './Group.vue';
import Game from '../../Stores/Game';


const route = useRoute();


const websocket = useWebsocketStore()
const user = useUserStore();

onMounted(() => {

	const code = route.query.code;

	if (code !== undefined) {
		// if not null, join game.
		console.log("joining")
		codeModel.value = code as string;
		websocket.send("PLAYER_JOIN", { code: code })
	} else {
		console.log("undeifned")
	}
})

const codeModel = ref('');
const triedInput = ref(false);
function joinGame() {
	if (codeModel.value.length != 4) {
		triedInput.value = true;
		return
	}
	websocket.send("PLAYER_JOIN", { code: codeModel.value })
}

function leaveGame() {
	if (websocket.game) {
		websocket.send("PLAYER_LEAVE", { code: websocket.game.id })
	} else {
		// TODO: alert to say you are not in a game.
	}
}

function startGame() {
	if (websocket.game) {
		websocket.send("GAME_START", { code: websocket.game.id })
	} else {
		// TODO: alert to say you are not in a game.
	}
}

function quitLast() {
	websocket.game = new Game(0, {});
}
</script>



<template>
	{{websocket.game}}
	<div class="join" v-if="websocket.game.id == 0">
		<h2>Input Code</h2>
		<input type="text" v-model="codeModel" placeholder="enter code" class="join__input" maxlength="4"
			:class="{ 'input--spacing': codeModel.length > 0, 'input--error': triedInput === true }">
		<button @click="joinGame" class="join__button">Join</button>
	</div>

	<div class="ingame" v-else>
		<div class="players">
			{{ codeModel }}

			<div class="player" v-for="player in websocket.game?.players.values()"
				v-if="websocket.game?.type == 'NORMAL'">
				{{ player.userName }}
			</div>
			<div class="group" v-else-if="websocket.game?.type == 'GROUP'">
				<div class="player">
					{{ user.userData?.userName }}
				</div>
				<div class="groups">
					<Group v-for="(group, ind) in websocket.game?.groups" :group="group" :max-size="Number(4)" :id="ind"
						:key="ind" />
				</div>
			</div>
			<button @click="quitLast">quit last</button>
		</div>

		<div class="start" v-if="websocket.game.leader == user.userData?.userID">
			<button @click="startGame">Start Game</button>
			
		</div>
	</div>

</template>


<style lang="css" scoped>
/* Join via Code */
.join {
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	gap: 1rem;
}

.join__input {
	text-align: center;
	width: 20%;
	line-height: 1.5em;
	padding: .5rem .375rem;
	border-radius: 8px;
	box-sizing: border-box;
	border: 2px solid grey;
}

.input--spacing {
	letter-spacing: 10px;
	font-weight: bold;
	text-transform: uppercase;
}

.input--error {
	animation: ease 0.5s identifier 5
}

@keyframes identifier {
	0% {
		border: 2px solid rgb(169, 17, 17);
	}

	50% {
		border: 2px solid rgb(248, 41, 41);
	}

	100% {
		border: 2px solid rgb(169, 17, 17);
	}
}

.join__button {
	width: 20%;
}


/* In game */
.groups {
	display: flex;
	gap: 1rem;
	justify-content: space-between;
}
</style>