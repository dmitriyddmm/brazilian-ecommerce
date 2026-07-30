from consts import *
import psycopg2
import pandas
import matplotlib.pyplot as plt


# получить данные из базы
conn = psycopg2.connect(
    dbname='brazilian_commerce',
    user='postgres',
    password='root',
    host='localhost',
    port=5432
)
query = sql_queries['changing_weight']
data = pandas.read_sql_query(query, conn)

# вынести месяц в отдельный столбец и округлить вес
data['month'] = data['period'].dt.month
data.drop('period', axis='columns', inplace=True)
data['sum'] = data['sum'].round(2)

# отфильтровать строки по категориям
categories = input('Категории через запятую: ').split(', ')  # agro_industry_and_commerce, air_conditioning, art
data = data[data['category_name'].isin(categories)]

# добавить недостающие месяцы
dfs = []
for i, category in enumerate(categories):
    dfs.append(data[data['category_name'] == category])
    dfs[i].rename(columns={'sum': dfs[i]['category_name'].iloc[0]}, inplace=True)
    dfs[i].drop('category_name', axis='columns', inplace=True)
    dfs[i].set_index('month', drop=True, inplace=True)
    for month in range(1, 12 - 1):
        if month not in dfs[i].index:
            value = 0 if month == 1 else dfs[i][dfs[i].columns[0]].loc[month - 1]
            dfs[i].loc[month] = [value]
        dfs[i].sort_index(inplace=True)
result_df = dfs[0]

# пересобрать датафрейм, чтобы одной строке соответствовал один месяц всех категорий
if len(dfs) > 1:
    for df in dfs:
        result_df[df.columns[0]] = df[df.columns[0]]

result_df.plot(kind='line', title='Суммарный вес товаров заказанных категорий в течение года', legend=True)
plt.show()