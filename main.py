import json
import numpy as np
import os.path
import shutil
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image

from asystent_planu.modules.data_reader import read_csv
from asystent_planu.modules.criteria_computation import gaps_counter, working_days_counter, early_hours_counter, \
    late_hours_counter, avg_lecturers_marks, evenness_of_classes
from asystent_planu.modules.marks_scrapper import join_marks, scrape, check_if_credentials_exists, save_credentials, \
    credentials_verification
from asystent_planu.modules.ahp import consistency_check, repair_consistency
from asystent_planu.modules.timetables_generator import generate
from asystent_planu.modules.visualization import visualize

kursy = None
filename = ""

valuelist = [-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8]
co_chcemy = ["1/9", "1/8", "1/7", "1/6", "1/5", "1/4", "1/3", "1/2", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
co_mamy = [1 / 9, 1 / 8, 1 / 7, 1 / 6, 1 / 5, 1 / 4, 1 / 3, 1 / 2, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def change_week():
    global tydzien_widok
    img = ImageTk.PhotoImage(
        Image.open(f"results/{ktory_plan}/{tydzien_widok.get()}.png").resize((1280, 720), Image.ANTIALIAS))
    imglab.configure(image=img)
    imglab.image = img
    if tydzien_widok.get() == "TN":
        tydzien_widok.set("TP")
    else:
        tydzien_widok.set("TN")


def save_plot():
    save_loc = tk.filedialog.askdirectory()
    if save_loc:
        shutil.copyfile(f'results/{ktory_plan}/TP.png', save_loc + '/TP.png')
        shutil.copyfile(f'results/{ktory_plan}/TN.png', save_loc + '/TN.png')
        tk.messagebox.showinfo("Zapisano", f"Zapisano pliki w {save_loc + '/'} jako TP.png i TN.png")


def show_group_codes():
    window = tk.Toplevel()
    window.title("Kody grup")
    kody_labels = [tk.Entry(window) for i in timetables[najlepsze[ktory_plan][1]]]
    for i in range(len(kody_labels)):
        kody_labels[i].insert(0, timetables[najlepsze[ktory_plan][1]][i])
        kody_labels[i].config(state='readonly')
        kody_labels[i].pack()


def change_photo(zmiana):
    global ktory_plan, next_button, previous_button
    if ktory_plan+zmiana > 0:
        ktory_plan += zmiana
        img = ImageTk.PhotoImage(
            Image.open(f"results/{ktory_plan}/{'TP' if tydzien_widok.get() == 'TN' else 'TN'}.png").resize((1280, 720),
                                                                                                           Image.ANTIALIAS))
        imglab.configure(image=img)
        imglab.image = img
    if ktory_plan == rozwiazania[-1]:
        next_button['state'] = tk.DISABLED
        if len(rozwiazania) > 1 and previous_button['state'] == tk.DISABLED:
            previous_button['state'] = tk.NORMAL
    elif ktory_plan == rozwiazania[0]:
        previous_button['state'] = tk.DISABLED
        if len(rozwiazania) > 1 and next_button['state'] == tk.DISABLED:
            next_button['state'] = tk.NORMAL
    elif previous_button['state'] == tk.DISABLED:
        previous_button['state'] = tk.NORMAL
    elif next_button['state'] == tk.DISABLED:
        next_button['state'] = tk.NORMAL


def calculate_objective_function(wagi, PLAN, kursy, timetable):
    obj_f_val = wagi[0] * (gaps_counter(PLAN)/(12*10))
    obj_f_val += wagi[1] * (working_days_counter(PLAN)/10)
    obj_f_val += wagi[2] * (early_hours_counter(PLAN)/10)
    obj_f_val += wagi[3] * (late_hours_counter(PLAN)/(4*10))
    obj_f_val += wagi[4] * (avg_lecturers_marks(kursy, timetable)/5.5)
    obj_f_val += wagi[5] * (evenness_of_classes(PLAN)/30)
    return obj_f_val


def valuecheck(value, i, wybor):
    global punktyp, punktyl, ahps
    punktyp[i].set(co_chcemy[int(value) + 8])
    punktyl[i].set(co_chcemy[-(int(value) + 8) - 1])
    ahp_triang_idcs = np.triu_indices(ahps[0].shape[0], 1)
    ahps[typy_studentow.index(wybor)][ahp_triang_idcs[0][i], ahp_triang_idcs[1][i]] = co_mamy[-(int(value) + 8) - 1]
    ahps[typy_studentow.index(wybor)][ahp_triang_idcs[1][i], ahp_triang_idcs[0][i]] = co_mamy[int(value) + 8]
    wyniki = consistency_check(ahps[typy_studentow.index(wybor)])
    crv.set(np.round(wyniki[1], 3))


def get_file():
    global kursy, filename, zaladujtxt
    filename = tk.filedialog.askopenfilename(filetypes=[("Pliki CSV", "*.csv")])
    kursy = read_csv(filename)
    szukaj_planu_butt['state'] = tk.NORMAL
    plik = filename[filename.rfind('/') + 1:filename.rfind('.')]
    zaladujtxt.set(f"Wczytany rozkład: {plik}")


def show_info():
    window_info = tk.Toplevel()
    window_info.title("Zaawansowane informacje")
    wart_f_celu = najlepsze[ktory_plan][0]
    wart_f_celu_label = tk.Label(window_info, text=f"Wartość funkcji celu: {np.round(wart_f_celu,3)}")
    wart_f_celu_label.pack()
    kryteria = ["Mniej okienek",
                "Więcej dni wolnych",
                "Rzadziej na 7:30",
                "Mniej zajęć po 17:05",
                "Wyższe oceny wykadowców",
                "Bardziej równomierny"]
    wagi_frame = tk.LabelFrame(window_info, text="Wagi")
    wagi_frame.pack()
    wagi_labels = [tk.Label(wagi_frame, justify=tk.LEFT,text=f"{kryteria[i]}:{' '*(len(max(kryteria,key=len)) - len(kryteria[i]))} {np.round(wagi[i],3)}") for i in range(6)]
    for i in range(6):
        wagi_labels[i].pack()


def szukaj_planu(wybor):
    global kursy, imglab, rozwiazania, next_button, change_week_button, timetables, najlepsze, save_button, pokaz_kody_button, wagi, ktory_plan, previous_button
    wyniki_frame.grid(row=0, column=2, rowspan=2)
    try:
        with open('data/lecturers_marks.json', 'r') as file:
            oceny = json.load(file)
    except FileNotFoundError:
        print('[ + ] Nie znaleziono pliku z bazą ocen wykładowców!')
        print('[ + ] Pobieranie bazy ocen wykładowców...')
        tk.messagebox.showinfo("Brak bazy ocen", "Trwa pobieranie bazy ocen wykładowców. Może chwile to potrwać!")
        oceny = scrape()
    kursy = join_marks(oceny, kursy)
    wagi = consistency_check(ahps[wybor])[2]
    plik = filename[filename.rfind('/') + 1:filename.rfind('.')]
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
        perc = int(float((i + 1) / len(timetables)) * 100)
        sys.stdout.write('\r')
        sys.stdout.write("[%-100s] %d%%" % ('=' * perc, perc))
        sys.stdout.flush()
        z = calculate_objective_function(wagi, PLANS[i], kursy, timetables[i])
        tab_Z[i] = z
        if z < zmax:
            zmax = z
            najlepsze = [[z, i]]
        elif z == zmax:
            najlepsze.append([z, i])
    ktory_plan = 0

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
    rozwiazania = sorted(list(map(int, os.listdir('results/'))))
    change_week_button['state'] = tk.NORMAL
    if len(rozwiazania) > 1:
        next_button['state'] = tk.NORMAL
    save_button['state'] = tk.NORMAL
    pokaz_kody_button['state'] = tk.NORMAL
    img = ImageTk.PhotoImage(Image.open("results/0/TN.png").resize((1280, 720), Image.ANTIALIAS))
    tydzien_widok.set("TP")
    imglab.configure(image=img)
    imglab.image = img
    tk.messagebox.showinfo("Znaleziono nowe rozwiązania",
                           f"Dla typu studenta {clicked.get()} znaleziono optymalne rozwiązania w liczbie {len(najlepsze)}")
    previous_button['state'] = tk.DISABLED


def szukaj_planu_p():
    global ahps
    wybor = typy_studentow.index(clicked.get())
    if crv.get() > 0.1:
        message = "Twoja macierz wyboru jest niespójna!\nW celu jej automatycznego poprawienia naciśnij Yes.\n" \
                  "Jeśli nie chcesz wprowadzać poprawek wciśnij No (może spowodować błędne rozwiązania).\n" \
                  "Jeśli natomiast chcesz sam przeprowadzić korekcję wciśnij Cancel. "
        odp = tk.messagebox.askyesnocancel("Twoja macierz wyboru jest niespójna!", message)
        if odp is None:
            return
        elif odp:
            ahps[wybor] = repair_consistency(consistency_check(ahps[wybor])[2])
            typ_stud()
            czy_pasuje = tk.messagebox.askyesno("Pytanko", "Czy pasują Ci skorygowane wagi?")
            if czy_pasuje:
                szukaj_planu(wybor)
            else:
                return
        elif not odp:
            szukaj_planu(wybor)
    else:
        szukaj_planu(wybor)


def typ_stud(trash=None):
    global punktyp, punktyl, szukaj_planu_butt
    wybor = clicked.get()
    ahp = ahps[typy_studentow.index(wybor)]
    crv.set(np.round(consistency_check(ahp)[1], 3))
    slider = [tk.Scale(ahpframe, from_=min(valuelist), to=max(valuelist),
                       command=lambda x, i=i, wybor=wybor: valuecheck(x, i, wybor), orient="horizontal", showvalue=0)
              for i in range(15)]
    pytaniatxt = [
        "Mniej okienek", "vs", "Więcej dni wolnych",
        "Mniej okienek", "vs", "Rzadziej na 7:30",
        "Mniej okienek", "vs", "Mniej zajęć po 17:05",
        "Mniej okienek", "vs", "Wyższe oceny wykadowców",
        "Mniej okienek", "vs", "Bardziej równomierny",
        "Więcej dni wolnych", "vs", "Rzadziej na 7:30",
        "Więcej dni wolnych", "vs", "Mniej zajęć po 17:05",
        "Więcej dni wolnych", "vs", "Wyższe oceny wykadowców",
        "Więcej dni wolnych", "vs", "Bardziej równomierny",
        "Rzadziej na 7:30", "vs", "Mniej zajęć po 17:05",
        "Rzadziej na 7:30", "vs", "Wyższe oceny wykadowców",
        "Rzadziej na 7:30", "vs", "Bardziej równomierny",
        "Mniej zajęć po 17:05", "vs", "Wyższe oceny wykadowców",
        "Mniej zajęć po 17:05", "vs", "Bardziej równomierny",
        "Wyższe oceny wykadowców", "vs", "Bardziej równomierny",
    ]
    pytania_label = [tk.Label(ahpframe, text=i) for i in pytaniatxt]

    for i in range(0, 45, 3):
        pytania_label[i].grid(row=i + 1, column=0)
        pytania_label[i + 1].grid(row=i + 1, column=1)
        pytania_label[i + 2].grid(row=i + 1, column=2)
        slider[int(i / 3)].grid(row=i + 2, column=1, pady=(2, 7))
    punktyl = [tk.StringVar() for i in range(15)]
    punktyp = [tk.StringVar() for i in range(15)]
    ahp_triang_idcs = np.triu_indices(ahp.shape[0], 1)
    ahp_triang = ahp[ahp_triang_idcs]
    for i in range(15):
        punktyl[i].set(co_chcemy[co_mamy.index(ahp_triang[i])])
        punktyp[i].set(co_chcemy[-co_mamy.index(ahp_triang[i]) - 1])
        slider[i].set(valuelist[-co_mamy.index(ahp_triang[i]) - 1])
    ahpp = [tk.Label(ahpframe, textvariable=punktyp[i], padx=10, width=3) for i in range(15)]
    ahpl = [tk.Label(ahpframe, textvariable=punktyl[i], padx=10, width=3) for i in range(15)]
    for i in range(0, 45, 3):
        ahpp[int(i / 3)].grid(row=i + 2, column=2, pady=(2, 7))
        ahpl[int(i / 3)].grid(row=i + 2, column=0, pady=(2, 7))


def zaloguj():
    global login_status, login_window, CREDENTIALS
    CREDENTIALS = {
        "username": login_entry.get(),
        "password": pass_entry.get()
    }
    if credentials_verification(CREDENTIALS):
        save_credentials(CREDENTIALS)
        login_window.destroy()
    else:
        login_status.set("Błędne dane logowania!")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Asystent planu®")
    login_status = tk.StringVar()
    login_status.set("")
    CREDENTIALS = {}
    if not check_if_credentials_exists():
        login_window = tk.Toplevel()
        info_txt = tk.Label(login_window, text="Wprowadź dane logowania do systemu polwro")
        info_txt.grid(row=0, column=0, columnspan=2)
        login_txt = tk.Label(login_window, text="Login: ")
        login_entry = tk.Entry(login_window)
        pass_txt = tk.Label(login_window, text="Hasło: ")
        pass_entry = tk.Entry(login_window, show="*")
        login_button = tk.Button(login_window, text="Zaloguj", command=zaloguj)
        login_status_lab = tk.Label(login_window, textvariable=login_status)
        login_txt.grid(row=1, column=0)
        login_entry.grid(row=1, column=1)
        pass_txt.grid(row=2, column=0)
        pass_entry.grid(row=2, column=1)
        login_button.grid(row=3, column=0, columnspan=2)
        login_status_lab.grid(row=4, column=0, columnspan=2)

    zaladujtxt = tk.StringVar()
    zaladujtxt.set("Wczytaj rozkład zajęć: ")
    zaladuj = tk.Label(root, textvariable=zaladujtxt, padx=10)
    zaladujbutton = tk.Button(root, text="Wczytaj", command=get_file)

    zaladuj.grid(row=0, column=0)
    zaladujbutton.grid(row=0, column=1)
    wagi = []
    ahpframe = tk.LabelFrame(root)
    ahpframe.grid(column=0, row=1, rowspan=2, columnspan=2)

    wybierz_stud_text = tk.Label(ahpframe, text="Wybierz typ studenta: ")
    wybierz_stud_text.grid(row=0, column=0)
    clicked = tk.StringVar()
    typy_studentow = ["Imprezowicz", "Dojeżdżający", "Leń", "Stypendysta", "Pracujący popołudniami",
                      "Stwórz własny typ"]
    clicked.set(typy_studentow[0])
    typy_stud_menu = tk.OptionMenu(ahpframe, clicked, *typy_studentow, command=typ_stud)
    typy_stud_menu.config(width=len(max(typy_studentow, key=len)))
    typy_stud_menu.grid(row=0, column=1, columnspan=2)

    ahps = [
        np.array([
            [1, 5, 1 / 9, 1 / 7, 1 / 3, 1 / 2],
            [1 / 5, 1, 1 / 9, 1 / 5, 1 / 2, 1],
            [9, 9, 1, 2, 4, 7],
            [7, 5, 1 / 2, 1, 2, 4],
            [3, 2, 1 / 4, 1 / 2, 1, 2],
            [2, 1, 1 / 7, 1 / 4, 1 / 2, 1]]),
        np.array([
            [1, 1 / 3, 1 / 3, 1 / 3, 5, 5],
            [3, 1, 3, 3, 7, 9],
            [3, 1 / 3, 1, 3, 9, 7],
            [3, 1 / 3, 1 / 3, 1, 7, 5],
            [1 / 5, 1 / 7, 1 / 9, 1 / 7, 1, 1 / 3],
            [1 / 5, 1 / 9, 1 / 7, 1 / 5, 3, 1]]),
        np.array([
            [1, 1 / 9, 1 / 9, 1, 1 / 7, 1],
            [9, 1, 3, 7, 1, 9],
            [9, 1 / 3, 1, 7, 1 / 3, 7],
            [1, 1 / 7, 1 / 7, 1, 1 / 7, 1 / 3],
            [7, 1, 3, 7, 1, 5],
            [1, 1 / 9, 1 / 7, 3, 1 / 5, 1]]),
        np.array([
            [1, 1 / 4, 1 / 3, 3, 1 / 4, 1],
            [4, 1, 2, 4, 1 / 3, 2],
            [3, 1 / 2, 1, 5, 1 / 4, 3],
            [1 / 3, 1 / 4, 1 / 5, 1, 1 / 7, 1 / 5],
            [4, 3, 4, 7, 1, 6],
            [1, 1 / 2, 1 / 3, 5, 1 / 6, 1]]),
        np.array([
            [1., 1., 8., 1 / 5, 2., 1.],
            [1., 1., 7., 1 / 6, 7., 1.],
            [1 / 8, 1 / 7, 1., 1 / 9, 1 / 4, 1 / 8],
            [5., 6., 9., 1., 9., 5.],
            [1 / 2, 1 / 7, 4., 1 / 9, 1., 1 / 2],
            [1., 1., 8., 1 / 5, 2., 1.]]),
        np.ones((6, 6))]

    crv = tk.DoubleVar()
    crv.set(0.0)
    typ_stud()
    cr = tk.Label(ahpframe, textvariable=crv, padx=10, width=3)
    cr.grid(row=45, column=1)
    crtxt = tk.Label(ahpframe, text="Współczynnik spójności")
    crtxt.grid(row=45, column=0)

    szukaj_planu_butt = tk.Button(ahpframe, text="Szukaj planu",
                                  command=szukaj_planu_p,
                                  state=tk.DISABLED)
    szukaj_planu_butt.grid(row=45, column=2)
    wyniki_frame = tk.LabelFrame(root, height=800, width=1280)
    imglab = tk.Label(wyniki_frame)
    imglab.grid(column=0, columnspan=4, row=1)

    next_button = tk.Button(wyniki_frame, text='>>', state=tk.DISABLED, command=lambda zmiana=1: change_photo(zmiana))
    previous_button = tk.Button(wyniki_frame, text='<<', state=tk.DISABLED,
                                command=lambda zmiana=-1: change_photo(zmiana))
    tydzien_widok = tk.StringVar()
    tydzien_widok.set("TP")
    change_timetable_txt = tk.Label(wyniki_frame, text="Przełącz plan:")
    change_timetable_txt.grid(row=0, column=0, sticky="e")
    show_info_button = tk.Button(wyniki_frame, text="Wyświetl zaawansowane", command=show_info)
    change_week_button = tk.Button(wyniki_frame, textvariable=tydzien_widok, state=tk.DISABLED, command=change_week)
    save_button = tk.Button(wyniki_frame, state=tk.DISABLED, text="Zapisz siatkę", command=save_plot)
    pokaz_kody_button = tk.Button(wyniki_frame, state=tk.DISABLED, text="Pokaż kody grup", command=show_group_codes)
    show_info_button.grid(row=2, column=2, sticky='w')
    next_button.grid(row=0, column=2, sticky='w')
    previous_button.grid(row=0, column=1, sticky='e')
    change_week_button.grid(row=0, column=3)
    save_button.grid(row=2, column=0)
    pokaz_kody_button.grid(row=2, column=3)

    timetables = []
    rozwiazania = []
    ktory_plan = 0
    najlepsze = []
    root.mainloop()
