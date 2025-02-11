<template>
  <div>
    <!-- You can open the modal using ID.showModal() method -->
    <button class="btn" onclick="model_labeling.showModal()">Continue Labeling</button>
    <dialog id="model_labeling" class="modal">
      <div class="modal-box">
        <form method="dialog">

          <!-- Container for the cards -->
          <div class="card-container flex space-x-4">

            <!-- Similar Publication -->
            <div class="card bg-base-100 w-96 shadow-xl">
              <figure>
                <img
                  src="https://img.daisyui.com/images/stock/photo-1606107557195-0e29a4b5b4aa.webp"
                  alt="Shoes" />
              </figure>
              <div class="card-body">
                <h2 class="card-title">Similar Publication</h2>
                <p>Description</p>
                <div class="card-actions justify-end">
                  <UButton>Link</UButton>
                </div>
              </div>
            </div>

            <!-- Similar SDG -->
            <div class="card bg-base-100 w-96 shadow-xl">
              <figure>
                <img
                  src="https://img.daisyui.com/images/stock/photo-1606107557195-0e29a4b5b4aa.webp"
                  alt="Shoes" />
              </figure>
              <div class="card-body">
                <h2 class="card-title">Similar SDGs</h2>
                <p>Description</p>
                <div class="card-actions justify-end">
                  <UButton>Link</UButton>
                </div>
              </div>
            </div>

            <!-- Similar Scenario -->
            <div class="card bg-base-100 w-96 shadow-xl">
              <figure>
                <img
                  src="https://img.daisyui.com/images/stock/photo-1606107557195-0e29a4b5b4aa.webp"
                  alt="Shoes" />
              </figure>
              <div class="card-body">
                <h2 class="card-title">Similar Scenarios</h2>
                <p>Description</p>
                <div class="card-actions justify-end">
                  <UButton>Link</UButton>
                </div>
              </div>
            </div>

          </div>

          <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
        </form>
        <h3 class="text-lg font-bold">Hello!</h3>
        <p class="py-4">Press ESC key or click on ✕ button to close</p>
      </div>
    </dialog>
  </div>
</template>

<script setup lang="ts">

</script>

