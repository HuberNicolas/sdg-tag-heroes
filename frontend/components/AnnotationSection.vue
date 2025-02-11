<template>
  <div>
    <!-- Annotation is attached to SDG Label Decision (in general) -->
    <ShapSelector></ShapSelector>
    <CommentInput></CommentInput>
    <CreateAnnotationButton></CreateAnnotationButton>
    <UDivider></UDivider>

    <!-- SDG User Label is attached to SDG Label decision -->
    <ConnectingDots></ConnectingDots>
    <CreateSDGLabelButton></CreateSDGLabelButton>
  </div>
</template>

<script setup lang="ts">
import CreateSDGLabelButton from "~/components/CreateSDGLabelButton.vue";
</script>
