<script lang="ts" setup>
import api from '@/api';
import { onMounted, ref, watch } from 'vue';

const currentUser = ref<any>(null);
const users = ref<any>([]);
const selectedSort = ref("totalScore");
const searchUser = ref("");

function userSearch() {
	getLeaderboard();
}

async function getCurrentUser() {
	const res = await api.get('/users/@me');
	console.log(res.data);
	currentUser.value = res.data;
}

async function getLeaderboard() {
	const res = await api.get('/users/leaderboard', { params: { sort_by: selectedSort.value, search: searchUser.value } });
	console.log(res.data);
	users.value = res.data;
}
onMounted(() => {
	getLeaderboard();
	getCurrentUser();
});

watch(searchUser, () => {
	userSearch();
})

</script>



<template>
	<div class="contentMe">
		<h1>LeaderBoard</h1>

		<div class="search">

			<div class="searchUser">
				<input type="text" placeholder="Enter username..." v-model="searchUser">
			</div>

			<div class="filterUsers">
				<select v-model="selectedSort" @change="getLeaderboard" class="select">
					<option value="totalScore">Filter by Score</option>
					<option value="games">Filter by the Number of Games</option>
					<option value="bestScore">Filter by Best Score</option>
					<option value="wins">Filter by Wins</option>
					<!-- <option value="Rate">Filter by the Win Rate</option> -->
				</select>
			</div>
		</div>


		<div class="leaderboard">
			<table>
				<tr>
					<th>Rank</th>
					<th>Username</th>
					<th>Score</th>
					<th>Games Played</th>
					<th>Best Score</th>
					<th>Wins</th>
				</tr>
				<tr v-for="(user, i) in users" :key="user.userID"
					:class="{ me: currentUser && user.userID === currentUser.userID }">

					<!-- RANK COLUMN -->
					<td class="rank-cell">

						<!-- TOP 3 MEDALS -->
						<span v-if="i === 0" class="medal gold">🥇</span>
						<span v-else-if="i === 1" class="medal silver">🥈</span>
						<span v-else-if="i === 2" class="medal bronze">🥉</span>
						<span v-else>{{ i + 1 }}</span>

					</td>

					<!-- USERNAME -->
					<td>
						{{ user.userName }}

						<span
							v-if="currentUser && user.userID === currentUser.userID"
							class="you-badge">
							YOU
						</span>
					</td>

					<td>{{ user.totalScore }}</td>
					<td>{{ user.wins + user.loses }}</td>
					<td>{{ user.bestScore }}</td>
					<td>{{ user.wins }}</td>

				</tr>
			</table>
		</div>
	</div>

	<!-- Contains leaderboards between you and your friends of how many points youve successfully collected overtime -->
</template>


<style lang="css" scoped>

/* PAGE WRAPPER */
.contentMe {
	display: flex;
	flex-direction: column;
	gap: 1.5rem;
	width: 100%;
	color: #fff;
	padding: 1rem;
	box-sizing: border-box;
}

/* TITLE */
h1 {
	font-size: 2.5rem;
	font-weight: 700;
	text-align: center;
	color: #ffffff;
	text-shadow: 0 0 12px rgba(77, 148, 255, 0.7);
	margin: 0;
}

/* SEARCH + FILTER ROW */
.search {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 1rem;
	flex-wrap: wrap;
	width: 100%;
	max-width: 1100px;
	margin: 0 auto;
}

.searchUser {
	flex: 1;
	min-width: 250px;
}

/* SEARCH INPUT */
.searchUser input {
	width: 100%;
	padding: 0.75rem 1rem;
	border-radius: 12px;
	border: 1px solid rgba(255, 255, 255, 0.2);
	background: rgba(255, 255, 255, 0.78);
	color: #000;
	font-size: 1rem;
	outline: none;
	backdrop-filter: blur(8px);
	transition: 0.2s;
}

.searchUser input:focus {
	border-color: #4d94ff;
	box-shadow: 0 0 12px rgba(77, 148, 255, 0.4);
}

.searchUser input::placeholder {
	color: rgba(0, 0, 0, 0.65);
}

/* FILTER */
.filterUsers select {
	padding: 0.75rem 1rem;
	border-radius: 12px;
	border: 1px solid rgba(255, 255, 255, 0.2);
	background: rgba(255, 255, 255, 0.78);
	color: #000;
	font-size: 1rem;
	cursor: pointer;
	outline: none;
	backdrop-filter: blur(8px);
	transition: 0.2s;
}

.filterUsers select:hover {
	box-shadow: 0 0 10px rgba(77, 148, 255, 0.35);
}

/* TABLE CONTAINER */
.leaderboard {
	width: 100%;
	max-width: 1100px;
	margin: 0 auto;
	background: rgba(255, 255, 255, 0.1);
	backdrop-filter: blur(14px);
	border-radius: 18px;
	padding: 1rem;
	box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
	overflow-x: auto;
}

/* TABLE */
table {
	width: 100%;
	border-collapse: collapse;
	min-width: 700px;
}

/* HEADER */
th {
	padding: 1rem 0.8rem;
	text-align: left;
	font-size: 0.95rem;
	font-weight: 700;
	color: #a9c9ff;
	border-bottom: 2px solid rgba(255, 255, 255, 0.15);
	letter-spacing: 0.4px;
}

/* CELLS */
td {
	padding: 0.95rem 0.8rem;
	color: #ffffff;
	font-size: 0.95rem;
	border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

/* ROWS */
tr {
	transition: 0.25s ease;
}

/* STRIPES */
tr:nth-child(even) {
	background: rgba(255, 255, 255, 0.04);
}

/* HOVER */
tr:hover {
	background: rgba(77, 148, 255, 0.18);
	transform: scale(1.005);
}

/* CURRENT USER ROW */
.me {
	background: linear-gradient(
		90deg,
		rgba(255, 60, 60, 0.45),
		rgba(255, 60, 60, 0.15)
	) !important;
	border-left: 5px solid #ff2d2d;
	font-weight: 700;
	box-shadow:
		inset 0 0 18px rgba(255, 60, 60, 0.45),
		0 0 12px rgba(255, 60, 60, 0.35);
}

/* KEEP RED ON HOVER TOO */
.me:hover {
	background: linear-gradient(
		90deg,
		rgba(255, 60, 60, 0.55),
		rgba(255, 60, 60, 0.2)
	) !important;
}



/* YOU BADGE */
.you-badge {
	margin-left: 0.6rem;
	padding: 0.22rem 0.6rem;
	border-radius: 999px;
	background: #ff2d2d;
	color: white;
	font-size: 0.72rem;
	font-weight: 800;
	letter-spacing: 0.8px;
	box-shadow: 0 0 12px rgba(255, 45, 45, 0.55);
	vertical-align: middle;
}

/* RANK CELL */
.rank-cell,
th:first-child,
td:first-child {
	text-align: center;
	width: 70px;
}

/* MEDALS */
.medal {
	display: inline-block;
	position: relative;
	font-size: 1.6rem;
	cursor: default;
	transition: transform 0.25s ease;
	overflow: hidden;
	border-radius: 50%;
}

/* MEDAL HOVER */
.medal:hover {
	transform: scale(1.18) rotate(-6deg);
}

/* SHINE EFFECT */
.medal::after {
	content: "";
	position: absolute;
	top: -40%;
	left: -120%;
	width: 55%;
	height: 190%;
	background: linear-gradient(
		120deg,
		rgba(255,255,255,0) 0%,
		rgba(255,255,255,0.15) 35%,
		rgba(255,255,255,0.9) 50%,
		rgba(255,255,255,0.15) 65%,
		rgba(255,255,255,0) 100%
	);
	transform: rotate(25deg);
	filter: blur(1px);
	opacity: 0;
}

.medal:hover::after {
	opacity: 1;
	animation: medalShine 0.75s ease forwards;
}
@keyframes medalShine {
	from {
		left: -120%;
	}
	to {
		left: 140%;
	}
}
/* GLOW COLORS */
.gold {
	filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.7));
}

.silver {
	filter: drop-shadow(0 0 8px rgba(220, 220, 220, 0.7));
}

.bronze {
	filter: drop-shadow(0 0 8px rgba(205, 127, 50, 0.7));
}

/* SCROLLBAR */
.leaderboard::-webkit-scrollbar {
	height: 8px;
}

.leaderboard::-webkit-scrollbar-thumb {
	background: rgba(255, 255, 255, 0.18);
	border-radius: 999px;
}

/* MOBILE */
@media (max-width: 768px) {
	h1 {
		font-size: 2rem;
	}

	.search {
		flex-direction: column;
		align-items: stretch;
	}

	.filterUsers select,
	.searchUser input {
		width: 100%;
	}

	table {
		min-width: 620px;
	}

	td, th {
		font-size: 0.88rem;
		padding: 0.8rem 0.6rem;
	}
}

</style>