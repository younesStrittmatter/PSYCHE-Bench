# %%
import numpy as np
import pandas as pd
import jsonlines
import sys
sys.path.append("..")
from utils import randomized_choice_options

# Note that we did not include data from experiment 2 because the preexperimental task cannot be translated into prompts for LLM.
datasets = ["exp1.csv"]
all_prompts = []

# %%
for dataset in datasets:
    df = pd.read_csv(dataset)
    df["task"] = df["task"].astype(int)
    df["trial"] = df["trial"].astype(int)
    df["choice"] = df["choice"].astype(int)

    num_participants = df.participant.max() + 1
    num_tasks = df.task.max() + 1
    num_trials = df.trial.max() + 1

    for participant in range(num_participants):
        df_participant = df[(df['participant'] == participant)]

        choice_options = randomized_choice_options(num_choices=2)


        prompt = 'You are going to plant different types of trees in two different gardens: (0): North and (1): South.\n' \
                 'The trees look different from each other regarding their leafiness and branchiness.\n' \
                 'There are 5 levels of leafiness (0,1,2,3,4) and 5 levels of branchiness (0,1,2,3,4).\n' \
                 'Your task is to learn which type of tree grows best in each garden. If you "accept" to plant the tree and your answer is correct, you will be rewarded with points, otherwise you will lose some points. If you "reject" to plan the tree, you will not be rewarded (0 point). \n' \
                 'There will be 600 trials in total divided into two blocks (400 trials for training, and 200 trials for testing). During training, there will be feedback on every trial about your decisions (as points). During testing, there will be no feedback for your decision.\n' \
                 'In addition, you are not allowed to choose the garden, and you can only decide whether to "accept" (option ' + choice_options[1]+') or "reject" (option ' + choice_options[0]+') to plan each tree given you are already in a specific garden.\n\n'


        for task in range(num_tasks):
            df_task = df_participant[(df_participant['task'] == task)]
            #prompt += 'Task ' + str(task + 1) + ':\n'
            for trial in range(num_trials):
                df_trial = df_task[(df_task['trial'] == trial)]
                c = df_trial.choice.item()
                r = df_trial.reward.item()
                g = df_trial.context.item()
                l = df_trial.leaf.item()
                b = df_trial.branch.item()
                if trial <= 399: # training block (with feedback)
                    prompt += '- In garden (' + str(g) + '), you get a tree with level ' + str(l) + ' of leafiness ' + ' and level ' +str(b) + ' of branchiness. ' + 'You selected option {' + choice_options[c] + '} and got ' + str(r) + ' points.\n'
                if trial > 399: # testing block (without feedback)
                    prompt += '- In garden (' + str(g) + '), you get a tree with level ' + str(l) + ' of leafiness ' + ' and level ' +str(b) + ' of branchiness. ' + 'You selected option {' + choice_options[c] + '}.\n'
            prompt += '\n'

        prompt = prompt[:-2]
        print(prompt)
        all_prompts.append({'text': prompt})

with jsonlines.open('prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)



# %%
