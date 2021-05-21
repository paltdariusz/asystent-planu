import pandas as pd
import numpy as np
import itertools

from data_reader import read_csv

GODZINY = {
    'rozpoczęcia': {
        '07:30': 0,
        '08:15': 1,
        '09:15': 2,
        '10:15': 3,
        '11:15': 4,
        '12:15': 5,
        '13:15': 6,
        '14:15': 7,
        '15:15': 8,
        '16:10': 9,
        '17:05': 10,
        '18:00': 11,
        '18:55': 12,
        '19:50': 13
    },
    'zakończenia': {
        '08:15': 0,
        '09:00': 1,
        '10:00': 2,
        '11:00': 3,
        '12:00': 4,
        '13:00': 5,
        '14:00': 6,
        '15:00': 7,
        '16:00': 8,
        '16:55': 9,
        '17:50': 10,
        '18:45': 11,
        '19:40': 12,
        '20:35': 13
    }
}


def generate(plan_name):
    kursy = read_csv(plan_name)
    timetables = []
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    grupy = \
        kursy[["Kod kursu", 'Grupa kursu']].groupby("Kod kursu")['Grupa kursu'].apply(list).reset_index(name='Grupy')[
            'Grupy'].tolist()
    PLANS = []
    for element in itertools.product(*grupy):
        # sprawdzenie czy każdy kursy jest unikalny
        if len(set(element)) != len(element):
            continue
        kp = kursy[["Kod kursu", 'Grupa kursu']].groupby("Kod kursu")['Grupa kursu'].apply(list).reset_index(
            name='Grupy').copy()
        # sprawdzenie czy zapisany na każdy kurs
        if len(element) != kp.shape[0]:
            continue
        for gr in element:
            for i in range(kp.shape[0]):
                if gr in kp.loc[i, 'Grupy']:
                    kp.drop(index=i, inplace=True)
                    kp.reset_index(drop=True, inplace=True)
                    break
        if kp.shape[0] != 0:
            continue
        # sprawdzenie czy kursy nie nakładają się na siebie
        PLAN = np.zeros((10, 14))
        for gr in element:
            dane = kursy[kursy['Grupa kursu'] == gr][['Godzina rozpoczęcia', 'Godzina zakończenia', 'Dzień', 'Tydzień']]
            g_roz = GODZINY['rozpoczęcia'][dane['Godzina rozpoczęcia'].values[0]]
            g_zak = GODZINY['zakończenia'][dane['Godzina zakończenia'].values[0]]
            if dane['Tydzień'].values[0] == 'C':
                for i in range(g_roz, g_zak + 1):
                    PLAN[dane['Dzień'].values[0] - 1, i] += 1
                    PLAN[dane['Dzień'].values[0] - 1 + 5, i] += 1
            elif dane['Tydzień'].values[0] == 'N':
                for i in range(g_roz, g_zak + 1):
                    PLAN[dane['Dzień'].values[0] - 1, i] += 1
            elif dane['Tydzień'].values[0] == 'P':
                for i in range(g_roz, g_zak + 1):
                    PLAN[dane['Dzień'].values[0] - 1 + 5, i] += 1
        p_n = PLAN[:5] + PLAN[5:]
        if len(p_n[p_n > 2]) > 0:
            continue
        if len(PLAN[PLAN > 1]) > 0:
            continue
        timetables.append(element)
        PLANS.append(PLAN)
    return timetables, PLANS


if __name__ == "__main__":
    generate("plan")
