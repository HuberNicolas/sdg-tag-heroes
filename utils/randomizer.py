import random as rand

from settings.settings import SeedSettings


seed = SeedSettings().SEED
rand.seed(seed)

