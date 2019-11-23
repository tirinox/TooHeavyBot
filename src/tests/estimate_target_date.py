import numpy as np
import matplotlib.pyplot as plt


def when_i_hit_target_weight():
    X = np.arange(1, 12)
    Y = np.array([
        100.1,
        100.5,
        99.5,
        99.3,
        99.8,
        97.6,
        97.9,
        98,
        97.2,
        97.1,
        96.2
    ])
    params = np.polyfit(X, Y, 1)
    a, b = params.tolist()

    def exterpolator(x):
        return a * x + b

    Xfit = np.linspace(1, 60, 50)
    Yfit = exterpolator(Xfit)

    def solve_lin(target_y, a, b):
        return (target_y - b) / a

    target_y = 88
    target_day = solve_lin(target_y, a, b)

    if target_day < 3650:
        plt.axvline(target_day)

    plt.plot(X, Y, 'g^')
    plt.plot(Xfit, Yfit, 'r')

    plt.show()
