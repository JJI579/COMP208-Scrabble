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
	</div>
	<div class="actions">
		<RouterLink :to="{ 'name': 'create' }">
			<button>
				Create new Game
			</button>
		</RouterLink>
		<RouterLink :to="{ 'name': 'join' }">
			<button>
				Join a new Game
			</button>
		</RouterLink>

	</div>
</template>


<style lang='css' scoped></style>