<script lang="ts" setup>
import type { Item } from '@/types';
import { computed, onMounted, ref, watch } from 'vue';
import LockedItem from './LockedItem.vue';
import UnlockedItem from './UnlockedItem.vue';

const score = ref(357);
const displayScore = ref(score.value);
let interval: ReturnType<typeof setInterval> | null=null;
const unlockFlash = ref(false);
const displayProgress = ref(0);
let progressInterval: ReturnType<typeof setInterval> | null=null;

const items = ref<Item[]>([
  {
    itemID: 1,
    name: "Golden Name",
    description: "Your name becomes golden!",
    xpRequired: 500,
    unlocked: false,
  },
  {
    itemID: 2,
    name: "apple pie",
    description: "applie pie",
    xpRequired: 1000,
    unlocked: false,
  }
])


const locked = computed(() => 
	items.value.filter(i => score.value < i.xpRequired)
);

const unlocked = computed(() =>
	items.value.filter(i => score.value >= i.xpRequired).map(i => ({ ...i, equipped: false }))
);

const nextUnlock = computed(() => {
  return locked.value.sort((a, b) => a.xpRequired - b.xpRequired)[0];
});

const progress = computed(() => {
  if (!nextUnlock.value) return 100;

  return Math.min(
    100,
    (score.value / nextUnlock.value.xpRequired) * 100
  );
});

function equipItem(id: number) {
  console.log("Equip item:", id);
}

function unequipItem(id: number) {
  console.log("Unequip item:", id);
}


function animate(from: number, to: number) {
  if (interval) clearInterval(interval);

  const steps = 25;
  let current = 0;

  interval = setInterval(() => {
    current++;

    displayScore.value = Math.round(
      from + (to - from) * (current / steps)
    );

    if (current >= steps) {
      displayScore.value = to;
      clearInterval(interval!);
      interval = null;
    }
  }, 20);
}


watch(score, (newVal, oldVal) => {
  animate(oldVal ?? displayScore.value, newVal);
});

onMounted(() => {
  animate(0, score.value);
});


function animateProgress(to: number) {
  if (progressInterval) clearInterval(progressInterval);

  const from = displayProgress.value;
  const steps = 30;
  let current = 0;

  progressInterval = setInterval(() => {
    current++;

    displayProgress.value = Math.round(
      from + (to - from) * (current / steps)
    );

    if (current >= steps) {
      displayProgress.value = to;
      clearInterval(progressInterval!);
      progressInterval = null;
    }
  }, 20);
}

onMounted(() => {
  displayScore.value = score.value;
  animateProgress(progress.value);
});

watch(progress, (newVal) => {
  animateProgress(newVal);
});

</script>



<template>
  <div class="shop" :class="{ flash: unlockFlash}">
    <div class="header">
      <h1 class="title glow-text">🛒 Scrabble Shop</h1>
      <div class="score card-glass">
        <span class="label">Lifetime Score</span>
        <span class="value">{{ displayScore }}</span>
      </div>
    </div>
    <div class="card-glass next">
      <h2 class="glow-text">
        Next Unlock: {{ nextUnlock?.name || "All unlocked 🎉" }}
      </h2>
      <div class="bar">
        <div class="bar__progress">
          <div class="fill" :style="{ width: displayProgress + '%' }"></div>
        </div>
        <div class="bar__titles">
          <span>0</span>
          <span>{{ nextUnlock?.xpRequired || "MAX" }}</span>
        </div>
      </div>
    </div>
    <section class="section">
      <h2 class="section-title">🔒 Locked Items</h2>
      <div class="grid">
        <LockedItem
          v-for="item in locked"
          :key="item.itemID"
          :item="item"
          :currentScore="score"
        />
      </div>
    </section>
    <section class="section">
      <h2 class="section-title">🔓 Unlocked Items</h2>
      <div class="grid">
        <UnlockedItem
          v-for="item in unlocked"
          :key="item.itemID"
          :item="item"
          @equip="equipItem"
          @unequip="unequipItem"
        />
      </div>
    </section>
  </div>
</template>

<style scoped>
.shop {
  min-height: 100vh;
  padding: 2rem;

  display: flex;
  flex-direction: column;
  gap: 2rem;

  color: white;

  background: linear-gradient(180deg, #0d1b2a, #1b263b);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 2.2rem;
}

.score {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.2rem 1.6rem;
  min-width: 160px;
}

.label {
  font-size: 0.9rem;
  opacity: 0.7;
  letter-spacing: 0.5px;
}

.value {
  font-size: 2.2rem;
  font-weight: 800;
  color: #4d94ff;
  text-shadow: 0 0 10px rgba(77,148,255,0.6);
  animation: pulse 1.8s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    text-shadow: 0 0 8px rgba(77,148,255,0.5);
  }
  50% {
    transform: scale(1.08);
    text-shadow: 0 0 18px rgba(77,148,255,0.9);
  }
}

.card-glass {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 18px;
  padding: 1.2rem;
  box-shadow: 0 8px 20px rgba(0,0,0,0.25);
}

.glow-text {
  color: #4d94ff;
  text-shadow: 0 0 10px rgba(77,148,255,0.8);
}

.next {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.next h2 {
	font-size: 2rem;
}
.bar__progress {
  width: 100%;
  height: 40px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.35);
  overflow: hidden;
}

.fill {
  height: 100%;
  background: linear-gradient(90deg, #4d94ff, #80c0ff, #4d94ff);
  background-size: 200% 100%;
  transition: width 0.5s ease;
  animation: glowMove 2.5s linear infinite;
  box-shadow: 0 0 12px rgba(77,148,255,0.6);
}
@keyframes glowMove {
  0% {
    background-position: 0% 50%;
  }
  100% {
    background-position: 200% 50%;
  }
}

.bar__titles {
  display: flex;
  justify-content: space-between;
  font-size: 2rem;
  font-weight: 600;
  opacity: 0.9;
  margin-top: 0.4rem;
}


.section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-title {
  font-size: 1.4rem;
  font-weight: 600;
  opacity: 0.9;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.flash {
  animation: screenFlash 0.6s ease;
}
@keyframes screenFlash {
  0% {
    filter: brightness(1);
  }
  30% {
    filter: brightness(1.8) drop-shadow(0 0 20px #4d94ff);
  }
  100% {
    filter: brightness(1);
  }
}


</style>