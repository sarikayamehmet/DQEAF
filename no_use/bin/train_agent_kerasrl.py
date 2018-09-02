import gym
import numpy as np

from no_use.bin import DQNAgent_Change
from no_use.bin.change_memory import SequentialMemory_Change

np.random.seed(123)  # set a random seed when setting up the gym environment (train_test_split)

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, ELU, Dropout, BatchNormalization
from keras.optimizers import RMSprop

# pip install keras-rl
from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy, EpsGreedyQPolicy
from rl.memory import SequentialMemory


# 原来的方法
# def generate_dense_model(input_shape, layers, nb_actions):
#     model = Sequential()
#     model.add(Flatten(input_shape=input_shape))
#     model.add(Dropout(0.1))  # drop out the input to make model less sensitive to any 1 feature
#
#     for layer in layers:
#         model.add(Dense(layer))
#         model.add(BatchNormalization())
#         model.add(ELU(alpha=1.0))
#
#     model.add(Dense(nb_actions))
#     model.add(Activation('linear'))
#     print(model.summary())
#
#     return model

# 冯畅修改的模型
def generate_dense_model(input_shape, layers, nb_actions):
    model = Sequential()
    model.add(Flatten(input_shape=input_shape))
    # normalize before compute
    model.add(BatchNormalization())
    model.add(Dropout(0.1))  # drop out the input to make model less sensitive to any 1 feature

    for layer in layers:
        model.add(Dense(layer))
        model.add(ELU(alpha=1.0))
        model.add(Dropout(0.1))

    model.add(Dense(nb_actions))
    model.add(Activation('linear'))
    print(model.summary())

    return model


def train_dqn_model(layers, rounds=10000, run_test=False, use_score=False):
    ENV_NAME = 'malware-pca-score-v0' if use_score else 'malware-pca-v0'
    env = gym.make(ENV_NAME)
    env.seed(123)
    nb_actions = env.action_space.n
    window_length = 1  # "experience" consists of where we were, where we are now

    # generate a policy model
    model = generate_dense_model((window_length,) + env.observation_space.shape, layers, nb_actions)

    # configure and compile our graduation_agent
    # BoltzmannQPolicy selects an action stochastically with a probability generated by soft-maxing Q values
    policy = BoltzmannQPolicy()

    # memory can help a model during training
    # for this, we only consider a single malware sample (window_length=1) for each "experience"
    memory = SequentialMemory(limit=1000, ignore_episode_boundaries=False, window_length=window_length)

    # DQN graduation_agent as described in Mnih (2013) and Mnih (2015).
    # http://arxiv.org/pdf/1312.5602.pdf
    # http://arxiv.org/abs/1509.06461
    agent = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=16,
                     enable_double_dqn=True, enable_dueling_network=True, dueling_type='avg',
                     target_model_update=1e-2, policy=policy, batch_size=16)

    # keras-rl allows one to use and built-in keras optimizer
    agent.compile(RMSprop(lr=1e-2), metrics=['mae'])

    # play the game. learn something!
    agent.fit(env, nb_steps=rounds, visualize=False, verbose=2)

    history_train = env.history
    history_test = None

    if run_test:
        # Set up the testing environment
        TEST_NAME = 'malware-score-test-v0' if use_score else 'malware-test-v0'
        test_env = gym.make(TEST_NAME)

        # evaluate the graduation_agent on a few episodes, drawing randomly from the test samples2
        agent.test(test_env, nb_episodes=100, visualize=False)
        history_test = test_env.history

    return agent, model, history_train, history_test


def train_dqn_model_EpsGreedy_Policy(layers, rounds=10000, run_test=False, use_score=False):
    ENV_NAME = 'malware-score-v0' if use_score else 'malware-v0'
    # ENV_NAME = 'malware-pca-score-v0' if use_score else 'malware-pca-v0'
    env = gym.make(ENV_NAME)
    env.seed(123)
    nb_actions = env.action_space.n
    window_length = 1  # "experience" consists of where we were, where we are now

    # generate a policy model
    model = generate_dense_model((window_length,) + env.observation_space.shape, layers, nb_actions)

    # configure and compile our graduation_agent
    # BoltzmannQPolicy selects an action stochastically with a probability generated by soft-maxing Q values
    policy = EpsGreedyQPolicy()
    # test_policy = EpsGreedyQPolicy()

    # memory can help a model during training
    # for this, we only consider a single malware sample (window_length=1) for each "experience"
    memory = SequentialMemory(limit=1000, ignore_episode_boundaries=False, window_length=window_length)

    # DQN graduation_agent as described in Mnih (2013) and Mnih (2015).
    # http://arxiv.org/pdf/1312.5602.pdf
    # http://arxiv.org/abs/1509.06461
    agent = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=16,
                     enable_double_dqn=True, enable_dueling_network=True, dueling_type='avg',
                     target_model_update=1e-2, policy=policy, batch_size=16)

    # keras-rl allows one to use and built-in keras optimizer
    agent.compile(RMSprop(lr=1e-2), metrics=['mae'])

    # play the game. learn something!
    agent.fit(env, nb_steps=rounds, visualize=False, verbose=2)

    history_train = env.history
    history_test = None

    if run_test:
        # Set up the testing environment
        TEST_NAME = 'malware-score-test-v0' if use_score else 'malware-test-v0'
        test_env = gym.make(TEST_NAME)

        # evaluate the graduation_agent on a few episodes, drawing randomly from the test samples2
        agent.test(test_env, nb_episodes=100, visualize=False)
        history_test = test_env.history

    return agent, model, history_train, history_test


def train_dqn_model_sarsa(layers, rounds=10000, run_test=False, use_score=False):
    ENV_NAME = 'malware-pca-score-v0' if use_score else 'malware-pca-v0'
    env = gym.make(ENV_NAME)
    env.seed(123)
    nb_actions = env.action_space.n
    window_length = 1  # "experience" consists of where we were, where we are now

    # generate a policy model
    model = generate_dense_model((window_length,) + env.observation_space.shape, layers, nb_actions)

    # configure and compile our graduation_agent
    # BoltzmannQPolicy selects an action stochastically with a probability generated by soft-maxing Q values
    policy = EpsGreedyQPolicy()
    # test_policy = EpsGreedyQPolicy()

    # memory can help a model during training
    # for this, we only consider a single malware sample (window_length=1) for each "experience"
    memory = SequentialMemory_Change(limit=32, ignore_episode_boundaries=False, window_length=window_length)

    # DQN graduation_agent as described in Mnih (2013) and Mnih (2015).
    # http://arxiv.org/pdf/1312.5602.pdf
    # http://arxiv.org/abs/1509.06461
    agent = DQNAgent_Change(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=16,
                            enable_double_dqn=True, enable_dueling_network=True, dueling_type='avg',
                            target_model_update=1000, policy=policy, batch_size=16)

    # keras-rl allows one to use and built-in keras optimizer
    agent.compile(RMSprop(lr=1e-3), metrics=['mae'])

    # play the game. learn something!
    agent.fit(env, nb_steps=rounds, visualize=False, verbose=2)

    history_train = env.history
    history_test = None

    if run_test:
        # Set up the testing environment
        TEST_NAME = 'malware-score-test-v0' if use_score else 'malware-test-v0'
        test_env = gym.make(TEST_NAME)

        # evaluate the graduation_agent on a few episodes, drawing randomly from the test samples2
        agent.test(test_env, nb_episodes=100, visualize=False)
        history_test = test_env.history

    return agent, model, history_train, history_test
