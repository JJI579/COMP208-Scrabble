<script lang='ts' setup>
import type { GameUser } from '@/game_types';
import type { modifiers } from '@/types';
import type { PropType } from 'vue';

type FinalData = {
	players: GameUser[],
	winner: GameUser,
	grid: (string | modifiers)[];
}

const finalData = history.state.finalData as FinalData
</script>


<template>
	<div class="content">
		CONTENT HERE
		should be variable with all details about the previous Game
		{{ finalData }}


		<div class="leaderboard">
			<div class="player" v-for="(player, ind) in finalData.players">
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