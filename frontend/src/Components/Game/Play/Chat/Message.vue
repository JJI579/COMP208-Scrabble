<script lang='ts' setup>
import type { MessageType } from '@/types';
import type { PropType } from 'vue';


const props = defineProps({
    message: {
        type: Object as PropType<MessageType>,
        required: true
    }
})
</script>


<template>
    <div class="message">
        <div class="author">
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
        gap: 5px;
        justify-content: left;
    }
    .author {
        color: grey;
        font-size: small;
        text-transform: capitalize;
    }

    
</style>