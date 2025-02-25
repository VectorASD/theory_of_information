from lab1 import H1, H_X
from lab2 import Haffman, HaffmanCodegen, check_codes, check_tree_packer
from math import log2, ceil

def slicer(data, n):
    L = (len(data) + n - 1) // n
    for i in range(0, L * n, n):
        block = data[i : i + n]
        if len(block) == n: yield block
    block_L = len(block)
    if block_L != n:
        pad = n - block_L
        repeats = (pad + block_L - 1) // block_L
        yield block + (block * repeats)[:pad] # дописываем в конец блока его же повторы
# print(tuple(slicer(b"meowmeow123", 8))) # (b'meowmeow', b'12312312')

def reader(name):
    with open(name, "r", encoding = "windows-1251") as file: data = file.read()

    for n in (1, 2, 3, 4):
        print()
        print("~" * 33, f"n = {n}", "~" * 33)
        blocks = tuple(slicer(data, n))
        AB = H1(blocks)
        print("Размер алфавита:", len(AB))
        print(f"Hmax = {H_X(len(AB)) / n:.5f}")
        L_mat = Haffman(AB)

        try: check_tree_packer(L_mat)
        except ValueError as e:
            if e.args != ('bytes must be in range(0, 256)',): raise
            print("Слишком большое дерево для записи")
            # элементарное решение - перемещать символы L-итого уровня на (L+1)-итый уровень, пока на каждом уровне не окажется максимум 255 символов (так в JPEG и решают проблему)
            # решение получше - кодировать количество символов L-итого уровня не байтом, а двумя байтами, либо uleb128

        optimal = ceil(log2(len(AB)))
        print(f"Размер файла до сжатия ({optimal}-битный равномерный код):", (len(blocks) * optimal + 7) // 8, "b.")

        codes = HaffmanCodegen(L_mat)
        check_codes(AB, len(blocks), codes, n)

if __name__ == "__main__":
    reader("lab1_file2.txt")
