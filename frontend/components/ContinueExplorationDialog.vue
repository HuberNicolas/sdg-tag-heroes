<template>
  <div>
    <!-- You can open the modal using ID.showModal() method -->
    <button class="btn" onclick="modal_exploration.showModal()">Continue Exploration</button>
    <dialog id="modal_exploration" class="modal">
      <div class="modal-box">
        <form method="dialog">

          <!-- Container for the cards -->
          <div class="card-container flex space-x-4">

            <!-- User Profile -->
            <div class="card bg-base-100 w-96 shadow-xl">
              <div class="card-body">
                <h2 class="card-title">User Profile</h2>
                <p>Explore your profile details</p>
                <div class="card-actions justify-end">
                  <NuxtLink :to="{ name: 'users-id', params: { id: 1 } }" class="btn btn-primary">
                    View Profile
                  </NuxtLink>
                </div>
              </div>
            </div>

            <!-- Go back to Worlds -->
            <div class="card bg-base-100 w-96 shadow-xl">
              <div class="card-body">
                <h2 class="card-title">Worlds</h2>
                <p>Discover new scenarios</p>
                <div class="card-actions justify-end">
                  <NuxtLink :to="{ name: 'scenarios' }" class="btn btn-primary">
                    Explore Worlds
                  </NuxtLink>
                </div>
              </div>
            </div>

          </div>

          <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
        </form>
      </div>
    </dialog>
  </div>
</template>

<script setup lang="ts">
</script>
