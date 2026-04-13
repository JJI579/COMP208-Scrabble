// import App from '@/App.vue'
// import Landing from '@/Components/Landing/Landing.vue'
import Dashboard from '@/Components/Dashboard/Dashboard.vue'
import Friends from '@/Components/Friends/Friends.vue'
import Create from '@/Components/Game/Create/Create.vue'
import Finish from '@/Components/Game/Finish/Finish.vue'
import Join from '@/Components/Game/Join/Join.vue'
import Play from '@/Components/Game/Play/Play.vue'
import Leaderboard from '@/Components/Leaderboard/Leaderboard.vue'
import Login from '@/Components/Login/LoginView.vue'
import Profile from '@/Components/Profile/Profile.vue'
import Shop from '@/Components/Shop/Shop.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: '/',
			name: 'home',
			component: Login
		},
		{
			path: '/finish',
			name: 'finish',
			component: Finish
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
