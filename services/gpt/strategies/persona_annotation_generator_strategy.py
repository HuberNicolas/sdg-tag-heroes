from .base_strategy import PromptStrategy
import random


class GenerateAnnotationStrategy(PromptStrategy):
    """Strategy for generating user annotations based on persona and trust score."""

    def __init__(self):
        self.context = (
            "You are an AI assistant helping users generate insightful, ultra-concise annotations for scientific publications. "
            "Responses must be short, information-dense, and free from introductory phrases like 'This study...'. "
            "Deliver the key insight directly. No unnecessary words. Avoid hedging."
            "Consider the user's persona, expertise level, and skill when generating annotations. "
            "Adjust tone and detail based on expertise and persona."
            "Provide a short answer, straight to the point. Use words with maximal information density. "
        )

    def generate_prompt(self, abstract: str, persona: str, interest: str, skill: str, trust_score: float) -> dict:
        """
        Generates a GPT-based annotation prompt based on persona traits and trust score.

        Parameters:
            abstract (str): The scientific abstract to be annotated.
            persona (str): User's Bartle persona (Achiever, Explorer, Socializer, Killer).
            interest (str): The user's interest related to the topic.
            skill (str): The user's profession/skillset.
            trust_score (float): A trust-based score (0-1) reflecting user expertise.

        Returns:
            dict: The formatted prompt for GPT processing.
        """

        # Define annotation styles based on persona
        persona_styles = {
            "Achiever": [
                "Highlight measurable impact, structured feedback, and real-world contributions.",
                "Focus on practical applications and tangible outcomes.",
                "Assess efficiency, scalability, and how the research can be optimized."
            ],
            "Explorer": [
                "Discuss potential new insights, knowledge gaps, and unexpected applications.",
                "Explore how this research might inspire new questions or interdisciplinary applications.",
                "Critically analyze assumptions and suggest alternative methodologies."
            ],
            "Socializer": [
                "Engage with potential social implications and encourage discussion points.",
                "Highlight how this research could influence communities, policies, or global discussions.",
                "Emphasize collaboration opportunities, ethical concerns, and public impact."
            ],
            "Killer": [
                "Identify potential flaws, challenge key assumptions, and push for stronger reasoning.",
                "Focus on limitations, contradictions, and overlooked variables in the study.",
                "Adopt a skeptical stance, questioning the methodology, biases, or practicality."
            ]
        }

        # Define expertise-driven styles (adds another layer of variation)
        expertise_styles = {
            "Expert": [
                "Incorporate references to existing literature or historical context.",
                "Use technical terminology and precise arguments to strengthen the critique.",
                "Provide alternative hypotheses or methodologies."
            ],
            "Intermediate": [
                "Present a well-structured analysis with clear, balanced insights.",
                "Use logical reasoning and offer constructive feedback while acknowledging gaps.",
                "Suggest practical extensions or modifications to enhance impact."
            ],
            "Basic": [
                "Summarize the key takeaways in a straightforward and accessible way.",
                "Ask relevant questions rather than making assumptions.",
                "Make general observations about the research scope and its importance."
            ]
        }

        # Assign expertise level based on trust score
        expertise_level = (
            "Expert" if trust_score > 0.7 else
            "Intermediate" if trust_score > 0.4 else
            "Basic"
        )

        # Randomly select one instruction from both persona and expertise styles for variety
        persona_instruction = random.choice(persona_styles.get(persona, ["Provide an insightful annotation."]))
        expertise_instruction = random.choice(expertise_styles.get(expertise_level, ["Provide a concise and relevant response."]))

        return {
            "instruction": (
                f"{expertise_level}-level annotation: {expertise_instruction}\n\n"
                f"Your persona is '{persona}', meaning you should {persona_instruction}\n\n"
                f"Your skill: {skill}\n"
                f"Your interest: {interest}\n\n"
                "Read the abstract and provide an annotation (max. 2 sentences, short and concise) that aligns with your persona style. "
                "The annotation should reflect your expertise, using the appropriate depth and tone. "
                "You may mention possible SDG connections if relevant.\n\n"
            ),
            "abstract": abstract,
            "persona": persona,
            "interest": interest,
            "skill": skill,
        }
