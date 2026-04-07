// import App from '@/App.vue'
// import Landing from '@/Components/Landing/Landing.vue'
import Dashboard from '@/Components/Dashboard/Dashboard.vue'
import Friends from '@/Components/Friends/Friends.vue'
import Landing from '@/Components/Landing/Landing.vue'
import Leaderboard from '@/Components/Leaderboard/Leaderboard.vue'
import Login from '@/Components/Login/Login.vue'
import Create from '@/Components/Play/Create.vue'
import Join from '@/Components/Play/Join.vue'
import Play from '@/Components/Play/Play.vue'
import Profile from '@/Components/Profile/Profile.vue'
import Shop from '@/Components/Shop/Shop.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: '/',
			name: 'home',
			component: Landing
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
			component: () => import('@/Components/Login/LoginView.vue')
		},
		{
			path: '/dashboard',
			name: 'dashboard',
			component: Dashboard
		}, {
			path: '/shop',
			name: 'shop',
			component: Shop
		}, {
			path: '/friends',
			name: 'friends',
			component: Friends
		}
	],
})

export default router
