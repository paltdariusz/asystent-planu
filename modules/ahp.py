import numpy as np


def consistency_check(ahp):
    eigenvector = np.prod(ahp, axis=1)
    eigenvector = np.float_power(eigenvector, 1 / ahp.shape[1])
    eigenvector /= np.sum(eigenvector)
    lambda_max = np.average((ahp @ eigenvector) / eigenvector)
    if lambda_max < ahp.shape[1]:
        raise ValueError("Consistency index should be larger than n")
    random_consistency_index = [0.0, 0.0, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49, 1.51, 1.48, 1.56, 1.57, 1.59]
    consistency_index = (lambda_max - ahp.shape[1]) / (ahp.shape[1] - 1)
    consistency_ratio = consistency_index / random_consistency_index[ahp.shape[1] - 1]
    if consistency_ratio > 0.1:
        return False, consistency_ratio, eigenvector
    else:
        return True, consistency_ratio, eigenvector


def repair_consistency(w_n):
    w_n = w_n.reshape(w_n.shape[0], 1)
    W = w_n @ (1/w_n).T
    ahp_n = np.ones_like(W)
    for i in range(ahp_n.shape[0]):
        for j in range(ahp_n.shape[1]):
            if W[i, j] > 1:
                if W[i, j] > 9:
                    ahp_n[i, j] = 9
                else:
                    ahp_n[i, j] = np.rint(W[i, j])
                ahp_n[j, i] = 1/ahp_n[i, j]
    print(ahp_n)
    return ahp_n


def create_ahp(debug=False):
    ahp = np.ones((6, 6))
    # TODO dodaj presety z odpowiedziami przykładowych studentów
    if debug:
        odpowiedz = ['1/9', '1/9', '1/9', '1', '1', '1/3', '1/5', '1/7', '1/7', '5', '7', '7', '5', '3', '5']
        odpowiedz = ['1/9', '1/9', '1', '1/7', '1', '3', '7', '1', '9', '7', '1/3', '7', '1/7', '1/3', '5']
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
            if not debug:
                print(consistency_check(ahp))
    return ahp


if __name__ == '__main__':
    # print(create_ahp(True))
    # print(create_ahp(True).sum())
    ahp = np.array([[[1, 1 / 9, 1 / 9, 1 / 9, 1, 1], [9, 1, 1 / 3, 1 / 5, 1 / 7, 1 / 7], [9, 3, 1, 5, 7, 7],
                     [9, 5, 1 / 5, 1, 5, 3], [1, 7, 1 / 7, 1 / 5, 1, 5], [1, 7, 1 / 7, 1 / 3, 1 / 5, 1]],
                    [[1, 1 / 3, 1 / 3, 1 / 3, 5, 5], [3, 1, 3, 3, 7, 9], [3, 1 / 3, 1, 3, 9, 7],
                     [3, 1 / 3, 1 / 3, 1, 7, 5], [1 / 5, 1 / 7, 1 / 9, 1 / 7, 1, 1 / 3],
                     [1 / 5, 1 / 9, 1 / 7, 1 / 5, 3, 1]],
                    [[1, 1 / 9, 1 / 9, 1, 1 / 7, 1], [9, 1, 3, 7, 1, 9], [9, 1 / 3, 1, 7, 1 / 3, 7],
                     [1, 1 / 7, 1 / 7, 1, 1 / 7, 1 / 3], [7, 1, 3, 7, 1, 5], [1, 1 / 9, 1 / 7, 3, 1 / 5, 1]],
                    [[1, 1 / 3, 7, 1 / 3, 1 / 7, 1 / 5], [3, 1, 5, 5, 1 / 5, 3], [1 / 7, 1 / 5, 1, 1 / 3, 1 / 9, 1 / 5],
                     [3, 1 / 5, 3, 1, 1 / 7, 1 / 5], [7, 5, 9, 7, 1, 5], [5, 1 / 3, 5, 5, 1 / 5, 1]],
                    [[1, 1 / 3, 9, 1 / 9, 7, 3], [3, 1, 9, 1 / 7, 7, 5], [1 / 9, 1 / 9, 1, 1 / 9, 1 / 9, 1 / 9],
                     [9, 7, 9, 1, 9, 7], [1 / 7, 1 / 7, 9, 1 / 9, 1, 1 / 3], [1 / 3, 1 / 5, 9, 1 / 7, 3, 1]]
                    ])
    # print(consistency_check(create_ahp(True)))
    # for a in ahp:
    #     print(consistency_check(a))

    test = np.array([
        [1, 9, 5, 2, 1, 1, 1 / 2],
        [1 / 9, 1, 1 / 3, 1 / 9, 1 / 9, 1 / 9, 1 / 9],
        [1 / 5, 2, 1, 1 / 3, 1 / 4, 1 / 3, 1 / 9],
        [1 / 2, 9, 3, 1, 1 / 2, 1, 1 / 3],
        [1, 9, 4, 2, 1, 2, 1 / 2],
        [1, 9, 3, 1, 1 / 2, 1, 1 / 3],
        [2, 9, 9, 3, 2, 3, 1]
    ])
    # test = np.array([
    #     [1, 1/3, 1/9, 1/5],
    #     [3, 1, 1, 1],
    #     [9, 1, 1, 3],
    #     [5, 1, 1/3, 1]
    # ])
    # test = np.array([
    #     [1, 9, 1 / 9],
    #     [1/9, 1, 9],
    #     [9, 1/9, 1]
    # ])
    # test = np.array([
    #     [1, 5, 1 / 2],
    #     [1/5, 1, 5],
    #     [2, 1/5, 1]
    # ])

    # print(np.linalg.eig(test))

    # print(np.lcm.reduce(testdz.flatten()))
    # print(consistency_check(test))
    # print(normalize_ahp(test))
    ahp = create_ahp(True)
    wyniki = consistency_check(ahp)
    repair_consistency(wyniki[2])