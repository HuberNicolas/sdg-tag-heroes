import { defineNuxtMiddleware } from 'nuxt3';

// Middleware function to check authentication
export default defineNuxtMiddleware(({ redirect }) => {
  const token = localStorage.getItem('access_token');

  if (!token) {
    return redirect('/login');
  }
});
