<script lang='ts' setup>
import useWebsocketStore from '@/Components/Stores/websocket';
import type { PropType } from 'vue';
import { computed } from 'vue';
import type { GameUser } from '@/game_types';

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

const groupPlayers = computed(() => {
    return props.group.map(id => websocket.game.players.get(Number(id))).filter(Boolean) as GameUser[]
})

const isFull = computed(() => groupPlayers.value.length >= props.maxSize)

function joinGroup() {
    if (isFull.value) return
    websocket.send("GROUP_JOIN", {index: props.id})
    // TODO: alert to say you have sent it.
}


</script>


<template>
    <div class="group">
        <h3 class="group__title">Group {{ props.id + 1 }}</h3>
        <div class="group__players">
            <div
                v-for="player in groupPlayers"
                :key="player.userID"
                class="player"
            >
                <span>{{ player.userName }}</span>
                <div class="player__icon" v-if="player.userID === websocket.game.leader">
                    👑
                </div>
            </div>
            <div v-if="groupPlayers.length === 0" class="empty-group">
                Empty
            </div>
        </div>
        <button
            v-if="!isFull"
            @click="joinGroup"
            class="group__join-btn"
        >
            Join Group
        </button>
        <div v-else class="full-indicator">
            Full
        </div>
    </div>
</template>


<style lang='css' scoped>
.group {
    padding: 1.5rem;
    border-radius: 16px;
    background: rgba(255,255,255,.08);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,.1);
    box-shadow:
        0 8px 20px rgba(0,0,0,.25),
        0 0 15px rgba(77,148,255,.12);
    display: flex;
    flex-direction: column;
    gap: 1rem;
    min-height: 200px;
    justify-content: space-between;
}

.group__title {
    text-align: center;
    color: #4d94ff;
    font-size: 1.2rem;
    margin: 0;
    font-weight: 600;
}

.group__players {
    display: flex;
    flex-direction: column;
    gap: .5rem;
    flex-grow: 1;
}

.player {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: .8rem 1rem;
    border-radius: 12px;
    background: rgba(255,255,255,.06);
    border: 1px solid rgba(255,255,255,.08);
    font-weight: 600;
    font-size: 0.9rem;
}

.player:hover {
    background: rgba(255,255,255,.1);
}

.player__icon {
    color: gold;
    font-size: 1rem;
}

.empty-group {
    text-align: center;
    color: rgba(255,255,255,.6);
    font-style: italic;
    padding: 1rem;
}

.group__join-btn {
    padding: .8rem 1.2rem;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    cursor: pointer;
    color: white;
    background: linear-gradient(135deg,#2a4d8f,#4169a9);
    transition: .25s ease;
    align-self: center;
}

.group__join-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 12px rgba(77,148,255,.35);
}

.full-indicator {
    text-align: center;
    color: #ff5555;
    font-weight: 600;
    font-size: 0.9rem;
}

/* MOBILE */
@media (max-width: 768px) {
    .group {
        padding: 1rem;
        min-height: 180px;
    }

    .group__title {
        font-size: 1rem;
    }

    .player {
        padding: .6rem .8rem;
        font-size: 0.8rem;
    }
}
</style>