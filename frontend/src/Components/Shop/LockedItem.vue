<script lang="ts" setup>
import type { Item } from '@/types';
import type { PropType } from 'vue';


const props = defineProps({
	item: {
		type: Object as PropType<Item>,
		required: true
	},
	currentScore: {
		type: Number,
		required: true
	}
})

const item = props.item;

</script>



<template>
	<div class="item">
		<div class="item__name">{{ item.name }} - <span class="item__score">
				{{ props.currentScore }}/{{ item.xpRequired }}
			</span></div>
	</div>

</template>


<style lang="css" scoped>

.item {

}
.item__name {

}
.item__score {

}
</style>