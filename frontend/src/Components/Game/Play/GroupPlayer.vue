<script lang="ts" setup>
import type { GameUser } from '@/game_types';
import { computed, type PropType } from 'vue';


const props = defineProps({
	activePlayer: {
		type: Number,
		required: true
	},
	users: {
		type: Object as PropType<GameUser[]>,
		required: true
	}
})

const name = computed(() => {
	if (props.users.length > 1) {
		return props.users.map(user => user.userName).join(' & ')
	} else if (props.users.length == 1 && props.users[0]) {
		return props.users[0].userName
	} else {
		return ""
	}
})

const score = computed(() => {
	return props.users[0]?.points
})
</script>



<template>

	<div class="player-card" :class="{ active: activePlayer === 1 }" v-if="props.users.length > 0">
		<img class="pfp" src="https://i.pravatar.cc/1000?img=50" />
		<div class="player-info">
			<p class="name">{{ name }}</p>
			<p class="score">Score: {{ score }}</p>
		</div>
	</div>
</template>


<style lang="css" scoped>
.player-card {
	/* height: 150px;
	width: 200px; */
	background: #2c8595;
	border-radius: 14px;
	box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
	display: flex;
	align-items: center;
	gap: 1rem;
	padding: 1rem;
	align-self: flex-start;
	transform: translateY(-5.3rem);
	animation: floatCard 4s ease-in-out infinite;
}

@keyframes floatCard {

	0%,
	100% {
		transform: translateY(-5.3rem);
	}

	50% {
		transform: translateY(-6rem);
	}
}

.player-card.active {
	transform: translateY(-5.3rem) scale(1);
	box-shadow:
		0 0 25px rgba(241, 188, 76, 0.8),
		0 0 60px rgba(241, 188, 76, 0.4),
		0 0 40px rgba(241, 188, 76, 0.6) inset;
	animation: glowCard 4s ease-in-out infinite;
	transition: transform 0.3s, box-shadow 0.3s;
}

@keyframes glowCard {
	0% {
		transform: translateY(-5.3rem) scale(1);
		box-shadow:
			0 0 20px rgba(241, 188, 76, 0.6),
			0 0 50px rgba(241, 188, 76, 0.3),
			0 0 30px rgba(241, 188, 76, 0.4) inset;
	}

	25% {
		transform: translateY(-5.5rem) scale(1.02);
		box-shadow:
			0 0 30px rgba(241, 188, 76, 0.8),
			0 0 60px rgba(241, 188, 76, 0.4),
			0 0 40px rgba(241, 188, 76, 0.5) inset;
	}

	50% {
		transform: translateY(-5.8rem) scale(1.04);
		box-shadow:
			0 0 40px rgba(241, 188, 76, 1),
			0 0 80px rgba(241, 188, 76, 0.5),
			0 0 50px rgba(241, 188, 76, 0.6) inset;
	}

	75% {
		transform: translateY(-5.5rem) scale(1.02);
		box-shadow:
			0 0 30px rgba(241, 188, 76, 0.8),
			0 0 60px rgba(241, 188, 76, 0.4),
			0 0 40px rgba(241, 188, 76, 0.5) inset;
	}

	100% {
		transform: translateY(-5.3rem) scale(1);
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
	width: 55px;
	height: 55px;
	border-radius: 50%;
	object-fit: cover;
	border: 3px solid #f1bc4c;
}

.player-info {
	display: flex;
	flex-direction: column;
	/* gap: 3px; */
}

.name {
	font-weight: bold;
	color: white;
}

.score {
	color: #f1bc4c;
	font-weight: bold;
}

.timer {
	color: white;
	font-size: 14px;
	position: relative;
}
</style>