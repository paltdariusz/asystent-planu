import pandas as pd
import os.path
import json


def clean_data(df):
    for i in df.index:
        df.at[i, "Prowadzący"] = list(map(lambda x: x.split(" "), df.loc[i]["Prowadzący"].split(", ")))
        if len(df.at[i, "Godzina rozpoczęcia"]) < 5:
            df.at[i, "Godzina rozpoczęcia"] = '0' + df.at[i, "Godzina rozpoczęcia"]
        if len(df.at[i, "Godzina zakończenia"]) < 5:
            df.at[i, "Godzina zakończenia"] = '0' + df.at[i, "Godzina zakończenia"]
    return df


def read_csv(name):
    path = "data/" + name + ".csv"
    if os.path.isfile(path):
        kursy = pd.read_csv(path, sep=";")
        kursy = clean_data(kursy)
        return kursy
    else:
        raise NameError("File error: No such file in the data directory!")


if __name__ == "__main__":
    from criteria_computation import avg_lecturers_marks

    x = read_csv("plan")
    with open(
            '/Users/dariuszpalt/OneDrive - Politechnika Wroclawska/STUDIA/studia sem6/ZAAW. METODY WSPOMAGANIA DECYZ/PROJEKT/asystent_planu/data/lecturers_marks.json') as file:
        marks = json.load(file)
    x['Marks'] = None
    print(x['Prowadzący'])
    for i in x.index:
        # print(i)
        avg = 0
        ile = 0
        d = x['Prowadzący'][i]
        for j in d:
            for lect in marks:
                if (j[1] in lect['name']) and (j[0] in lect['name']):
                    avg += float(lect['mark'])
                    ile += 1
        if ile != 0:
            avg /= ile
            x.at[i, 'Marks'] = avg
    print(avg_lecturers_marks(x))
