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
					<td> {{ Number(i) + 1 }}</td>
					<td>
						<span v-if="currentUser && user.userID === currentUser.userID"> (You)</span>
						{{ user.userName }}
					</td>
					<td> {{ user.totalScore }}</td>
					<td> {{ user.wins + user.loses }}</td>
					<td> {{ user.bestScore }}</td>
					<td> {{ user.wins }}</td>
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
}

/* TITLE */
h1 {
	font-size: 2.5rem;
	font-weight: 700;
	text-align: center;
	color: #ffffff;
	text-shadow: 0 0 12px rgba(77, 148, 255, 0.7);
}

/* ROW 2: SEARCH + FILTER */
.search {
	display: flex;
	justify-content: space-between;
	width: 100%;
	max-width: 1100px;
	margin-left: auto;
	margin-right: auto;
	align-items: center;
	gap: 1rem;
	flex-wrap: wrap;

}

.searchUser {
	flex: 1;
}

/* SEARCH */
.searchUser input {
	padding: 0.7rem 1rem;
	border-radius: 10px;
	border: 1px solid rgba(255, 255, 255, 0.2);
	background: rgba(255, 255, 255, 0.1);
	color: #fff;
	min-width: 220px;
	width: 100%;
	backdrop-filter: blur(6px);
}

.searchUser input::placeholder {
	color: rgba(255, 255, 255, 0.6);
}

/* FILTER */
.filterUsers select {
	padding: 0.7rem 1rem;
	border-radius: 10px;
	border: 1px solid rgba(255, 255, 255, 0.2);
	background: rgba(255, 255, 255, 0.1);
	color: #fff;
	cursor: pointer;
	backdrop-filter: blur(6px);
}

/* TABLE CONTAINER */
.leaderboard {
	width: 100%;
	max-width: 1100px;
	margin-left: auto;
	margin-right: auto;
	background: rgba(255, 255, 255, 0.12);
	backdrop-filter: blur(12px);
	border-radius: 16px;
	padding: 1rem;
	box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
	overflow-x: auto;
}

/* TABLE */
table {
	width: 100%;
	border-collapse: collapse;
	min-width: 600px;
}

/* HEADER */
th {
	color: #a9c9ff;
	font-weight: 600;
	padding: 0.8rem;
	border-bottom: 2px solid rgba(255, 255, 255, 0.2);
	text-align: left;
}

/* CELLS */
td {
	padding: 0.8rem;
	color: #ffffff;
}

/* ROWS */
tr {
	transition: 0.2s;
}

/* STRIPES */
tr:nth-child(even) {
	background: rgba(255, 255, 255, 0.05);
}

/* HOVER */
tr:hover {
	background: rgba(77, 148, 255, 0.2);
}

/* CURRENT USER */
.me {
	background: rgba(77, 148, 255, 0.2);
	border-left: 4px solid #4d94ff;
	font-weight: 600;
}

</style>