<script lang="ts" setup>
import type { Item, UnlockedItemType } from '@/types';
import { computed, onMounted, ref } from 'vue';
import LockedItem from './LockedItem.vue';
import UnlockedItem from './UnlockedItem.vue';

const score = ref(100);

const locked: Item[] = [
	{
		itemID: 1,
		name: "Midnight Background",
		description: "it makes your background midnight!",
		xpRequired: 1000,
		unlocked: false
	}
]

const unlocked: UnlockedItemType[] = [
	{
		itemID: 1,
		name: "Midnight Background",
		description: "it makes your background midnight!",
		xpRequired: 1000,
		unlocked: true,
		equipped: true
	}
]


const nextUnlock = computed(() => {
	var item = locked[0];
	return item;
})

const progress = ref(0);
onMounted(() => {
	// TODO: load content here, keep the function below to make progress animated...
	// THIS INCLUDES LOADING THE SCORE
	setTimeout(() => {
		if (nextUnlock.value) {
			progress.value = Math.round((score.value / nextUnlock.value.xpRequired) * 100)
		} else {
			progress.value = 0
		}
	}, 2000);
})
</script>



<template>

	<div class="score">
		Score: {{ score }}
	</div>
	{{ progress }}
	<!-- there will always be an unlockable item -->
	<div class="nunlock__item">
		Next Unlock: '<span class="nunlock__name">{{ nextUnlock?.name }}</span>'
		<div class="bar">
			<div class="bar__progress">
				<div class="fill" :style="{ width: progress + '%' }"></div>
			</div>
			<div class="bar__titles">
				<div class="bar__start">0</div>
				<div class="bar__end">{{ nextUnlock?.xpRequired }}</div>
			</div>
		</div>
	</div>
	<div class="locked">
		<h3>Locked</h3>
		<div class="locked__items">

			<LockedItem v-for="(item, ind) in locked" :item="item" :currentScore="score" :key="ind" />
		</div>

	</div>
	<div class="unlocked">
		<h3>Unlocked</h3>
		<div class="unlocked__items">
			<UnlockedItem v-for="(item, ind) in unlocked" :item="item" :key="ind" />
		</div>
	</div>

</template>


<style lang="css" scoped>
.score {
	padding: .5rem;
	border: 1px solid black;
	border-radius: 10px;
	width: fit-content;
}

.nunlock__item {}

.nunlock__name {}

.bar {}

.bar__progress {
	width: 100%;
	border: 2px solid black;
	height: 2rem;

}

.fill {
	height: 100%;
	background-color: black;
	transition: 0.5s cubic-bezier(0.23, 1, 0.320, 1) all;
	width: 0;
}


.bar__titles {
	display: flex;
	justify-content: space-between;
}

.bar__start {
	transform: translateX(-50%);
}

.bar__end {
	transform: translateX(50%);
}
</style>