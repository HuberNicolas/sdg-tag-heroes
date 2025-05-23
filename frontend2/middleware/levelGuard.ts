export default defineNuxtRouteMiddleware((to) => {
  const levelId = parseInt(to.params.level_id as string, 10);

  if (levelId < 1 || levelId > 3) {
    // Redirect to the parent page if the level_id is invalid
    return navigateTo(`/worlds/${to.params.id}`);
  }
});
