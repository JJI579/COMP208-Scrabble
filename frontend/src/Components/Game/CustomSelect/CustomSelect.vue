<script lang="ts" setup>
import { ref, computed, watch } from 'vue';
import CustomOption from './CustomOption.vue';

type Option = [string, string, string?];

const props = defineProps<{
	options: Option[]
	label: string
}>();

const selected = defineModel<string>('selected', { default: "" });

const emit = defineEmits(['open', 'close']);

const menuOpen = defineModel('isopen', { type: Boolean, required: true });

watch(menuOpen, (val) => {
	console.log('menuOpen changed:', val);
});

function toggleMenu() {
	if (menuOpen.value) {
		emit("close", props.label);
		return
	}
	emit('open', props.label);
}

function optionClicked(option: Option) {
	selected.value = option[0];
	menuOpen.value = false;
}

const selectedOption = computed(() => {
	return props.options.find(o => o[0] === selected.value) ?? props.options[0];
});
</script>



<template>
	<div class="select__container">
		<div class="label">
			{{ label }}
		</div>
		<div class="select">
			<div class="selected card-glass" @click="toggleMenu">
				<div class="left">
					<i v-if="selectedOption?.[2]" :class="selectedOption[2]" class="icon"></i>
					<span>{{ selectedOption?.[1] }}</span>
				</div>
				<i class="pi pi-chevron-down chevron" :class="{ active: menuOpen }"></i>
			</div>
			<div v-if="menuOpen" class="options card-glass">
				<div v-for="option in options" :key="option[0]" class="option" @click="optionClicked(option)">
					<i v-if="option[2]" :class="option[2]" class="icon"></i>
					<span>{{ option[1] }}</span>
				</div>
			</div>
		</div>
	</div>
</template>


<style scoped>
.select__container {
	display: flex;
	flex-direction: column;
	gap: 0.45rem;
}

.label {
	font-size: 0.85rem;
	font-weight: 600;
	letter-spacing: 0.3px;
	opacity: 0.75;
	color: rgba(255, 255, 255, 0.9);
}




.selected {
	padding: 0.85rem 1rem;

	display: flex;
	justify-content: space-between;
	align-items: center;

	border-radius: 14px;

	cursor: pointer;

	color: white;

	background: rgba(255, 255, 255, 0.08);
	border: 1px solid rgba(255, 255, 255, 0.06);

	backdrop-filter: blur(14px);

	transition: all 0.18s ease;
}

.selected:hover {
	border-color: rgba(77, 148, 255, 0.35);
	box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
	transform: translateY(-1px);
}



.left {
	display: flex;
	align-items: center;
	gap: 0.55rem;
}

.icon {
	font-size: 1.05rem;
	opacity: 0.9;
}



.chevron {
	font-size: 0.9rem;
	opacity: 0.7;
	transition: transform 0.25s ease, opacity 0.2s ease;
}

.chevron.active {
	transform: rotate(180deg);
	opacity: 1;
}

.options {
	position: absolute;
	margin-top: 0.5rem;
	width: 100%;
	z-index: 50;

	border-radius: 14px;

	background: rgba(15, 23, 42, 0.95);
	border: 1px solid rgba(255, 255, 255, 0.06);

	backdrop-filter: blur(16px);

	overflow: hidden;

	box-shadow: 0 18px 45px rgba(0, 0, 0, 0.45);

	animation: pop 0.12s ease-out;
}

.option {
	display: flex;
	align-items: center;
	gap: 0.6rem;

	padding: 0.85rem 1rem;

	cursor: pointer;

	color: rgba(255, 255, 255, 0.9);

	transition: background 0.15s ease;
}

.option:hover {
	background: rgba(77, 148, 255, 0.15);
}

@keyframes pop {
	from {
		opacity: 0;
		transform: translateY(-6px) scale(0.98);
	}

	to {
		opacity: 1;
		transform: translateY(0) scale(1);
	}
}
</style>