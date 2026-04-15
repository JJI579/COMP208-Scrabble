<script lang="ts" setup>

const props = defineProps({
	message: {
		type: String,
		required: true
	}
})

const emit = defineEmits(['click'])
</script>



<template>
	<div class="preset" @click="emit('click', props.message)">
		{{ props.message }}
	</div>

</template>


<style lang="css" scoped>
.preset {
	padding: 0.25rem 0.5rem;
	width: fit-content;
	cursor: pointer;
	background: linear-gradient(145deg, var(--tile-background-colour), #e9d7a6);
	color: var(--tile-text-colour);
	font-weight: 500;
	border-radius: 12px;
	border: 1px solid #c5a569;
	transition: all 0.2s ease;
	box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
	font-size: 0.75rem;
	white-space: nowrap;
	line-height: 1.2;
}

.preset:hover {
	transform: translateY(-1px);
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
	background: linear-gradient(145deg, #e9d7a6, var(--tile-background-colour));
}

.preset:active {
	transform: translateY(0);
	box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}
</style>