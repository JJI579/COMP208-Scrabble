<script lang="ts" setup>
import { computed, ref, watch } from 'vue';
import useUserStore from '../Stores/user';
import HeaderLink from './HeaderLink.vue';
import router from '@/router';
import { useRoute } from 'vue-router';

const route = useRoute();

const userStore = useUserStore();

const menuOpen = ref(false);

function toggleMenu() {
	menuOpen.value = !menuOpen.value;
}


function profileClicked() {
	console.log("pfp button clicked")
	if (userStore.isLoggedIn) {
		router.push({ name: 'profile' });
	} else {
		router.push({ name: 'login' });
	}
}

function goTo(routeName: string) {
	menuOpen.value = false;
	router.push({ name: routeName });
}

function openExternal(url: string) {
	menuOpen.value = false;
	window.open(url, "_blank");
}




</script>

<template>
	<div class="header">
		<div class="inner">
			<div class="first">
				<div class="first__icon" @click="toggleMenu">
					<i class="pi pi-bars"></i>
				</div>

			</div>
			
			<RouterLink :to="{ name: 'home' }" class="link">
				
				<div class="tiles">
					<div v-for="l in ['S', 'C', 'R', 'A', 'B', 'B', 'L', 'E']" :key="l" class="tile">
						{{ l }}
					</div>
				</div>
			</RouterLink>

			<div class="end">
				<button class="user-btn" @click="profileClicked">
					<div class="user">

						<!-- TODO: eventually add functionality for custom pfps etc..-->
						<img :src="userStore.userData?.profilePicture || '/profile.png'" alt="User Profile Picture" />
					</div>
				</button>
			</div>
		</div>
	</div>
	<div class="menu-backdrop">
		<div class="menu__container" :class="{ 'menu--active': menuOpen }" @click.stop>
			<div class="menu">
				<button class="menu-item" @click="toggleMenu">
					<i class="pi pi-times out__icon"></i>
					<span>Close</span>
				</button>

				<button class="menu-item" :class="{ active: route.name === 'home' }" @click="goTo('home')">
					<i class="pi pi-home"></i>
					<span>Home</span>
				</button>

				<button class="menu-item" @click="openExternal('https://www.scrabble-solver.com/')">
					<i class="pi pi-search"></i>
					<span>Word Finder</span>
				</button>

				<button class="menu-item" @click="openExternal('https://scrabblewordfinder.org/dictionary-checker')">
					<i class="pi pi-book"></i>
					<span>Dictionary</span>
				</button>

				<button class="menu-item" :class="{ active: route.name === 'shop' }" @click="goTo('shop')">
					<i class="pi pi-shopping-cart"></i>
					<span>Shop</span>
				</button>

				<button class="menu-item" :class="{ active: route.name === 'friends' }" @click="goTo('friends')">
					<i class="pi pi-users"></i>
					<span>Friends</span>
				</button>
			</div>
		</div>
	</div>
</template>


<style lang="css" scoped>
.header {
	user-select: none;
	position: sticky;
	top: 0;
	z-index: 1000;

	width: 100%;
	background: rgba(20, 20, 20, 0.35);
	-webkit-backdrop-filter: blur(16px);
	backdrop-filter: blur(10px);

	display: flex;
	justify-content: center;

	padding-block: 1rem;
	color: white;
	border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.title {
	font-size: 1.5em;
	font-weight: 600;
	color: var(--text-colour);
}

.link {
	text-decoration: none;
	color: var(--text-colour);
	transition: 0.2s ease all;
}

.link:hover {
	color: black;
}


.end {
	display: flex;
	gap: .5rem;
}




.inner {
	display: flex;
	justify-content: space-between;
	align-items: center;
	width: 95%;
}

.first {
	display: flex;
	align-items: center;
	gap: 1rem;
}

.link {
	color: inherit;
	text-decoration: none;
}

.first__icon {
	font-size: 1.25rem;
	cursor: pointer;
	display: flex;
	align-items: center;
}

.tiles {
	display: flex;
	align-items: center;
	gap: 4px;
	margin: 0;
}

.tile {
	width: 24px;
	height: 24px;
	font-size: 0.8rem;
	background-color: var(--tile-background-colour);
	color: var(--tile-text-colour);
	font-weight: bold;
	border-radius: 4px;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 2px 0 #c9b48d, 0 3px 6px rgba(0, 0, 0, 0.25);
}



.user-btn {
	background: transparent;
	border: none;
	cursor: pointer;
	padding: 0;
}

.user {
	width: 40px;
	height: 40px;
	border-radius: 50%;

	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.25);
	transition: transform 0.2s;
	background: rgba(255, 255, 255, 0.08);
	backdrop-filter: blur(10px);
	border-bottom: 1px solid rgba(255, 255, 255, 0.15);
	box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.user img {
	width: 100%;
	height: 100%;
	object-fit: cover;
	display: block;
	border-radius: 50%;
}

.user-btn:hover .user {
	transform: scale(1.1);
}

.menu__container {
	user-select: none;
	position: fixed;
	top: 0;
	left: 0;
	transform: translateX(-100%);
	width: 280px;
	height: 100%;
	/* -webkit-backdrop-filter: blur(16px); */
	/* backdrop-filter: blur(10px); */
	transition: all 0.25s ease;
	z-index: 2000;

	box-shadow: 8px 0 30px rgba(0, 0, 0, 0.4);
	background-color: rgba(20, 20, 20, 0.8);
}

.menu-backdrop {
	position: fixed;
	top: 0;
	left: 0;
	z-index: 1500;
}

@keyframes fadeIn {
	from {
		opacity: 0
	}

	to {
		opacity: 1
	}
}

.menu--active {
	transform: translateX(0);

}

.menu {
	margin-top: 1rem;
	display: flex;
	flex-direction: column;
	gap: 0.5rem;

}

.out {
	padding: 1rem;
	color: black;
}

.out__icon {
	font-size: 1.4rem;
	cursor: pointer;
}

.menu-item:first-child {
	color: #ff4d4d;
	margin-bottom: 0.5rem;
	border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.menu-item:first-child i {
	color: #ff4d4d;
}

.menu-item {
	display: flex;
	align-items: center;
	gap: 1rem;

	width: 90%;
	padding: 0.9rem 1.2rem;

	background: transparent;
	border: none;
	color: white;
	font-size: 1rem;
	text-align: left;
	font-weight: bold;

	cursor: pointer;
	border-radius: 10px;
	transition: all 0.2s ease;
}

.menu-item i {
	font-size: 1.2rem;
	color: #4d94ff;
}

.menu-item:hover {
	background: rgba(77, 148, 255, 0.15);
	transform: translateX(6px);
}

.menu-item:active {
	transform: scale(0.97);
}

.menu-item.active {
	background: rgba(255, 255, 255, 0.616);
}
</style>