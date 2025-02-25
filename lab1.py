# генераторы

from random import randint
import os

AB = b"abcdefghijklmnopqrstuvwxyz"
AB = b"0123456789abcde" + AB + AB.upper() # а на практике мы используем только 012345... т.е. с запасиком на будущие работы, если вообще понадобится

def generator(len_B, size, name):
    assert len_B in range(1, len(AB))
    len_B_m1 = len_B - 1
    data = bytes(AB[randint(0, len_B_m1)] for i in range(size))
    with open(name, "wb") as file: file.write(data)

def P2arr(P):
    return tuple(idx for idx, count in enumerate(P) for i in range(count))
    #    тот же код, но как это изначально выглядело (конечно он медленее):
    # arr = []
    # for idx, count in enumerate(P):
    #     arr.extend(idx for i in range(count))
    # return tuple(arr)

def p_generator(P_arr, size, name):
    assert max(P_arr) in range(1, len(AB))
    L_m1 = len(P_arr) - 1
    data = bytes(AB[P_arr[randint(0, L_m1)]] for i in range(size))
    with open(name, "wb") as file: file.write(data)

def art_generator(src_name, size, name):
    prev_space = False
    def getter():
        nonlocal prev_space
        while True:
            letter = read(1).lower()
            if letter in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя":
                prev_space = False
                if letter == "ё": return "е"
                if letter == "ъ": return "ь"
                return letter
            if prev_space: continue # удаляем повторяющиеся пробелы
            prev_space = True
            return " "
    with open(src_name, "r", encoding = "windows-1251") as src:
        read = src.read
        with open(name, "w", encoding = "windows-1251") as file:
            write = file.write
            for i in range(size): write(getter())

size = 1024 * 16 # len_A, он же |A| по сути
P = 36, 18, 18, 12, 9, 7 # 0.36, 0.18, ... для удобства задал не от 0 до 1, а целыми числами, которые при делении на их сумму, дают реальную P

len_B = len(P) # |B| по сути
P_arr = P2arr(P) # 36 раз 0, 18 раз 1, 18 раз 2, 12 раз 3...
assert len(P_arr) == 100

if not os.path.exists("lab1_file3.txt"):
    generator(len_B, size, "lab1_file1.txt")
    p_generator(P_arr, size, "lab1_file2.txt")
    art_generator("Гарри Поттер и философский камень.txt", size, "lab1_file3.txt")



# подсчёты

from math import log2, log

Mu = lambda p: -p * log2(p) if p else 0 # по сути та самая таблица с ГИА

def H(P): # энтропия Шеннона
    S = sum(P)
    return sum(Mu(p / S) for p in P) # приводим в нормальную форму вероятности от 0 до 1

def H_X(len_B): # энтропия Хартли (ещё записывают, как Hmax)
    return log2(len_B)

# print("Hteor1:", H((1,) * len_B), "=", Mu(1 / len_B) * len_B, "=", H_X(len_B)) # сразу 3 способа. 2 и 3 способ будут быстрее на порядок, чем первый
# print("Hteor2:", H(P))

def Craft(L, len_B): # неравенство Крафта, чтобы было
    S = sum(len_B ** (-len) for len in L)
    return S, S <= 1
# print(Craft((1, 2, 2), 2)) # 1.0, True
# print(Craft((1, 1, 2), 2)) # 1.25, False (то самое с лекции)
# print(Craft((1, 1, 2), 3)) # 0.777, True

def H1(data):
    A = {}
    for letter in data:
        try: A[letter] += 1
        except KeyError: A[letter] = 1
    return A

def H2_plus(data, group_n):
    if group_n == 1: return H1(data)
    # при group_n = 1, работает точно также, как и H1, но медленнее
    A = {}
    for i in range(len(data) - group_n + 1):
        letter = data[i : i + group_n]
        try: A[letter] += 1
        except KeyError: A[letter] = 1
    return A

def reader(name):
    print()
    print("~" * 33, name, "~" * 33)
    with open(name, "r", encoding = "windows-1251") as file: data = file.read()

    for group_n in (1, 2, 3, 4, 5, 6, 7, 8):
        A = H2_plus(data, group_n)
        if group_n == 1:
            len_B = len(A)
            Hmax = H_X(len_B)
            print("Hmax:", Hmax) # log2(6)
        if group_n <= 3: print("H%s:" % group_n, A)
        # A, P = zip(*sorted(A.items(), reverse = True, key = lambda i: i[1])) # для удобства отсортировал по вероятностям и разделил на алфавит и P
        P = A.values() # не отсортировано
        h = H(P) / group_n # похоже на энтропию L-той степени. groun_n и есть эта L
        mu = h / Hmax # относительная энтропия (коэфф. сжатия)
        rho = 1 - mu # величина избыточности
        print("H%s:" % group_n, h , "µ = %.3f%%" % (mu * 100), "r = %.3f%%" % (rho * 100))
        print()

if __name__ == "__main__":
    reader("lab1_file1.txt")
    reader("lab1_file2.txt")
    reader("lab1_file3.txt")
