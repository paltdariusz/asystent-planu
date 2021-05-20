import requests as rq
import os.path
from cryptography.fernet import Fernet
import json
from bs4 import BeautifulSoup
import re
import time


def credentials_verification(CREDENTIALS):
    data = {
        "username": CREDENTIALS["username"],
        "password": CREDENTIALS["password"],
        "redirect": ",",
        "login": "Zaloguj",
    }
    with rq.Session() as s:
        p = s.post("https://polwro.pl/login.php?redirect=", data=data)
        p.encoding = "ISO-8859-2"
        if "Błędne hasło dla użytkownika" in p.text:
            return False
        elif "Konto zostało zablokowane z powodu wielokrotnej próby logowania" in p.text:
            print("Konto zostało zablokowane z powodu wielokrotnej próby logowania, spróbuj ponownie później")
            return False
        else:
            return True


def read_user_credentials():
    if os.path.isfile("../data/user_credentials.json") and os.path.isfile("../data/user_credentials_tokens.json"):
        with open("../data/user_credentials.json", "r") as file:
            CREDENTIALS = json.load(file)
        with open("../data/user_credentials_tokens.json", "r") as file:
            KEYS = json.load(file)
        f1 = Fernet(bytes(KEYS["1"], "utf-8"))
        f2 = Fernet(bytes(KEYS["2"], "utf-8"))
        CREDENTIALS["username"] = f1.decrypt(bytes(CREDENTIALS["username"], "utf-8")).decode("utf-8")
        CREDENTIALS["password"] = f2.decrypt(bytes(CREDENTIALS["password"], "utf-8")).decode("utf-8")
    else:
        username = input("Podaj nazwe użytkownika: ")
        password = input("Podaj hasło: ")
        CREDENTIALS = {
            "username": username,
            "password": password
        }
        while not credentials_verification(CREDENTIALS):
            print("Niepoprawne dane!")
            username = input("Podaj nazwe użytkownika: ")
            password = input("Podaj hasło: ")
            CREDENTIALS = {
                "username": username,
                "password": password
            }

        KEYS = {
            "1": Fernet.generate_key().decode("utf-8"),
            "2": Fernet.generate_key().decode("utf-8")
        }
        f1 = Fernet(bytes(KEYS["1"], "utf-8"))
        f2 = Fernet(bytes(KEYS["2"], "utf-8"))
        CREDENTIALS_ENCRYPTED = {}
        CREDENTIALS_ENCRYPTED["username"] = f1.encrypt(bytes(CREDENTIALS["username"], "utf-8")).decode("utf-8")
        CREDENTIALS_ENCRYPTED["password"] = f2.encrypt(bytes(CREDENTIALS["password"], "utf-8")).decode("utf-8")
        with open("../data/user_credentials.json", "w") as file:
            json.dump(CREDENTIALS_ENCRYPTED, file)
        with open("../data/user_credentials_tokens.json", "w") as file:
            json.dump(KEYS, file)
    return CREDENTIALS


def scrape():
    CREDENTIALS = read_user_credentials()
    topics = [6, 7, 8, 9, 10, 11, 12, 25, 42]
    data = {
        "username": CREDENTIALS["username"],
        "password": CREDENTIALS["password"],
        "redirect": ",",
        "login": "Zaloguj",
    }
    lecturers_marks = []
    with rq.Session() as s:
        s.post("https://polwro.pl/login.php?redirect=", data=data)
        for topic in topics:
            start = 0
            response = s.get(f"https://polwro.pl/viewforum.php?f={topic}&topicdays=0&start={start}")
            response.encoding = "ISO-8859-2"
            soup = BeautifulSoup(response.text, 'html.parser')
            while len(soup.find_all("a", "postmenu")) > 0 and "następna" in str(soup.find_all("a", "postmenu")[-1]):
                response = s.get(f"https://polwro.pl/viewforum.php?f={topic}&topicdays=0&start={start}")
                response.encoding = "ISO-8859-2"
                soup = BeautifulSoup(response.text, 'html.parser')
                lecturers = soup.find_all("div", "hrw")[3:]
                for lecturer in lecturers:
                    lecturer = str(lecturer).split("\n")[0]
                    mark = re.findall("[0-9],*[0-9]*[0-9]*", lecturer)[0].replace(",", ".")
                    name = re.findall("title *= *\"(?:.*)\" *>(.*?)< */ *a *>", lecturer)[0]
                    name = name.strip().replace(",", "").replace(".", "").split()
                    lecturers_marks.append({"name": name, "mark": mark})
                start += 50
                time.sleep(0.5)
    with open("../data/lecturers_marks.json", "w") as file:
        json.dump(lecturers_marks, file)
    return lecturers_marks

if __name__ == "__main__":
    scrape()
