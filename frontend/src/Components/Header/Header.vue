<script lang="ts" setup>
import { computed, ref, watch } from 'vue';
import useUserStore from '../Stores/user';
import HeaderLink from './HeaderLink.vue';

const userStore = useUserStore();

const menuOpen = ref(false);

function toggleMenu() {
	menuOpen.value = !menuOpen.value;
}


function profileClicked() {
	/* in future go to profile page if signed 
	in or go to login page if not signed in */
	console.log("pfp button clicked");
}


</script>

<template>
	<div class="header">
		<div class="inner">
			<div class="first">
				<div class="first__icon" @click="toggleMenu">
					<i class="pi pi-bars"></i>
				</div>

				<RouterLink :to="{ name: 'home' }" class="link">
					<div class="tiles">
						<div v-for="l in ['S', 'C', 'R', 'A', 'B', 'B', 'L', 'E']" :key="l" class="tile">
							{{ l }}
						</div>
					</div>
				</RouterLink>
			</div>

			<div class="end">
				<button class="user-btn" @click="profileClicked">
					<div class="user">

						<!-- TODO: eventually add functionality for custom pfps etc..-->
						<img :src="userStore.profilePicture || '/profile.png'" alt="User Profile Picture" />
					</div>
				</button>
			</div>
		</div>
	</div>

	<div class="menu__container" :class="{ 'menu--active': menuOpen }">
		<div class="menu">
			<div class="out">
				<i class="pi pi-times out__icon" @click="toggleMenu"></i>
			</div>

			<HeaderLink location="home" name="Home" icon="pi-home" />
			<HeaderLink location="home" name="Word Finder" icon="pi-search" />
			<HeaderLink location="home" name="Dictionary" icon="pi-book" />
			<HeaderLink location="home" name="Shop" icon="pi-shopping-cart" />
			<HeaderLink location="home" name="Friends" icon="pi-users" />
		</div>
	</div>
</template>


<style lang="css" scoped>
.header {
	position: sticky;
	top: 0;
	width: 100%;
	z-index: 999998;
	min-height: 64px;
	background: rgba(255, 255, 255, 0.08);
	backdrop-filter: blur(10px);
	border-bottom: 1px solid rgba(255, 255, 255, 0.15);
	box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
	display: flex;
	justify-content: center;
	align-items: center;
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
	background: #f4e2b8;
	color: #2c2c2c;
	font-weight: bold;
	border-radius: 4px;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 2px 0 #c9b48d, 0 3px 6px rgba(0, 0, 0, 0.25);
}

.end {
	display: flex;
	align-items: center;
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
	overflow: hidden;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.25);
	transition: transform 0.2s;
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
	height: 100%;
	width: 25%;
	background-color: var(--clr-surface-a10);
	position: absolute;
	top: 0;
	left: -30%;
	transition: 0.5s cubic-bezier(0.075, 0.82, 0.165, 1) all;
	z-index: 9999999;
}

.menu--active {
	left: 0;
}

.menu {
	margin: 1rem;
	margin-block: 2rem;
	display: flex;
	flex-direction: column;
	gap: 1rem;
}

.out {
	padding: 1rem;
}

.out__icon {
	font-size: 1.25rem;
	cursor: pointer;
}
</style>