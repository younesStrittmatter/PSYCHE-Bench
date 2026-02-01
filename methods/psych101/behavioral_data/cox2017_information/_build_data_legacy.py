import pandas as pd
import numpy as np

# Load the original data
df = pd.read_csv("original_data/all_data_studytest.csv")

# Define a function to map resp.type values to rewards
def map_reward(resp_type):
    if resp_type in ['Hit', 'CR']:
        return 1
    elif resp_type in ['Miss', 'FA']:
        return -1
    else:
        return None
    
# Apply the mapping function to create the 'reward' column
df['reward'] = df['resp.type'].apply(map_reward)

# Rearrange columns
df = df[['subject', 'block', 'trial', 'phase', 'condition', 'resp', 'resp.type', 'resp.string', 'reward', 'rt', 'stim.string.left', 'stim.string.right']]
# Rename columns
df.columns = ['participant', 'task', 'trial', 'phase', 'condition', 'choice', 'resp.type', 'resp.string', 'reward', 'rt', 'stim.string.left', 'stim.string.right']


#############################################################
#############################################################


# Initialize a dictionary to store 'study' block values for each unique combination
study_block_dict_left = {}
study_block_dict_right = {}

for index, row in df.iterrows():
    if row['phase'] == 'study':
        # Create a unique key based on 'participant' and 'task' columns
        key = (row['participant'], row['task'])
        if key not in study_block_dict_left:
            study_block_dict_left[key] = []
        if key not in study_block_dict_right:
            study_block_dict_right[key] = []
        study_block_dict_left[key].append(row['stim.string.left'])
        study_block_dict_right[key].append(row['stim.string.right'])

# if row['condition'] != 'Lexical decision':
    # Create a new 'study.list' column in the DataFrame
    # df['study.list.left'] = [study_block_dict_left[(row['participant'], row['task'])] if row['phase'] == 'test' else [] for _, row in df.iterrows()]
    # df['study.list.right'] = [study_block_dict_right[(row['participant'], row['task'])] if row['phase'] == 'test' else [] for _, row in df.iterrows()]
df['study.list.left'] = [study_block_dict_left.get((row['participant'], row['task']), []) if row['phase'] == 'test' else [] for _, row in df.iterrows()]
df['study.list.right'] = [study_block_dict_right.get((row['participant'], row['task']), []) if row['phase'] == 'test' else [] for _, row in df.iterrows()]


#############################################################
#############################################################


# Filter the DataFrame to keep only rows where 'phase' is 'test'
df = df[df['phase'] == 'test']
df.reset_index(drop=True, inplace=True)


#############################################################
#############################################################

participant_index = 0
task_index = 0

current_participant = None
current_task = None

participant_indices = []
task_indices = []

# For zero indexing participant, task, and trial
for index, row in df.iterrows():
    if current_participant != row['participant']:
        current_participant = row['participant']
        participant_index += 1
        task_index = 0  # Reset task index when participant changes
    if current_task != row['task']:
        current_task = row['task']
        task_index += 1  # Increment task index when task changes
    participant_indices.append(participant_index)
    task_indices.append(task_index)

# Add the new columns to the DataFrame
df['participant'] = participant_indices
df['task'] = task_indices

# Zero-index
df['participant'] = df['participant'] - 1
df['task'] = df['task'] - 1
df['trial'] = df['trial'] - 1

# Save the updated data in one file
# Each experiment includes 5 different tasks: Single item recognition, associative recognition, cued recall, free recall and lexical decision
df.to_csv("exp1.csv", index=False)