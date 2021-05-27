import os

import numpy as np
import ray
from gym.spaces import Box
from gym_env.envs.agent import Agent
from multiagent_env.envs import MultiAgentBeerGame
from ray.rllib.agents.impala import ImpalaTrainer
from ray.tune import register_env
from ray.tune.logger import pretty_print

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

N_AGENTS = 4
OBSERVATIONS_TO_TRACK = 5


def create_env(config):
    return MultiAgentBeerGame(config)


env_config = {
    "n_agents": N_AGENTS,
    "n_iterations": 1000,
    "observations_to_track": OBSERVATIONS_TO_TRACK,
    'accumulate_backlog_cost': False,
    'accumulate_stock_cost': False
}
env = create_env(env_config)
register_env("mabeer-game", create_env)

obs_space = Box(low=0, high=np.finfo(np.float32).max, shape=(OBSERVATIONS_TO_TRACK * Agent.N_OBSERVATIONS,),
                dtype=np.float32)
action_space = Box(low=0, high=100000, shape=(1,), dtype=np.float32)
policies = {str(agent.name): (None, obs_space, action_space, {}) for agent in env.agents}

ray.init()
trainer = ImpalaTrainer(env="mabeer-game", config={
    # "model": {"use_lstm": True}
    "clip_rewards": True,
    "num_workers": 0,
    "env_config": env_config,
    "multiagent": {
        "policies": policies,
        "policy_mapping_fn": (lambda agent_id: agent_id),
        "policies_to_train": '1'
    },
})

for i in range(100):
    result = trainer.train()
    print(pretty_print(result))

## maknuti backlog, samo ga racunati u reward, pass as parameter (+ zasicenje za backlog (backlog ne raste nakon thresholda))
## svi uce nad istim policyjem
## ppotrainer freeze network for n-th agent --> policies_to_train??

##maybe this
# Optional whitelist of policies to train, or None for all policies.
# "policies_to_train": None,
