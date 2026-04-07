// import App from '@/App.vue'
// import Landing from '@/Components/Landing/Landing.vue'
import Dashboard from '@/Components/Dashboard/Dashboard.vue'
import Create from '@/Components/Game/Create/Create.vue'
import Join from '@/Components/Game/Join/Join.vue'
import Play from '@/Components/Game/Play/Play.vue'
import Landing from '@/Components/Landing/Landing.vue'
import Leaderboard from '@/Components/Leaderboard/Leaderboard.vue'
import Login from '@/Components/Login/Login.vue'
import Profile from '@/Components/Profile/Profile.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: '/',
			name: 'home',
			component: Dashboard
		},
		{
			path: '/play',
			name: 'play',
			component: Play
		},
		{
			path: '/create',
			name: 'create',
			component: Create
		},
		{
			path: '/join',
			name: 'join',
			component: Join
		},
		{
			path: '/profile',
			name: 'profile',
			component: Profile
		},
		{
			path: '/leaderboard',
			name: 'leaderboard',
			component: Leaderboard
		},
		{
			path: '/login',
			name: 'login',
			component: Login
		},
		{
			path: '/dashboard',
			name: 'dashboard',
			component: Dashboard
		}
	],
})

export default router
