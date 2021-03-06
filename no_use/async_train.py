# coding=UTF-8
# ! /usr/bin/python
import argparse
import datetime
import os

from no_use.bin.train_agent_chainer import *
from gym_malware.envs.controls import manipulate2 as manipulate

ACTION_LOOKUP = {i: act for i, act in enumerate(manipulate.ACTION_TABLE.keys())}

q_hook = VisdomPlotHook('Average Q Value')
loss_hook = VisdomPlotHook('Average Loss', plot_index=1)

env_list = {}
env_test_list = {}


def make_env(process_idx, test):
    if test:
        if env_test_list.__contains__(process_idx):
            env = env_test_list.get(process_idx)
        else:
            env = gym.make('malware-test-v0')
            env_test_list[process_idx] = env
    else:
        if env_list.__contains__(process_idx):
            env = env_list.get(process_idx)
        else:
            env = gym.make('malware-v0')
            env_list[process_idx] = env

    return env


# 开始训练
def train_agent(rounds=10000, use_score=False, name='result_dir', create_agent=create_acer_agent):
    ENV_NAME = 'malware-score-v0' if use_score else 'malware-v0'
    env = gym.make(ENV_NAME)
    np.random.seed(123)
    env.seed(123)

    agent = create_agent(env)

    chainerrl.experiments.train_agent_async(
        outdir=name,
        processes=8,
        make_env=make_env,
        steps=rounds,
        eval_interval=2000,
        eval_n_runs=20,
        max_episode_len=80,
        successful_score=7,
        agent=agent,
        global_step_hooks=[q_hook, loss_hook]
    )

    return env, agent


# 用于快速调用chainerrl的训练方法，参数如下：
# python train.py --rounds rounds(训练的次数)
model_dir = "models/"
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
parser = argparse.ArgumentParser()
parser.add_argument('--rounds', type=int, default=50000)
args = parser.parse_args()

model_saved_name = timestamp
rounds = args.rounds
agent_method = create_acer_agent

model = "{}{}_{}".format(model_dir, model_saved_name, rounds)
test_result = "{}{}_{}/scores.txt".format(model_dir, model_saved_name, rounds)

if not os.path.exists(model):
    os.makedirs(model)

# start time
training_start_time = datetime.datetime.now()
with open(test_result, 'a+') as f:
    f.write("start->{}\n".format(training_start_time))

# black box
env, agent = train_agent(rounds=int(rounds), use_score=False, name=model, create_agent=agent_method)
# with open(test_result, 'a+', encoding='utf-8') as f:
#     f.write("total_turn/episode->{}({}/{})\n".format(env.total_turn / env.episode, env.total_turn, env.episode))

training_end_time = datetime.datetime.now()
with open(test_result, 'a+') as f:
    f.write("end->{}\n".format(training_end_time))

# test
# total = len(sha256_holdout)
# fe = pefeatures.PEFeatureExtractor()
#
# def agent_policy(agent):
#     def f(bytez):
#         # first, get features from bytez
#         feats = fe.extract(bytez)
#         action_index = agent.act(feats)
#         return ACTION_LOOKUP[action_index]
#
#     return f
#
# # ddqn
# success, _ = evaluate(agent_policy(agent))
# blackbox_result = "black: {}({}/{})".format(len(success) / total, len(success), total)
# with open(test_result, 'a+') as f:
#     f.write("result->{}\n".format(blackbox_result))
