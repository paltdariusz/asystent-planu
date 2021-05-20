import requests as rq
import os.path
from cryptography.fernet import Fernet
import json


def credentials_verification(CREDENTIALS):
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
        CREDENTIALS["username"] = f1.encrypt(bytes(CREDENTIALS["username"], "utf-8")).decode("utf-8")
        CREDENTIALS["password"] = f2.encrypt(bytes(CREDENTIALS["password"], "utf-8")).decode("utf-8")
        with open("../data/user_credentials.json", "w") as file:
            json.dump(CREDENTIALS, file)
        with open("../data/user_credentials_tokens.json", "w") as file:
            json.dump(KEYS, file)
    return CREDENTIALS


def connection(url=""):
    pass


if __name__ == "__main__":
    print(read_user_credentials())
    print(read_user_credentials())
