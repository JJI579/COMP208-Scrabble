<script setup lang="ts">
import Login from "./Login.vue"
</script>

<template>
  <div class="page">

    <div class="overlay"></div>

    <div class="card">
      <div class="tiles">
        <div v-for="l in ['S', 'C', 'R', 'A', 'B', 'B', 'L', 'E']" :key="l" class="tile">
          {{ l }}
        </div>
      </div>
      <Login />
    </div>


  </div>
</template>

<style scoped>
.page {
  height: 100vh;
  width: 100vw;
  background-image: url('/scrabble-bg.png');
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
  position: fixed;
  inset: 0;
  z-index: 0;
}

.overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom,
      rgba(0, 0, 0, 0.25),
      rgba(0, 0, 0, 0.7));
  backdrop-filter: blur(6px);
}

.card {
  position: relative;
  margin-top: 7vh;
  z-index: 2;
  width: 420px;
  padding: 2.5rem;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(18px);
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.15);
  text-align: center;
}

.logo {
  color: white;
  letter-spacing: 8px;
  font-size: 2.2rem;
  margin-bottom: 2rem;
}

.tiles {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.tile {
  width: 42px;
  height: 37px;
  background: #f4e2b8;
  color: #2c2c2c;
  font-weight: bold;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    0 4px 0 #c9b48d,
    0 6px 12px rgba(0, 0, 0, 0.4);
  font-size: 1.2rem;
}
</style>
