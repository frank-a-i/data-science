import pandas as pd
import os 
from sqlalchemy.engine import create_engine

messages = pd.read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "ressources", "messages.csv"))

categories = pd.read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "ressources",  "categories.csv"))


df = pd.merge(messages, categories, on="id")

categories = df.get("categories").str.split(";", expand=True)

row = [categories.get(col)[0] for col in range(categories.columns[-1] + 1)]
category_colnames = [col.split("-")[0] for col in row]

categories.columns = category_colnames

for column in categories:
    categories[column] = [float(col.split("-")[1]) for col in categories[column]]

df.drop("categories", axis=1, inplace=True)
ddf = df.join(categories)
ddf.duplicated().value_counts()
df_nodup = ddf.drop_duplicates()
df_nodup.duplicated().value_counts()


engine = create_engine(f'sqlite:///{os.path.join(os.path.dirname(os.path.realpath(__file__)),  "..", "ressources", "ETLFAI.db")}')
df_nodup.to_sql('TableFAI', engine, index=False, if_exists='replace')