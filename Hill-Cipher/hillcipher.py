import math

MODULUS = 26


def text_to_numbers(text):
    text = text.upper().replace(" ", "")
    if not text.isalpha() or not text.isascii():
        raise ValueError("Teks hanya boleh berisi huruf A-Z.")
    return [ord(character) - ord("A") for character in text]


def numbers_to_text(numbers):
    return "".join(chr((number % MODULUS) + ord("A")) for number in numbers)


def input_key(order=None):
    if order is None:
        values = input("Masukkan semua elemen key (pisahkan spasi): ").split()
        element_count = len(values)
        order = math.isqrt(element_count)
        if order < 2 or order * order != element_count:
            raise ValueError("Jumlah elemen key harus kuadrat, minimal 4 angka.")
    else:
        values = []
        print(f"Masukkan key {order} x {order} (setiap baris dipisahkan spasi):")
        for row_number in range(order):
            row = input(f"Baris {row_number + 1}: ").split()
            if len(row) != order:
                raise ValueError(f"Setiap baris key harus berisi {order} angka.")
            values.extend(row)

    if len(values) != order * order:
        raise ValueError("Jumlah elemen key tidak sesuai dengan ordo matriks.")
    numbers = [int(value) % MODULUS for value in values]
    return [numbers[row * order:(row + 1) * order] for row in range(order)]


def determinant(matrix):
    size = len(matrix)
    if size == 1:
        return matrix[0][0] % MODULUS
    result = 0
    for column in range(size):
        minor = [
            [matrix[row][item] for item in range(size) if item != column]
            for row in range(1, size)
        ]
        sign = 1 if column % 2 == 0 else -1
        result += sign * matrix[0][column] * determinant(minor)
    return result % MODULUS


def validate_key(key):
    if math.gcd(determinant(key), MODULUS) != 1:
        raise ValueError("Key tidak valid: determinannya harus relatif prima dengan 26.")


def modular_inverse(number):
    for candidate in range(MODULUS):
        if number * candidate % MODULUS == 1:
            return candidate
    raise ValueError("Invers modular tidak ditemukan.")


def inverse_key(key):
    validate_key(key)
    size = len(key)
    augmented = [
        [value % MODULUS for value in key[row]]
        + [1 if row == column else 0 for column in range(size)]
        for row in range(size)
    ]

    for column in range(size):
        pivot = next(
            (row for row in range(column, size)
             if math.gcd(augmented[row][column], MODULUS) == 1),
            None,
        )
        if pivot is None:
            raise ValueError("Key tidak memiliki invers modulo 26.")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_inverse = modular_inverse(augmented[column][column])
        augmented[column] = [
            value * pivot_inverse % MODULUS for value in augmented[column]
        ]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                (augmented[row][item] - factor * augmented[column][item]) % MODULUS
                for item in range(size * 2)
            ]
    return [row[size:] for row in augmented]


def multiply_matrix_vector(matrix, vector):
    size = len(matrix)
    return [
        sum(matrix[row][column] * vector[column] for column in range(size))
        % MODULUS
        for row in range(size)
    ]


def process_text(text, key):
    block_size = len(key)
    numbers = text_to_numbers(text)
    numbers += [ord("X") - ord("A")] * ((-len(numbers)) % block_size)
    result = []
    for index in range(0, len(numbers), block_size):
        result.extend(multiply_matrix_vector(key, numbers[index:index + block_size]))
    return numbers_to_text(result)


def encryption():
    plain_text = input("Masukkan plaintext: ")
    key = input_key()
    validate_key(key)
    print(f"CIPHERTEXT: {process_text(plain_text, key)}")


def decryption():
    cipher_text = input("Masukkan ciphertext: ")
    key = input_key()
    print(f"PLAINTEXT: {process_text(cipher_text, inverse_key(key))}")


def multiply_matrix(left, right):
    size = len(left)
    return [
        [
            sum(left[row][item] * right[item][column] for item in range(size))
            % MODULUS
            for column in range(size)
        ]
        for row in range(size)
    ]


def find_key():
    order = int(input("Masukkan ordo matriks key: "))
    if order < 2:
        raise ValueError("Ordo matriks minimal 2.")
    plain_text = input(
        f"Masukkan {order * order} huruf plaintext yang diketahui: "
    )
    cipher_text = input(
        f"Masukkan {order * order} huruf ciphertext pasangannya: "
    )
    plain_numbers = text_to_numbers(plain_text)
    cipher_numbers = text_to_numbers(cipher_text)
    required_length = order * order
    if len(plain_numbers) != required_length or len(cipher_numbers) != required_length:
        raise ValueError(f"Plaintext dan ciphertext harus tepat {required_length} huruf.")

    # Setiap blok sepanjang ordo adalah satu vektor kolom.
    plain_matrix = [
        [plain_numbers[row + column * order] for column in range(order)]
        for row in range(order)
    ]
    cipher_matrix = [
        [cipher_numbers[row + column * order] for column in range(order)]
        for row in range(order)
    ]
    key = multiply_matrix(cipher_matrix, inverse_key(plain_matrix))
    validate_key(key)
    print("KEY:")
    print(f"{key[0][0]} {key[0][1]}")
    print(f"{key[1][0]} {key[1][1]}")


def menu():
    print("\n=== HILL CIPHER ===")
    print("1. Enkripsi")
    print("2. Dekripsi")
    print("3. Cari kunci")
    print("4. Keluar")
    return input("Masukkan pilihan: ").strip()


def main():
    actions = {"1": encryption, "2": decryption, "3": find_key}
    while True:
        pilihan = menu()
        if pilihan == "4":
            print("Program selesai.")
            return
        action = actions.get(pilihan)
        if action is None:
            print("Pilihan tidak valid.")
            continue
        try:
            action()
        except (ValueError, TypeError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
