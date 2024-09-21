rus_to_lat = {
    'А': 'A', 'В': 'B', 'Е': 'E', 'К': 'K', 'М': 'M',
    'Н': 'H', 'О': 'O', 'Р': 'P', 'С': 'C', 'Т': 'T', 
    'У': 'Y', 'Х': 'X',
    'а': 'a', 'е': 'e', 'к': 'k',
    'о': 'o', 'р': 'p', 'с': 'c',
    'у': 'y', 'х': 'x'
}

lat_to_rus = {v: k for k, v in rus_to_lat.items()}

def text_to_bits(text):
    bits = ''.join(format(ord(c), '08b') for c in text)
    print(f"Message to bits: {text} -> {bits}")
    return bits

def bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    text = ''.join(chr(int(b, 2)) for b in chars)
    print(f"Bits to text: {bits} -> {text}")
    return text

def embed_message(container_text, message):
    bits = text_to_bits(message)
    bit_index = 0
    embedded_text = []
    num_embedded_bits = 0

    print(f"Embedding message: {message}")
    for char in container_text:
        if char in rus_to_lat and bit_index < len(bits):
            if bits[bit_index] == '1':
                embedded_text.append(rus_to_lat[char])
            else:
                embedded_text.append(char)
            bit_index += 1
            num_embedded_bits += 1
        else:
            embedded_text.append(char)

    print(f"Embedded text: {''.join(embedded_text)}")
    return ''.join(embedded_text), num_embedded_bits

def extract_message(embedded_text, message_length):
    bits = []
    print(f"Extracting message from: {embedded_text}")

    for char in embedded_text:
        if char in lat_to_rus:
            bits.append('1')
        elif char in rus_to_lat:
            bits.append('0')

        if len(bits) >= message_length * 8:
            break

    message = bits_to_text(''.join(bits))
    print(f"Extracted message: {message}")
    return message

def calculate_capacity(container_text):
    capacity = sum(1 for char in container_text if char in rus_to_lat)
    print(f"Calculated capacity: {capacity}")
    return capacity

def hiding_coefficient(container_text, num_embedded_bits):
    coefficient = num_embedded_bits / len(container_text) if len(container_text) > 0 else 0
    print(f"Calculated hiding coefficient: {coefficient}")
    return coefficient

if __name__ == "__main__":
    container_text = """Это пример текста для демонстрации стегосистемы. Здесь можно спрятать сообщение."""
    message = "Привет"

    embedded_text, num_embedded_bits = embed_message(container_text, message)

    capacity = calculate_capacity(container_text)
    hiding_coeff = hiding_coefficient(container_text, num_embedded_bits)

    print(f"Исходный текст:\n{container_text}")
    print(f"Текст с внедренным сообщением:\n{embedded_text}\n")
    print(f"Количество внедренных бит: {num_embedded_bits}")
    print(f"Информационная емкость контейнера: {capacity}")
    print(f"Коэффициент сокрытия: {hiding_coeff:.2f}\n")

    extracted_message = extract_message(embedded_text, len(message))
    print(f"Извлеченное сообщение: {extracted_message}")
