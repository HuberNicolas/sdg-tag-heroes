import { createAvatar } from '@dicebear/core';
import { thumbs } from '@dicebear/collection';

/**
 * Generates a Data URI for an avatar based on the provided seed and options.
 * @param seed - The unique identifier for the avatar (e.g., user email).
 * @param options - Additional options for avatar generation.
 * @returns A string containing the Data URI of the generated avatar.
 */
export function generateAvatar(seed: string, options: Record<string, any> = {}): string {
  return createAvatar(thumbs, {
    seed,
    size: 128,
    scale: 150,
    ...options,
  }).toDataUri();
}
