import { createAvatar } from '@dicebear/core';
import { thumbs } from '@dicebear/collection';

/**
 * Generates an avatar data URI for a given seed and size.
 * @param seed - The seed used to generate the avatar (e.g., email or username).
 * @param size - The size of the avatar (default: 64).
 * @returns The avatar data URI.
 */
export function generateAvatar(seed: string, size: number = 64): string {
  if (!seed) return ''; // Return an empty string if no seed is provided

  const avatar = createAvatar(thumbs, {
    seed,
    size,
  });

  const uri = avatar.toDataUri();
  console.log(`Generated avatar URI for seed '${seed}':`, uri); // Debug
  return uri; // Return the data URI of the avatar
}
