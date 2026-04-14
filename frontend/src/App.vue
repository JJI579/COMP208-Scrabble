<script setup lang="ts">
import { onMounted, watch } from 'vue';
import { RouterView, useRoute } from 'vue-router';
import Header from './Components/Header/Header.vue';
import useUserStore from './Components/Stores/user';
import useWebsocketStore from './Components/Stores/websocket';
import Alert from './Components/Alert/Alert.vue';
import useAlertStore from './Components/Stores/alert';

const route = useRoute();
const websocket = useWebsocketStore()

onMounted(() => {
	var hasToken = localStorage.getItem('token');
	const userStore = useUserStore();
	if (hasToken) userStore.login();
	if (!websocket.websocket) {
		console.log("Try to connect...")
		websocket.connect()
	}
	watch(() => userStore.isLoggedIn, () => {
		if (userStore.isLoggedIn) {
			if (!websocket.websocket) {
				websocket.connect()
			}
		}
	})
})

</script>

<template>
	<Alert />
	<Header />
	<div class="content" :class="{ 'content--playing': route.name == 'play' }">
		<RouterView />
	</div>
</template>

<style scoped>
/* Main Content Wrapper */
.content {
	
	margin: auto;
}

.content--playing {
	width: 100%;
}

@media (max-width: 999px) {
	.content {
		width: 80%;
	}
}

@media (max-width: 650px) {
	.content {
		width: 100%;
	}
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
	background-color: #0f172a;
}

*,
*::before,
*::after {
	box-sizing: border-box;
}
</style>
