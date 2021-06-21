import pandas as pd
import os.path


def clean_data(df):
    for i in df.index:
        df.at[i, "Prowadzący"] = list(map(lambda x: x.split(" "), df.loc[i]["Prowadzący"].split(", ")))
        if len(df.at[i, "Godzina rozpoczęcia"]) < 5:
            df.at[i, "Godzina rozpoczęcia"] = '0' + df.at[i, "Godzina rozpoczęcia"]
        if len(df.at[i, "Godzina zakończenia"]) < 5:
            df.at[i, "Godzina zakończenia"] = '0' + df.at[i, "Godzina zakończenia"]
    return df


def read_csv(path):
    if os.path.isfile(path):
        kursy = pd.read_csv(path, sep=";")
        kursy = clean_data(kursy)
        return kursy
    else:
        raise NameError("File error: No such file in the data directory!")


if __name__ == "__main__":
    pass
