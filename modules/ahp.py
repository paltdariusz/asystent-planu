import numpy as np


def normalize_ahp(ahp):
    ahp /= np.sum(ahp, axis=0)
    results = np.average(ahp, axis=1)
    return results


def create_ahp(debug=False):
    ahp = np.eye(6, 6)
    # TODO dodaj presety z odpowiedziami przykładowych studentów
    if debug:
        odpowiedz = ['1/9', '1/9', '1/9', '1', '1', '1/3', '1/5', '1/7', '1/7', '5', '7', '7', '5', '3', '5']
        # odpowiedz = ['1/9', '1/9', '1', '1/7', '1', '3', '7', '1', '9', '7', '1/3', '7', '1/7', '1/3', '5']
        odpowiedz = ['1/3', '7', '1/3', '1/7', '1/5', '5', '5', '1/5', '3', '1/3', '1/9', '1/5', '1/7', '1/5', '5']
    pytania = [
        '1.	Jak ważna jest dla Ciebie liczba okienek w porównaniu do liczby dni wolnych?',
        '2.	Jak ważna jest dla Ciebie liczba okienek w porównaniu do liczby zajęć rozpoczynających się o 7:30?',
        '3.	Jak ważna jest dla Ciebie liczba okienek w porównaniu do liczby zajęć kończących się o 17:05 i później?',
        '4.	Jak ważna jest dla Ciebie liczba okienek w porównaniu do średniej ocen wykładowców?',
        '5.	Jak ważna jest dla Ciebie liczba okienek w porównaniu do zbalansowania planu (podobnej liczby zajęć każdego dnia)?',
        '6.	Jak ważna jest dla Ciebie liczba dni wolnych w porównaniu do liczby zajęć rozpoczynających się o 7:30?',
        '7.	Jak ważna jest dla Ciebie liczba dni wolnych w porównaniu do liczby zajęć kończących się o 17:05 i później?',
        '8.	Jak ważna jest dla Ciebie liczba dni wolnych w porównaniu do średniej ocen wykładowców?',
        '9.	Jak ważna jest dla Ciebie liczba dni wolnych w porównaniu do zbalansowania planu (podobnej liczby zajęć każdego dnia)?',
        '10. Jak ważna jest dla Ciebie liczba zajęć rozpoczynających się o 7:30 w porównaniu do liczby zajęć kończących się o 17:05 i później?',
        '11. Jak ważna jest dla Ciebie liczba zajęć rozpoczynających się o 7:30 w porównaniu do średniej ocen wykładowców?',
        '12. Jak ważna jest dla Ciebie liczba zajęć rozpoczynających się o 7:30 w porównaniu do zbalansowania planu (podobnej liczby zajęć każdego dnia)?',
        '13. Jak ważna jest dla Ciebie liczba zajęć kończących się o 17:05 i później w porównaniu do średniej ocen wykładowców?',
        '14. Jak ważna jest dla Ciebie liczba zajęć kończących się o 17:05 i później w porównaniu do zbalansowania planu (podobnej liczby zajęć każdego dnia)?',
        '15. Jak ważna jest dla Ciebie średnia ocen wykładowców w porównaniu do zbalansowania planu (podobnej liczby zajęć każdego dnia)?'
    ]
    pytanie = 0
    for i in range(0, 5):
        for j in range(i + 1, 6):
            if not debug:
                answer = input(pytania[pytanie] + ' ')
            else:
                answer = odpowiedz[pytanie]
            pytanie += 1
            if '/' in answer:
                ahp[i][j] = float(answer[0]) / float(answer[2])
                ahp[j][i] = float(answer[2])
            else:
                ahp[i][j] = float(answer[0])
                ahp[j][i] = 1 / float(answer[0])
    return ahp


if __name__ == '__main__':
    print(create_ahp(True))
    print(create_ahp(True).sum())
