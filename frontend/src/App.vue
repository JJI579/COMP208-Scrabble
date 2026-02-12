<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { RouterView } from 'vue-router';
import Header from './Components/Header/Header.vue';
import useUserStore from './Components/Stores/user';
import useWebsocketStore from './Components/Stores/websocket';

const websocket = useWebsocketStore()
onMounted(() => {
	var hasToken = localStorage.getItem('token');
	const userStore = useUserStore();
	if (hasToken) userStore.login();
	if (!websocket.websocket) {
		websocket.connect()
	}

})
</script>

<template>
	<Header />
	<div class="content">
		<RouterView />
	</div>
</template>

<style scoped>
/* Main Content Wrapper */
.content {
	width: 60%;
	height: 100%;
	margin: auto;
}
</style>

<style>
#app,
body,
html {
	height: 100%;
	width: 100%;
	margin: 0;
	font-family: "Roboto", sans-serif;
}

*,
*::before,
*::after {
	box-sizing: border-box;
}
</style>
