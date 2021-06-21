import numpy as np
import itertools
import sys
import multiprocessing as mp
import functools

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


def constraints_check(variant, kursy):
    kp = kursy[["Kod kursu", 'Grupa kursu']].groupby("Kod kursu")['Grupa kursu'].apply(list).reset_index(
        name='Grupy').copy()
    # sprawdzenie czy zapisany na każdy kurs
    if len(variant) != kp.shape[0]:
        return
    # sprawdzenie czy kursy nie nakładają się na siebie
    PLAN = np.zeros((10, 14))
    for gr in variant:
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
        return
    if len(PLAN[PLAN > 1]) > 0:
        return
    return variant, PLAN


def dividing_data(results):
    PLANS = []
    timetables = []
    for res in results:
        if res is None:
            continue
        else:
            timetables.append(res[0])
            PLANS.append(res[1])
    return timetables, PLANS


def generate(kursy):
    timetables = []
    grupy = \
        kursy[["Kod kursu", 'Grupa kursu']].groupby("Kod kursu")['Grupa kursu'].apply(list).reset_index(
            name='Grupy')[
            'Grupy'].tolist()
    num = 0
    all_solutions = kursy[["Kod kursu", 'Grupa kursu']].groupby("Kod kursu").count().prod().values[0]
    for element in itertools.product(*grupy):
        perc = int(float((num + 1) / all_solutions) * 100)
        sys.stdout.write('\r')
        sys.stdout.write("[%-100s] %d%%" % ('=' * perc, perc))
        sys.stdout.flush()
        num += 1
        timetables.append(element)
    partial_constraints_check = functools.partial(constraints_check, kursy=kursy)
    with mp.Pool() as pool:
        res = pool.map(partial_constraints_check, timetables)
    timetables, PLANS = dividing_data(res)
    return timetables, PLANS


if __name__ == "__main__":
    pass
