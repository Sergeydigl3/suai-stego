import yaml

class TextSteganography:
    def __init__(self, dictionary_file=None):
        self.rus_to_lat = {}
        self.lat_to_rus = {}
        
        if dictionary_file:
            self.load_dictionary(dictionary_file)

    def load_dictionary(self, dictionary_file):
        with open(dictionary_file, 'r', encoding='utf-8') as file:
            self.rus_to_lat = yaml.safe_load(file)
            self.lat_to_rus = {v: k for k, v in self.rus_to_lat.items()}
        print(f"Loaded dictionary: {self.rus_to_lat}")

    def text_to_bits(self, text):
        # Преобразуем текст в байты с использованием UTF-8 и далее в битовую строку
        bits = ''.join(format(byte, '08b') for byte in text.encode('utf-8'))
        print(f"Message to bits: {text} -> {bits}")
        return bits

    def bits_to_text(self, bits):
        # Преобразуем битовую строку обратно в байты, затем в текст с использованием UTF-8
        bytes_array = bytearray(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
        text = bytes_array.decode('utf-8')
        print(f"Bits to text: {bits} -> {text}")
        return text

    def embed_message(self, container_text, message):
        bits = self.text_to_bits(message)
        bit_index = 0
        embedded_text = []
        num_embedded_bits = 0

        print(f"Embedding message: {message}")
        for char in container_text:
            if char in self.rus_to_lat and bit_index < len(bits):
                if bits[bit_index] == '1':
                    embedded_text.append(self.rus_to_lat[char])
                else:
                    embedded_text.append(char)
                bit_index += 1
                num_embedded_bits += 1
            else:
                embedded_text.append(char)

        print(f"Embedded text: {''.join(embedded_text)}")
        return ''.join(embedded_text), num_embedded_bits

    def extract_message(self, embedded_text, message_bytes_length):
        bits = []

        # Проходим по тексту и собираем биты
        for char in embedded_text:
            if char in self.lat_to_rus:
                bits.append('1')
            elif char in self.rus_to_lat:
                bits.append('0')

            # Проверяем, достаточно ли битов для восстановления сообщения
            if len(bits) >= message_bytes_length * 8:
                break

        # Проверка, что количество битов кратно 8 (целое количество байтов)
        if len(bits) % 8 != 0:
            print(f"Warning: extracted bits do not form a complete byte sequence. Length of bits: {len(bits)}")
            # Обрезаем неполные байты
            bits = bits[:-(len(bits) % 8)]

        # Преобразуем битовую строку в текст (байтовый массив -> строка)
        message = self.bits_to_text(''.join(bits))
        print(f"Extracted message: {message}")
        return message



    def calculate_capacity(self, container_text):
        capacity = sum(1 for char in container_text if char in self.rus_to_lat)
        print(f"Calculated capacity: {capacity}")
        return capacity

    def hiding_coefficient(self, container_text, num_embedded_bits):
        coefficient = num_embedded_bits / len(container_text) if len(container_text) > 0 else 0
        print(f"Calculated hiding coefficient: {coefficient}")
        return coefficient

    def load_text_from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()
        print(f"Loaded text from file {filename}: {text[:100]}...")
        return text

    def save_text_to_file(self, text, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text)
        print(f"Saved text to file {filename}")

    def load_text_from_string(self, text):
        print(f"Loaded text from string: {text[:100]}...")
        return text


if __name__ == "__main__":
    steg = TextSteganography()

    steg.load_dictionary('dict.yaml')

    container_text = steg.load_text_from_file('book.txt')

    # Сообщение для внедрения
    message = "hi"

    # Внедрение сообщения
    embedded_text, num_embedded_bits = steg.embed_message(container_text, message)

    # Сохранение текста с внедренным сообщением
    steg.save_text_to_file(embedded_text, 'embedded.txt')

    # Рассчет ёмкости и коэффициента сокрытия
    capacity = steg.calculate_capacity(container_text)
    hiding_coeff = steg.hiding_coefficient(container_text, num_embedded_bits)

    print(f"Исходный текст:\n{container_text[:100]}...")
    print(f"Текст с внедренным сообщением:\n{embedded_text[:100]}...\n")
    print(f"Количество внедренных бит: {num_embedded_bits}")
    print(f"Информационная емкость контейнера: {capacity}")
    print(f"Коэффициент сокрытия: {hiding_coeff:.2f}\n")

    # Извлечение сообщения (передаём длину сообщения в байтах, а не символах)
    message_bytes_length = len(message.encode('utf-8'))
    extracted_message = steg.extract_message(embedded_text, message_bytes_length)
    print(f"Извлеченное сообщение: {extracted_message}")
