<script lang="ts" setup>
import router from '../../router';
import api from '../../api';
import { ref} from 'vue';
import useUserStore from '@/Components/Stores/user';


const username = ref('');
const confirmUsername = ref('');
const hasChecked = ref(false);
const error = ref('');
const userStore = useUserStore();


async function changeUsername() {

    hasChecked.value = true;
    if (username.value === '' || confirmUsername.value === '') {
        error.value = 'Please fill in all fields.';
        console.log(error.value);
        return;
    }

    if (username.value !== confirmUsername.value) {
        error.value = 'Usernames do not match.';
        console.log(error.value);
        return;
    }

    if (username.value === userStore.userData?.userName) {
        error.value = 'New username must be different from the current username.';
        console.log(error.value);
        return;
    }

    console.log("Changing username to ", username.value);

    try {
        await api.post('/users/changeUsername/@me?new_username=' + username.value);
        router.push({ name: 'settings' });
    }
    catch (err: any) {
        if (err.response?.data?.detail) {
            error.value = err.response.data.detail;
            return;
        }
    }
}

</script>



<template>
    <div class="content">
    
        <h2>Change Username</h2>

        <div class="alert" v-if="error">
			<span class="pi pi-exclamation-circle icon"></span>
		    <h4>{{ error }}</h4>
        </div>
    
        <div class="settingItems">
            <h3>New Username:</h3>
            <input class="form__input" type="text" v-model="username" name="username"
				:class="{ error: username == '' && hasChecked }" />
            <h3>Confirm New Username:</h3>
            <input class="form__input" type="text" v-model="confirmUsername" name="confirmUsername"
				:class="{ error: confirmUsername == '' && hasChecked }" />
            <br>
            <button class="form__button" @click="changeUsername()">Change Username</button>
        </div>
    
    </div>
</template>



<style lang="css" scoped>
.content {
	height: 100%;
	width: 100%;
	padding: 2rem;
	display: flex;
	flex-direction: column;
	align-items: center;
}

h2 {
	font-size: 2rem;
	color: var(--title-colour);
	text-align: center;
	margin-bottom: 2rem;
}

.settingItems {
	width: 100%;
	max-width: 700px;
	background: linear-gradient(135deg, #2a4d8f, #4169a9);
	border-radius: 14px;
	padding: 2rem;
	display: flex;
	flex-direction: column;
	gap: 0.8rem;

	box-shadow:
		0 8px 20px rgba(0, 0, 0, 0.3),
		0 0 15px rgba(77, 148, 255, 0.2);
}

.settingItems h3 {
	margin: 0;
	color: white;
	font-size: 1rem;
	font-weight: 500;
}

.form__input {
	width: 100%;
	padding: 0.9rem 1rem;
	border: 2px solid transparent;
	border-radius: 10px;
	outline: none;
	font-size: 1rem;
	background: rgba(255, 255, 255, 0.95);
	color: #1a1a1a;
	transition: 0.2s ease;
	box-sizing: border-box;
}

.form__input:focus {
	border-color: #80c0ff;
	box-shadow: 0 0 10px rgba(128, 192, 255, 0.3);
}

.form__input.error {
	border: 2px solid #d64545;
	background: #fff5f5;
}

.form__button {
	background: linear-gradient(135deg, #838f2a, #199a26);
	border: none;
	color: white;
	padding: 0.9rem 2rem;
	border-radius: 12px;
	cursor: pointer;
	font-size: 1rem;
	font-weight: 600;
	transition: 0.25s ease;

	box-shadow:
		0 8px 20px rgba(0, 0, 0, 0.25),
		0 0 12px rgba(77, 148, 255, 0.15);
}

.form__button:hover {
	transform: translateY(-2px);
	background: linear-gradient(135deg, #2f340f, #08330c);
	box-shadow:
		0 10px 24px rgba(0, 0, 0, 0.35),
		0 0 18px rgba(77, 148, 255, 0.3);
}

.alert {
	width: 100%;
	max-width: 700px;
	margin-bottom: 1.5rem;
	padding: 1rem 1.2rem;
	border-radius: 12px;

	background: linear-gradient(135deg, #8f2a2a, #b13a3a);
	color: white;

	display: flex;
	align-items: center;
	gap: 0.8rem;

	box-shadow:
		0 8px 20px rgba(0, 0, 0, 0.25),
		0 0 15px rgba(255, 77, 77, 0.15);
}

.alert h4 {
	margin: 0;
	font-weight: 500;
	font-size: 0.95rem;
}

.icon {
	font-size: 1.2rem;
	color: #ffd6d6;
}
</style>