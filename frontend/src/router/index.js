import { createRouter, createWebHistory } from 'vue-router'
import Login from '../pages/Login.vue'
import UserChat from '../pages/UserChat.vue'
import AdminDashboard from '../pages/AdminDashboard.vue'
import { useUserStore } from '../stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login,
    },
    {
      path: '/',
      name: 'chat',
      component: UserChat,
      meta: { requiresAuth: true },
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminDashboard,
      meta: { requiresAuth: true, requiresAdmin: true },
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const publicPages = ['/login'];
  const authRequired = !publicPages.includes(to.path);
  const token = localStorage.getItem('token');

  if (authRequired && !token) {
    return next('/login');
  }

  if (to.meta.requiresAdmin) {
    if (token) {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]))
            if (payload.role !== 'admin') {
                return next('/')
            }
        } catch (e) {
            return next('/login')
        }
    }
  }

  next();
})

export default router
