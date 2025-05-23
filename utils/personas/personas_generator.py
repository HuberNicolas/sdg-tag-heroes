import numpy as np
from collections import Counter
from typing import List, Tuple
from faker import Faker
from random import choices

from enums.enums import BartlePersonaType, BartlePersonaDistributionType
from models.users.user import User

faker = Faker()
Faker.seed(31011997)


def generate_realistic_distribution():
    """Create a dynamic Bartle persona distribution with slight random variation."""

    base_distribution = {
        BartlePersonaType.ACHIEVER: BartlePersonaDistributionType.ACHIEVER_PORTION.value,
        BartlePersonaType.EXPLORER: BartlePersonaDistributionType.EXPLORER_PORTION.value,
        BartlePersonaType.SOCIALIZER: BartlePersonaDistributionType.SOCIALIZER_PORTION.value,
        BartlePersonaType.KILLER: BartlePersonaDistributionType.KILLER_PORTION.value,
    }

    base = np.array(list(base_distribution.values()), dtype=float)  # Ensure numeric values
    variation = np.random.normal(0, 0.05, size=len(base))  # Add slight variation
    adjusted = np.clip(base + variation, 0.05, 0.5)  # Keep within reasonable bounds
    adjusted /= adjusted.sum()  # Normalize to sum = 1

    return dict(zip(base_distribution.keys(), adjusted))


def assign_personas(users: List[User]) -> dict:
    """Assign temporary Bartle personas to users without modifying the DB."""

    if not users:
        print("No users provided for persona assignment.")
        return {}

    dist = generate_realistic_distribution()
    personas = choices(
        population=list(dist.keys()),
        weights=list(dist.values()),
        k=len(users)
    )

    user_persona_map = {}  # Temporary mapping of users to personas

    for user, persona in zip(users, personas):
        trust_score = round(np.clip(np.random.normal(0.5, 0.2), 0, 1), 2)
        interest, skill = generate_interest_and_skill(persona)

        user_persona_map[user.user_id] = {  # Ensure we're using user.user_id, not BartlePersona
            "persona": persona,
            "trust_score": trust_score,
            "interest": interest,
            "skill": skill,
        }

    return user_persona_map  # Return a temporary mapping


def generate_interest_and_skill(persona: BartlePersonaType) -> Tuple[str, str]:
    """Assigns interest and skill sets based on persona type."""

    # Mapping persona types to interest categories
    persona_interest_map = {
        BartlePersonaType.ACHIEVER: "SDG",
        BartlePersonaType.EXPLORER: "General",
        BartlePersonaType.SOCIALIZER: "Hobby",
        BartlePersonaType.KILLER: "Mixed"
    }

    # SDG-Related Fields (Higher education and specialized skills)
    sdg_fields = {
        "Climate Science": ["Environmental Scientist", "Renewable Energy Engineer", "Sustainability Consultant"],
        "AI Ethics": ["Data Scientist", "Ethics Researcher", "AI Policy Analyst"],
        "Healthcare Innovation": ["Biomedical Engineer", "Public Health Expert", "Medical Researcher"],
        "Social Justice": ["Human Rights Activist", "Community Organizer", "Legal Advocate"],
        "Economics & Development": ["Economist", "Urban Planner", "Policy Analyst"]
    }

    # Non-SDG High-Skill Fields
    general_fields = {
        "Technology": ["Software Engineer", "Game Developer", "IT Consultant"],
        "Business & Finance": ["Entrepreneur", "Investment Analyst", "Marketing Specialist"],
        "Arts & Entertainment": ["Graphic Designer", "Filmmaker", "Music Producer"],
        "Gaming & Esports": ["Professional Gamer", "Game Streamer", "Level Designer"],
        "Sports & Fitness": ["Athlete", "Personal Trainer", "Sports Journalist"],
        "Education": ["Teacher", "Professor", "Education Consultant"]
    }

    # Everyday Professions (Low-Skill or General Public Jobs)
    everyday_fields = {
        "Retail & Services": ["Shopkeeper", "Cashier", "Waiter/Waitress"],
        "Transportation": ["Bus Driver", "Taxi Driver", "Delivery Worker"],
        "Trades & Labor": ["Electrician", "Factory Worker", "Construction Worker"],
        "Food Industry": ["Chef", "Baker", "Bartender"],
        "Manual & Maintenance": ["Janitor", "Security Guard", "Mechanic"]
    }

    # Casual and Hobby Interests
    hobby_fields = {
        "Music": ["Musician", "DJ", "Music Teacher"],
        "Art": ["Painter", "Illustrator", "Sculptor"],
        "Shopping": ["Retail Worker", "Fashion Consultant", "Salesperson"],
        "Hiking": ["Tour Guide", "Outdoor Enthusiast", "Park Ranger"]
    }

    # Mixed Interests
    mixed_fields = {
        "Psychology & Human Behavior": ["Psychologist", "Behavioral Researcher", "Mental Health Advocate"],
        "Media & Communication": ["Journalist", "Content Creator", "Public Relations Manager"],
        "History & Society": ["Historian", "Anthropologist", "Museum Curator"]
    }

    interest_category = persona_interest_map.get(persona, "General")

    # Assign interest and skill based on category
    if interest_category == "SDG":
        interest = faker.random_element(list(sdg_fields.keys()))
        skill = faker.random_element(sdg_fields[interest])
    elif interest_category == "General":
        interest = faker.random_element(list(general_fields.keys()))
        skill = faker.random_element(general_fields[interest])
    elif interest_category == "Everyday":
        interest = faker.random_element(list(everyday_fields.keys()))
        skill = faker.random_element(everyday_fields[interest])
    elif interest_category == "Hobby":
        interest = faker.random_element(list(hobby_fields.keys()))
        skill = faker.random_element(hobby_fields[interest])
    else:
        interest = faker.random_element(list(mixed_fields.keys()))
        skill = faker.random_element(mixed_fields[interest])

    return interest, skill
