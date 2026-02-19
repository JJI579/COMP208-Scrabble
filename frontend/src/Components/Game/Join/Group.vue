<script lang='ts' setup>
import useWebsocketStore from '@/Components/Stores/websocket';
import type { PropType } from 'vue';


const props = defineProps({
    group: {
        type: Array as PropType<Number[]>,
        required: true
    },
    maxSize: {
        type: Number,
        required: true
    },
    id: {
        type: Number,
        required: true
    }
})

const emit = defineEmits(['join-group'])
const websocket = useWebsocketStore();

function joinGroup() {
    websocket.send("GROUP_JOIN", {index: props.id})
    // TODO: alert to say you have sent it.
}


</script>


<template>
    <div class="group">
        {{ props.group }}
        <div class="button" @click="joinGroup()">
            Join Group
        </div>
    </div>
</template>


<style lang='css' scoped>

</style>