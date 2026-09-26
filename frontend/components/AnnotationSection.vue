<template>
  <div class="flex flex-col gap-3 min-h-0">
    <!-- Annotation is attached to SDG Label Decision (in general) -->
    <div class="flex-none frame-container">
      <div class="frame-title"><b>Record</b> Your Thoughts: Add Comments to Specific Sections</div>
      <ShapSelector/>
      <CommentInput/>
      <CreateAnnotationButton/>
    </div>

    <!-- Divider: annotate above, label below -->
    <div class="flex-none flex items-center gap-3 border-y-4 border-gray-400 px-3 py-2">
      <div class="flex flex-col items-start gap-1">
        <div class="flex items-center gap-2">
          <Icon class="w-6 h-6 text-gray-400" name="heroicons-outline:arrow-up" />
          <span class="text-gray-600 text-sm font-semibold"><b>Annotate</b> Publication</span>
          <Icon class="w-6 h-6 text-gray-400" name="heroicons-outline:pencil-alt" />
        </div>
        <p class="text-xs text-gray-500">Provide insights on the machine explanation.</p>
      </div>
      <span class="flex-1 text-center text-gray-700 font-bold text-sm">and</span>
      <div class="flex flex-col items-end gap-1">
        <p class="text-xs text-gray-500">Label the publication with an SDG.</p>
        <div class="flex items-center gap-2">
          <Icon class="w-6 h-6 text-gray-400" name="heroicons-outline:tag" />
          <span class="text-gray-600 text-sm font-semibold"><b>Label</b> Publication</span>
          <Icon class="w-6 h-6 text-gray-400" name="heroicons-outline:arrow-down" />
        </div>
      </div>
    </div>

    <!-- SDG User Label is attached to SDG Label decision -->
    <div class="flex-1 min-h-0 overflow-y-auto frame-container">
      <div class="frame-title"><b>Identify</b> the Most Relevant SDG & Justify Your Selection to Help the Community</div>
      <ConnectingDots/>
      <CreateSDGLabelButton/>
    </div>

    <div class="flex-none frame-container">
      <div class="frame-title"><b>Continue</b> Labeling process</div>
      <div class="flex justify-between items-center gap-2">
        <ContinueLabelingDialog />
        <ContinueExplorationDialog />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import CreateSDGLabelButton from "~/components/CreateSDGLabelButton.vue";
import ContinueLabelingDialog from "~/components/ContinueLabelingDialog.vue";
import ContinueExplorationDialog from "~/components/ContinueExplorationDialog.vue";
</script>
