<script lang="ts" setup>

import api from '@/api';
import { onMounted, ref, watch } from 'vue';
import { resolveComponent } from 'vue';
import router from '../../router';
import useUserStore from '../Stores/user';

const userStore = useUserStore();
const user = ref();
const friends = ref<any>([]);

async function getFriends() {
	const res = await api.get('/friends/myFriends', {
		params: {
			limit: 5
		}
	})
	friends.value = res.data;
}

watch(() => userStore.userData, () => {
	user.value = userStore.userData
})
onMounted(() => {
	getFriends();
})

function logout() {
	localStorage.removeItem('token');
	localStorage.removeItem('refresh_token');
	localStorage.removeItem('userID');
	router.push({ name: 'login' });
}

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
				<h2>{{ user.rank }}</h2>
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
				<h3>Total Games: {{ user.wins + user.loses }}</h3>
				<h3>Best Score: {{ user.bestScore }}</h3>
			</div>
		</div>

		<h1>Friends</h1>
		<RouterLink to="/friends" class="friendsLink">
			<div class="friendsCard">
				<div class="friendsHeader">
					<h2>Friends</h2>
				</div>

				<ul class="friendsList">
					<li v-for="(user, i) in friends" :key="user.userID" class="friend">
						<div class="friendLeft">
							<span class="friendNumber"> {{ Number(i) + 1 }}</span>
							<i class="pi pi-user"></i>
							<span class="friendName"> {{ user.userName }}</span>
						</div>
					</li>
				</ul>
			</div>
		</RouterLink>

		<div class="logoutSection">
			<button class="logoutButton" @click="logout()">Logout</button>
		</div>

		<h2>Member Since: {{ new Date(user.userCreatedAt).toLocaleDateString() }}</h2>

	</div>

	<div v-else class="loading">
		<h1 class="loading__title">Loading...</h1>
	</div>
</template>


<style lang="css">
body {
	background-color: #0d1b2a;
}

.loading {

	display: flex;
	height: 100%;
	justify-content: center;
	align-items: center;
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

.profile>h1,
.profile>h2 {
	grid-column: 1 / -1;
	text-align: center;
	color: #e0e0ff;
}

.winsLoses,
.rankScore,
.stats {
	display: contents;
}

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

.profile i {
	margin-bottom: 8px;
	color: #80c0ff;
	width: 100%;
	;
}

.profile h2 {
	margin: 0;
	font-size: 24px;
	margin-bottom: 10px;
	color: #ffffff;
}

.profile p {
	margin-top: 5px;
	color: #dbe6ff;
}

.logoutSection {
	grid-column: 1 / -1;
	margin-top: 2rem;
	width: 100%;
	display: flex;
	justify-content: center;
	padding-bottom: 2rem;
}

.logoutButton {
	background-color: rgb(183, 1, 1);
	border: 2px solid rgb(140, 0, 0);
	color: white;
	padding: 0.5rem 3rem;
	border-radius: 10px;
	cursor: pointer;
}

.friendsLink {
	grid-column: 1 / -1;
	text-decoration: none;
}

.friendsCard {
	background: linear-gradient(135deg, #2a4d8f, #4169a9);
	border-radius: 14px;
	padding: 1.5rem;
	cursor: pointer;
	transition: 0.25s;

	box-shadow:
		0 8px 20px rgba(0, 0, 0, 0.3),
		0 0 15px rgba(77, 148, 255, 0.2);
}

.friendsHeader {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 1rem;
}

.friendsHeader h2 {
	margin: 0;
	color: white;
}

.friendsList {
	list-style: none;
	padding: 0;
	margin: 0;

	display: flex;
	flex-direction: column;
	gap: 0.6rem;
}

.friend {
	display: flex;
	align-items: center;
	justify-content: space-between;

	padding: 0.6rem 0.8rem;
	border-radius: 10px;

	background: rgba(255, 255, 255, 0.08);
	transition: 0.2s;
}

.friend:hover {
	background: rgba(255, 255, 255, 0.15);
}

.friendLeft {
	display: flex;
	align-items: center;
	gap: 0.6rem;
}

.friendNumber {
	font-size: 0.85rem;
	color: #a9c7ff;
	width: 20px;
}

.friend i {
	color: #80c0ff;
}

.friendName {
	color: white;
	font-weight: 500;
}
</style>