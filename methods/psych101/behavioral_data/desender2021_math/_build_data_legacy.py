# Johannes 2023-07-05

# %%
import pandas as pd
import numpy as np

files = ['original_data/MathAxietyRawData_cleaned.txt']

df = pd.read_csv(files[0], sep=' ')
df 

# %%


# add a task column specifying the task with all variations
df['brugofniet'] = df['brugofniet'].replace({'Geen brug': 'without_carry-over', 'Brug': 'with_carry-over'})
# 11 assignments * 3 variations regarding what is shown (33 in total)
# convert tasks into categories from 0 to 32
df['task'] = df.apply(lambda row: f"{row['opgaveAbstr']}_{row['brugofniet']}_{row['afleider']}", axis=1)
df['task'] = df['task'].astype('category')
df['task'] = df['task'].cat.codes

# Exclude subjects where trials != 264
# only subject 66 has 220 trials and no counterbalance setting specified (NaN)
subjects  = df.groupby('Subject').count()
subjects[subjects['Procedure.SubTrial.'] != 264]
df = df[df['Subject'] != 66]

# add a trial column for participants
df['trial'] = df.groupby('Subject').cumcount()

# create a reward column based on Target.ACC.SubTrial. with 1, -1
df['reward'] = df['Target.ACC.SubTrial.'].map({1: 1, 0: -1})

# rename from Dutch to English
df.rename(columns={'Subject': 'participant', 
                   'Counterbalance': 'counterbalance',
                   'afleider': 'distractor',
                   'brugofniet': 'carry-over', 
                   'opgaveAbstr': 'abstract_task', 
                   'operator.SubTrial.': 'operator',
                   'antwoord.SubTrial.': 'displayed_answer',
                   'Target.ACC.SubTrial.': 'accuracy',
                   'stim1.SubTrial.': 'stim1',
                   'stim2.SubTrial.': 'stim2',
                   'Target.RT.SubTrial.': 'RT',
                   'PostConf.RESP.SubTrial.': 'post_confidence',
                   'PreCj.RESP.SubTrial.': 'pre_confidence',
                   }, inplace=True)

#zero based indexing
df.participant = df.participant - 1
df.counterbalance = df.counterbalance - 1

# in columns pre_confidence and post_confidence replace {SPACE} to _
df['pre_confidence'] = df['pre_confidence'].replace({'{SPACE}': '_'})
df['post_confidence'] = df['post_confidence'].replace({'{SPACE}': '_'})

df
# %%
# create choice variable
correct_displayed_answer = df[df['distractor'].str.contains('Correct')].copy()
incorrect_displayed_answer = df[~df['distractor'].str.contains('Correct')].copy()

# for correct_displayed_answer
# counterbalance = 0
# accuracy == 1 -> choice == 'c'
# accuracy == 0 -> choice == 'n'
# counterbalance = 1
# accuracy == 1 -> choice == 'n'
# accuracy == 0 -> choice == 'c'
conditions = [
    (correct_displayed_answer['counterbalance'] == 0) & (correct_displayed_answer['accuracy'] == 1),
    (correct_displayed_answer['counterbalance'] == 0) & (correct_displayed_answer['accuracy'] == 0),
    (correct_displayed_answer['counterbalance'] == 1) & (correct_displayed_answer['accuracy'] == 1),
    (correct_displayed_answer['counterbalance'] == 1) & (correct_displayed_answer['accuracy'] == 0)
]
choices = ['c', 'n', 'n', 'c']
correct_displayed_answer['choice'] = np.select(conditions, choices, default='default')

# for incorrect_displayed_answer
conditions = [
    (incorrect_displayed_answer['counterbalance'] == 0) & (incorrect_displayed_answer['accuracy'] == 1),
    (incorrect_displayed_answer['counterbalance'] == 0) & (incorrect_displayed_answer['accuracy'] == 0),
    (incorrect_displayed_answer['counterbalance'] == 1) & (incorrect_displayed_answer['accuracy'] == 1),
    (incorrect_displayed_answer['counterbalance'] == 1) & (incorrect_displayed_answer['accuracy'] == 0)
]
choices = ['n', 'c', 'c', 'n']
incorrect_displayed_answer['choice'] = np.select(conditions, choices, default='default')

# checkout if incorrect_displayed_answer / correct_displayed_answer is correctly mapped in choice
#check = incorrect_displayed_answer[['choice', 'counterbalance', 'accuracy']]
#check[check['counterbalance'] == 1]

df = pd.concat([incorrect_displayed_answer, correct_displayed_answer], axis=0)

# add tasks for the prompt
df['task_no_answer'] = df.apply(lambda row: str(row['stim1']) + str(row['operator']) + str(row['stim2']), axis=1)
df['task_answer'] = df.apply(lambda row: str(row['task_no_answer']) + '=' + str(row['displayed_answer']), axis=1)

# rearrange columns
df = df[['participant', 'task', 'trial', 'choice', 'reward', 'task_no_answer', 'task_answer', 'counterbalance', 'pre_confidence', 'post_confidence', 'RT', 'carry-over', 'distractor', 'accuracy', 'abstract_task', 'stim1', 'stim2', 'displayed_answer']]

print(df)
df.to_csv('exp1.csv', index=False)
df

# NOTE
# Since it is not noted what Counterbalance 0/1 mean check both
#df[(df['task'] == 'XX-X_without_carry-over') & (df['counterbalance'] == 0)]
#df[(df['task'] == 'XX-X_without_carry-over') & (df['counterbalance'] == 1)]
# it seems like Counterbalance 0 is the the condition mentioned in the paper
# and Counterbalance 1 is the reversed condition
# %%
