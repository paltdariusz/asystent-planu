import modules.data_reader as data_reader
from modules import criteria_computation
from modules import marks_scrapper
from modules import ahp
from modules import timetables_generator
import json

kursy = data_reader.read_csv('plan')
with open('data/lecturers_marks.json') as file:
    oceny = json.load(file)
kursy = marks_scrapper.join_marks(oceny, kursy)
wagi = ahp.normalize_ahp(ahp.create_ahp(True))
timetables, PLANS = timetables_generator.generate(kursy)
zmax = 1000000
idx = 0
for i in range(len(timetables)):
    z = wagi[0] * criteria_computation.gaps_counter(PLANS[i])
    z += wagi[1] * criteria_computation.working_days_counter(PLANS[i])
    z += wagi[2] * criteria_computation.early_hours_counter(PLANS[i])
    z += wagi[3] * criteria_computation.late_hours_counter(PLANS[i])
    z += wagi[4] * criteria_computation.avg_lecturers_marks(kursy, timetables[i])
    z += wagi[5] * criteria_computation.evenness_of_classes(PLANS[i])
    if z < zmax:
        zmax = z
        idx = i

print(zmax)
print(idx)
print(PLANS[idx])
print(timetables[idx])
