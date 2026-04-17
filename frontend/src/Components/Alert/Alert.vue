<script lang='ts' setup>
import useAlertStore from '../Stores/alert';
import useWebsocketStore from '../Stores/websocket';

const alertStore = useAlertStore();


// Group Mode Only

const websocketStore = useWebsocketStore();

function accept() {
	// [[[0, 0], [3, 'I', None], None], [[1, 0], [4, 'O', None], None]]
	// [[[7, 7], 'C', None], [[8, 7], 'I', None], [[9, 7], 'A', None], [[10, 7], 'O', None]]}
	const toSend: [number[], string, string?][] = [];
	Object.entries(websocketStore.game.partnerPlaced).forEach((value, key) => {
		var letter = value[1][1] as string;
		var cellID = Number(value[0]);
		var substitute = value[1][2];
		const x = cellID % 15;
		const y = Math.floor(cellID / 15);
		toSend.push([[x, y], letter, substitute])
	})

	websocketStore.send("TURN_CONFIRMATION", { letters: toSend });
	alertStore.dismiss();
}

function decline() {
	websocketStore.send("TURN_DECLINE", {});
	alertStore.dismiss();
}
</script>


<template>
	<div class="alert" :class="[
		{ 'alert--active': alertStore.isActive },
		alertStore.currentAlert?.type && `alert--${alertStore.currentAlert.type}`
	]">
		<div class="alert__content">
			<i class="pi pi-bell alert__icon"></i>
			<div class="alert__accent"></div>
			<span class="alert__text">
				{{ alertStore.currentAlert?.text }}
			</span>
			<i class="pi pi-times alert__close" @click.stop="alertStore.dismiss()"></i>
		</div>
		<div class="alert__actions" v-if="alertStore.currentAlert?.type == 'game'">
			<button class="action action--accept" @click="accept()">Accept</button>
			<button class="action action--decline" @click="decline()">Decline</button>
		</div>
	</div>
</template>


<style lang='css' scoped>
.alert {
	position: fixed;
	right: -40%;
	top: 10%;
	z-index: 100000000;
	height: auto;
	min-width: 280px;
	max-width: 380px;
	gap: .75rem;
	line-height: 1.5em;

	padding: .75rem 1rem;
	border-radius: 14px;
	font-size: .9rem;
	font-weight: 500;
	letter-spacing: .2px;
	color: white;
	background: rgba(40, 40, 60, 0.85);
	backdrop-filter: blur(12px);
	box-shadow:
		0 10px 25px rgba(0, 0, 0, .35),
		inset 0 0 0 1px rgba(255, 255, 255, .08);
	transform: translateX(20px);
	opacity: 0;
	transition:
		right 0.35s cubic-bezier(.22, 1, .36, 1),
		transform 0.35s cubic-bezier(.22, 1, .36, 1),
		opacity 0.25s ease;
	display: flex;
	flex-direction: column;
	justify-content: left;
	gap: 1rem;
}


.alert__content {
	display: flex;
	align-items: center;
}

.alert__actions {
	display: flex;
	gap: .5rem;
}

.action {
	flex: 1;
	padding: .75rem 1rem;
	border: none;
	border-radius: 12px;
	font-weight: 700;
	font-size: .95rem;
	letter-spacing: .25px;
	cursor: pointer;
	transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
	box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.action:hover {
	transform: translateY(-1px);
}

.action:active {
	transform: translateY(0);
}

.action--accept {
	color: white;
	background: linear-gradient(135deg, #28be8a, #1b7f5c);
}

.action--accept:hover {
	box-shadow: 0 0 18px rgba(40, 190, 138, 0.35);
}

.action--decline {
	color: white;
	background: linear-gradient(135deg, #d06262, #b13535);
}

.action--decline:hover {
	box-shadow: 0 0 18px rgba(208, 98, 98, 0.35);
}

.alert__icon {
	font-size: 1.25rem;
	opacity: .9;
}

.alert__text {
	flex: 1;
}

.alert__close {
	font-size: .9rem;
	opacity: .6;
	cursor: pointer;
	transition: 0.2s ease;
}

.alert--active {
	right: 2rem;
	transform: translateX(0);
	opacity: 1;
}


.alert--success {
	background: linear-gradient(180deg, #4ade80, #22c55e);
}

.alert--error {
	background: linear-gradient(180deg, #f87171, #ef4444);
}

.alert--warning {
	background: linear-gradient(180deg, #facc15, #eab308);
}

.alert--info {
	background: linear-gradient(180deg, #60a5fa, #3b82f6);
}

/* Hari what is this? */
.alert__accent {
	width: 6px;
	height: 70%;
	border-radius: 6px;
	background: linear-gradient(180deg, #60a5fa, #3b82f6);
}
</style>