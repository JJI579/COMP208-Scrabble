import axios, { AxiosError, type AxiosInstance } from 'axios';
import router from './router';
import Logger from './logging/Logger';
import { BASE_URL } from './types';


const api: AxiosInstance = axios.create({
	baseURL: BASE_URL,
	withCredentials: true, // if using cookies
});

// Optional: Add request interceptor to attach token
api.interceptors.request.use((config) => {
	const token = localStorage.getItem('token');
	if (token) {
		config.headers.Authorization = `Bearer ${token}`;
	}
	return config;
});

const authLogger = new Logger("auth");

// Optional: Add response interceptor to handle 401 globally
api.interceptors.response.use(
	(response) => response,
	async (error: AxiosError & { config?: any }) => {
		const originalRequest = error.config;
		if (!originalRequest) return Promise.reject(error);
		if (error.response?.status === 401 && !originalRequest._retry) {
			originalRequest._retry = true;
			try {
				// Call refresh endpoint
				const refreshToken = localStorage.getItem('refresh_token');
				if (refreshToken === null) {
					localStorage.removeItem('token');
					localStorage.removeItem('refresh_token');
					router.push({ name: 'login' });
					return Promise.reject(error);
				}
				const { data } = await axios.post(
					`${BASE_URL}/auth/refresh`,
					{
						token: localStorage.getItem('refresh_token'),
					},
					{ withCredentials: true }
				);

				localStorage.setItem('token', data.access_token);
				authLogger.info("Refreshed token, reperforming initial request")
				originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
				return api(originalRequest);
			} catch (err) {
				authLogger.warn("Refresh Token expired, Logging User out.")
				localStorage.removeItem('token');
				localStorage.removeItem('refresh_token');
				authLogger.info("Removed token, refresh_token from localstorage")
				router.push({ name: 'login' });
				authLogger.info("Moved to login page.")
				return Promise.reject(err);
			}
		}

		return Promise.reject(error);
	}
);
export default api;
