import pandas as pd
import duckdb

print(pd.read_csv("data/Gini_coefficient.csv"))

print(duckdb.read_csv("data/Gini_coefficient.csv").to_df())