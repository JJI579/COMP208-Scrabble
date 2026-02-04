<script lang="ts" setup>
import { computed, ref, useTransitionState } from 'vue';
import InputField from './InputField.vue';



const usernameModel = ref('');
const passwordModel = ref('');
const ex = computed(() => {
	return window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
})
</script>



<template>

	<!-- Login / register page! -->
	<div class="content">
		<div class="form">
			<h2>Scrabble</h2>
			<InputField v-model:input="usernameModel" :placeholder="'Username'" />
			<InputField v-model:input="passwordModel" :placeholder="'Password'" :type="'password'" />

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

@media (max-width: 999px) {
	.content {
		width: 80%;
		padding: 1rem;
	}

	.form {
		width: 100%;
	}
}
</style>