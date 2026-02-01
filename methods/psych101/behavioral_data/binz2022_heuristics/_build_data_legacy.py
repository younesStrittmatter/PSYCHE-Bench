import pandas as pd
import numpy as np

files = ['original_data/exp1.csv', 'original_data/exp2.csv', 'original_data/exp3.csv']

for i, file in enumerate(files):
    df = pd.read_csv(file)

    # add reward
    df['reward'] = 2 * ((df['choice'] == df['target']).astype(float) - 0.5)

    # rearrange columns
    if i < 2:
        df = df[['participant', 'task', 'step', 'choice', 'reward', 'x0', 'x1', 'x2', 'x3', 'target', 'time']]
        df.columns = ['participant', 'task', 'trial', 'choice', 'reward', 'x0', 'x1', 'x2', 'x3', 'target', 'time']
    else:
        df = df[['participant', 'task', 'step', 'choice', 'reward', 'x0', 'x1', 'target', 'time']]
        df.columns = ['participant', 'task', 'trial', 'choice', 'reward', 'x0', 'x1', 'target', 'time']

    print(df)
    df.to_csv('exp' + str(i + 1) + '.csv')
