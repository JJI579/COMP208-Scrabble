<script lang="ts" setup>

import { ref, computed, onMounted } from 'vue';
import api from '@/api';
import router from '@/router';
import type { Item } from '@/types';
const streak = ref(1);


const currentUser = ref<any>(null);

async function getCurrentUser() {
	const res = await api.get('/users/@me');
	console.log(res.data);
	currentUser.value = res.data;
}
const users = ref<any>([]);

const flameLevel = computed(() => {
	if (streak.value >= 5) return 'legend';
	if (streak.value >= 3) return 'hot';
	if (streak.value >= 1) return 'warm';
	return 'idle';
});

const userRank = computed(() => {
	if (!currentUser.value || !users.value.length) return null;
	const index = users.value.findIndex(
		u => u.userID === currentUser.value.userID
	);
	return index === -1 ? null : index + 1;
});

const shopPreview = ref<Item[]>([
	{
		itemID: 1,
		name: "Gradient Name",
		xpRequired: 300,
	},
	{
		itemID: 2,
		name: "Bronze Border",
		xpRequired: 600,
	},
	{
		itemID: 3,
		name: "Silver Border",
		xpRequired: 900,
	}
]);

async function getLeaderboard() {
	const res = await api.get('/users/leaderboard', { params: { sort_by: "totalScore", limit: 5 } });
	console.log(res.data);
	users.value = res.data;
}

onMounted(() => {
	getLeaderboard();
	getCurrentUser();
})


const score = ref(0);

function createPage(type: string, groupSize: number) {
	router.push({
		name: 'create',
		query: {
			type,
			groupSize: String(groupSize)
		}
	});
}

onMounted(async () => {
	const { data } = await api.get("/users/@me")

	console.log("API RESPONSE:", data)
	score.value = data.totalScore
})

</script>


<template>

	<div class="dashboard">

		<div class="bg-aurora"></div>
		<div class="bg-orb orb1"></div>
		<div class="bg-orb orb2"></div>
		<div class="bg-orb orb3"></div>


		<main class="main">

			<div class="streak-box card-glass">
				<span class="flame" :class="flameLevel">🔥</span>
				<p class="streak-text">Weekly Streak</p>
				<span class="streak-number" :class="{ active: streak > 0 }">{{ streak }}</span>
			</div>

			<h1 class="play-text glow-text">Play a Game</h1>
			<div class="play-options">
				<button class="play-btn card-glass glow-hover card-hover" @click="createPage('BOT', 2)">
					<i class="pi pi-android"></i>
					<span>Solo Vs Bot</span>
				</button>

				<button class="play-btn card-glass glow-hover card-hover" @click="createPage('NORMAL', 2)">
					<i class="pi pi-users"></i>
					<span>Play Vs Friends</span>
				</button>

				<button class="play-btn card-glass glow-hover card-hover" @click="createPage('GROUP', 4)">
					<i class="pi pi-sitemap"></i>
					<span>Team Mode</span>
				</button>
			</div>

			<RouterLink to="/leaderboard" class="leaderboard-link">
				<button class="leaderboard card-glass hover-shadow card-hover">
					<h2 class="glow-text">🏆 Lifetime Leaderboard</h2>

					<div class="leaderboard-header">
						<span>Rank</span>
						<span>Player</span>
						<span>Score</span>
					</div>

					<!-- TOP 3 -->
					<ul class="leaderboard-list">
						<li
							v-for="(user, i) in users.slice(0,3)"
							:key="user.userID"
							class="leaderboard-item">

							<!-- RANK -->
							<span class="rank-wrap">
								<span v-if="i === 0" class="medal gold">🥇</span>
								<span v-else-if="i === 1" class="medal silver">🥈</span>
								<span v-else class="medal bronze">🥉</span>
							</span>

							<span>{{ user.userName }}</span>
							<span>{{ user.totalScore }}</span>
						</li>

						<!-- CURRENT USER ROW -->
						<li class="leaderboard-item-self">
							<span>{{ userRank ?? '-' }}</span>
							<span>{{ currentUser?.userName || 'You' }}</span>
							<span>{{ score }}</span>
						</li>
					</ul>
				</button>
			</RouterLink>

			<div class="score-box card-glass hover-shadow">
				<h2 class="glow-text">Lifetime Score</h2>
				<p class="score-number">{{ score }}</p>
			</div>

			<RouterLink to="/shop" class="score-shop card-glass hover-shadow">
				<h2 class="glow-text">🛒 Shop</h2>
				<p>Unlock exclusive rewards!</p>

				<div class="shop-preview">
					<span v-for="item in shopPreview" :key="item.itemID">
						{{ item.name }} • {{ item.xpRequired }} XP
					</span>
				</div>
			</RouterLink>
		</main>
	</div>

	<footer class="footer">
		&copy; 2026 Scrabble Teams. All rights reserved.
	</footer>
</template>


<style lang="css" scoped>

.shop-preview {
	margin-top: 0.8rem;
	display: flex;
	flex-direction: column;
	gap: 0.25rem;
	font-size: 0.85rem;
	opacity: 0.8;
}

.shop-preview span {
	padding: 0.2rem 0.4rem;
	border-radius: 6px;
	background: rgba(255,255,255,0.08);
}
.dashboard {
	position: relative;
	display: flex;
	flex-direction: column;
	gap: 1rem;
	background: linear-gradient(180deg, #0d1b2a, #1b263b);
	padding: 2rem;
	padding-bottom: 6rem;
	margin: 0;
	box-sizing: border-box;
	margin-left: calc(-50vw + 50%);
	min-height: 100vh;
	width: 100vw;
	overflow-x: hidden;
}

.main {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 2rem;
	min-height: calc(100vh - 4rem);
}

/* GENERIC CARD EFFECTS */
.card-hover {
	transition: all 0.3s ease;
}

.card-hover:hover {
	transform: translateY(-6px) scale(1.03);
	box-shadow:
		0 15px 30px rgba(0, 0, 0, 0.25),
		0 0 25px rgba(77, 148, 255, 0.35);
}

.card-glass {
	background: rgba(255, 255, 255, 0.18);
	backdrop-filter: blur(12px);
	border-radius: 20px;
	padding: 1.5rem 2rem;
	transition: all 0.3s ease;
	box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.hover-shadow:hover {
	transform: translateY(-5px) scale(1.02);
	box-shadow: 0 15px 25px rgba(0, 0, 0, 0.25);
}

.glow-text {
	color: #4d94ff;
	text-shadow: 0 0 12px rgba(77, 148, 255, 0.45);
}

/* STREAK */
.streak-box {
	display: grid;
	grid-template-columns: auto 1fr auto;
	align-items: center;
	gap: 1rem;
	background: linear-gradient(135deg, #ffe0e0, #ffd6d6);
}

.flame {
	font-size: 2rem;
	animation: flame-bounce 1s infinite alternate;
}

.flame.idle {
	opacity: 0.35;
}

.flame.warm {
	text-shadow: 0 0 8px #ffae42, 0 0 16px #ff8c00;
}

.flame.hot {
	text-shadow: 0 0 12px #ff5500, 0 0 25px #ff2a00;
	transform: scale(1.2);
}

.flame.legend {
	text-shadow:
		0 0 15px #ff0000,
		0 0 35px #ff4d00,
		0 0 60px #ffaa00;
	transform: scale(1.4);
}

@keyframes flame-bounce {
	from { transform: translateY(0); }
	to { transform: translateY(-5px); }
}

.streak-text {
	font-size: 1.6rem;
	font-weight: 600;
	color: #111;
	text-align: center;
}

.streak-number {
	font-size: 2rem;
	font-weight: 800;
	color: #ff5d5d;
	text-shadow: 0 0 12px rgba(255, 90, 90, 0.7);
}

/* PLAY */
.play-text {
	text-align: center;
	font-size: 2.2rem;
}

.play-options {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
	gap: 2rem;
}

.play-btn {
	padding: 3rem 1rem;
	font-size: 1.35rem;
	font-weight: 700;
	border-radius: 20px;
	border: none;
	cursor: pointer;
	background: linear-gradient(135deg, #2a4d8f, #4169a9);
	color: white;
	transition: 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 0.75rem;
	flex-direction: column;
}

.play-btn:hover {
	transform: scale(1.05);
	box-shadow: 0 0 20px rgba(77, 148, 255, 0.65);
}

.play-btn:active {
	transform: scale(0.98);
}

/* DASHBOARD LEADERBOARD BUTTON */
.leaderboard-link {
	text-decoration: none;
	color: inherit;
}

.leaderboard {
	background: linear-gradient(135deg, #1e3a5f, #2a4d8f);
	padding: 1.5rem;
	border-radius: 16px;
	width: 100%;
	border: none;
	cursor: pointer;
	color: #fff;
	text-align: left;
}

.leaderboard:hover {
	background: linear-gradient(135deg, #294c7a, #3963b5);
}

.leaderboard h2 {
	margin: 0 0 1rem 0;
	text-align: center;
	font-size: 2rem;
}

/* LEADERBOARD GRID */
.leaderboard-header,
.leaderboard-item,
.leaderboard-item-self {
	display: grid;
	grid-template-columns: 80px 1fr 100px;
	align-items: center;
	column-gap: 0.5rem;
}

.leaderboard-header {
	font-weight: 700;
	color: #dbe7ff;
	padding-bottom: 0.5rem;
	border-bottom: 1px solid rgba(255,255,255,0.15);
	margin-bottom: 0.3rem;
}

.leaderboard-list {
	list-style: none;
	padding: 0;
	margin: 0;
}

.leaderboard-item,
.leaderboard-item-self {
	padding: 0.7rem 0;
	border-bottom: 1px solid rgba(255,255,255,0.08);
}

.leaderboard-item:last-child {
	border-bottom: none;
}

/* USER ROW */
.leaderboard-item-self {
	background: linear-gradient(
		90deg,
		rgba(255, 60, 60, 0.45),
		rgba(255, 60, 60, 0.15)
	);
	border-left: 5px solid #ff2d2d;
	padding-left: 0.6rem;
	border-radius: 10px;
	margin-top: 0.45rem;
	font-weight: 600;
	box-shadow:
		inset 0 0 18px rgba(255,60,60,0.45),
		0 0 12px rgba(255,60,60,0.28);
}

/* RANK */
.rank-wrap {
	display: flex;
	justify-content: center;
	align-items: center;
}

/* MEDALS */
.medal {
	display: inline-block;
	position: relative;
	font-size: 1.55rem;
	cursor: default;
	transition: transform 0.25s ease;
	overflow: hidden;
	border-radius: 50%;
}

.medal:hover {
	transform: scale(1.18) rotate(-6deg);
}

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
		rgba(255,255,255,0.95) 50%,
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
	from { left: -120%; }
	to { left: 140%; }
}

.gold {
	filter: drop-shadow(0 0 8px rgba(255,215,0,0.75));
}

.silver {
	filter: drop-shadow(0 0 8px rgba(220,220,220,0.75));
}

.bronze {
	filter: drop-shadow(0 0 8px rgba(205,127,50,0.75));
}

/* SCORE CARD */
.score-box {
	text-align: center;
	background: linear-gradient(
		135deg,
		rgba(255, 255, 255, 0.18),
		rgba(255, 255, 255, 0.08)
	);
	backdrop-filter: blur(14px);
	border-radius: 22px;
	padding: 2rem 1.5rem;
	border: 1px solid rgba(255, 255, 255, 0.12);
	box-shadow:
		0 12px 30px rgba(0, 0, 0, 0.28),
		inset 0 0 20px rgba(255, 255, 255, 0.05);
	position: relative;
	overflow: hidden;
	transition: 0.3s ease;
}


.score-box:hover {
	transform: translateY(-4px) scale(1.015);
	box-shadow:
		0 18px 35px rgba(0, 0, 0, 0.32),
		0 0 22px rgba(77, 148, 255, 0.22);
}

.score-box::after {
	content: "";
	position: absolute;
	top: -40%;
	left: -60%;
	width: 40%;
	height: 180%;
	background: linear-gradient(
		120deg,
		rgba(255,255,255,0),
		rgba(255,255,255,0.22),
		rgba(255,255,255,0)
	);
	transform: rotate(20deg);
	transition: 0.8s ease;
}

.score-box:hover::after {
	left: 130%;
}

/* TITLE */
.score-box h2 {
	margin: 0;
	font-size: 2.4rem;
	font-weight: 700;
	color: #dbe8ff;
	letter-spacing: 0.4px;
}

/* BIG SCORE NUMBER */
.score-number {
	margin-top: 0.8rem;
	font-size: 3.4rem;
	font-weight: 900;
	line-height: 1;
	color: #4d94ff;
	text-shadow:
		0 0 10px rgba(77, 148, 255, 0.65),
		0 0 22px rgba(77, 148, 255, 0.35);
	animation: scorePulse 2.2s ease-in-out infinite;
}
@keyframes scorePulse {
	0%, 100% {
		transform: scale(1);
	}
	50% {
		transform: scale(1.05);
	}
}

/* SHOP */
.score-shop {
	text-decoration: none;
	color: white;
	text-align: center;
	background: linear-gradient(135deg, #4b4bff, #6a6aff);
	padding: 2rem;
	border-radius: 18px;
	transition: 0.3s ease;
}

.score-shop:hover {
	transform: scale(1.02);
	box-shadow: 0 0 20px rgba(106,106,255,0.35);
}

.score-shop h2 {
	margin: 0 0 0.5rem 0;
}

/* FOOTER */
.footer {
	width: 100%;
	padding: 0.8rem 0;
	text-align: center;
	background: #f0f0f0;
	color: #222;
}

/* MOBILE */
@media (max-width: 900px) {
	.play-options {
		grid-template-columns: 1fr;
	}
}

@media (max-width: 768px) {
	.dashboard {
		padding: 1rem;
		padding-bottom: 5rem;
	}

	.play-text {
		font-size: 1.8rem;
	}

	.streak-text {
		font-size: 1.2rem;
	}

	.leaderboard-header,
	.leaderboard-item,
	.leaderboard-item-self {
		grid-template-columns: 65px 1fr 80px;
		font-size: 0.92rem;
	}
}
</style>