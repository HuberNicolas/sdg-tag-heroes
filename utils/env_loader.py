import os

from dotenv import load_dotenv

from settings.settings import EnvLoaderSettings

env_loader_settings = EnvLoaderSettings()

DEBUG = env_loader_settings.ENV_LOADER_DEBUG_OUTPUT

def is_running_in_docker():
    return os.getenv('IN_DOCKER', 'false').lower() == 'true'

# Load environment variables from the specified .env files
def load_env(env_file):

    # Resolve path to the project's root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Construct the path to the env directory
    env_path = os.path.join(project_root, 'env', env_file)

    # print(f"Loading .env file from: {env_path}")  # Print the path for debugging
    if os.path.exists(env_path):
        
        # Print the contents of the .env file for debugging
        if DEBUG is True: 
            with open(env_path, 'r') as file:
                print("Contents of the .env file:")
                print(file.read())
        load_dotenv(env_path)
    else:
        print(f"Env file not found at {env_path}")

# Helper function to get environment variables
def get_env_variable(key, default=None):
    return os.getenv(key, default)
