from random import randint

def num2row(num, m):
    return tuple(map(int, bin(num)[2:].rjust(m, '0')))
def mat2num(mat):
    return tuple(int("".join(map(str, row)), 2) for row in mat)

def gen(n, m):
    if m <= n: exit("Требуется матрица с избыточностью (m > n)")
    mat = tuple(
        tuple(
            int(col == row) if col < n else randint(0, 1)
            for col in range(m))
        for row in range(n))
    G = n, m, "G", mat2num(mat)
    return G

def print_mat(mat):
    _, m, name, mat = mat
    it = iter(mat)
    print(name, "=", num2row(next(it), m))
    for row in it: print("     ", num2row(row, m))

def G2H(mat):
    n, m, _, mat = mat
    if m <= n: exit("Требуется матрица с избыточностью (m > n)")
    m1 = m - 1
    new_mat = tuple(
        tuple(
            mat[row] >> (m1 - col) & 1 if row < n else int(col == row)
            for col in range(n, m))
        for row in range(m))
    H = m, m - n, "H", mat2num(new_mat)
    return H

def Transpose(mat):
    n, m, name, mat = mat
    new_mat = mat2num(zip(*(num2row(row, m) for row in mat)))
    return m, n, "t" + name, new_mat

def mul(mat, code):
    n, m, name, mat = mat
    res = 0
    for row, bit in zip(mat, code):
        if int(bit): res ^= row
    return bin(res)[2:].rjust(m, '0')

def calculate(G):
    print_mat(G)
    H = G2H(G)
    print_mat(H)
    tH = Transpose(H)
    n, m = G[:2]
    count = 2 ** n
    min_dist = float("inf")
    for i in range(count):
        code = bin(i)[2:].rjust(n, '0')
        encoded = mul(G, code)

        dist = encoded.count("1")
        if dist: min_dist = min(min_dist, dist)

        #encoded ^= 1 << (m - 1)
        checked = mul(H, encoded)
        if i < 25 or i >= count - 25:
            print(code, encoded, checked)#, mul(tH, checked))
        elif i == 25 and count > 50: print("...")

    print("n:", n)
    print("m:", m)
    print("count:", count)
    print("min_dist:", min_dist)

def reader(fname):
    try:
        with open(fname, "rb") as file:
            n, m, name = file.readline().split(b" ", 2)
            n, m = int(n), int(m)
            name = name.strip(b"\r\n").decode("utf-8")
            mat = tuple(tuple(map(int, file.readline().split())) for i in range(n))
            G = n, m, name, mat2num(mat)
    except FileNotFoundError:
        n = randint(3, 10)
        m = n + randint(2, 10)
        n, m, name, mat = G = gen(n, m)
        with open(fname, "w", encoding = "utf-8") as file:
            write = file.write
            write(f"{n} {m} {name}\n")
            for row in mat:
                write(" ".join(map(str, num2row(row, m))))
                write("\n")
    return G

if __name__ == "__main__":
    for i in range(1, 6):
        name = f"lab4_mat{i}.txt"
        print("~" * 33, name, "~" * 33)
        G = reader(name)
        calculate(G)
