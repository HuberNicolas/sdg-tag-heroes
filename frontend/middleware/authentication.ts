import { defineNuxtRouteMiddleware, useCookie } from '#app';

export default defineNuxtRouteMiddleware((to) => {
  const accessToken = useCookie('access_token'); // Use Nuxt's useCookie

  // Redirect to login if no token and trying to access a protected route
  if (!accessToken.value && to.path !== '/login') {
    return navigateTo('/login');
  }

  // Redirect to profile if already authenticated and trying to access login
  if (accessToken.value && to.path === '/login') {
    return navigateTo('/profile');
  }
});
