import pandas as pd
import glob

# config is ignore for now
data = []
for participant, file in enumerate(glob.glob("original_data/magic_carpet/choices/*_game.csv")):
    participant_string = file.split("_game")[0]
    tutorial_file = participant_string + "_tutorial.csv"
    config_file = participant_string + "_config.txt"
    df = pd.read_csv(file)
    for index, row in df.iterrows():
        data.append([participant, 0, 2*index, 999, row.choice1-1, 0, row.rt1, row.isymbol_lft-1, row.isymbol_rgt-1])
        data.append([participant, 0, 2*index+1, row.final_state-1, row.choice2-1, row.reward, row.rt2, row.fsymbol_lft-1, row.fsymbol_rgt-1])

df = pd.DataFrame(data, columns=['participant', 'task', 'trial', 'current_state', 'choice', 'reward', 'RT', 'state_left', 'state_right'])
df['current_state'] = df['current_state'].astype('int')
df['choice'] = df['choice'].astype('int')
df['state_left'] = df['state_left'].astype('int')
df['state_right'] = df['state_right'].astype('int')

df['choice'] = df['choice'].replace(-2, -1)
df['current_state'] = df['current_state'].replace(-2, -1)
print(df)
df.to_csv('exp1.csv')
