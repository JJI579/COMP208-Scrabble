<script lang="ts" setup>
import api from '@/api';
import type { UnlockedItemType } from '@/types';
import type { PropType } from 'vue';
import useAlertStore from '../Stores/alert';



const props = defineProps({
	item: {
		type: Object as PropType<UnlockedItemType>,
		required: true,
	}
});
const emit = defineEmits(['equip', "unequip"])
const item = props.item;

// TODO: implement a store that contains all user config and then apply it when it matters across the website.

async function equip() {
	try {
		const resp = await api.post(`/items/${props.item.itemID}/equip`)
		emit("equip", props.item.itemID)
		item.equipped = true;
	} catch (error: any) {
		useAlertStore().alert({
			// TODO: set right text...
			text: "",
			type: "error"
		})
	}
}


async function unequip() {
	try {
		const resp = await api.post(`/items/${props.item.itemID}/unequip`)
		emit("unequip", props.item.itemID)
		item.equipped = false;

	} catch (error: any) {
		useAlertStore().alert({
			// TODO: set right text...
			text: "",
			type: "error"
		})
	}
}

function toggleEquip() {
	if (item.equipped) {
		unequip()

	} else {
		equip()

	}


}
</script>



<template>

	<div class="item">
		<div class="item__name">
			{{ item.name }} -

			<span @click="toggleEquip" :class="{ 'item--equip': item.equipped, 'item--unequip': !item.equipped }">[{{
				item.equipped ? 'UN' : '' }}EQUIP]</span>

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