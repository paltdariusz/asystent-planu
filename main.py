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
timetables, PLANS = timetables_generator.generate(kursy)
print(criteria_computation.avg_lecturers_marks(kursy, timetables[0]))
print(criteria_computation.late_hours_counter(PLANS[0]))
print(criteria_computation.early_hours_counter(PLANS[0]))
print(criteria_computation.evenness_of_classes(PLANS[0]))
print(criteria_computation.working_days_counter(PLANS[0]))
print(criteria_computation.gaps_counter(PLANS[0]))
print(PLANS[0])
print(timetables[0])
print(kursy)
