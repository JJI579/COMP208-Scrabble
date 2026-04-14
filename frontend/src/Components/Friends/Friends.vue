<script lang="ts" setup>
import api from '@/api';
import { onMounted, ref, watch, computed } from 'vue';

// Important components for the friends page
const users = ref<any>([]);
const friends = ref<any>([]);
const currentUser = ref<any>(null);
const searchUser = ref("");
const myRequests = ref<any>([]);
const requestedUsers = ref<Set<number>>(new Set());
const mode = ref<"idle" | "search" | "requests">("idle");


// Function for searching users based on the search input.
function userSearch() {
	fetchPeople();
}

// Fetches the list of users (additionally takes the search query as a parameter to filter results)
async function fetchPeople() {
	const res = await api.get('/users/players', {
		params: {
			search: searchUser.value
		}
	})
	console.log(res.data);
	users.value = res.data;
}

// Fetching the list of friends for the current user
async function fetchFriends() {
	const res = await api.get('/friends/myFriends', {
		params: {
			limit: 1000
		}
	});
	console.log(res.data);
	friends.value = res.data;
}

// Fetching outselves
async function getCurrentUser() {
	const res = await api.get('/users/@me');
	console.log(res.data);
	currentUser.value = res.data;
}

// Sending a friend request to another user based on their userID
async function sendFriendRequest(userID: number) {
	console.log(currentUser.value.userID, "is sending friend request to userID: ", userID);
	await api.post('/friends/request', {
		toUserID: userID
	});

	requestedUsers.value.add(userID);
}

// Fetching the list of incoming friend requests for the user
async function checkRequests() {
	const res = await api.get('/friends/requests');
	myRequests.value = res.data;
	console.log(res.data);
}

// Fetching the list of sent friend requests
async function getSentRequests() {
	const res = await api.get('/friends/sent');
	console.log(res.data);
	requestedUsers.value = new Set(res.data);

}

// Accepting a friend request based on the userID of the sender
async function acceptRequest(userID: number) {
	await api.post('/friends/accept', {
		toUserID: userID
	});

	myRequests.value = myRequests.value.filter(
		(u: any) => u.userID !== userID
	);
	console.log("accepted friend request from userID:", userID);
}

// Declining the friend request
async function declineRequest(userID: number) {
	await api.post('/friends/decline', {
		toUserID: userID
	});

	myRequests.value = myRequests.value.filter(
		(u: any) => u.userID !== userID
	);
	console.log("Declined friend request from userID:", userID);
}

// Running these functions when the page loads to fetch the necessary data
onMounted(() => {
	getCurrentUser();
	checkRequests();
	getSentRequests();
	fetchFriends();
})

// Watching the search input for changes to update the displayed user list
watch(searchUser, (value) => {
	if (value.trim() === "") {
		mode.value = "idle";
		return;
	}

	mode.value = "search";
	userSearch();
})

// Function to show incoming friend requests when the button is clicked
function showRequests() {
	mode.value = "requests";
}

function challengeToGame() {
	console.log("Challenge to game button clicked");
}

function inviteToGame() {
	console.log("Invite to team game button clicked");
}

// Filtering the users to display (excliding friends and the current user)
const filteredUsers = computed(() => {
	if (!currentUser.value) return users.value;

	return users.value
		.filter((user: any) => user.userID !== currentUser.value.userID)
		.filter((user: any) =>
			!friends.value.some((friend: any) => friend.userID === user.userID)
		)
		.filter((user: any) =>
			!myRequests.value.some((request: any) => request.userID === user.userID)
		);
});

// Deciding which users to display based on the current mode
const displayUsers = computed(() => {
	if (mode.value === "idle") return friends.value;
	if (mode.value === "search") return filteredUsers.value;
	if (mode.value === "requests") return myRequests.value;
	return [];
});

</script>



<template>
	<h1 class="title"> Friends </h1>

	<div class="container">
		<div class="userChoiceBar">
			<input type="text" placeholder="Search people... " v-model="searchUser" class="searchInput"></input>

			<div class="requestsButton">
				<button @click="showRequests()">Requests {{ myRequests.length }}</button>
			</div>
		</div>

		<!-- If the user has no friends and theyre in the idle mode print this -->
		<div v-if="mode === 'idle' && friends.length === 0" class="emptyState">
			<p>Search for users or view requests</p>
		</div>


		<div v-else class="users">
			<div v-for="user in displayUsers" :key="user.userID" class="userCard">

				<div class="profilePicture">
					<i class="pi pi-user"></i>
				</div>

				<div class="userName">
					{{ user.userName }}
				</div>

				<button v-if="mode === 'search'" class="addFriend" @click="sendFriendRequest(user.userID)"
					:disabled="requestedUsers.has(user.userID)">
					{{ requestedUsers.has(user.userID) ? "Request is sent!" : "Add Friend" }}
				</button>

				<div v-if="mode === 'requests'" class="requestActions">
					<button class="acceptButton" @click="acceptRequest(user.userID)">
						Accept
					</button>
					<button class="declineButton" @click="declineRequest(user.userID)">
						Decline
					</button>
				</div>

				<div v-if="mode === 'idle'" class="myFriends">
					<button class="challengeButton" @click="challengeToGame()">
						Challenge to Game
					</button>
					<button class="teamGameButton" @click="inviteToGame()">
						Invite to Team Game
					</button>
				</div>
			</div>
		</div>
	</div>

</template>


<style lang="css" scoped>
.container {
	max-width: 1100px;
	margin: 0 auto;
	padding: 2rem;
}

.title {
	font-size: 2.5rem;
	font-weight: 700;
	text-align: center;
	color: var(--title-colour);
	user-select: none;
}

.userChoiceBar {
	display: flex;
	align-items: center;
	gap: 1rem;
	margin-bottom: 2rem;
}

.searchInput {
	flex: 1;
	padding: 0.7rem 1rem;
	border-radius: 12px;
	border: none;
	outline: none;

	background: rgba(255, 255, 255, 0.08);
	color: white;

	backdrop-filter: blur(6px);
	transition: 0.2s;
}

.searchInput::placeholder {
	color: rgba(255, 255, 255, 0.5);
}

.searchInput:focus {
	background: rgba(255, 255, 255, 0.12);
}

.requestsButton button,
.selectButton {
	padding: 0.6rem 1rem;
	border-radius: 10px;
	border: none;

	background: rgba(255, 255, 255, 0.08);
	color: white;

	cursor: pointer;
	transition: 0.2s;
}

.requestsButton button:hover,
.selectButton:hover {
	background: rgba(255, 255, 255, 0.18);
}

.emptyState {
	text-align: center;
	margin-top: 3rem;
	color: rgba(255, 255, 255, 0.5);
	font-size: 1.2rem;
}

/* GRID */
.users {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
	gap: 1.5rem;
}

/* CARD */
.userCard {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: space-between;

	padding: 1.5rem 1rem;
	border-radius: 18px;

	background: rgba(255, 255, 255, 0.06);
	backdrop-filter: blur(12px);

	box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
	transition: 0.25s;
	min-height: 240px;
}

.userCard:hover {
	transform: translateY(-6px);
	background: rgba(255, 255, 255, 0.12);
}

/* AVATAR */
.profilePicture {
	font-size: 3rem;
	color: rgba(255, 255, 255, 0.8);
	margin-bottom: 0.8rem;
}

/* USERNAME */
.userName {
	color: white;
	font-weight: 600;
	font-size: 1rem;
	margin-bottom: 1rem;
	text-align: center;
}

/* BUTTON GROUP */
.requestActions {
	display: flex;
	gap: 0.5rem;
	width: 100%;
	justify-content: center;
}

.addFriend {
	padding: 0.4rem 0.8rem;
	border-radius: 8px;
	border: none;

	background: #225ec5;
	color: white;

	cursor: pointer;
	transition: 0.2s;
}

.myFriends {
	display: flex;
	gap: 0.5rem;
	width: 100%;
	justify-content: center;
	flex-direction: column;
}

/* PRIMARY BUTTON */
.challengeButton {
	width: 100%;
	padding: 0.5rem;
	border-radius: 10px;
	border: none;

	background: #3b82f6;
	color: white;

	cursor: pointer;
	transition: 0.2s;
	font-size: 0.9rem;
}

.challengeButton:hover {
	background: #2563eb;
	transform: scale(1.05);
}

.challengeButton:disabled {
	background: gray;
	cursor: not-allowed;
	transform: none;
}

/* SECONDARY BUTTON */
.teamGameButton {
	width: 100%;
	padding: 0.5rem;
	border-radius: 10px;
	border: none;

	background: rgba(255, 255, 255, 0.15);
	color: white;

	cursor: pointer;
	transition: 0.2s;
}

.teamGameButton:hover {
	background: rgba(255, 255, 255, 0.25);
}

/* ACCEPT */
.acceptButton {
	flex: 1;
	padding: 0.4rem;
	border-radius: 8px;
	border: none;

	background: #22c55e;
	color: white;

	cursor: pointer;
	transition: 0.2s;
}

.acceptButton:hover {
	background: #16a34a;
	transform: scale(1.05);
}

/* DECLINE */
.declineButton {
	flex: 1;
	padding: 0.4rem;
	border-radius: 8px;
	border: none;

	background: #ef4444;
	color: white;

	cursor: pointer;
	transition: 0.2s;
}

.declineButton:hover {
	background: #dc2626;
	transform: scale(1.05);
}
</style>