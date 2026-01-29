import scipy.io
import pandas as pd
import numpy as np

mat = scipy.io.loadmat('original_data/HilbigMoshagen2016TrialLevel.mat')
data = []
for i in range(mat['d']['nSubjects'].item().item()):
  for j in range(mat['d']['nTrials'].item().item()):
    choice = mat['d']['decision'].item()[i, j] - 1
    item_type = mat['d']['itemType'].item()[i, j]
    stimulus_0 = mat['d']['stimulus'].item()[:, 0, i, j]
    stimulus_1 = mat['d']['stimulus'].item()[:, 1, i, j]
    validities = mat['d']['validity'].item()
    data.append([i, 0, j, choice, 0, stimulus_0, stimulus_1, validities[0], item_type])
df = pd.DataFrame(data, columns=['participant', 'task', 'trial', 'choice', 'reward', 'stimulus_0', 'stimulus_1', 'validities', 'item_type'])
print(df)
df.to_csv('exp1.csv')
