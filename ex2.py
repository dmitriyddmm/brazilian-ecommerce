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
query = sql_queries['count_orders']
data = pandas.read_sql_query(query, conn)

# извлечь месяц в отдельный столбец и установить штат в качестве индекса
data['month'] = data['period'].dt.strftime('%Y.%m')
data.drop('period', axis='columns', inplace=True)
data.set_index('state', drop=True, inplace=True)

# отфильтровать строки по нужному месяцу
month = input('Год.Месяц: ')  # 2016.10
data = data[data['month'] == month]
data.drop('month', axis='columns', inplace=True)

# оставить для диаграммы топ 5 штатов, остальные убрать в одну отдельную строку
data.sort_values(by=['count'], ascending=[False], inplace=True)
data.loc['others'] = [data.iloc[6:]['count'].sum()]
data = pandas.concat([data.iloc[:5], data[data.index == 'others']])

# создать диаграмму
data.plot(y='count', title=month, autopct='%.1f%%', legend=False, kind='pie')
plt.show()