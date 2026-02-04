<script lang="ts" setup>
import { computed, ref, watch } from 'vue';
import useUserStore from '../Stores/user';

const userStore = useUserStore();



</script>

<template>

	<div class="header">
		<div class="first">
			<RouterLink :to="{ name: 'home' }" class="link">
				<p class="title">Scrabble</p>
			</RouterLink>
		</div>
		<div class="end" v-if="userStore.isLoggedIn">
			<RouterLink class="link" :to="{ name: 'dashboard' }">
				Home
			</RouterLink>
		</div>
		<div class="end" v-else>
			<RouterLink class="link" :to="{ name: 'login' }">Login</RouterLink>
			<RouterLink class="link" :to="{ name: 'login', query: { register: 'true' } }">Sign Up</RouterLink>
		</div>
	</div>
</template>


<style lang="css" scoped>
/* Header */
.header {
	position: sticky;
	top: 0;
	display: flex;
	justify-content: space-between;
	width: 80%;
	margin: auto;
	align-items: center;
}

.first {}

.title {
	font-size: 1.5em;
	font-weight: 600;
}

.link {
	text-decoration: none;
	color: initial;
}


.end {
	display: flex;
	gap: .5rem;
}

.user {
	padding: .25rem;
	height: 1.5rem;
	width: 1.5rem;
	display: flex;
	justify-content: center;
	align-items: center;
	border-radius: 50%;
	border: 2px solid black;
	box-sizing: content-box;
}
</style>