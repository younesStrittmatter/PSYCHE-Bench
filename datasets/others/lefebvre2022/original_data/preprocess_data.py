import numpy as np
import matplotlib.pyplot as plt
import scipy
import scipy.io
import torch
import pandas as pd

#! Save as pickle file
## Population definition
exps = []

for exp in range(2): # exp 1 == reward and reward omission, exp 2 == reward and punishment
    exp+=1
    path = './original_data/b_data/'
    n_subjects = 0
    ## Data Extraction
    if exp == 1:
        n_subjects = 50
        path += 'data_exp1'
    elif exp == 2:
        n_subjects = 35
        path += 'data_exp2'

    conditions = np.zeros((n_subjects, 96))
    choices = np.zeros((n_subjects, 96))
    reward = np.zeros((n_subjects, 96))

    for i in range(n_subjects):
        if exp == 1:
            data = scipy.io.loadmat(path + '/exp1_' + str(i+1))
            data = data['data']
            conditions[i,:] = data[:,2] # 1 to 4 as per condition
            choices[i,:] = data[:, 6] / 2 + 1.5 # 1 for left, 2 for right
            reward[i,:] = data[:, 7] / 2 # 0 or 0.5 euro
        elif exp == 2:
            data = scipy.io.loadmat(path + '/exp2_' + str(i+1)) # 1 to 4 as per condition
            data = data['data']
            conditions[i,:] = data[:,2] # 1 for left, 2 for right
            choices[i,:] = data[:, 4] / 2 + 1.5 # -0.5 or 0.5 euros
            reward[i,:] = data[:, 7]
    exps.append((conditions, choices, reward))

torch.save(exps, './original_data/extracted_data.pt')

#! Save as csv file
def load_exp(n_exp):
    """
    Parameters:
        :n_exp: number of experiment (1 or 2)

    Returns: (context, c, r, q_initial)
    """
    exps = torch.load('./original_data/extracted_data.pt')
    exp = exps[n_exp-1]
    context,c,r = exp  # participants x trials
    c = (c - 1).astype(int) 
    context = (context - 1).astype(int)
    return context, c, r


# Experiment 1
context, c, r = load_exp(1) # set exp 1 or 2

n_participants = context.shape[0]
n_trials = context.shape[1]

context.shape

exp1 = pd.DataFrame({
        'participant_idx': np.repeat(np.arange(0,n_participants),n_trials),
        'trials_idx': np.tile(np.arange(0,n_trials),n_participants),
        'cues': context.flatten(),
        'actions': c.flatten(),
        'rewards': r.flatten()
        })

exp1 = exp1.rename(columns={'participant_idx': 'participant', 'cues': 'task', 'rewards': 'reward', 'trials_idx': 'all_trial', 'actions': 'choice'})
for participant in exp1.participant.unique():
    for task in exp1.task.unique():
        exp1.loc[(exp1['participant'] == participant) & (exp1['task'] == task), 'trial'] = np.arange(24)

# exp1['task'] = exp1['task'] - 1 # 0 to 3 for 0-indexing
exp1.to_csv('./exp1.csv') # set exp1 

# Experiment 2
context, c, r = load_exp(2) 

n_participants = context.shape[0]
n_trials = context.shape[1]

context.shape

exp2 = pd.DataFrame({
        'participant_idx': np.repeat(np.arange(0,n_participants),n_trials),
        'trials_idx': np.tile(np.arange(0,n_trials),n_participants),
        'cues': context.flatten(),
        'actions': c.flatten(),
        'rewards': r.flatten()
        })

exp2 = exp2.rename(columns={'participant_idx': 'participant', 'cues': 'task', 'rewards': 'reward', 'trials_idx': 'all_trial', 'actions': 'choice'})
for participant in exp2.participant.unique():
    for task in exp2.task.unique():
        exp2.loc[(exp2['participant'] == participant) & (exp2['task'] == task), 'trial'] = np.arange(24)

# exp2['task'] = exp2['task'] - 1 # 0 to 3 for 0-indexing
exp2.to_csv('./exp2.csv') # set exp2
