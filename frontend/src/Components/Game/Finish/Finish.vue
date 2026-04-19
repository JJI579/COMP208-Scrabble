<script lang="ts" setup>
import useWebsocketStore from '@/Components/Stores/websocket';
import type { GameUser } from '@/game_types';
import type { modifiers } from '@/types';
import { computed } from 'vue';

type FinalData = {
	players: GameUser[],
	winner: GameUser,
	grid: (string | modifiers)[];
	groups?: number[][]
	partners?: Record<string, number>
}

const finalData = history.state.finalData as FinalData;

useWebsocketStore();

const playerMap = computed(() => {
	const map = new Map();
	finalData.players.forEach(player => {
		map.set(player.userID, player);
	});
	return map;
});

const leaderIDs = computed(() => {
	return finalData.groups?.flatMap(group => group[0]);
});

function getPartner(leader: number | undefined) {
	if (leader === undefined) return '';
	if (!finalData.partners) return '';
	const partner = playerMap.value.get(finalData.partners[leader]);
	if (!partner) return '';

	return ` & ${partner.userName}`;
}
</script>

<template>
	<div class="finish-page">

		<div class="bg-aurora"></div>
		<div class="bg-orb orb1"></div>
		<div class="bg-orb orb2"></div>

		<div class="finish-card">

			<div class="winner-box">
				<div class="winner-crown">👑</div>
				<h1>Game Finished</h1>
				<p class="winner-name">{{ finalData.winner.userName }} Wins!</p>
			</div>

			<div class="leaderboard">
				<div class="leaderboard-title">
					🏆 Final Standings
				</div>

				<div class="board-header">
					<span>Rank</span>
					<span>Player</span>
					<span>Score</span>
				</div>
				<div v-if="finalData.groups">
					<div v-for="(player, ind) in finalData.players" :key="player.userID" class="board-row"
						:class="{ champion: player.userID === finalData.winner.userID }">
						<span class="rank">
							<span v-if="ind === 0">🥇</span>
							<span v-else-if="ind === 1">🥈</span>
							<span v-else-if="ind === 2">🥉</span>
							<span v-else>{{ ind + 1 }}</span>
						</span>

						<span>{{ player.userName }}</span>

						<span>{{ player.points }}</span>
					</div>
				</div>
				<div v-else>
					<div v-for="(player, ind) in finalData.players" :key="player.userID" class="board-row"
						:class="{ champion: player.userID === finalData.winner.userID }">
						<span class="rank">
							<span v-if="ind === 0">🥇</span>
							<span v-else-if="ind === 1">🥈</span>
							<span v-else-if="ind === 2">🥉</span>
							<span v-else>{{ ind + 1 }}</span>
						</span>

						<span>{{ player.userName }}</span>
						<span>{{ player.points }}</span>
					</div>
				</div>
			</div>

			<RouterLink :to="{ name: 'home' }" class="home-link">
				<button class="home-btn">
					<i class="pi pi-home"></i>
					Back Home
				</button>
			</RouterLink>

		</div>
	</div>
</template>

<style lang="css" scoped>
.finish-page {
	min-height: 100vh;
	background: linear-gradient(180deg, #0d1b2a, #1b263b);
	display: flex;
	justify-content: center;
	align-items: center;
	padding: 2rem;
	position: relative;
	overflow: hidden;
}


.bg-aurora {
	position: absolute;
	inset: 0;
	background:
		radial-gradient(circle at 20% 20%, rgba(77, 148, 255, .18), transparent 30%),
		radial-gradient(circle at 80% 30%, rgba(140, 80, 255, .16), transparent 30%),
		radial-gradient(circle at 40% 80%, rgba(0, 255, 180, .12), transparent 30%);
}

.bg-orb {
	position: absolute;
	border-radius: 50%;
	filter: blur(80px);
	opacity: .25;
}

.orb1 {
	width: 220px;
	height: 220px;
	background: #4d94ff;
	top: 8%;
	left: 10%;
}

.orb2 {
	width: 260px;
	height: 260px;
	background: #7d5cff;
	bottom: 10%;
	right: 10%;
}

.finish-card {
	position: relative;
	z-index: 2;
	width: min(800px, 100%);
	background: rgba(255, 255, 255, 0.14);
	backdrop-filter: blur(14px);
	border-radius: 24px;
	padding: 2rem;
	box-shadow: 0 20px 40px rgba(0, 0, 0, .35);
	color: white;
}

.winner-box {
	text-align: center;
	margin-bottom: 2rem;
}

.winner-crown {
	font-size: 3rem;
	margin-bottom: .4rem;
	animation: bounce 1.5s infinite alternate;
}

.winner-box h1 {
	margin: 0;
	font-size: 2.2rem;
	color: #4d94ff;
	text-shadow: 0 0 14px rgba(77, 148, 255, .45);
}

.winner-name {
	margin-top: .5rem;
	font-size: 1.5rem;
	font-weight: 700;
	color: #ffd86a;
}

@keyframes bounce {
	from {
		transform: translateY(0);
	}

	to {
		transform: translateY(-6px);
	}
}

.leaderboard {
	background: rgba(255, 255, 255, .08);
	border-radius: 18px;
	padding: 1.25rem;
}

.leaderboard-title {
	text-align: center;
	font-size: 1.5rem;
	font-weight: 800;
	margin-bottom: 1rem;
	color: #dbe7ff;
}

.board-header,
.board-row {
	display: grid;
	grid-template-columns: 80px 1fr 100px;
	align-items: center;
	gap: .5rem;
	padding: .8rem;
}

.board-header {
	font-weight: 700;
	color: #aecdff;
	border-bottom: 1px solid rgba(255, 255, 255, .15);
}

.board-row {
	border-bottom: 1px solid rgba(255, 255, 255, .08);
}

.board-row:last-child {
	border-bottom: none;
}

.rank {
	font-size: 1.2rem;
	font-weight: 700;
}

.champion {
	background: linear-gradient(90deg,
			rgba(255, 215, 0, .18),
			rgba(255, 215, 0, .05));
	border-left: 4px solid gold;
	border-radius: 10px;
}

.home-link {
	text-decoration: none;
}

.home-btn {
	margin-top: 1.5rem;
	width: 100%;
	padding: 1rem;
	border: none;
	border-radius: 16px;
	background: linear-gradient(135deg, #2a4d8f, #4169a9);
	color: white;
	font-size: 1.15rem;
	font-weight: 700;
	cursor: pointer;
	display: flex;
	justify-content: center;
	align-items: center;
	gap: .6rem;
	transition: .25s ease;
}

.home-btn:hover {
	transform: translateY(-3px) scale(1.02);
	box-shadow: 0 0 20px rgba(77, 148, 255, .45);
}

/* MOBILE */
@media (max-width: 700px) {
	.finish-card {
		padding: 1.2rem;
	}

	.board-header,
	.board-row {
		grid-template-columns: 60px 1fr 70px;
		font-size: .9rem;
	}

	.winner-box h1 {
		font-size: 1.8rem;
	}

	.winner-name {
		font-size: 1.2rem;
	}
}
</style>