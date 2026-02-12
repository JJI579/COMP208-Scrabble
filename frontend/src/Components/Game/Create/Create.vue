<script lang="ts" setup>
import { ref } from 'vue';
import SegmentedControl from '../SegmentedControl/SegmentedControl.vue';
import CustomSelect from '../CustomSelect/CustomSelect.vue';
import api from '@/api';


const gameTypeRef = ref("normal");
const options = [['normal', "Normal"], ['team', "Team"], ["bot", "Bot"]]

const timeLimitRef = ref();
const timeLimitOptions = [["none", "None"], ["45", "45 Minutes"], ["1", "1 Hour"], ["2", "2 Hours"]]

const useDictionaryRef = ref("false");
const dictionaryOptions = [["true", "Yes"], ["false", "No"]]

const groupSizeRef = ref();
const groupSizeOptions = [["2", "2"], ["3", "3"]]
// game_type: GAME_TYPE
// group_size: Optional[int]
// time_limit: str | bool
// dictionary: bool # whether dictionary is allowed

async function createGame() {
	// TODO: implement.
	await api.post("/game/create", {
		game_type: gameTypeRef.value,
		group_size: groupSizeRef.value,
		time_limit: timeLimitRef.value,
		dictionary: useDictionaryRef.value
	})
}


</script>



<template>
	<div class="options">
		<CustomSelect :options="options" :label="'Game Type'" v-model:selected="gameTypeRef" />
		<CustomSelect :options="timeLimitOptions" :label="'Time Limit'" v-model:selected="timeLimitRef" />
		<CustomSelect :options="dictionaryOptions" :label="'Dictionary Allowed'" v-model:selected="useDictionaryRef" />
		<CustomSelect :options="groupSizeOptions" :label="'Group Size'" v-model:selected="groupSizeRef" />
	</div>
	<button @click="createGame">Create Game</button>
</template>


<style lang="css" scoped>
.options {
	display: flex;
	flex-direction: column;
	gap: 1rem;
	width: 100%;
	margin-bottom: 1rem;
}

.opt {
	/* display: flex; */
}
</style>