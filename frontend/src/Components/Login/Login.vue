<script lang="ts" setup>
import { computed, onMounted, ref, useTransitionState } from 'vue';
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

const rememberMe = ref(false);


onMounted(() => {
	if (route.query.register) {
		currentSelection.value = "register"
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
	// Remember me logic
	if (rememberMe.value) {
		localStorage.setItem("token", token)
		localStorage.setItem("refresh_token", refresh_token)
	} else {
		sessionStorage.setItem("token", token)
		sessionStorage.setItem("refresh_token", refresh_token)

	}
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
</script>



<template>

	<!-- Login / register page! -->
	<div class="content">
		<div class="form">
			<h2 class="title">Scrabble</h2>
			<div class="error" v-if="errorMessage.length > 0">
				{{ errorMessage }}
			</div>
			<div class="option">
				<div class="text"
					@click="currentSelection == 'login' ? currentSelection = 'register' : currentSelection = 'login'">
					{{ currentSelection == 'login' ? 'Register' : 'Login' }}
				</div>
			</div>
			<InputField v-model:input="usernameModel" :placeholder="'Username'" :show-error="triedSubmit" />
			<InputField v-model:input="passwordModel" :placeholder="'Password'" :type="'password'"
				:show-error="triedSubmit" />
			<label class="remember">
				<input type="checkbox" v-model="rememberMe" />
				Remember me
			</label>
			<div class="submit" @click="handleSubmit">
				<div class="submit__text">
					{{ currentSelection == 'login' ? 'Login' : 'Register' }}
				</div>
			</div>
		</div>
	</div>
</template>


<style lang="css" scoped>
.form {
	width: 100%;
	display: flex;
	align-items: center;
	flex-direction: column;
	gap: 1rem;
}

.title {
	display: none;
}

.option {
	width: 100%;
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
}

.submit:hover {
	transform: translateY(-2px);
	box-shadow: 0 8px 20px rgba(88, 101, 242, 0.4);
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