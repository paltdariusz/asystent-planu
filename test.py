from multiprocessing import Process
import multiprocessing as mp
import time
import json
import numpy as np
import os.path
import shutil
import sys

from asystent_planu.modules.data_reader import read_csv
from asystent_planu.modules.timetables_generator import generate


def fun(name):
    print(f"hello {name}")


def main():
    # p1 = Process(target=fun, args=('Peter',))
    # p2 = Process(target=fun, args=('Annie',))
    # p1.start()
    # p2.start()
    # num_workers = mp.cpu_count()
    # print(num_workers)
    plik = 'plan2'
    kursy = read_csv(plik)
    start = time.time()
    timetables, PLANS = generate(kursy, True)
    print(f"\nwygenerowanie wyniosło: {time.time() - start}")


if __name__ == '__main__':
    main()
