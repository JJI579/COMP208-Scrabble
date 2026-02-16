<script lang="ts" setup>
import { computed, onMounted, ref, useTransitionState, watch } from 'vue';
import InputField from './InputField.vue';
import api from '@/api';

import type { LoginReturn } from '@/types';
import { useRoute, useRouter } from 'vue-router';
import useUserStore from '../Stores/user';

const usernameModel = ref('');
const passwordModel = ref('');
const triedSubmit = ref(false);
const errorMessage = ref('');
const currentSelection = ref('login');

const router = useRouter();
const route = useRoute();

const userStore = useUserStore();


onMounted(() => {
	if (route.query.register) {
		currentSelection.value = "register"
	}
})

watch(() => userStore.isLoggedIn, () => {
	if (userStore.isLoggedIn) {
		// if logged in force to dashboard
		router.push({ name: "dashboard" })
	}
})

async function login() {
	console.log("Tried")
	if (usernameModel.value.length == 0 || passwordModel.value.length == 0) return triedSubmit.value = true;
	const data = {
		username: usernameModel.value,
		password: passwordModel.value
	}

	const resp = await api.post('/auth/login', data);
	console.log(resp)
	const { id, token, refresh_token, expires_at }: LoginReturn = resp.data;
	localStorage.setItem("refresh_token", refresh_token)
	localStorage.setItem("token", token)
	router.push({ name: "dashboard" })
	// This should work as all tokens have been pushed etc
	setTimeout(() => {
		userStore.login()
	}, 500);
}

async function register() {
	if (usernameModel.value.length == 0 || passwordModel.value.length == 0) return triedSubmit.value = true;
	const data = {
		username: usernameModel.value,
		password: passwordModel.value
	}
	try {
		const resp = await api.post('/auth/register', data);
		return await login();
	} catch (error: any) {
		const errorData = error.response?.data;
		if (errorData) {
			const errorDetail = errorData.detail;
			if (errorDetail) {
				errorMessage.value = errorDetail
			}
		} else {
			console.log(error);
		}
	}
}

async function handleSubmit() {
	if (currentSelection.value == 'login') {
		await login();
	} else {
		await register();
	}
}

const d = computed(() => {
	return window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
})
</script>



<template>

	<!-- Login / register page! -->

	<div class="content">
		<div class="form">

			<div class="title__container">
				<div class="title__options">
					<h2 class="title">Let's get you Playing!</h2>
					<div class="option">
						<span @click="currentSelection = 'login'" class="clickable">Sign in</span> or <span
							@click="currentSelection = 'register'" class="clickable">create an account.</span>
					</div>
				</div>
				<div class="logo__container">
					<img src="" alt="" class="logo">
				</div>

			</div>
			<div class="error" v-if="errorMessage.length > 0">
				{{ errorMessage }}
			</div>
			<InputField v-model:input="usernameModel" :placeholder="'Username'" :show-error="triedSubmit" />
			<InputField v-model:input="passwordModel" :placeholder="'Password'" :type="'password'"
				:show-error="triedSubmit" />
			<div class="submit" @click="handleSubmit">
				<div class="submit__text">
					{{ currentSelection == 'login' ? 'Login' : 'Register' }}
				</div>
			</div>
			<div class="no__lose">
				<p>Don't lose your progress!</p>
				<p @click="currentSelection = 'register'" class="clickable">Create an Account!</p>
			</div>
		</div>
	</div>
</template>


<style lang="css" scoped>
.content {
	display: flex;
	justify-content: center;
	align-items: center;
	/* background-color: blue; */
	height: 90%;
}

.form {
	height: 75%;
	width: 70%;

	background-color: whitesmoke;
	border: 1px solid whitesmoke;
	border-radius: 10px;
	padding: 1rem;

	display: flex;
	align-items: center;
	flex-direction: column;
	gap: .75rem;
}

.title {
	margin-bottom: 3rem;
}

.text {
	margin-right: auto;
	width: fit-content;
	padding: .5rem;
	border-radius: 10px;
	color: #5865f2;
	font-weight: 500;
}

.submit {
	margin-top: 1.5rem;
	width: 80%;
	display: flex;
	justify-content: center;
	align-items: center;
	border-radius: 20px;
	background-color: #5865f2;
	color: white;
	cursor: pointer;
	font-weight: 500;
	font-size: 1rem;
	padding: 0.6em 0.8em;
}


.title__container {
	display: flex;
	justify-content: space-between;
	align-items: top;
	/* background-color: pink; */
	width: 80%;
	margin-bottom: 2rem;
}

.title__options {
	display: flex;
	flex-direction: column;
	/* background-color: blue; */
}

.title {
	padding: 0;
	margin: 0;
	margin-block: 1rem;
}

.option {
	display: flex;
	width: 100%;
	gap: .25rem;
}

.logo__container {
	margin-top: 1rem;
	height: 48px;
	width: 48px;
}

.logo {
	height: 100%;
	width: 100%;
	object-fit: cover;
}

.no__lose {
	text-align: left;
	width: 80%;

}

.clickable {
	cursor: pointer;
	text-decoration: underline;
}

@media (max-width: 999px) {
	.content {
		width: 80%;
	}

	.form {
		width: 75%;
	}
}
</style>