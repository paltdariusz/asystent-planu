import numpy as np


def gaps_counter(PLAN):
    idxy = np.argwhere(PLAN == 1)
    columns = np.unique(idxy[:, 0])
    temp = idxy[:, 0]
    idxp = []
    idxo = []
    for i in columns:
        localize = np.argwhere(temp == i).flatten()
        idxp.append(idxy[np.min(localize), 1])
        idxo.append(idxy[np.max(localize), 1])
    z = 0
    for i in range(len(idxp)):
        z += idxo[i] - idxp[i] + 1 - np.sum(PLAN[i, idxp[i]:idxo[i] + 1])
    return z


def avg_lecturers_marks(kursy, grupy):
    ile = 0
    z = 0
    for grupa in grupy:
        ocena = kursy[kursy['Grupa kursu'] == grupa]['Marks']
        if ocena.values[0] != 0:
            ile += 1
            z -= float(ocena.values[0])
    z /= ile
    return z


def working_days_counter(PLAN):
    temp = np.sum(PLAN, axis=1)
    temp = temp[temp > 0]
    z = temp.shape[0]
    return z


def evenness_of_classes(PLAN):
    zprim = 1 / working_days_counter(PLAN) * PLAN.sum()
    z = 0
    for i in range(PLAN.shape[0]):
        if all(PLAN[i, :] == np.zeros_like(PLAN[i, :])):
            continue
        z += np.abs(zprim - PLAN[i, :].sum())
    return z


def early_hours_counter(PLAN):
    z = PLAN[:, 0].sum()
    return z


def late_hours_counter(PLAN):
    z = PLAN[:, 10:].sum()
    return z


if __name__ == '__main__':
    from timetables_generator import generate
    from data_reader import read_csv

    timetables, PLANS = generate(read_csv('plan'))
    print(timetables[0])
    print(PLANS[0])
    print(f"gaps: {gaps_counter(PLANS[0])}")
    print(f"working days: {working_days_counter(PLANS[0])}")
    print(f"eveness: {evenness_of_classes(PLANS[0])}")
    print(f"early: {early_hours_counter(PLANS[0])}")
    print(f"late: {late_hours_counter(PLANS[0])}")
