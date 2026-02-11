<script lang="ts" setup>
import { computed, ref, watch } from 'vue';
import useUserStore from '../Stores/user';
import HeaderLink from './HeaderLink.vue';

const userStore = useUserStore();

const menuOpen = ref(false);

function toggleMenu() {
	menuOpen.value = !menuOpen.value;
}

</script>

<template>

	<div class="header">
		<div class="first">
			<div class="first__icon" @click="toggleMenu">
				<i class="pi pi-bars"></i>
			</div>
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
	<div class="menu__container">
		<div class="menu">
			<HeaderLink location="home" name="Home" icon="pi-home" />
			<HeaderLink location="home" name="Word Finder" icon="pi-search" />
			<HeaderLink location="home" name="Dictionary" icon="pi-book" />
			<HeaderLink location="home" name="Shop" icon="pi-shopping-cart" />
			<HeaderLink location="home" name="Friends" icon="pi-users" />
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

.first {
	display: flex;
	gap: 1rem;
	align-items: center;
}

.first__icon {
	font-size: 1.25rem;
	font-weight: bold;

}

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

/* Menu */
.menu__container {
	height: 100%;
	width: 25%;
	background-color: var(--clr-surface-a10);
	position: absolute;
	top: 0;
}

.menu {
	margin: 1rem;
	margin-block: 2rem;
	display: flex;
	justify-content: center;
	flex-direction: column;
	gap: 2rem;
}


</style>