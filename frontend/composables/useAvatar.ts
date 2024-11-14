// composables/useAvatar.js
import { ref, watchEffect } from 'vue';
import { createAvatar } from '@dicebear/core';
import { thumbs } from '@dicebear/collection';

export default function useAvatar() {
  const seed = ref('');
  const avatar = ref('');

  const generateAvatar = () => {
    if (seed.value) {
      avatar.value = createAvatar(thumbs, {
        seed: seed.value,
        size: 64, // Adjust size as needed
      }).toDataUri();
    }
  };

  watchEffect(generateAvatar);

  return {
    avatar,
    seed,
    generateAvatar
  };
}
