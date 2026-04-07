<script lang="ts" setup>
import api from '@/api';
import { onMounted, ref, watch } from 'vue';

const users = ref<any>([]);
const searchUser = ref("");

function userSearch() {
	fetchPeople();
}

async function fetchPeople () {
    const res = await api.get('/users/players', {
        params: {
            search: searchUser.value
        }
    })
    console.log(res.data);
    users.value = res.data;
}
// onMounted(() => {
//     fetchPeople();
// })

watch(searchUser, () => {
	userSearch();
})

</script>



<template>
    <h1> This is the Friends page </h1>

    <div class="container">
        <input type="text" placeholder="Search people... " v-model="searchUser"></input>

        <button>Requests</button>

        <select>
      		<option value="totalScore">Filter by Score</option>
    	</select>

        <div class="users">
            <p v-for="user in users" :key="user.userID">{{ user.userName }}</p>
        </div>
    </div>

	<!-- This is the page for managing friends  -->
</template>


<style lang="css" scoped>
p {
    color: red;
}

</style>