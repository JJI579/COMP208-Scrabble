
import api from "@/api";
import type { SelfReturn } from "@/types";
import { defineStore } from "pinia";
import { ref } from "vue";

const useUserStore = defineStore("user", () => {
	const isLoggedIn = ref(false);

	// Will reference a type
	const userData = ref<SelfReturn | null>(null);

	async function login() {
		try {
			const resp = await api.get("/users/@me");
			userData.value = resp.data;
			isLoggedIn.value = true
		} catch (error) {

		}
	}


	return { isLoggedIn, login, userData };
})

export default useUserStore;
