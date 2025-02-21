<template>
  <div>
    <!-- Open Modal Button -->
    <UButton color="primary" variant="solid" @click="openModal">
      Continue Exploration
    </UButton>

    <!-- Modal -->
    <dialog id="modal_exploration" class="modal">
      <div class="modal-box">
        <form method="dialog">

          <!-- Container for the cards -->
          <div class="card-container flex space-x-4">

            <!-- User Profile -->
            <div class="card bg-base-100 w-96 shadow-xl">
              <div class="card-body">
                <h2 class="card-title">User Profile</h2>
                <p>Explore your profile history</p>
                <div class="card-actions justify-end">
                  <UButton color="primary" variant="solid" :to="{ name: 'users-id', params: { id: 1 } }">
                    View Profile
                  </UButton>
                </div>
              </div>
            </div>

            <!-- Go back to Worlds -->
            <div class="card bg-base-100 w-96 shadow-xl">
              <div class="card-body">
                <h2 class="card-title">Game Mode</h2>
                <p>Decide between specialization and sandboxing</p>
                <div class="card-actions justify-end">
                  <UButton color="primary" variant="solid" :to="{ name: 'scenarios' }">
                    Choose Game Mode
                  </UButton>
                </div>
              </div>
            </div>

          </div>

          <!-- Close Button -->
          <UButton color="gray" variant="soft" class="absolute right-2 top-2" @click="closeModal">
            ✕
          </UButton>

        </form>
      </div>
    </dialog>
  </div>
</template>

<script setup>
const openModal = () => {
  document.getElementById('modal_exploration').showModal();
};

const closeModal = () => {
  document.getElementById('modal_exploration').close();
};
</script>
