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

      <div class="row-span-7 col-span-1">
        <!-- SDG User Label is attached to SDG Label decision -->
        <div class="frame-container">
          <div class="frame-title"><b>Identify</b> the Most Relevant SDG & Justify Your Selection to Help the Community</div>
          <ConnectingDots></ConnectingDots>
          <CreateSDGLabelButton></CreateSDGLabelButton>
        </div>
      </div>

      <div class="row-span-1 col-span-1">
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

<script setup lang="ts">
import CreateSDGLabelButton from "~/components/CreateSDGLabelButton.vue";
import ContinueLabelingDialog from "~/components/ContinueLabelingDialog.vue";
import ContinueExplorationDialog from "~/components/ContinueExplorationDialog.vue";
</script>
