import pandas as pd

def load_csv(file):
    return pd.read_csv(file)


def dataframe_to_text(df):
    return df.to_string(index=False)