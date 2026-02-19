<script lang="ts" setup>


const props = defineProps({
	name: {
		type: String,
		required: true
	},
	selected: {
		type: Boolean,
		required: true
	}
})

const emit = defineEmits(['click'])
</script>



<template>

	<div class="option" @click="emit('click', props.name)" :class="{ 'option--active': props.selected }">
		{{ props.name }}
	</div>
</template>


<style lang="css" scoped>
.option {
	transition: 0.25s ease all;
}

.option--active {
	border-bottom: 1px solid blue;
}
</style>