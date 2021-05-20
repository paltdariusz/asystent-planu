import pandas as pd
import os.path


def clean_data(df):
    for i in df.index:
        df.at[i, "Prowadzący"] = list(map(lambda x: x.split(" "), df.loc[i]["Prowadzący"].split(", ")))
    return df


def read_csv(name):
    path = "../data/" + name + ".csv"
    if os.path.isfile(path):
        kursy = pd.read_csv(path, sep=";")
        kursy = clean_data(kursy)
        return kursy
    else:
        raise NameError("File error: No such file in the data directory!")


if __name__ == "__main__":
    read_csv("plan")
