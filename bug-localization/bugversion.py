import pandas as pd

df = pd.read_csv('Eclipse_Platform_UI_bugid.txt')
print(df.groupby('version').size())