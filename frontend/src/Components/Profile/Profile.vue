<script lang="ts" setup>

import api from '@/api';
import { onMounted, ref } from 'vue';
import { resolveComponent } from 'vue';

const user = ref<any>(null);

async function getUser() {
	const res = await api.get('/users/@me');
	console.log(res.data);
	user.value = res.data;
}

onMounted(() => {
	getUser();
})

function calculateWinRate() {
	if (!user.value) {
		return 0;
	}
	const wins = user.value.wins;
	const totalGames = user.value.wins + user.value.loses;
	if (totalGames === 0) {
		return 0;
	}
	const winRate = (wins / totalGames) * 100;
	return winRate.toFixed(2);
}

function calculateAverageScore() {
	if (!user.value) {
		return 0;
	}
	const totalScore = user.value.totalScore;
	const totalGames = user.value.wins + user.value.loses;
	if (totalGames === 0) {
		return 0;
	}
	const averageScore = totalScore / totalGames;
	return averageScore.toFixed(2);
}

</script>


<template>

	<div class="profile" v-if="user">

		<div class="userName-row">
			<div class="userName">
				<i class="pi pi-user" style="font-size: 3rem"></i>
				<h2>
					{{ user.userName }}
				</h2>
				<!-- <p>Username</p> -->
			</div>
		</div>

		<div class="winsLoses">
			<div class="wins">
				<i class="pi pi-trophy" style="font-size: 2rem"></i>
				<h2>
					{{ user.wins }}
				</h2>
				<p>Wins</p>
			</div>

			<div class="loses">
				<i class="pi pi-times" style="font-size: 2rem"></i>
				<h2>
					{{ user.loses }}
				</h2>
				<p>Loses</p>
			</div>
		</div>

		<div class="rankScore">
			<div class="rank">
				<h2>We'll have the rank here</h2>
				<p>Rank</p>
			</div>

			<div class="score">
				<h2>
					{{ user.totalScore }}
				</h2>
				<p>Total Score</p>
			</div>
		</div>

		<h1>Statistics</h1>
		<div class="stats">
			<div class="statsPart1">
				<h3>Win rate: {{ calculateWinRate() }}% </h3>
				<h3>Average Score: {{ calculateAverageScore() }}</h3>
			</div>

			<div class="statsPart2">
				<h3>Total Games: {{  user.wins + user.loses }}</h3>
				<h3>Best Score: {{ user.bestScore }}</h3>
			</div>
		</div>

		<h1>Friends</h1>
		<p>I am going to add a box with all the friends and it will have a link to go to the friends page</p>

		<h2>Member Since: {{ new Date(user.userCreatedAt).toLocaleDateString() }}</h2>

	</div>

	<!-- Self explanatory via the name... -->
</template>


<style lang="css">

body {
	background: #0d1b2a;
}

.profile {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 1.5rem;
	margin-top: 2rem;
	width: 100%;
	max-width: 800px;
	margin-left: auto;
	margin-right: auto;
}

/* Username row (full width) */
.userName-row {
	grid-column: 1 / -1;
	display: flex;
	justify-content: center;
}

.userName {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	text-align: center;
}

/* Headings full width */
.profile > h1,
.profile > h2 {
	grid-column: 1 / -1;
	text-align: center;
	color: #e0e0ff;
}

/* Break parent containers */
.winsLoses,
.rankScore,
.stats {
	display: contents;
}

/* BOXES — brighter for contrast */
.wins,
.loses,
.rank,
.score,
.statsPart1,
.statsPart2 {
	background: linear-gradient(135deg, #2a4d8f, #4169a9); 
	border-radius: 12px;
	padding: 1.5rem;
	box-shadow:
		0 8px 20px rgba(0, 0, 0, 0.3),
		0 0 15px rgba(77, 148, 255, 0.25);
	color: #ffffff;
}

/* Centered boxes */
.wins,
.loses,
.rank,
.score {
	display: flex;
	flex-direction: column;
	align-items: center;
	text-align: center;
	justify-content: center;
}

/* Stats boxes */
.statsPart1,
.statsPart2 {
	display: flex;
	flex-direction: column;
	gap: 0.2rem;
}

.statsPart1 h3,
.statsPart2 h3 {
	margin: 10px;
}

/* Typography */
.profile i {
	margin-bottom: 8px;
	color: #80c0ff; /* softer glow */
}

.profile h2 {
	margin: 0;
	font-size: 24px;
	margin-bottom: 10px;
	color: #ffffff;
}

.profile p {
	margin-top: 5px;
	color: #dbe6ff; /* brighter for readability */
}

</style>