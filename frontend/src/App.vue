<script setup lang="ts"></script>

<template>
	<div class="header">
		<RouterLink to="/login">Login</RouterLink>
	</div>
	<div class="content">

		<RouterView />
	</div>
</template>

<style scoped>
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
