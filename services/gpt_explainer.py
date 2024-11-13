import json
from openai import OpenAI

from settings.settings import ExplainerSettings
from utils.env_loader import load_env, get_env_variable

# Load the API environment variables
load_env('api.env')

explainer_settings = ExplainerSettings()
client = OpenAI(api_key=get_env_variable('OPENAI_API_KEY'))


class PromptStrategy:
    def generate_prompt(self, title, abstract):
        raise NotImplementedError("Subclasses should implement this method.")


class ExtractKeywordsStrategy(PromptStrategy):
    def generate_prompt(self, title, abstract):
        return f"""
        Read the following abstract and extract exactly 4 keywords that best represent the main topics and themes discussed in the abstract.
        Limit your output to return only 4 keywords.

        Title: {title}
        Abstract: {abstract}

        Structure your answer as a JSON object following the previous example without any markdown notation.
        """


class TargetStrategy(PromptStrategy):
    def __init__(self, target):
        self.target = target

    def generate_prompt(self, title, abstract):
        return f"""
        Read the following abstract and reason about its relevance to the UN SDG Target {self.target}.
        Explain why it is relevant to the target, and why it is not.

        Title: {title}
        Abstract: {abstract}

        Structure your answer as a JSON object following the previous example without any markdown notation.
        """


class GoalStrategy(PromptStrategy):
    def __init__(self, goal):
        self.goal = goal

    def generate_prompt(self, title, abstract):
        return f"""
        Read the following abstract and reason about its relevance to the UN SDG Goal {self.goal}.
        Explain why it is relevant to the goal, and why it is not.

        Title: {title}
        Abstract: {abstract}

        Structure your answer as a JSON object following the previous example without any markdown notation.
        """


class SDGExplainer:
    context = "You are an expert on sustainability research. You provide structured answers in JSON."

    def __init__(self):
        prompt_base_path = explainer_settings.PROMPT_PATH
        print(f"{prompt_base_path}/example_prompt.json")
        with open(f"{prompt_base_path}/example_prompt.json") as f:
            self.example_prompt = json.load(f)

        with open(f"{prompt_base_path}/example_answer.json") as f:
            self.example_answer = json.load(f)

    def make_prompt(self, title, abstract, strategy: PromptStrategy):
        return strategy.generate_prompt(title, abstract)

    def explain(self, pub, goal: str = None, target: str = None):
        if target:
            strategy = TargetStrategy(target)
        elif goal:
            strategy = GoalStrategy(goal)
        else:
            raise RuntimeError("Either 'goal' or 'target' must be specified.")

        prompt = self.make_prompt(pub.title, pub.description, strategy)

        example_strategy = (
            GoalStrategy(self.example_prompt['goal'])
            if goal else TargetStrategy(self.example_prompt['target'])
        )
        example_prompt = self.make_prompt(
            self.example_prompt['title'],
            self.example_prompt['abstract'],
            example_strategy,
        )

        example_answer = {
            "title": self.example_answer['title'],
        }

        if target:
            example_answer['target'] = self.example_answer['target']
            example_answer['target_explanation'] = self.example_answer['target_explanation']
        elif goal:
            example_answer['goal'] = self.example_answer['goal']
            example_answer['goal_explanation'] = self.example_answer['goal_explanation']

        response = client.chat.completions.create(
            model=explainer_settings.GPT_MODEL,
            messages=[
                {"role": "system", "content": self.context},
                {"role": "user", "content": example_prompt},
                {"role": "assistant", "content": json.dumps(example_answer)},
                {"role": "user", "content": prompt},
            ],
            temperature=explainer_settings.GPT_TEMPERATURE,
        )

        try:
            # Accessing and parsing the content from the response correctly
            content = response.choices[0].message.content
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = {"error": "Failed to parse response."}

        return parsed

    def extract_keywords(self, title, abstract):
        strategy = ExtractKeywordsStrategy()
        prompt = self.make_prompt(title, abstract, strategy)

        response = client.chat.completions.create(
            model=explainer_settings.GPT_MODEL,
            messages=[
                {"role": "system", "content": self.context},
                {"role": "user", "content": prompt},
            ],
            temperature=explainer_settings.GPT_TEMPERATURE,
        )

        try:
            # Accessing and parsing the content from the response correctly
            content = response.choices[0].message.content
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = {"error": "Failed to parse response."}
        return parsed.get("keywords", [])

