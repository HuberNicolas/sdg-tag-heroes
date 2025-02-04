import { useCookie, useRuntimeConfig } from "nuxt/app";
import type { AnnotationCreateRequest, AnnotationSchemaBase, AnnotationSchemaFull } from "~/types/annotation";
import { snakeToCamel } from "~/utils/snakeToCamel";

export default function useAnnotations() {
  const config = useRuntimeConfig();
  const accessToken = useCookie("access_token");

  async function getAnnotations(): Promise<AnnotationSchemaFull[]> {
    try {
      const response = await $fetch<AnnotationSchemaFull[]>(
        `${config.public.apiUrl}/annotations`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch annotations: ${error}`);
    }
  }

  async function getAnnotationById(annotationId: number): Promise<AnnotationSchemaFull> {
    try {
      const response = await $fetch<AnnotationSchemaFull>(
        `${config.public.apiUrl}/annotations/${annotationId}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch annotation: ${error}`);
    }
  }

  async function createAnnotation(request: AnnotationCreateRequest): Promise<AnnotationSchemaFull> {
    try {
      const response = await $fetch<AnnotationSchemaFull>(
        `${config.public.apiUrl}/annotations`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
            "Content-Type": "application/json",
          },
          body: request,
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to create annotation: ${error}`);
    }
  }

  return {
    getAnnotations,
    getAnnotationById,
    createAnnotation
  };
}
