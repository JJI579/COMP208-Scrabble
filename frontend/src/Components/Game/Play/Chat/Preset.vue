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
	padding: .25rem;
	padding-inline: .5rem;
	width: fit-content;
	cursor: pointer;
	background-color: var(--tile-background-colour);
	color: var(--tile-text-colour);
	font-weight: 500;
	border-radius: 8px;
}
</style>