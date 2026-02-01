import pandas as pd
import numpy as np

hum_dat_raw = pd.read_csv('original_data/raw_dat.csv')

hum_centaur = hum_dat_raw.copy()
hum_centaur = hum_centaur.rename(columns={'id': 'participant'})
hum_centaur['trial'] = np.repeat(np.arange(150), max(hum_centaur['participant']))
hum_centaur['participant'] -= 1
hum_centaur['choice'] -= 1
hum_centaur['task'] = 'four_armed_bandit'

hum_centaur.to_csv('exp.csv')
