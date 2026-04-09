<!--Not sure where to implement this:
<RouterLink to="/create">Create</RouterLink>
<RouterLink to="/join">Join</RouterLink>
-->

<script lang="ts" setup>
import { R } from 'vue-router/dist/router-CWoNjPRp.mjs';
import { ref, computed, onMounted } from 'vue';
import router from '@/router';
import api from '@/api';

const streak = ref(7);

const flameLevel = computed(() => {
  if (streak.value >= 5) return 'legend';
  if (streak.value >= 3) return 'hot';
  if (streak.value >= 1) return 'warm';
  return 'idle';
});

const score = ref(0);

function createPage() {
  router.push({
    name: 'create'
  })
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
					<span class="streak-number" :class="{active: streak > 0}">{{ streak }}</span>
			</div>

			<h1 class="play-text glow-text">Play a Game</h1>
			<div class="play-options">
				<button class="play-btn card-glass glow-hover card-hover" @click="createPage">Solo Vs Bot</button>
				<button class="play-btn card-glass glow-hover card-hover" @click="createPage">Play Vs Friends</button>
				<button class="play-btn card-glass glow-hover card-hover" @click="createPage">Team Mode</button>
			</div>

			<RouterLink to="/leaderboard" class="leaderboard-link">
			<button class="leaderboard card-glass hover-shadow card-hover">
				<h2 class="glow-text">🏆 Lifetime Leaderboard</h2>
				<div class="leaderboard-header">
					<span>Rank</span>
					<span>Player</span>
					<span>Score</span>
				</div>

				<ul class="leaderboard-list">
					<li class="leaderboard-item"><span class="rank-badge gold">1</span><span>PlayerOne</span><span>1500 pts</span></li>
					<li class="leaderboard-item"><span class="rank-badge silver">2</span><span>PlayerTwoWithLongName</span><span>1200 pts</span></li>
					<li class="leaderboard-item"><span class="rank-badge bronze">3</span><span>PlayerThree</span><span>900 pts</span></li>
					<li class="leaderboard-item-self"><span>9</span><span>You</span><span>0 pts</span></li>
          		</ul>

			</button>
			</RouterLink>

			<div class="score-box card-glass hover-shadow">
				<h2 class="glow-text">Lifetime Score</h2>
				<p class="score-number">{{ score }}</p>
			</div>

			<RouterLink to="/shop" class="score-shop card-glass hover-shadow">
				<h2 class="glow-text">🛒Shop</h2>
				<p>Unlock exclusive rewards!</p>
			</RouterLink>
		</main>
	</div>

	<footer class="footer">
		&copy; 2026 Scrabble Teams. All rights reserved.
	</footer>
</template>


<style lang="css" scoped>
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
	
}

.main {
	flex: 1;
}


.card-hover {
  transition: all 0.3s ease;
}

.card-hover:hover {
	transform: translateY(-6px) scale(1.03);
	box-shadow:
		0 15px 30px rgba(0,0,0,.25),
		0 0 25px rgba(77, 148, 255, 0.35);
}

.card-glass {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
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
  text-shadow: 0 0 8px #4d94ff, 0 0 16px #80c0ff;
}

.menu-btn {
	position: fixed;
	top: 1rem;
	left: 1rem;
	font-size: 1.5rem;
	background: none;
	border: none;
	cursor: pointer;
	z-index: 1001;
}

.sidebar {
	position: fixed;
	top: 0;
	left: -220px;
	height: 100%;
	width: 220px;
	background: #f0f0f0;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 1.5rem;
	padding-top: 4rem;
	transition: left 0.3s ease;
	z-index: 1000;
}

.sidebar.open {
	left: 0;
}

.icon {
	font-size: 1.2rem;
	cursor: pointer;
}

.theme-icon {
	display: flex;
	gap: 0.5rem;
	align-items: center;
	font-size: 1.2rem;
}

.theme-btn {
	font-size: 1.2rem;
	cursor: pointer;
}

.main {
	display: flex;
	flex-direction: column;
	gap: 2rem;
	min-height: calc(100vh - 4rem);
}

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
  text-align: left;
}

.flame.idle {
  opacity: 0.3;
  transform: scale(0.9);
  text-shadow: none;
}
.flame.warm {
  text-shadow:
    0 0 8px #ffae42,
    0 0 16px #ff8c00;
  transform: scale(1);
}

.flame.hot {
  text-shadow:
    0 0 12px #ff5500,
    0 0 25px #ff2a00,
    0 0 40px #ff7300;
  transform: scale(1.2);
}

.flame.legend {
  text-shadow:
    0 0 15px #ff0000,
    0 0 35px #ff4d00,
    0 0 60px #ffaa00;
  transform: scale(1.4);
  animation: flameLegend 1s infinite alternate;
}

@keyframes flameLegend {
  from { transform: scale(1.35) rotate(-3deg); }
  to { transform: scale(1.45) rotate(3deg); }
}

@keyframes flame-bounce {
  from { transform: translateY(0); }
  to { transform: translateY(-5px); }
}


.streak-text {
  font-size: 1.6rem;
  font-weight: 500;
  text-align: center;
  color: #000000;
}
.streak-number {
  color: #ff6b6b;
  text-shadow:
    0 0 8px #ff6b6b,
    0 0 16px rgba(255,107,107,0.5);
  font-size: 2rem;
  font-weight: 700;
  text-align: center;
  animation: streakPulse 2s ease-in-out infinite;
}

@keyframes streakPulse {
0%, 100% {
transform: scale(1);
text-shadow:
	0 0 6px rgba(255, 80, 80, 0.8),
	0 0 12px rgba(255, 80, 80, 0.5);
}
50% {
transform: scale(1.08);
text-shadow:
	0 0 10px rgba(255, 80, 80, 1),
	0 0 20px rgba(255, 80, 80, 0.7);
}
}

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
  font-size: 1.4rem;
  font-weight: 600;
  border-radius: 20px;
  border: none;
  cursor: pointer;
  background: linear-gradient(135deg, #2a4d8f, #4169a9);
  color: #f0f0f0;
  transition: all 0.3s ease;
}

.glow-hover:hover {
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(77, 148, 255, 0.7);
}

.play-btn:hover {
  background: linear-gradient(135deg, #4169a9, #5a7dbb);
  box-shadow: 0 0 20px rgba(65,105,169,0.5);
  transform: scale(1.05);
}

.play-btn:active {
  background: linear-gradient(135deg, #1f3a6b, #2a4d8f);
  transform: scale(0.98);
}

.play-btn:focus {
	outline: 2px solid #8080ff;
}

.leaderboard h2 {
	margin-bottom: 1rem;
}

.leaderboard {
  background: linear-gradient(135deg, #1e3a5f, #2a4d8f);
  padding: 1.5rem;
  border-radius: 12px;
  width: 100%;
  border: none;
  cursor: pointer;
  color: #fff;
}

.leaderboard:hover {
  background: linear-gradient(135deg, #2a4d8f, #3b61b0);
}
.leaderboard:active {
  background: linear-gradient(135deg, #1b3050, #254172);
  transform: scale(0.98);
}

.leaderboard:focus {
	outline: 2px solid #ccc056;
}

.leaderboard-header,
.leaderboard-item,
.leaderboard-item-self {
	display: grid;
	grid-template-columns: 80px 1fr 100px;
	align-items: center;
}

.leaderboard-header {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #e0e0ff;
}

.leaderboard-list {
	list-style: none;
	padding: 0;
	margin: 0;
}

.leaderboard-item, .leaderboard-item-self {
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.leaderboard-item-self {
  background: rgba(253, 0, 0, 0.664);
  font-weight: 600;
}

.rank-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-weight: bold;
  color: white;
  font-size: 0.9rem;
  box-shadow: 0 0 10px rgba(0,0,0,0.3);
  justify-self: center;
  position: relative;
  
}

.rank-badge.gold {
  background: linear-gradient(135deg, #ffd700, #ffc700);
  box-shadow: 0 0 12px #ffd700, 0 0 25px rgba(255,215,0,0.6);
}

.rank-badge.silver {
  background: linear-gradient(135deg, #c0c0c0, #a8a8a8);
  box-shadow: 0 0 12px #c0c0c0, 0 0 25px rgba(192,192,192,0.6);
}

.rank-badge.bronze {
  background: linear-gradient(135deg, #cd7f32, #b06b2b);
  box-shadow: 0 0 12px #cd7f32, 0 0 25px rgba(205,127,50,0.6);
}

.rank-badge::after {
  content: "";
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(
    120deg,
    transparent,
    rgba(255,255,255,0.6),
    transparent
  );
  opacity: 0;
  transition: opacity 0.3s;
}

.rank-badge:hover::after {
  opacity: 1;
}

.score-box {
	background-color: #f0f0f0;
	padding: 1rem 1.5rem;
	border-radius: 12px;
	text-align: center;
}

.score-box h2 {
	font-size: 1.7rem;
	font-weight: 700;
	margin-bottom: 0.5rem;
}

.score-number {
  font-size: 1.8rem;
  font-weight: 700;
  color: #4d94ff;
}

.score-shop {
  display: inline-block;
  text-decoration: none;
  color: inherit;
  padding: 2rem 1.5rem;
  margin-top: 1rem;
  text-align: center;
  background: linear-gradient(135deg, #4b4bff, #6a6aff);
  transition: all 0.3s ease;
  color: #fff;
}

.score-shop h2 {
	font-size: 1.7rem;
	font-weight: 600;
	margin-bottom: 0.5rem;
}

.score-shop:hover {
  background: linear-gradient(135deg, #6a6aff, #8c8cff);
  transform: scale(1.02);
  box-shadow: 0 0 20px rgba(106,106,255,0.3);
}

.score-shop:active {
  background: linear-gradient(135deg, #2f2fff, #4b4bff);
  transform: scale(0.98);
}
.score-shop:focus {
	outline: 2px solid #8080ff;
}

@media (max-width: 900px) {
	.dashboard {
		grid-template-columns: 1fr;
	}

	.sidebar {
		display: none;
	}

	.play-btn {
		grid-template-columns: 1fr;
	}
}

.footer {
  
  width: 100%;
  padding: 0.75rem 0;
  text-align: center;
  background: #f0f0f0;
}

/*
.bg-aurora {
  position: fixed;
  inset: 0;
  z-index: -3;
  background: linear-gradient(
    120deg,
    #000000,
    #424242,
    #868686,
    #ffffff
  );
  background-size: 400% 400%;
  animation: auroraMove 10s ease infinite;
  opacity: 0.8;
}

.bg-orb {
  position: fixed;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.7;
  z-index: -2;
  mix-blend-mode: screen;
}

.orb1 {
  width: 400px;
  height: 400px;
  background: #010a16;
  top: 10%;
  left: 10%;
  animation: float1 12s infinite ease-in-out;
}

.orb2 {
  width: 300px;
  height: 300px;
  background: #210124;
  bottom: 15%;
  right: 15%;
  animation: float2 14s infinite ease-in-out;
}

.orb3 {
  width: 250px;
  height: 250px;
  background: #02252b;
  top: 50%;
  right: 5%;
  animation: float3 10s infinite ease-in-out;
}

@keyframes float1 {
  0%,100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-80px) scale(1.08); }
}
@keyframes float2 {
  0%,100% { transform: translateX(0) scale(1); }
  50% { transform: translateX(-100px) scale(1.08); }
}
@keyframes float3 {
  0%,100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(120px) scale(1.1); }
}

@keyframes auroraMove {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
*/
</style>