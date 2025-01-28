import type {
  SDGPrediction,
  UserEnrichedInterestsDescription,
  UserEnrichedSkillsDescription,
  UserProfileSkillsRequest,
  UserProfileInterestsRequest,
} from "~/types/gptAssistantService";

export default function useGPTAssistantService() {
  const config = useRuntimeConfig();
  const accessToken = useCookie("access_token");

  // Fetch enriched skills description
  async function getSkillsDescription(
    request: UserProfileSkillsRequest
  ): Promise<UserEnrichedSkillsDescription> {
    try {
      const response = await $fetch<UserEnrichedSkillsDescription>(
        `${config.public.apiUrl}/users-profiles/skills`,
        {
          method: "POST",
          body: { skills: request.skills },
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
            "Content-Type": "application/json",
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch skills description: ${error}`);
    }
  }

  // Fetch enriched interests description
  async function getInterestsDescription(
    request: UserProfileInterestsRequest
  ): Promise<UserEnrichedInterestsDescription> {
    try {
      const response = await $fetch<UserEnrichedInterestsDescription>(
        `${config.public.apiUrl}/users-profiles/interests`,
        {
          method: "POST",
          body: { interests: request.interests },
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
            "Content-Type": "application/json",
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to fetch interests description: ${error}`);
    }
  }

  // Propose SDG based on skills
  async function proposeSdgBasedOnSkills(
    request: UserProfileSkillsRequest
  ): Promise<SDGPrediction> {
    try {
      const response = await $fetch<SDGPrediction>(
        `${config.public.apiUrl}/users-profiles/skills/sdgs`,
        {
          method: "POST",
          body: { skills: request.skills },
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
            "Content-Type": "application/json",
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to propose SDG based on skills: ${error}`);
    }
  }

  // Propose SDG based on interests
  async function proposeSdgBasedOnInterests(
    request: UserProfileInterestsRequest
  ): Promise<SDGPrediction> {
    try {
      const response = await $fetch<SDGPrediction>(
        `${config.public.apiUrl}/users-profiles/interests/sdgs`,
        {
          method: "POST",
          body: { interests: request.interests },
          headers: {
            Authorization: `Bearer ${accessToken.value}`,
            "Content-Type": "application/json",
          },
        }
      );
      return snakeToCamel(response);
    } catch (error) {
      throw new Error(`Failed to propose SDG based on interests: ${error}`);
    }
  }

  return {
    getSkillsDescription,
    getInterestsDescription,
    proposeSdgBasedOnSkills,
    proposeSdgBasedOnInterests,
  };
}
