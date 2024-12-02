import { ref, watchEffect } from 'vue';
import { createAvatar } from '@dicebear/core';
import { thumbs } from '@dicebear/collection';

export default function useAvatar() {
  const seed = ref('');
  const avatar = ref('');

  const generateAvatar = (options: { seed: string; size?: number }) => {
    const { seed, size = 64 } = options;
    if (seed) {
      return createAvatar(thumbs, {
        seed,
        size,
      });
    }
    return null;
  };

  watchEffect(() => {
    if (seed.value) {
      const avatarInstance = generateAvatar({ seed: seed.value });
      avatar.value = avatarInstance?.toDataUri() || '';
    }
  });

  return {
    avatar,
    seed,
    generateAvatar
  };
}

