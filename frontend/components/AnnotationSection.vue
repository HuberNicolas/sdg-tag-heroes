<template>
  <div class="h-full overflow-hidden">
    <div class="grid grid-rows-12 grid-cols-1 grid-flow-col h-full">
      <div class="row-span-4 col-span-1">
        <!-- Annotation is attached to SDG Label Decision (in general) -->
        <div class="frame-container">
          <div class="frame-title"><b>Record</b> Your Thoughts: Add Comments to Specific Sections</div>
          <ShapSelector></ShapSelector>
          <CommentInput></CommentInput>
          <CreateAnnotationButton></CreateAnnotationButton>
        </div>
      </div>
      <div class="row-span-1 col-span-1 h-full">
        <!-- Custom Horizontal Divider with Text and Diagonal Line -->
        <div class="relative my-0 flex items-center justify-center h-full">
        <span class="absolute left-0 w-full h-full border-t-4 border-b-4 border-gray-400 flex justify-between items-center px-4">

          <!-- Left Side: Arrow Up with Label -->
            <div class="flex flex-col items-start space-y-1">
                <div class="flex items-center space-x-2">
                    <Icon class="w-6 h-6 text-gray-400" name="heroicons-outline:arrow-up" />
                    <span class="text-gray-600 text-sm font-semibold"><b>Annotate</b> Publication</span>
                    <Icon class="w-6 h-6 text-gray-400" name="heroicons-outline:pencil-alt" />
                </div>
                <p class="text-xs text-gray-500">Provide insights on the machine explanation.</p>
            </div>

          <!-- Custom Horizontal Divider with Text -->
      <div class="relative my-6 flex items-center justify-center">
        <span class="absolute left-0 w-full border-t-4 border-gray-400"></span>
        <span class="relative bg-white px-4 text-gray-700 font-bold text-sm">and</span>
      </div>

          <!-- Right Side: Arrow Down with Label -->
            <div class="flex flex-col items-end space-y-1">
                <p class="text-xs text-gray-500">Label the publication with an SDG.</p>
              <div class="flex items-center space-x-2">
                    <Icon class="w-6 h-6 text-gray-400" name="heroicons-outline:tag" />
                    <span class="text-gray-600 text-sm font-semibold"><b>Label</b> Publication</span>
                    <Icon class="w-6 h-6 text-gray-400" name="heroicons-outline:arrow-down" />
                </div>
            </div>
        </span>
        </div>
      </div>



      <div class="row-span-6 col-span-1">
        <!-- SDG User Label is attached to SDG Label decision -->
        <div class="frame-container">
          <div class="frame-title"><b>Identify</b> the Most Relevant SDG & Justify Your Selection to Help the Community
          </div>
          <ConnectingDots></ConnectingDots>
          <CreateSDGLabelButton></CreateSDGLabelButton>
        </div>
      </div>

      <div class="col-span-1">
        <div class="frame-container">
          <div class="frame-title"><b>Continue</b> Labeling process</div>
          <div class="flex justify-between items-center">
            <ContinueLabelingDialog />
            <ContinueExplorationDialog />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import CreateSDGLabelButton from "~/components/CreateSDGLabelButton.vue";
import ContinueLabelingDialog from "~/components/ContinueLabelingDialog.vue";
import ContinueExplorationDialog from "~/components/ContinueExplorationDialog.vue";
</script>
