<script lang="ts" setup>
import type { Item } from '@/types';
import type { PropType } from 'vue';


const props = defineProps<{
	item: Item,
	currentScore: number
}>();

const item = props.item;

</script>



<template>
	<div class="item">
		<div class="item__name">{{ item.name }} - <span class="item__score">
				{{ props.currentScore }}/{{ item.xpRequired }}
			</span>
		</div>
		<div class="item__description">
			<i>{{ props.item.description }}</i>
		</div>
	</div>

</template>


<style lang="css" scoped>
.item {
	display: flex;
	flex-direction: column;
	gap: .25rem;
	justify-content: left;
}

.item__description {
	font-size: small;
}
</style>