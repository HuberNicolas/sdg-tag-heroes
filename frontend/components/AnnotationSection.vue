<template>
  <div class="flex flex-col gap-3 min-h-0">
    <!-- Annotation is attached to SDG Label Decision (in general) -->
    <div class="flex-none frame-container">
      <div class="frame-title"><b>Record</b> your thoughts on a passage of the abstract</div>
      <ShapSelector/>
      <CommentInput/>
      <CreateAnnotationButton/>
    </div>

    <!-- Divider: annotate above, label below -->
    <div class="flex-none flex items-center gap-3 px-1 font-mono text-[11px] text-fg-faint">
      <span class="flex items-center gap-1.5"><Icon name="heroicons-outline:arrow-up" class="h-3.5 w-3.5 text-accent" />annotate the explanation</span>
      <span class="h-px flex-1 bg-line" />
      <span class="text-fg-dim">and</span>
      <span class="h-px flex-1 bg-line" />
      <span class="flex items-center gap-1.5">label the publication<Icon name="heroicons-outline:arrow-down" class="h-3.5 w-3.5 text-accent" /></span>
    </div>

    <!-- SDG User Label is attached to SDG Label decision -->
    <div class="flex-1 min-h-0 overflow-y-auto frame-container">
      <div class="frame-title"><b>Identify</b> the most relevant SDG and explain your choice</div>
      <ConnectingDots/>
      <CreateSDGLabelButton/>
    </div>

    <div class="flex-none frame-container">
      <div class="frame-title"><b>Continue</b> with another publication or go back to the map</div>
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
