from random import randint # только для break_file
from io import StringIO
from os.path import exists

# 0 1 1
# 1 0 1
# * * b1

# 0 0 0 1 1 1 1
# 0 1 1 0 0 1 1
# 1 0 1 0 1 0 1
# * * b1 * b2 b3 b4

# 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1
# 0 0 0 1 1 1 1 0 0 0 0 1 1 1 1
# 0 1 1 0 0 1 1 0 0 1 1 0 0 1 1
# 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1
# * * b1 * b2 b3 b4 * b5-b11

# 0 1 3 7
# 1 2 4 8
# 2 3 5 9

def coder_generator(service_bits):
    assert service_bits >= 2
    bits = (1 << service_bits) - 1
    common_bits = bits - service_bits
    # print(service_bits, bits, common_bits)

    # формирование массива связей битов входящего сообщения с выходящим
    arr = []
    common = 0
    for i in range(bits):
        service = i == (1 << i.bit_length()) - 1
        if service:
            n = i.bit_length()
            # print(i, n, (1 << n) + 1, [(i + 1) >> n & 1 for i in range(1 << n, bits)])
            arr.append(tuple(i for i in range(1 << n, bits) if i + 1 >> n & 1))
        else:
            arr.append(common)
            common += 1

    # индексные на элементы этого же массивов переделываем в индексы на сами биты входящего сообщения
    for i, item in enumerate(arr):
        if type(item) is tuple:
            arr[i] = tuple(arr[idx] for idx in item)

    # основная кодировальная функция (шифратор)
    def encoder(code):
        assert len(code) == common_bits, f"Длина кодируемого блока (={len(code)}) не соответствует {common_bits}"
        ints = tuple(map(int, code))
        res = []; app = res.append
        for idx in arr:
            if type(idx) is tuple:
                bit = 0
                for idx in idx: bit ^= ints[idx]
            else: bit = ints[idx]
            app(bit)
        code2 = "".join(map(str, res))
        return code2

    common_idxs = tuple(i for i, idx in enumerate(arr) if type(idx) is int)
    check_idxs = tuple(
        (1 << i, tuple(num for num in range(bits) if num + 1 >> i & 1))
        for i in range(service_bits))

    # основная декодировальная функция (дешифратор)
    def decoder(code):
        assert len(code) == bits, f"Длина декодируемого блока (={len(code)}) не соответствует {bits}"
        check = 0
        for num, idxs in check_idxs:
            if sum(int(code[idx]) for idx in idxs) & 1:
                check += num
        if check: # упс, что-то сломалось!
            check -= 1
            if check < len(code): # иначе нельзя починить, увы :/ очевидные 2+ ошибки
                code = f"{code[:check]}{'10'[int(code[check])]}{code[check+1:]}" # сама фиксилка
        code2 = "".join(code[idx] for idx in common_idxs)
        return code2

    def all():
        # кешируем ВСЁ! самая тяжёлая часть ;'-} O(2^(2^service_bits))... так что лучше обойдусь без кеша XD
        count = 1 << common_bits
        break_idx = 6 # взял все возможные значения от 0 до bits-1
        # Значение check внутри decoder реагирует верно! Фиксит ошибку верно!
        for i in range(count):
            code = bin(i)[2:].rjust(common_bits, '0')
            code2 = encoder(code)
            code2 = f"{code2[:break_idx]}{'10'[int(code2[break_idx])]}{code2[break_idx+1:]}"
            code3 = decoder(code2)
            print(code, code2, code3)
        exit()

    # all() # только для разработки и проверки
    return (common_bits, encoder), (bits, decoder)

# при coder_generator(2): encoder("0") выдаёт "000", а encoder("1") выдаёт "111"





def encode_file(_in, out, encoder):
    common_bits, encoder = encoder
    read = _in.read
    write = out.write
    while True:
        data = read(common_bits)
        if not data: break
        if len(data) != common_bits:
            data += "0" * (common_bits - len(data)) # padding в конце файла
        write(encoder(data))

def break_file(_in, out, p):
    read = _in.read
    write = out.write
    p = round(1 / p)
    print("1 к", p)
    while True:
        byte = read(1)
        if not byte: break
        if randint(1, p) == 1: byte = "10"[int(byte)]
        write(byte)

def decode_file(_in, out, decoder):
    bits, decoder = decoder
    read = _in.read
    write = out.write
    while True:
        data = read(bits)
        if not data: break
        write(decoder(data)) # без padding, т.к. файл должен гарантировать file size % bits = 0

def check_files(file1, file2):
    read1 = file1.read
    read2 = file2.read
    errors = 0
    while True:
        data1 = read1(1)
        if not data1: break
        data2 = read2(1)
        if not data2: break
        if data1 != data2: errors += 1
    return errors

def final_solve(name, service_bits): # закрывающая весь курс ТИ функция ;'-} последняя в моём случае
    encoder, decoder = coder_generator(service_bits)

    name2 = f"encoded/sb{service_bits}.txt"
    if not exists(name2):
        with open(name, "r") as _in:
            with open(name2, "w") as out:
                encode_file(_in, out, encoder)

    with open(name2, "r") as _in:
        for p in (0.0001, 0.001, 0.01, 0.1, 0.25, 0.5, 1):
            name3 = f"encoded/sb{service_bits}_p{p}.txt"
            if not exists(name3):
                _in.seek(0)
                with open(name3, "w") as out:
                    break_file(_in, out, p)

    res = []
    with open(name, "r") as orig:
        for p in (0.0001, 0.001, 0.01, 0.1, 0.25, 0.5, 1):
            name3 = f"encoded/sb{service_bits}_p{p}.txt"
            out = StringIO()
            with open(name3, "r") as _in:
                decode_file(_in, out, decoder)
            orig.seek(0)
            out.seek(0)
            errors = check_files(orig, out)
            print(name3, "  | errors:", errors)
            res.append(errors)
    print(*res, sep = "\t", end = "\n\n")



# lab2_file3.txt - самый толстый файл
final_solve("lab2_file3.txt", 2)
final_solve("lab2_file3.txt", 3)
final_solve("lab2_file3.txt", 4)
final_solve("lab2_file3.txt", 5)
final_solve("lab2_file3.txt", 6)
