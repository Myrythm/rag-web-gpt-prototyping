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

  // Parse user role from token
  let userRole = null;
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      userRole = payload.role;
    } catch (e) {
      // Invalid token, redirect to login
      localStorage.removeItem('token');
      return next('/login');
    }
  }

  // Redirect admin to /admin if they try to access user chat page
  if (to.path === '/' && userRole === 'admin') {
    return next('/admin');
  }

  // Prevent non-admin from accessing admin pages
  if (to.meta.requiresAdmin && userRole !== 'admin') {
    return next('/');
  }

  next();
})

export default router
