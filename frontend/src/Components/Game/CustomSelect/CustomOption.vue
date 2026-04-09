<script lang="ts" setup>


const props = defineProps({
	option: {
		required: true,
		type: Array<string>,
		default: []
	},
	index: {
		required: true,
		type: Number
	}
})


const emit = defineEmits(['click'])
</script>



<!-- Format: [id, name] -->
<template>
	<div class="option" @click="emit('click', props.index)">
		{{ props.option[1] }}
	</div>
</template>


<style lang="css" scoped>
.option {
	padding: .75rem;
	cursor: pointer;
}
</style>