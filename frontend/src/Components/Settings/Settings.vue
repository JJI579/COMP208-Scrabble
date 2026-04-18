
<script lang="ts" setup>
import router from '../../router';
import api from '../../api';
import { ref} from 'vue';



function logout() {
	localStorage.removeItem('token');
	localStorage.removeItem('refresh_token');
	localStorage.removeItem('userID');
	router.push({ name: 'home' });
}

async function deleteAccount() {
	try {
		await api.delete('/users/delete/@me');
		logout();
	} catch (error) {
		console.error('Error deleting account:', error);
	}
}

const showOptions = ref(false);
function toggleOptions() {
  showOptions.value = !showOptions.value;
}

</script>


<template>
	<div class="content">

		<h2 class="settings">Settings</h2>

		<div class="settingItems">
      		<p class="setting__item" @click="router.push( { name: 'changeUsername' })">Change Username</p>
			<p class="setting__item" @click="router.push({ name: 'changePassword' })">Change Password</p>
			<p class="setting__item" @click="toggleOptions()">Delete Account</p>
		</div>

    <Teleport to="body">
			<div class="popup__wrapper" v-if="showOptions">
				<div class="popup">
					<div class="popup__content">
						<p class="popup__button__delete" @click="deleteAccount">
                            Yes, I want to delete my account
                        </p>
						<hr class="popup__hr">
						<button class="popup__button" @click="toggleOptions">
                            No, take me back
                        </button>
					</div>
				</div>
			</div>
		</Teleport>


    <div class="logoutSection">
      <button class="logoutButton" @click="logout()">Logout</button>
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

/* Title */
.settings {
	font-size: 2rem;
	color: var(--title-colour);
	text-align: center;
	margin-bottom: 2rem;
}

/* Settings container */
.settingItems {
	width: 100%;
	max-width: 700px;
	display: flex;
	flex-direction: column;
	/* gap: 0.5rem; */
}

/* Individual setting cards */
.setting__item {
	background: linear-gradient(135deg, #2a4d8f, #4169a9);
	border-radius: 14px;
	padding: 1.2rem 1.5rem;
	color: white;
	font-size: 1rem;
	font-weight: 500;
	cursor: pointer;
	transition: 0.25s ease;

	box-shadow:
		0 8px 20px rgba(0, 0, 0, 0.3),
		0 0 15px rgba(77, 148, 255, 0.2);
}

.setting__item:hover {
	transform: translateY(-2px);
	background: linear-gradient(135deg, #315aa3, #4a79c2);
	box-shadow:
		0 10px 24px rgba(0, 0, 0, 0.35),
		0 0 18px rgba(77, 148, 255, 0.3);
}

/* Delete account styling */
.setting__item:last-child {
	background: linear-gradient(135deg, #8f2a2a, #b13a3a);
	box-shadow:
		0 8px 20px rgba(0, 0, 0, 0.3),
		0 0 15px rgba(255, 77, 77, 0.2);
}

.setting__item:last-child:hover {
	background: linear-gradient(135deg, #a83232, #c94444);
	box-shadow:
		0 10px 24px rgba(0, 0, 0, 0.35),
		0 0 18px rgba(255, 77, 77, 0.3);
}

/* Logout section */
.logoutSection {
	margin-top: 3rem;
	width: 100%;
	display: flex;
	justify-content: center;
	padding-bottom: 2rem;
}

.logoutButton {
	background-color: rgb(183, 1, 1);
	border: 2px solid rgb(140, 0, 0);
	color: white;
	padding: 0.75rem 3rem;
	width: 220px;
	border-radius: 12px;
	cursor: pointer;
	font-size: 1rem;
	font-weight: 600;
	transition: 0.2s ease;
}

.logoutButton:hover {
	background-color: rgb(210, 10, 10);
	transform: translateY(-2px);
}

/* Popup overlay */
.popup__wrapper {
	position: fixed;
	inset: 0;
	display: flex;
	justify-content: center;
	align-items: center;
	background: rgba(0, 0, 0, 0.55);
	backdrop-filter: blur(4px);
	z-index: 999;
}

/* Popup box */
.popup {
	background: linear-gradient(135deg, #1f3f75, #2f5ea8);
	border-radius: 18px;
	padding: 1.5rem;
	width: 90%;
	max-width: 420px;
	box-shadow:
		0 10px 30px rgba(0, 0, 0, 0.4),
		0 0 20px rgba(77, 148, 255, 0.25);
}

/* Tighter spacing */
.popup__content {
	display: flex;
	flex-direction: column;
	gap: 0.5rem; /* reduced from 1rem */
	text-align: center;
}

/* Delete account button */
.popup__button__delete {
	background: linear-gradient(135deg, #8f2a2a, #b13a3a);
	color: white;
	font-weight: 600;
	cursor: pointer;
	padding: 0.9rem;
	border-radius: 10px;
	transition: 0.2s;
}

.popup__button__delete:hover {
	background: linear-gradient(135deg, #a83232, #c94444);
	transform: translateY(-1px);
}

/* Divider smaller */
.popup__hr {
	border: none;
	height: 1px;
	margin: 0.5rem 0;
	background: rgba(255, 255, 255, 0.12);
}

/* Cancel button */
.popup__button {
	background: rgba(255, 255, 255, 0.08);
	border: none;
	color: white;
	padding: 0.9rem;
	border-radius: 10px;
	cursor: pointer;
	font-weight: 500;
	transition: 0.2s;
}

.popup__button__delete,
.popup__button {
	padding: 0.9rem;
	border-radius: 10px;
	margin: 0;
}

.popup__button:hover {
	background: rgba(255, 255, 255, 0.15);
}
</style>