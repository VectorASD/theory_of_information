from lab1 import H as Shannon, H1, H2_plus, Mu
from sortedcontainers import SortedList # pip install sortedcontainers
import os
from io import BytesIO
from codecs import getreader
from math import log2, ceil

WindowsReader = getreader("windows-1251")

class Probability:
    def __init__(self, p):
        self.p = p
    def __eq__(left, right): return left.p == right.p
    def __ne__(left, right): return left.p != right.p
    def __lt__(left, right): return left.p < right.p
    def __gt__(left, right): return left.p > right.p
    def __le__(left, right): return left.p <= right.p
    def __ge__(left, right): return left.p >= right.p
# проверено, что для сортировки в приоритете используется __lt__ (<).
# если нет __lt__ (<), то используется __gt__ (>)
# если нет ни того (<), ни другого (>), тогда будет TypeError: '<' not supported between instances of 'Leaf' and 'Leaf'

class Leaf(Probability):
    def __init__(self, letter, p):
        super().__init__(p)
        self.letter = letter
    def __repr__(self):
        return "Leaf(%r, %r)" % (self.letter, self.p)

class Node(Probability):
    def __init__(self, p, left, right):
        super().__init__(p)
        self.left = left
        self.right = right
    def __repr__(self):
        return "Node(%r, %r, %r)" % (self.p, self.left, self.right)

def HaffmanTreegen(root):
    def recurs(node, depth = -1):
        if isinstance(node, Node):
            L, R = node.left, node.right
            depth += 1
            recurs(L, depth)
            recurs(R, depth)
        else:
            while len(L_mat) <= depth: L_mat.append([])
            L_mat[depth].append(node.letter)

    assert isinstance(root, Node)
    L_mat = tuple([] for i in range(16)) # так выглядит дерево-Хаффмана на "языке" JPEG, т.е. кодовые слова НЕ длиннее 16 битов
    L_mat = [] # но в нашей реализации я сделал массив динамического размера
    recurs(root)
    return tuple(L_mat)

def HaffmanCodegen(L_mat):
    code, limit = 0, 2
    codes = {}
    for L, block in enumerate(L_mat, 1):
        for letter in block:
            assert code < limit, "L_mat нарушает неравенство Крафта"
            bin_code = bin(code)[2:].rjust(L, '0')
            print(f"{bin_code:16} | {letter!r}")
            codes[letter] = bin_code
            code += 1
        code <<= 1
        limit <<= 1
    return codes

def packTree(L_mat):
    max_L = max(L for L, arr in enumerate(L_mat, 1) if arr)
    if len(L_mat) != max_L: L_mat = L_mat[:max_L]

    lets_per_char = len(L_mat[-1][0])

    res = BytesIO()
    res.write(bytes((max_L, lets_per_char))) # (1)
    res.write(bytes(len(block) for block in L_mat)) # (2)
    res.write("".join(letter for block in L_mat for letter in block).encode("windows-1251")) # (3)
    return res.getvalue()

def unpackTree(file):
    max_L, lets_per_char = file.read(2) # (1)
    L = file.read(max_L) # (2)
    read = WindowsReader(file).read
    return tuple([read(lets_per_char) for i in range(Li)] for Li in L) # (3)

def Haffman(AB):
    leafs = tuple(Leaf(letter, p) for letter, p in AB.items())
    # leafs = sorted(leafs, key = lambda leaf: leaf.p, reverse = True) старый и неоптимальный вариант для дальнейшей вставки
    leafs = SortedList(leafs)
    print(leafs)
    while len(leafs) > 1:
        B, A = leafs.pop(0), leafs.pop(0)
        leafs.add(Node(A.p + B.p, A, B))
    root = leafs[0]
    return HaffmanTreegen(root)

def ShennonFano(AB):
    def recurs(bin_code, start, end):
        assert start <= end
        if start == end:
            letter = A[start]
            print(f"{bin_code:16} | {letter!r}")
            codes[letter] = bin_code
            return
        dS = sum(P[start : end]) / 2 # среднее значение частоты в последовательности
        Q = 0
        for i in range(start, end):
            Q += P[i]
            if Q >= dS: break
        recurs(bin_code + "0", start, i)
        recurs(bin_code + "1", i + 1, end)
    A, P = zip(*sorted(AB.items(), reverse = True, key = lambda i: i[1]))
    codes = {}
    recurs("", 0, len(P) - 1)
    return codes

def check_codes(AB, size, codes, n = 1): # чисто теория. Нет фактической сборки данных в кодированную цепочку битов
    # size = sum(AB.values())
    bits = 0
    L_avg = 0
    H = 0
    for letter, count in AB.items():
        L = len(codes[letter])
        p = count / size
        bits += count * L
        L_avg += p * L
        H += Mu(p)
    L_avg /= n
    H /= n
    print("Размер кодированных данных неравномерным кодом (теоретический):", (bits + 7) // 8, "b.")
    print(f"Lср.: {L_avg:.5f}")
    print(f"H: {H:.5f}")
    r = L_avg - H
    print(f"r: {r:.5f}") # должна быть строго от 0 до 1. А на деле выходит как на ГИА: от 0 до 0.1

def coder(data, codes): # а вот и кодирование ради H1, H2, H3...
    bin_stream = "".join(codes[letter] for letter in data)
    print("Размер кодированных данных неравномерным кодом (практический):", (len(bin_stream) + 7) // 8, "b.")
    for group_n in (1, 2, 3, 4, 5, 6, 7):
        AB = H2_plus(bin_stream, group_n)
        P = AB.values()
        h = Shannon(P) / group_n
        print(f"H{group_n} = {h:.5f}")

def check_tree_packer(L_mat):
    packed = packTree(L_mat)
    unpacked = unpackTree(BytesIO(packed))
    print("Размер дерева Хаффмана:", len(packed), "b.")
    print(L_mat)
    print(unpacked) # дабы убедиться, что L_mat из байтового потока декодируется назад без помех
    print("Сошлись?", "Да" if L_mat == unpacked else ":///")

def encode_to_file(data, codes, name):
    with open(name, "w") as file:
        write = file.write
        for letter in data: write(codes[letter])

def reader(name):
    print()
    print("~" * 33, name, "~" * 33)
    with open(name, "r", encoding = "windows-1251") as file: data = file.read()
    size = os.stat(name).st_size

    AB = H1(data) # алфавит с частотами
    L_mat = Haffman(AB)

    check_tree_packer(L_mat)

    optimal = ceil(log2(len(AB)))
    print("Размер файла до сжатия (байтами, т.е. 8-битный равномерный код):", size, "b.")
    print(f"Размер файла до сжатия ({optimal}-битный равномерный код):", (size * optimal + 7) // 8, "b.")

    codes = HaffmanCodegen(L_mat)
    check_codes(AB, size, codes)
    coder(data, codes)
    encode_to_file(data, codes, name.replace("lab1", "lab2"))

    codes = ShennonFano(AB)
    check_codes(AB, size, codes)
    coder(data, codes)

if __name__ == "__main__":
    reader("lab1_file1.txt")
    reader("lab1_file2.txt")
    reader("lab1_file3.txt")
