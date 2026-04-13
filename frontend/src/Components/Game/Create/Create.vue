<script lang="ts" setup>
import { ref } from 'vue';
import SegmentedControl from '../SegmentedControl/SegmentedControl.vue';
import CustomSelect from '../CustomSelect/CustomSelect.vue';
import api from '@/api';
import { useRouter, useRoute } from 'vue-router';
import { onMounted } from 'vue';

const route = useRoute();

type Option = [string, string, string?];

const gameTypeRef = ref("NORMAL");
const options: Option[] = [['NORMAL', "Normal", "pi pi-play"], ['GROUP', "Team", "pi pi-users"], ["BOT", "Bot", "pi pi-android"]]

const timeLimitRef = ref("none");
const timeLimitOptions: Option[] = [["none", "None"], ["45", "45 Minutes"], ["1", "1 Hour"], ["2", "2 Hours"]]

const useDictionaryRef = ref("false");
const dictionaryOptions: Option[] = [["false", "No"], ["true", "Yes"]]

const groupSizeRef = ref("4");
const groupSizeOptions: Option[] = [["2", "2"], ["3", "3"], ["4", "4"]]

const router = useRouter();

onMounted(() => {
  const type = route.query.type as string;
  const groupSize = route.query.groupSize as string;

  if (type) {
    gameTypeRef.value = type;
  }

  if (groupSize) {
    groupSizeRef.value = groupSize;
  }
});
// game_type: GAME_TYPE
// group_size: Optional[int]
// time_limit: str | bool
// dictionary: bool # whether dictionary is allowed

function goToJoin() {
	router.push({ name: "join" });
}

async function createGame() {
	// TODO: implement.
	const resp = await api.post("/game/create", {
		game_type: gameTypeRef.value,
		group_size: Number(groupSizeRef.value),
		time_limit: timeLimitRef.value,
		dictionary: useDictionaryRef.value
	})
	router.push({ name: "join", query: { code: resp.data.code } })
}


</script>



<template>
  <div class="create">

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
        <CustomSelect :options="options" label="Game Type" v-model:selected="gameTypeRef" />
        <CustomSelect :options="timeLimitOptions" label="Time Limit" v-model:selected="timeLimitRef" />
        <CustomSelect :options="dictionaryOptions" label="Dictionary Allowed" v-model:selected="useDictionaryRef" />
        <CustomSelect :options="groupSizeOptions" label="Number of Groups" v-model:selected="groupSizeRef" />
      </div>
      <button class="create__btn glow-hover" @click="createGame">
        Create Game
      </button>
    </div>
  </div>
</template>

<style scoped>
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

  box-shadow: 0 8px 25px rgba(0,0,0,0.25);
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
  box-shadow: 0 8px 20px rgba(65,105,169,0.25);
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

  box-shadow: 0 8px 25px rgba(0,0,0,0.2);
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