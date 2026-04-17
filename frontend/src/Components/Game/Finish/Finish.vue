<script lang='ts' setup>
import useWebsocketStore from '@/Components/Stores/websocket';
import type { GameUser } from '@/game_types';
import type { modifiers } from '@/types';
import { computed, ref } from 'vue';

type FinalData = {
	players: GameUser[],
	winner: GameUser,
	grid: (string | modifiers)[];
	groups?: number[][]
	partners?: Record<string, number>
}

const finalData = history.state.finalData as FinalData

const websocket = useWebsocketStore();

const wasGroup = ref(false);
// onMounted(() => {

// 	if (finalData.groups !== undefined) {
// 		wasGroup.value = true;
// 	}
// })


console.log(wasGroup.value)

const playerMap = computed(() => {
	var map = new Map();
	finalData.players.forEach(player => {
		map.set(player.userID, player)
	})
	return map
})

const leaderIDs = computed(() => {
	var leaders = finalData.groups?.flatMap(group => group[0])
	return leaders?.filter(a => a !== undefined)
})
console.log(leaderIDs.value)



function getPartner(leader: number) {
	if (finalData.partners === undefined) {
		return ''
	}

	var resp = playerMap.value.get(finalData.partners[leader.toString()])
	if (resp === undefined) {
		return ''
	}
	return ` & ${resp.userName}`;
}

</script>


<template>
	<div class="content">
		<div class="leaderboard">
			<div class="groups" v-if="finalData.groups">
				<div class="player" v-for="(leader, ind) in leaderIDs">

					<div>{{ ind + 1 }}.</div>
					<div><span v-if="leader == finalData.winner.userID"><i class="pi pi-crown"></i></span> {{
						playerMap.get(leader)?.userName }}{{ finalData.partners && getPartner(leader) }}
					</div>
					<div>{{ playerMap.get(leader)?.points }}</div>
				</div>
			</div>
			<div class="player" v-for="(player, ind) in finalData.players" v-else>
				<div>{{ ind + 1 }}.</div>
				<div><span v-if="player.userID == finalData.winner.userID"><i class="pi pi-crown"></i></span> {{
					player.userName }}</div>
				<div>{{ player.points }}</div>

			</div>
		</div>
	</div>
	<div class="actions">
		<RouterLink :to="{ 'name': 'home' }">
			<Button>Home</Button>
		</RouterLink>

	</div>
</template>


<style lang='css' scoped>
.content {
	color: white;
}

.leaderboard {
	display: flex;
	flex-direction: column;
	gap: 1rem;
}

.player {
	display: flex;
	gap: 1rem;
}
</style>