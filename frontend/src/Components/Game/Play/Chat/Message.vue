<script lang='ts' setup>
import type { MessageType } from '@/types';
import { computed, type PropType } from 'vue';

const props = defineProps({
    message: {
        type: Object as PropType<MessageType>,
        required: true
    }
})

const flairColor = computed(() => {
	const palette = ['#ff6b6b', '#4dabf7', '#51cf66', '#fcc419', '#b197fc', '#ff922b', '#2ec4b6', '#f06595'];
	const userId = Number(props.message.author.id ?? 0);
	return palette[Math.abs(userId) % palette.length];
});

const messageStyle = computed(() => ({
	borderLeftColor: flairColor.value,
}));

const authorStyle = computed(() => ({
	color: flairColor.value,
}));
</script>


<template>
    <div class="message" :style="messageStyle">
        <div class="author" :style="authorStyle">
            {{ props.message.author.name }}
        </div>
        <div class="text">
            {{ props.message.text }}
        </div>
    </div>
</template>


<style lang='css' scoped>
.message {
	display: flex;
	flex-direction: column;
	gap: 4px;
	justify-content: left;
	padding: 0.5rem;
	margin-bottom: 0.5rem;
	background: white;
	border-radius: 8px;
	border-left: 6px solid var(--clr-primary-a20);
	box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
	transition: all 0.2s ease;
}

.message:hover {
	box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
	transform: translateX(2px);
}

.author {
	color: var(--clr-primary-a40);
	font-size: 0.85rem;
	font-weight: 600;
	text-transform: capitalize;
	margin-bottom: 2px;
}

.text {
	color: #495057;
	font-size: 0.95rem;
	line-height: 1.4;
	word-wrap: break-word;
}
</style>