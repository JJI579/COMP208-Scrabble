<script lang="ts" setup>
import type { UnlockedItemType } from '@/types';
import type { PropType } from 'vue';



const props = defineProps({
	item: {
		type: Object as PropType<UnlockedItemType>,
		required: true,
	}
});
const emit = defineEmits(['equip', "unequip"])
const item = props.item;


function equip() {
	// TODO: implement
}

function unequip() {
	// TODO: implement
}

function toggleEquip() {
	if (item.equipped) {
		unequip()
		emit("unequip", props.item.itemID)
	} else {
		equip()
		emit("equip", props.item.itemID)
	}


}
</script>



<template>

	<div class="item">
		<div class="item__name">
			{{ item.name }} - <span v-if="item.equipped" class="item--unequip">[UNEQUIP]</span> <span
				class="item--equip" v-else>[EQUIP]</span>
		</div>
		<div class="item__description">
			{{ item.description }}
		</div>
	</div>
</template>


<style lang="css" scoped>
.item {
	display: flex;
	flex-direction: column;
	gap: .5rem;
	justify-content: left;
}

.item__name {}

.item--unequip {}

.item--equip {}

.item__description {}
</style>