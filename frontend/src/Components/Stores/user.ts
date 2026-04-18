
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

	async function fetch() {
		try {
			userLogger.info("Fetching User Data");
			const resp = await api.get("/users/@me");
			userData.value = resp.data;
			return true;
		} catch (error) {
			userLogger.error("Erroring fetching User Data: " + error);
			return false
		}
	}
	async function login() {
		try {
			const hasFetched = await fetch();
			if (!hasFetched) return
			// turn true since credentials worked.
			isLoggedIn.value = true
		} catch (error) {
			userLogger.error("Erroring fetching User Data: " + error);
		}
	}

	return { isLoggedIn, login, fetch, userData };
})

export default useUserStore;
