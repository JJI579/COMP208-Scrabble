<script lang="ts" setup>
import { ref, watch } from 'vue';
import SegmentedControl from '../SegmentedControl/SegmentedControl.vue';
import CustomSelect from '../CustomSelect/CustomSelect.vue';
import api from '@/api';
import { useRouter, useRoute } from 'vue-router';
import { onMounted } from 'vue';
import useWebsocketStore from '@/Components/Stores/websocket';
import Game from '@/Components/Stores/Game';

const route = useRoute();

type Option = [string, string, string?];

const gameTypeRef = ref("NORMAL");
const options: Option[] = [['NORMAL', "Normal", "pi pi-play"], ['GROUP', "Team", "pi pi-users"], ["BOT", "Bot", "pi pi-android"]]

const timeLimitRef = ref("none");
const timeLimitOptions: Option[] = [["none", "None"], ["45", "45 Minutes"], ["1", "1 Hour"], ["2", "2 Hours"]]

// const useDictionaryRef = ref("false");
// const dictionaryOptions: Option[] = [["false", "No"], ["true", "Yes"]]

const groupSizeRef = ref("4");
const groupSizeOptions: Option[] = [["2", "2"], ["3", "3"], ["4", "4"]]

const botDifficultyRef = ref("hard");
const botDifficultyOptions: Option[] = [["easy", "Easy"], ["medium", "Medium"], ["hard", "Hard"]]

const gtModel = ref(false);
const tlModel = ref(false);
const ngModel = ref(false);
const bdModel = ref(false);


const router = useRouter();

const websocket = useWebsocketStore()
const waitingForWebsocket = ref(false);
watch(() => websocket.readyToSend, () => {
	waitingForWebsocket.value = websocket.readyToSend;
})

onMounted(() => {
	const type = route.query.type as string;
	const groupSize = route.query.groupSize as string;
	waitingForWebsocket.value = websocket.readyToSend;
	if (type) {
		gameTypeRef.value = type;
	}

	if (groupSize) {
		groupSizeRef.value = groupSize;
	}
});



function goToJoin() {
	if (websocket.game.id !== 0) {
		websocket.send('PLAYER_LEAVE', {
			code: websocket.game.id
		})
		websocket.game.reset()
	}
	setTimeout(() => {
		router.push({ name: "join" });
	}, 500);

}

async function createGame() {

	if (websocket.game.id !== 0) {
		websocket.send('PLAYER_LEAVE', {
			code: websocket.game.id
		})
		websocket.game.reset();
		console.log("Resetting game state");
	}
	const resp = await api.post("/game/create", {
		game_type: gameTypeRef.value,
		group_size: Number(groupSizeRef.value),
		time_limit: timeLimitRef.value,
		dictionary: false,
		bot_difficulty: gameTypeRef.value === "BOT" ? botDifficultyRef.value : undefined
		// dictionary: useDictionaryRef.value === "true"
	})
	router.push({ name: "join", query: { code: resp.data.code } })
}

function closeOthers(whichMenu: string) {
	console.log(whichMenu)
	gtModel.value = false;
	tlModel.value = false;
	ngModel.value = false;
	bdModel.value = false;

	if (whichMenu === "Game Type") {
		gtModel.value = true;
	} else if (whichMenu == "Time Limit") {
		console.log("time limit")
		tlModel.value = true;
	} else if (whichMenu === "Bot Difficulty") {
		bdModel.value = true;
	} else {
		ngModel.value = true;
	}
}
function closeMenu(whichMenu: String) {
	if (whichMenu === "Game Type") {
		gtModel.value = false;
	} else if (whichMenu === "Time Limit") {
		tlModel.value = false;
	} else if (whichMenu === "Bot Difficulty") {
		bdModel.value = false;
	} else {
		ngModel.value = false;
	}

}
</script>



<template>
	<div class="create" v-if="waitingForWebsocket">

		<div class="join__card card-glass">
			<div class="join__text">
				<h2>Join a Game</h2>
				<p>Enter a game code to join an existing match</p>
			</div>

			<button class="join__btn glow-hover" @click="goToJoin">
				Join Game
			</button>
		</div>
		<div class="create__header">
			<h1 class="glow-text">Create Game</h1>
			<p>Configure your match settings before starting</p>
		</div>
		<div class="create__card card-glass">
			<div class="create__grid">
				<CustomSelect :options="options" label="Game Type" v-model:selected="gameTypeRef" @open="closeOthers"
					@close="closeMenu" v-model:isopen="gtModel" />
				<CustomSelect :options="timeLimitOptions" label="Time Limit" v-model:selected="timeLimitRef"
					@close="closeMenu" @open="closeOthers" v-model:isopen="tlModel" />
				<!-- <CustomSelect :options="dictionaryOptions" label="Dictionary Allowed"
					v-model:selected="useDictionaryRef" /> -->
				<CustomSelect v-if="gameTypeRef === 'GROUP'" :options="groupSizeOptions" label="Number of Groups" v-model:selected="groupSizeRef"
					@close="closeMenu" @open="closeOthers" v-model:isopen="ngModel" />
				<CustomSelect v-if="gameTypeRef === 'BOT'" :options="botDifficultyOptions" label="Bot Difficulty" v-model:selected="botDifficultyRef"
					@close="closeMenu" @open="closeOthers" v-model:isopen="bdModel" />
			</div>
			<button class="create__btn glow-hover" @click="createGame">
				Create Game
			</button>
		</div>
	</div>
	<div v-else class="middle">
		<div class="loading">
			<div class="loading__spinner"></div>
			<p class="loading__title">Connecting...</p>
		</div>
	</div>
</template>

<style scoped>
.middle {
	display: flex;
	justify-content: center;
	align-items: center;
	min-height: 85vh;
}

.loading {
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;

	gap: 1rem;
}

/* Loading Page */
.loading__spinner {
	width: 60px;
	height: 60px;
	border: 6px solid #334155;
	border-top: 6px solid #38bdf8;
	border-radius: 50%;
	animation: spin 1s linear infinite;
}

.loading__title {
	font-size: large;
	color: white;
}

@keyframes spin {
	0% {
		transform: rotate(0deg);
	}

	100% {
		transform: rotate(360deg);
	}
}




.create {
	min-height: 100vh;
	padding: 2rem;
	display: flex;
	flex-direction: column;
	align-items: center;
	background: linear-gradient(180deg, #0d1b2a, #1b263b);
	color: rgb(255, 255, 255);
}

.create__header {
	text-align: center;
	margin-bottom: 2rem;
}

.create__header h1 {
	font-size: 2.4rem;
	font-weight: 800;
}

.create__header p {
	opacity: 0.75;
	margin-top: 0.5rem;
}

.create__card {
	width: 100%;
	max-width: 650px;
	border-radius: 20px;
	padding: 2rem;

	background: rgba(255, 255, 255, 0.15);
	backdrop-filter: blur(12px);

	box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
}


.create__grid {
	display: grid;
	grid-template-columns: 1fr;
	gap: 1.2rem;
	margin-bottom: 2rem;
}

.create__btn {
	width: 100%;
	padding: 1rem;
	border: none;
	border-radius: 16px;
	font-size: 1.2rem;
	font-weight: 700;
	letter-spacing: 0.5px;
	color: #f0f0f0;
	background: linear-gradient(135deg, #2a4d8f, #4169a9);
	cursor: pointer;
	transition: all 0.25s ease;
	box-shadow: 0 8px 20px rgba(65, 105, 169, 0.25);
}

.create__btn:hover {
	transform: scale(1.04);
	background: linear-gradient(135deg, #4169a9, #5a7dbb);
	box-shadow: 0 0 20px rgba(77, 148, 255, 0.6);
}

.create__btn:active {
	transform: scale(0.98);
}

.glow-text {
	color: #4d94ff;
	text-shadow: 0 0 8px #4d94ff, 0 0 16px #80c0ff;
}

.glow-hover:hover {
	box-shadow: 0 0 20px rgba(77, 148, 255, 0.7);
}

.join__card {
	width: 100%;
	max-width: 650px;
	margin-top: 1.5rem;
	padding: 1.5rem 2rem;
	border-radius: 20px;
	display: flex;
	justify-content: space-between;
	align-items: center;
	background: rgba(255, 255, 255, 0.08);
	backdrop-filter: blur(12px);

	box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.join__text h2 {
	font-size: 1.3rem;
	font-weight: 700;
	margin: 0;
}

.join__text p {
	font-size: 0.9rem;
	opacity: 0.7;
	margin-top: 0.3rem;
}

.join__btn {
	padding: 0.9rem 1.2rem;
	border: none;
	border-radius: 14px;
	font-weight: 700;
	color: white;
	background: linear-gradient(135deg, #4d94ff, #2a4d8f);
	cursor: pointer;

	transition: all 0.2s ease;
}

.join__btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 0 18px rgba(77, 148, 255, 0.6);
}
</style>