from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from backend.accounts.models import Labeler, Expert  # Import the Labeler and Expert models
from django.db.utils import IntegrityError
from utils.env_loader import get_env_variable, load_env

load_env('users.env')


@receiver(post_migrate)
def create_initial_users(sender, **kwargs):
    User = get_user_model()
    user_count = int(get_env_variable('USER_COUNT'))

    for i in range(0, user_count):
        try:
            # Load user data from environment variables dynamically
            user_email = get_env_variable(f'USER_{i}_EMAIL')
            user_password = get_env_variable(f'USER_{i}_PASSWORD')
            user_role = get_env_variable(f'USER_{i}_ROLE')

            # Check if the user already exists
            if not User.objects.filter(email=user_email).exists():
                print(f"Creating user {user_email} with role {user_role}")

                # Handle role-specific logic
                if user_role == 'admin':
                    User.objects.create_superuser(
                        email=user_email,
                        password=user_password,
                        role=user_role
                    )
                elif user_role == 'labeler':
                    labeler = Labeler.objects.create_user(
                        email=user_email,
                        password=user_password,
                        role=user_role
                    )
                    labeling_score = float(get_env_variable(f'USER_{i}_LABELING_SCORE'))
                    labeler.labeling_score = labeling_score
                    labeler.save()
                elif user_role == 'expert':
                    expert = Expert.objects.create_user(
                        email=user_email,
                        password=user_password,
                        role=user_role
                    )
                    labeling_score = float(get_env_variable(f'USER_{i}_LABELING_SCORE'))
                    expert_score = float(get_env_variable(f'USER_{i}_EXPERT_SCORE'))
                    expert.labeling_score = labeling_score
                    expert.expert_score = expert_score
                    expert.save()
                else:
                    print(f"Unknown role {user_role} for user {user_email}")
            else:
                print(f"User {user_email} already exists")

        except IntegrityError as e:
            print(f"Error creating user {i}: {e}")
        except KeyError as e:
            print(f"Missing required environment variable for user {i}: {e}")
