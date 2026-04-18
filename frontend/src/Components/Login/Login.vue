<script lang="ts" setup>
import { computed, onMounted, ref, watch } from 'vue';
import InputField from './InputField.vue';
import api from '@/api';

import type { LoginReturn } from '@/types';
import { useRoute, useRouter } from 'vue-router';
import useUserStore from '../Stores/user';
import Logger from '@/logging/Logger';

const usernameModel = ref('');
const passwordModel = ref('');
const triedSubmit = ref(false);
const errorMessage = ref('');
const currentSelection = ref('login');

const router = useRouter();
const route = useRoute();

const userStore = useUserStore();

const rememberMe = ref(false);


onMounted(() => {
	if (route.query.register) {
		currentSelection.value = "register"
	}
	if (userStore.isLoggedIn) {
		// if logged in force to dashboard
		router.push({ name: "dashboard" })
	}

})

watch(() => userStore.isLoggedIn, () => {
	if (userStore.isLoggedIn) {
		// if logged in force to dashboard
		router.push({ name: "dashboard" })
	}
})

async function login() {
	const loginLogger = new Logger("login")
	if (usernameModel.value.length == 0 || passwordModel.value.length == 0) return triedSubmit.value = true;
	const data = {
		username: usernameModel.value,
		password: passwordModel.value
	}

	const resp = await api.post('/auth/login', data);
	loginLogger.info("Login successful")
	const { id, token, refresh_token, expires_at }: LoginReturn = resp.data;
	localStorage.setItem("refresh_token", refresh_token)
	localStorage.setItem("token", token)
	// Remember me logic
	if (rememberMe.value) {
		localStorage.setItem("token", token)
		localStorage.setItem("refresh_token", refresh_token)
	} else {
		sessionStorage.setItem("token", token)
		sessionStorage.setItem("refresh_token", refresh_token)

	}
	router.push({ name: "dashboard" })
	loginLogger.info("Taken to dashboard")
	// This should work as all tokens have been pushed etc
	setTimeout(() => {
		userStore.login()
	}, 500);
}


async function register() {
	const registerLogger = new Logger("register")
	if (usernameModel.value.length == 0 || passwordModel.value.length == 0) return triedSubmit.value = true;
	const data = {
		username: usernameModel.value,
		password: passwordModel.value
	}
	try {
		const resp = await api.post('/auth/register', data);
		registerLogger.info("Register successful | " + resp)
		return await login();
	} catch (error: any) {
		const errorData = error.response?.data;
		if (errorData) {
			const errorDetail = errorData.detail;
			if (errorDetail) {
				errorMessage.value = errorDetail
				registerLogger.error("Error: " + errorMessage.value)
			}
		} else {
			registerLogger.error("Error: " + error)
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

function toggleMode() {
	currentSelection.value =
		currentSelection.value === 'login' ? 'register' : 'login';
}
</script>



<template>

	<!-- Login / register page! -->

	<div class="content">
		<form class="form" @submit.prevent="handleSubmit">
			<div class="title__container">
				<div class="title__options">
					<h2 class="title">Let's get you Playing!</h2>
				</div>
				<div class="logo__container"></div>

			</div>
			<div class="error" v-if="errorMessage.length > 0">
				{{ errorMessage }}
			</div>
			<InputField v-model:input="usernameModel" :placeholder="'Username'" :show-error="triedSubmit" />
			<InputField v-model:input="passwordModel" :placeholder="'Password'" :type="'password'"
				:show-error="triedSubmit" />
			<label class="remember">
				<input type="checkbox" v-model="rememberMe" />
				Remember me
			</label>
			<button type="submit" class="submit">
				<div class="submit__text">
					{{ currentSelection == 'login' ? 'Login' : 'Register' }}
				</div>
			</button>
			<div class="no__lose">
				<p v-if="currentSelection === 'login'">
					Don't lose your progress!
				</p>

				<p v-else>
					Already have an account?
				</p>

				<p class="clickable" @click="toggleMode">
					{{ currentSelection === 'login' ? 'Create an Account' : 'Sign in' }}
				</p>
			</div>
		</form>
	</div>
</template>


<style lang="css" scoped>
.form {
	width: 100%;
	display: flex;
	align-items: center;
	flex-direction: column;
	gap: 0.8rem;
	padding-top: 0.5rem;
}
input {
	margin: 0;
}

.title {
	display: none;
}

.option {
	width: 100%;
	display: flex;
	justify-content: center;
	align-items: center;
	gap: 0.4rem;
	text-align: center;
	font-size: 0.9rem;
	color: rgba(255,255,255,0.7);
}

.text {
	margin-right: auto;
	padding: .4rem .6rem;
	border-radius: 8px;
	color: #9aa4ff;
	cursor: pointer;
	transition: 0.2s;
}

.text:hover {
	background: rgba(255, 255, 255, 0.1);
}

.submit {
	margin-top: 1rem;
	width: 100%;
	border-radius: 12px;
	background: linear-gradient(135deg, #5865f2, #7b86ff);
	color: white;
	cursor: pointer;
	font-weight: 600;
	font-size: 1rem;
	padding: 0.75em;
	transition: 0.2s ease all;
	text-align: center;
	border: none;
}


.title__container {
	display: flex;
	align-items: flex-start;
	/* background-color: pink; */
	width: 80%;
	margin-bottom: -5rem;
	margin-left: 40px;
}
.title__options {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	width: 100%;
	text-align: center;
}

.option {
	display: flex;
	justify-content: center;
	align-items: center;
	gap: 0.35rem;
	font-size: 0.9rem;
	color: rgba(255,255,255,0.7);

	white-space: nowrap;
	flex-wrap: nowrap;
	width: 100%;
}


.title {
	padding: 0;
	margin: 0;
	margin-block: 1rem;
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
	text-align: center;
	width: 80%;
	margin-top: 1rem;
	padding-top: 1rem;
	border-top: 1px solid rgba(255,255,255,0.1);
}

.no__lose p {
	margin: 0.3rem 0;
	color: rgba(255,255,255,0.7);
	font-size: 0.85rem;
}
.no__lose .clickable {
	display: inline-block;
	margin-top: 0.3rem;
	color: #9aa4ff;
	font-weight: 500;
}

.clickable {
	cursor: pointer;
	color: #9aa4ff;
	text-decoration: none;
	padding: 0.2rem 0.5rem;
	border-radius: 8px;
	transition: 0.2s;
	border: 1px solid transparent;
}

.clickable:hover {
	background: rgba(123, 134, 255, 0.15);
	border: 1px solid rgba(123, 134, 255, 0.3);
	color: white;
}

@media (max-width: 999px) {
	.content {
		width: 80%;
	}

	.form {
		width: 75%;
	}
}

.submit:hover {
	transform: translateY(-2px);
	box-shadow: 0 10px 25px rgba(88, 101, 242, 0.35);
}

.error {
	width: 100%;
	background: rgba(255, 0, 0, 0.15);
	border: 1px solid rgba(255, 0, 0, 0.3);
	color: #ffb3b3;
	padding: .6rem;
	border-radius: 8px;
}

.remember {
	width: 100%;
	display: flex;
	align-items: center;
	gap: .5rem;
	color: #9aa4ff;
	font-size: 0.9rem;
	margin-top: .5rem;
}
</style>