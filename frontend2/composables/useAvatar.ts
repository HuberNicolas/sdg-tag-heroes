import { createAvatar } from '@dicebear/core';
import { thumbs } from '@dicebear/collection';

export default function useAvatar() {
  // Generate an avatar for a given seed and size
  const generateAvatar = (seed: string, size: number = 64): string => {
    if (!seed) return ''; // Return an empty string if no seed is provided
    const avatar = createAvatar(thumbs, {
      seed,
      size,
    });
    const dataUri = avatar.toDataUri();
    return dataUri; // Return the data URI of the avatar
  };

  return {
    generateAvatar,
  };
}
