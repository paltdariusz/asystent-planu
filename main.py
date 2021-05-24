import json
import numpy as np

from asystent_planu.modules.data_reader import read_csv
from asystent_planu.modules.criteria_computation import gaps_counter, working_days_counter, early_hours_counter, \
    late_hours_counter, avg_lecturers_marks, evenness_of_classes
from asystent_planu.modules.marks_scrapper import join_marks, scrape
from asystent_planu.modules.ahp import create_ahp, normalize_ahp
from asystent_planu.modules.timetables_generator import generate
from asystent_planu.modules.visualization import visualize


def calculate_objective_function(wagi, PLAN, kursy, timetable):
    obj_f_val = wagi[0] * gaps_counter(PLAN)
    obj_f_val += wagi[1] * working_days_counter(PLAN)
    obj_f_val += wagi[2] * early_hours_counter(PLAN)
    obj_f_val += wagi[3] * late_hours_counter(PLAN)
    obj_f_val += wagi[4] * avg_lecturers_marks(kursy, timetable)
    obj_f_val += wagi[5] * evenness_of_classes(PLAN)
    return obj_f_val


if __name__ == '__main__':
    kursy = read_csv('plan')
    try:
        with open('data/lecturers_marks.json') as file:
            oceny = json.load(file)
    except FileNotFoundError:
        print('[ + ] Nie znaleziono pliku z bazą ocen wykładowców!')
        print('[ + ] Pobieranie bazy ocen wykładowców...')
        oceny = scrape()
    kursy = join_marks(oceny, kursy)
    wagi = normalize_ahp(create_ahp(True))
    timetables, PLANS = generate(kursy)
    zmax = 1000000
    tab_Z = np.zeros((len(timetables)))
    najlepsze = []
    for i in range(len(timetables)):
        z = calculate_objective_function(wagi, PLANS[i], kursy, timetables[i])
        tab_Z[i] = z
        if z < zmax:
            zmax = z
            najlepsze = [[z, i]]
        elif z == zmax:
            najlepsze.append([z, i])
    # print(tab_Z)
    for i in range(len(najlepsze)):
        # print(naj)
        # print(PLANS[naj[1]])
        # print(timetables[naj[1]])
        # print(kursy[kursy['Grupa kursu'].isin(timetables[naj[1]])].to_string())
        visualize(kursy[kursy['Grupa kursu'].isin(timetables[najlepsze[i][1]])], i)
    # print(kursy.to_string())
