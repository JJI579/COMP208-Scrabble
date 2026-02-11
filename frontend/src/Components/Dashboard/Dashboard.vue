<!--Not sure where to implement this:
<RouterLink to="/create">Create</RouterLink>
<RouterLink to="/join">Join</RouterLink>
-->



<script lang="ts" setup>

	import { ref } from 'vue';
	const sidebarOpen = ref(false);

</script>


<template>

	<div class="dashboard">

		<button class="menu-btn" @click="sidebarOpen = !sidebarOpen">☰</button>

		<aside class="sidebar" :class="{ open: sidebarOpen }">
			<button class="icon">🏠 Home</button>
			<button class="icon">🔎 Word Finder</button>
			<button class="icon">📖 Dictionary</button>

			<div class="theme-icon">
				<div class="theme-text">Theme</div>
				<button class="theme-btn">🌞</button>
				<button class="theme-btn">🌜</button>
			</div>

			<div class="icon">Score: 0</div>
			<button class="icon">🛒 Shop</button>
			<button class="icon">👥 Friends</button>
		</aside>

		<main class="main">

			<div class="streak-box">
				<span class="flame">🔥</span>
				<p class="streak-text">Weekly Streak</p>
				<span class="streak-number">0</span>
			</div>
			
			<h1 class="play-text">Play a Game</h1>

			<div class="play-options">
				<button class="play-btn">Solo Vs Bot</button>
				<button class="play-btn">Play Vs Friends</button>
				<button class="play-btn">Team Mode</button>
			</div>

			<button class="leaderboard">
				<h2>Lifetime Leaderboard</h2>
				<div class="leaderboard-header">
					<span>Rank</span>
					<span>Player</span>
					<span>Score</span>
				</div>

				<ul class="leaderboard-list">
					<li class="leaderboard-item">
						<span class="rank">1</span>
						<span class="player-name"> PlayerOne</span>
						<span class="score"> 1500 pts</span>
					</li>
					<li class="leaderboard-item">
						<span class="rank">2</span>
						<span class="player-name"> PlayerTwoWithLongName</span>
						<span class="score"> 1200 pts</span>
					</li>
					<li class="leaderboard-item">
						<span class="rank">3</span>
						<span class="player-name"> PlayerThree</span>
						<span class="score"> 900 pts</span>
					</li>
					<li class="leaderboard-item-self">
						<span class="rank">9</span>
						<span class="player-name"> You</span>
						<span class="score"> 0 pts</span>
					</li>
				</ul>
			</button>

			<div class="score-box">
				<h2>Current Score</h2>
				<p class="score-number">0 pts</p>
			</div>

			<button class="score-shop">
				<h2>🛒Shop</h2>
				<p>Unlock exclusive rewards!</p>
			</button>
		</main>
	</div>

	<footer class="footer">
		&copy; 2026 Scrabble Teams. All rights reserved.
	</footer>

</template>


<style lang="css" scoped>

	.dashboard {
		position: relative;
		max-width: 1200px;
		margin: 2rem auto;	
		padding: 0 1rem;
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
		display: flex;
		align-items: center;
		justify-content: space-between;
		background: #ffe0e0;
		padding: 1.5rem 2rem;
		border-radius: 12px;
		width: 100%;
	}

	.flame {
		font-size: 1.5rem;
	}

	.streak-text {
		font-size: 1.5rem;
		font-weight: 500;
	}

	.streak-number {
		font-size: 1.5rem;
		font-weight: 700;
		color: #ff4d4d;
	}

	.play-text {
		text-align: center;
		font-size: 2.2rem;
	}

	.play-options {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 2rem;
	}


	.play-btn {
		padding: 5rem 1rem;
		font-size: 1.5rem;
		font-weight: 600;
		border-radius: 16px;
		border: none;
		background: #e0e0ff;
		cursor: pointer;
	}

	.play-btn:hover {
		background-color: #c0c0ff;
	}

	.play-btn:active {
		transform: scale(0.98);
		background-color: #a0a0ff;
	}

	.play-btn:focus {
		outline: 2px solid #8080ff;
	}

	.leaderboard {
		background: #fced68;
		padding: 1.5rem;
		border-radius: 12px;
		width: 100%;
		border: none;
		cursor: pointer;
	}

	.leaderboard:hover {
		background-color: #ecdf63;
	}

	.leaderboard:active {
		transform: scale(0.98);
		background-color: #dacd5b;
	}

	.leaderboard:focus {
		outline: 2px solid #ccc056;
	}

	.leaderboard-header, .leaderboard-item, .leaderboard-item-self {
		display: grid;
		grid-template-columns: 80px 1fr 100px;
		align-items: center;
	}

	.leaderboard-header {
		font-weight: 600;
		margin-bottom: 0.5rem;
	}

	.leaderboard-list {
		list-style: none;
		padding: 0;
		margin-top: .5rem;
	}

	.leaderboard-item, .leaderboard-item-self {
		padding: 0.5rem 0;
		border-bottom: 1px solid #ddd;
	}

	.leaderboard-item-self {
		background: #e0ffe0;
		font-weight: 600;
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
		font-size: 1.5rem;
		font-weight: 700;
		color: #4d94ff;
	}

	.score-shop {
		background-color: #e0e0ff;
		padding: 1rem 1.5rem;
		border-radius: 12px;
		text-align: center;
		border: none;
		cursor: pointer;
	}

	.score-shop h2 {
		font-size: 1.7rem;
		font-weight: 600;
		margin-bottom: 0.5rem;
	}

	.score-shop:hover {
		background-color: #c0c0ff;
	}

	.score-shop:active {
		transform: scale(0.98);
		background-color: #a0a0ff;
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
		width: 100vw;
		margin-left: calc(-50vw + 50%);
		padding: 0.75rem 0;
		text-align: center;
		background: #f0f0f0;
		font-size: 0.9rem;
	}

</style>