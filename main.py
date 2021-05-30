import json
import numpy as np
import os.path
import shutil
import sys

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
    plik = 'plan2'
    kursy = read_csv(plik)
    try:
        with open('data/lecturers_marks.json', 'r') as file:
            oceny = json.load(file)
    except FileNotFoundError:
        print('[ + ] Nie znaleziono pliku z bazą ocen wykładowców!')
        print('[ + ] Pobieranie bazy ocen wykładowców...')
        oceny = scrape()
    kursy = join_marks(oceny, kursy)
    wagi = normalize_ahp(create_ahp(True))
    try:
        with open(f'data/results/{plik}/timetables.json', 'r') as file:
            timetables = json.load(file)
        with open(f'data/results/{plik}/PLANS.json', 'r') as file:
            PLANS = json.load(file)
            PLANS = [np.array(i) for i in PLANS]
    except FileNotFoundError:
        print("GENEROWANIE DOPUSZCZALNYCH PLANÓW:", sep=' ')
        timetables, PLANS = generate(kursy)
        print('\n')
        if not os.path.exists(f'data/results/{plik}'):
            os.makedirs(f'data/results/{plik}')
        with open(f'data/results/{plik}/timetables.json', 'w') as file:
            json.dump(timetables, file)
        with open(f'data/results/{plik}/PLANS.json', 'w') as file:
            temp = [i.tolist() for i in PLANS]
            json.dump(temp, file)
    zmax = 1000000
    tab_Z = np.zeros((len(timetables)))
    print(f'LICZBA DOPUSZCZALNYCH ROZWIĄZAŃ: {len(timetables)}\n')
    najlepsze = []
    print('WYBIERANIE NAJLEPSZYCH ROZWIĄZAŃ:', sep=' ')
    for i in range(len(timetables)):
        perc = int(float((i+1)/len(timetables))*100)
        sys.stdout.write('\r')
        sys.stdout.write("[%-100s] %d%%" % ('='*perc, perc))
        sys.stdout.flush()
        z = calculate_objective_function(wagi, PLANS[i], kursy, timetables[i])
        tab_Z[i] = z
        if z < zmax:
            zmax = z
            najlepsze = [[z, i]]
        elif z == zmax:
            najlepsze.append([z, i])

    dir = 'results'
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

    print('\n\nWYNIKI\n')
    print(f'LICZBA OPTYMALNYCH ROZWIĄZAŃ: {len(najlepsze)}\n')
    print('WARTOŚCI FUNKCJI CELU:')
    print(tab_Z)
    print("\nNAJLEPSZE WYNIKI:")
    for i in range(len(najlepsze)):
        print(f"\nRozwiązanie {i + 1}.\n")
        print(
            f"WARTOŚĆ FUNKCJI CELU: {najlepsze[i][0]}\nNUMER INDEKSU W WYGENEROWANYCH ROZWIĄZANIACH: {najlepsze[i][1]}\n")
        print("TABLICA BINARNA PRZEDSTAWIAJĄCA ZAJĘTE GODZINY")
        print(PLANS[najlepsze[i][1]])
        print()
        print('WYBRANE GRUPY ZAJĘCIOWE')
        print(timetables[najlepsze[i][1]])
        print()
        print(kursy[kursy['Grupa kursu'].isin(timetables[najlepsze[i][1]])].to_string())
        visualize(kursy[kursy['Grupa kursu'].isin(timetables[najlepsze[i][1]])], i)
    # print(kursy.to_string())
