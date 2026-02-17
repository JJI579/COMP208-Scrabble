
import api from "@/api";
import Logger from "@/logging/Logger";
import type { SelfReturn } from "@/types";
import { defineStore } from "pinia";
import { ref } from "vue";

const userLogger = new Logger("user");

const useUserStore = defineStore("user", () => {
	const isLoggedIn = ref(false);

	// Will reference a type
	const userData = ref<SelfReturn | null>(null);

	async function login() {
		try {
			userLogger.info("Fetching User Data");
			const resp = await api.get("/users/@me");
			userData.value = resp.data;
			isLoggedIn.value = true
		} catch (error) {
			userLogger.error("Erroring fetching User Data: " + error);
		}
	}
	return { isLoggedIn, login };
})

export default useUserStore;
