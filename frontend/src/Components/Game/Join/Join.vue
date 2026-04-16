<script lang="ts" setup>
import useUserStore from '@/Components/Stores/user'
import useWebsocketStore from '@/Components/Stores/websocket'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Group from './Group.vue'
import Game from '../../Stores/Game'

const route = useRoute()

const websocket = useWebsocketStore()
const user = useUserStore()

const codeModel = ref('')
const triedInput = ref(false)

/* 2 page state */
const inGame = computed(() => Boolean(websocket.game.id))
const isLeader = computed(
	() => websocket.game.leader === user.userData?.userID
)

onMounted(() => {
	const code = route.query.code

	if (code !== undefined) {
		codeModel.value = code as string
		websocket.send('PLAYER_JOIN', { code })
	}
})

watch([inGame, () => websocket.game.type, isLeader], ([inGameVal, type, leader]) => {
	if (inGameVal && type === 'BOT' && leader) {
		setTimeout(() => startGame(), 500); // small delay to ensure UI is ready
	}
})

function joinGame() {
	if (codeModel.value.length !== 4) {
		triedInput.value = true
		return
	}

	websocket.send('PLAYER_JOIN', {
		code: codeModel.value.toUpperCase()
	})
}

function leaveGame() {
	if (websocket.game) {
		websocket.send('PLAYER_LEAVE', {
			code: websocket.game.id
		})
	}

	websocket.game = new Game(0, {})
}

function startGame() {
	if (websocket.game) {
		websocket.send('GAME_START', {
			code: websocket.game.id
		})
	}
}
</script>

<template>
	<!-- JOIN PAGE -->
	<div class="join" v-if="!inGame">
		<div class="join__card">
			<h2>Join Game</h2>
			<p class="join__subtitle">Enter the 4-letter game code to join your friends.</p>

			<input
				type="text"
				v-model="codeModel"
				placeholder="ABCD"
				maxlength="4"
				class="join__input"
				:class="{
					'input--spacing': codeModel.length > 0,
					'input--error': triedInput
				}"
			/>

			<button @click="joinGame" class="join__button">
				Join
			</button>
		</div>
	</div>

	<!-- LOBBY PAGE -->
	<div class="ingame" v-else :key="websocket.game.id">

		<!-- separate code box -->
		<div class="ingame__code">
			{{ websocket.game.id }}
		</div>

		<!-- player panel -->
		<div class="ingame__players">

			<h2 class="players__title">
				Players ({{ websocket.game.players.size }})
			</h2>

			<!-- NORMAL -->
			<div
				v-if="websocket.game.type === 'NORMAL' || websocket.game.type === 'BOT'"
				class="player-list"
			>
				<div
					v-for="player in websocket.game.players.values()"
					:key="player.userID"
					class="player"
				>
					<span>{{ player.userName }}</span>

					<div class="player__icon">
						<span
							v-if="player.userID === websocket.game.leader"
						>
							👑
						</span>
					</div>
				</div>
			</div>

			<!-- GROUP -->
			<div
				v-else-if="websocket.game.type === 'GROUP'"
			>
				<h2 class="players__title">
					Groups ({{ websocket.game.players.size }})
				</h2>
				<div class="groups">
					<Group
						v-for="(group, ind) in websocket.game.groups"
						:key="ind"
						:group="group"
						:id="ind"
						:max-size="4"
					/>
				</div>
			</div>

			<!-- buttons -->
			<div class="ingame__actions">
				<button @click="leaveGame">
					Leave
				</button>

				<button
					v-if="isLeader && websocket.game.type !== 'BOT'"
					class="start-btn"
					@click="startGame"
				>
					Start Game
				</button>
			</div>

		</div>
	</div>
</template>

<style scoped>
/* PAGE */
.join,
.ingame {
	min-height: 100vh;
	width: 100%;
	padding: 2rem;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	background: linear-gradient(180deg, #0d1b2a, #1b263b);
	box-sizing: border-box;
	color: white;
	gap: 1.5rem;
}

/* GLASS PANEL */
.join,
.ingame__players {
	width: 100%;
	max-width: 720px;
	margin: 0 auto;
	padding: 2rem;
	border-radius: 24px;
	background: rgba(255,255,255,.08);
	backdrop-filter: blur(14px);
	border: 1px solid rgba(255,255,255,.1);
	box-shadow:
		0 12px 30px rgba(0,0,0,.25),
		0 0 25px rgba(77,148,255,.12);
}

.join__card {
	width: 100%;
	max-width: 420px;
	padding: 2.2rem;
	border-radius: 30px;
	background: rgba(255,255,255,.14);
	backdrop-filter: blur(18px);
	border: 1px solid rgba(255,255,255,.18);
	box-shadow:
		0 18px 45px rgba(0,0,0,.24),
		0 0 30px rgba(77,148,255,.15);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 1rem;
	text-align: center;
}

.join__subtitle {
	margin: 0;
	color: rgba(255,255,255,.75);
	font-size: 1rem;
	text-align: center;
	max-width: 360px;
}

/* HEADINGS */
h2,
.players__title {
	text-align: center;
	color: #4d94ff;
	font-size: 2rem;
	margin: 0;
}

/* JOIN */
.join__input {
	width: 100%;
	max-width: 360px;
	padding: 1.25rem 1.2rem;
	font-size: 2rem;
	text-align: center;
	border-radius: 20px;
	border: 2px solid rgba(255,255,255,.18);
	background: rgba(255,255,255,.1);
	color: white;
	outline: none;
	text-transform: uppercase;
	letter-spacing: .35rem;
}

.join__button {
	width: 100%;
	max-width: 320px;
	padding: 1rem 1.4rem;
	border: none;
	border-radius: 18px;
	font-weight: 700;
	cursor: pointer;
	color: white;
	background: linear-gradient(135deg,#2a4d8f,#4169a9);
	transition: .25s ease, transform .25s ease;
}

.join__button:hover {
	transform: translateY(-2px);
	box-shadow: 0 0 18px rgba(77,148,255,.35);
}

.join__input:focus {
	border-color: #4d94ff;
	box-shadow: 0 0 20px rgba(77,148,255,.35);
}

.input--spacing {
	letter-spacing: 10px;
	font-weight: 800;
}

.input--error {
	border-color: #ff5555;
	animation: shake .35s ease 2;
}

@keyframes shake {
	0% { transform: translateX(0); }
	25% { transform: translateX(-6px); }
	50% { transform: translateX(6px); }
	75% { transform: translateX(-6px); }
	100% { transform: translateX(0); }
}

/* BUTTONS */
.join__button,
.ingame__actions button {
	padding: 1rem 1.4rem;
	border: none;
	border-radius: 16px;
	font-weight: 700;
	cursor: pointer;
	color: white;
	background: linear-gradient(135deg,#2a4d8f,#4169a9);
	transition: .25s ease;
}

.join__button:hover,
.ingame__actions button:hover {
	transform: translateY(-2px);
	box-shadow: 0 0 18px rgba(77,148,255,.35);
}

.start-btn {
	background: linear-gradient(135deg,#13b35e,#19d977) !important;
}

/* LOBBY */
.ingame {
	justify-content: flex-start;
	padding-top: 4rem;
}

.ingame__code {
	padding: 1rem 2rem;
	border-radius: 18px;
	font-size: 2rem;
	font-weight: 800;
	letter-spacing: 8px;
	background: rgba(255,255,255,.08);
	color: #4d94ff;
	box-shadow: 0 0 20px rgba(77,148,255,.15);
}

.ingame__players {
	display: flex;
	flex-direction: column;
	gap: 1rem;
}

/* PLAYER LIST */
.player-list {
	display: flex;
	flex-direction: column;
	gap: .8rem;
}

.player {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 1rem 1.2rem;
	border-radius: 16px;
	background: rgba(255,255,255,.06);
	border: 1px solid rgba(255,255,255,.08);
	font-weight: 600;
}

.player:hover {
	background: rgba(255,255,255,.1);
}

.player__icon {
	color: gold;
	font-size: 1.2rem;
}

/* GROUP */
.groups {
	display: grid;
	grid-template-columns: repeat(auto-fit,minmax(220px,1fr));
	gap: 1rem;
}

/* ACTIONS */
.ingame__actions {
	display: flex;
	gap: 1rem;
	justify-content: center;
	flex-wrap: wrap;
	margin-top: .5rem;
}

/* MOBILE */
@media (max-width: 768px) {
	.join,
	.ingame {
		padding: 1rem;
	}

	h2,
	.players__title {
		font-size: 1.5rem;
	}

	.join__input {
		font-size: 1.5rem;
	}

	.ingame__code {
		font-size: 1.6rem;
		letter-spacing: 5px;
	}

	.ingame__actions {
		flex-direction: column;
	}

	.ingame__actions button {
		width: 100%;
	}
}
</style>