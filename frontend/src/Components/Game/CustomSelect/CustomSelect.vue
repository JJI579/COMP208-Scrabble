<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';

import CustomOption from './CustomOption.vue';



const props = defineProps({
	options: {
		required: true,
		type: Array<Array<string>>,
		default: []
	},
	label: {
		required: true,
		type: String
	}
})

const menuOpen = ref(false);
function toggleMenu() {
	menuOpen.value = !menuOpen.value
}

const selectedOption = defineModel('selected', { default: "", type: String });
const indexRef = ref(0);

onMounted(() => {
	if (selectedOption.value) {
		const index = props.options.findIndex(option => option[0] === selectedOption.value)
		if (index == -1) {
			indexRef.value = 0;
			return;
		}
		indexRef.value = index;

	}
})


function optionClicked(index: number) {
	selectedOption.value = props.options[index]?.[0] || ""
	indexRef.value = index;
	menuOpen.value = false;
}

</script>



<template>

	<div class="select__container">
		<div class="label">
			{{ props.label }}
		</div>
		<div class="select">
			<div class="selected" @click="toggleMenu">
				<span>{{ props.options[indexRef]?.[1] }}</span>
				<span><i class="pi pi-chevron-down chevron" :class="{ 'chevron--active': menuOpen }"></i></span>
			</div>
			<div class="options" v-if="menuOpen">
				<CustomOption v-for="(option, index) in props.options" :option="option" :index="index" :key="index"
					@click="optionClicked" />
			</div>
		</div>
	</div>
</template>


<style lang="css" scoped>
.select__container {
	
	display: flex;
	flex-direction: column;
	gap: .5rem;
	min-width: 30%;
	

	/* background-color: blue; */
	/* background-color: blue; */
}



.chevron {
	transition: 0.5s cubic-bezier(0.075, 0.82, 0.165, 1) all;
}

.chevron--active {
	transform: rotate(180deg);
}


.select {
	position: relative;
}

.selected {
	/* background-color: beige; */
	padding: 1rem;
	width: 100%;
	display: flex;
	justify-content: space-between;
	background-color: var(--clr-surface-a10);
	border-radius: 10px;
	font-weight: 500;
}

.options {
	position: absolute;
	top: 110%;
	min-width: 12.5rem;
	display: flex;
	flex-direction: column;
	border-radius: 8px;
	background-color: var(--clr-surface-a10);
	z-index: 999999;
}

.options .option:not(:last-child) {
	border-bottom: 1px solid rgba(0, 0, 0, 0.5);
}
</style>