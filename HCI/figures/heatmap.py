import pandas
import matplotlib.pyplot as plt

morten = pandas.read_csv("./morten.csv", index_col='id').sort_index()
arash = pandas.read_csv("./arash.csv", index_col='id').sort_index()
mikael = pandas.read_csv("./mikael.csv", index_col='id').sort_index()
andreas = pandas.read_csv("./andreas.csv", index_col='id').sort_index()

ex_name = pandas.read_csv("./exercise_names.csv", index_col='id').sort_index()


def get_avg(key):
    return (morten[key] + arash[key] + mikael[key] + andreas[key]) / 4

df_avg = pandas.DataFrame()

df_avg['pleasure'] = get_avg('pleasure')
df_avg['arousal'] = get_avg('arousal')
df_avg['name'] = ex_name['name']

df_all = morten.copy()
df_all = df_all.append(arash)
df_all = df_all.append(mikael)
df_all = df_all.append(andreas)

df_all[df_all.index > 5].plot(kind='hexbin', x='pleasure', y='arousal', gridsize=9)
plt.savefig('hexbin.png')


names = ex_name['name'][ex_name.index > 5]

morten[morten.index > 5].plot(kind='bar', title='Person 3', x=names, ylim=(0, 9))
plt.savefig('AGmorten.png')

arash[arash.index > 5].plot(kind='bar', title='Person 2', x=names, ylim=(0, 9))
plt.savefig('AGarash.png')

mikael[mikael.index > 5].plot(kind='bar', title='Person 1', x=names, ylim=(0, 9))
plt.savefig('AGmikael.png')

andreas[andreas.index > 5].plot(kind='bar', title='Person 4', x=names, ylim=(0, 9))
plt.savefig('AGandreas.png')

