<script lang="ts" setup>
import type { GameUser } from '@/game_types';
import type { UserReturn } from '@/types';
import type { PropType } from 'vue';

// userID: number
// 	userName: string
// 	userCreatedAt: string

const props = defineProps({
	activePlayer: {
		type: Number,
		required: true
	},
	userGameData: {
		type: Object as PropType<GameUser>,
		required: true
	}
})
</script>



<template>

	<div class="player-card" :class="{ active: activePlayer === props.userGameData.userID }">
		<img class="pfp" src="https://i.pravatar.cc/1000?img=50" />
		<div class="player-info">
			<p class="name">{{ props.userGameData.userName }}</p>
			<p class="score">Score: {{ props.userGameData.points }}</p>
		</div>
	</div>
</template>


<style lang="css" scoped>
.player-card {
	height: 150px;
	width: 250px;
	background: #2c8595;
	border-radius: 14px;
	box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
	display: flex;
	align-items: center;
	gap: 0.6rem;
	padding: 1rem;
	position: relative;
	animation: floatCard 4s ease-in-out infinite;
}

@keyframes floatCard {
	0%,
	100% {
		transform: translateY(0);
	}

	50% {
		transform: translateY(-8px);
	}
}

.player-card.active {
	box-shadow:
		0 0 25px rgba(241, 188, 76, 0.8),
		0 0 60px rgba(241, 188, 76, 0.4),
		0 0 40px rgba(241, 188, 76, 0.6) inset;
	animation: glowCard 4s ease-in-out infinite;
	transition: transform 0.3s, box-shadow 0.3s;
}

@keyframes glowCard {
	0% {
		transform: scale(1);
		box-shadow:
			0 0 20px rgba(241, 188, 76, 0.6),
			0 0 50px rgba(241, 188, 76, 0.3),
			0 0 30px rgba(241, 188, 76, 0.4) inset;
	}

	25% {
		transform: scale(1.02);
		box-shadow:
			0 0 30px rgba(241, 188, 76, 0.8),
			0 0 60px rgba(241, 188, 76, 0.4),
			0 0 40px rgba(241, 188, 76, 0.5) inset;
	}

	50% {
		transform: scale(1.04);
		box-shadow:
			0 0 40px rgba(241, 188, 76, 1),
			0 0 80px rgba(241, 188, 76, 0.5),
			0 0 50px rgba(241, 188, 76, 0.6) inset;
	}

	75% {
		transform: scale(1.02);
		box-shadow:
			0 0 30px rgba(241, 188, 76, 0.8),
			0 0 60px rgba(241, 188, 76, 0.4),
			0 0 40px rgba(241, 188, 76, 0.5) inset;
	}

	100% {
		transform: scale(1);
		box-shadow:
			0 0 20px rgba(241, 188, 76, 0.6),
			0 0 50px rgba(241, 188, 76, 0.3),
			0 0 30px rgba(241, 188, 76, 0.4) inset;
	}
}

.player-card.active .timer {
	animation: pulseTimer 1s infinite;
}

@keyframes pulseTimer {
	0%,
	100% {
		opacity: 1;
	}

	50% {
		opacity: 0.3;
	}
}

.pfp {
	width: clamp(44px, 3.4vw, 58px);
	height: clamp(44px, 3.4vw, 58px);
	border-radius: 50%;
	object-fit: cover;
	border: 3px solid #f1bc4c;
	flex-shrink: 0;
}

.player-info {
	display: flex;
	flex-direction: column;
	min-width: 0;
}

.name {
	font-weight: bold;
	color: white;
	font-size: clamp(0.95rem, 1vw, 1.1rem);
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.score {
	color: #f1bc4c;
	font-weight: bold;
	font-size: clamp(0.9rem, 0.95vw, 1rem);
}

.timer {
	color: white;
	font-size: 14px;
	position: relative;
}

@media (max-width: 1100px) {
	.player-card {
		width: clamp(160px, 42vw, 220px);
		height: 95px;
		padding: 0.8rem;
	}

	.name,
	.score {
		font-size: 0.95rem;
	}
}
</style>