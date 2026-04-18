<script lang="ts" setup>
import router from '../../router';
import api from '../../api';
import { ref} from 'vue';
import useUserStore from '@/Components/Stores/user';

const currentPassword = ref('');
const newPassword = ref('');
const confirmNewPassword = ref('');
const error = ref('');
const userStore = useUserStore();

const showCurrentPassword = ref(false);
const showNewPassword = ref(false);
const showConfirmNewPassword = ref(false);


async function changePassword() {
  if (currentPassword.value === '' || newPassword.value === '' || confirmNewPassword.value === '') {
    error.value = 'Please fill in all fields.';
    return;
  }

  try {
    const res = await api.post('/auth/verifyPassword/@me?password=' + currentPassword.value);
    if (!res.data) {
        error.value = "Current password is incorrect.";
        return;
    }
  } catch (err: any) {
    if (err.response?.data?.detail) {
        console.log("Error checking with the current password:", err.response.data.detail);
        error.value = 'Current password is incorrect';
    }
  }

  if (newPassword.value !== confirmNewPassword.value) {
    error.value = 'New passwords do not match.';
    return;
  }

  if (String(newPassword.value).length < 8) {
    error.value = 'New password must be at least 8 characters long.';
    return;
  }

  if (currentPassword.value === newPassword.value) {
    error.value = 'New password must be different from the current password.';
    return;
  }

  console.log("Changing password for user:", userStore.userData?.userName);

  try {
    await api.post('/auth/changePassword/@me?new_password=' + newPassword.value);
    router.push({ name: 'settings' });
  }
  catch (err: any) {
    if (err.response?.data?.detail) {
        console.log("Error changing password:", err.response.data.detail);
        error.value = err.response.data.detail;
        return;
    }
  }
}
</script>



<template>

    <div class="content">
    
        <h2>Change Password</h2>

        <div class="alert" v-if="error">
            <span class="pi pi-exclamation-circle icon"></span>
            <h4>{{ error }}</h4>
        </div>
    
        <div class="settingItems">
            <h3>Current Password:</h3>
            <div class="passwordField">
                <input class="form__input" :type="showCurrentPassword ? 'text' : 'password'" v-model="currentPassword" name="currentPassword" />
                <span class="pi" :class="showCurrentPassword ? 'pi-eye-slash' : 'pi-eye'" @click="showCurrentPassword = !showCurrentPassword"></span>
            </div>

            <h3>New Password:</h3>
            <div class="passwordField">
                <input class="form__input" :type="showNewPassword ? 'text' : 'password'" v-model="newPassword" name="newPassword" />
                <span class="pi" :class="showNewPassword ? 'pi-eye-slash' : 'pi-eye'" @click="showNewPassword = !showNewPassword"></span>
            </div>
        
            <h3>Confirm New Password:</h3>
            <div class="passwordField">
                <input class="form__input" :type="showConfirmNewPassword ? 'text' : 'password'" v-model="confirmNewPassword" name="confirmNewPassword" />
                <span class="pi" :class="showConfirmNewPassword ? 'pi-eye-slash' : 'pi-eye'" @click="showConfirmNewPassword = !showConfirmNewPassword"></span>
            </div>
        
            <br>
            <button class="form__button" @click="changePassword()">Change Password</button>
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

/* Page title */
h2 {
	font-size: 2rem;
	color: var(--title-colour);
	text-align: center;
	margin-bottom: 2rem;
}

/* Error alert */
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
	font-size: 0.95rem;
	font-weight: 500;
}

.icon {
	font-size: 1.2rem;
	color: #ffd6d6;
}

/* Main card */
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

/* Labels */
.settingItems h3 {
	margin: 0;
	color: white;
	font-size: 1rem;
	font-weight: 500;
}

/* Password field wrapper */
.passwordField {
	position: relative;
	display: flex;
	align-items: center;
	width: 100%;
}

/* Input */
.form__input {
	width: 100%;
	padding: 0.9rem 3rem 0.9rem 1rem;
	border: 2px solid transparent;
	border-radius: 10px;
	outline: none;
	font-size: 1rem;
	background: rgba(255, 255, 255, 0.95);
	color: #1a1a1a;
	box-sizing: border-box;
	transition: 0.2s ease;
}

.form__input:focus {
	border-color: #80c0ff;
	box-shadow: 0 0 10px rgba(128, 192, 255, 0.3);
}

/* Eye icon */
.passwordField .pi {
	position: absolute;
	right: 1rem;
	cursor: pointer;
	font-size: 1.1rem;
	color: #2a4d8f;
	transition: 0.2s ease;
}

.passwordField .pi:hover {
	transform: scale(1.08);
	color: #4169a9;
}

/* Button */
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
</style>