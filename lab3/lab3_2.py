import numpy as np
from PIL import Image
import random
import math

def text_to_bits(text):
    return ''.join(format(ord(char), '08b') for char in text)

def bits_to_text(bits):
    return ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))

def embed_message(image_path, message, d):
    # Открываем изображение и конвертируем в массив NumPy
    img = Image.open(image_path)
    img_array = np.array(img)

    # Преобразуем сообщение в биты
    message_bits = text_to_bits(message)
    bits_count = len(message_bits)

    # Создаем копию изображения для встраивания
    stego_img = img_array.copy()

    # Встраиваем биты сообщения
    bit_index = 0
    for channel in [2, 0, 1]:
        height, width = img_array.shape[:2]
        for i in range(height):
            for j in range(width):
                if bit_index >= bits_count:
                    break
                
                if abs(int(img_array[i, j, channel])) > d:
                    if message_bits[bit_index] == '1':
                        stego_img[i, j, channel] = min(255, img_array[i, j, channel] + d)
                    else:
                        stego_img[i, j, channel] = max(0, img_array[i, j, channel] - d)
                    bit_index += 1
            
            if bit_index >= bits_count:
                break
        
        if bit_index >= bits_count:
            break

    # Сохраняем стегоизображение
    stego_image = Image.fromarray(stego_img)
    stego_image.save("stego_output.bmp")

    return bits_count
def extract_message(stego_path, original_path, d, bits_count):
    # Открываем стегоизображение и оригинальное изображение
    stego_img = np.array(Image.open(stego_path))
    original_img = np.array(Image.open(original_path))

    extracted_bits = ""
    bit_index = 0

    for channel in [2, 0, 1]:
        height, width = stego_img.shape[:2]
        for i in range(height):
            for j in range(width):
                if bit_index >= bits_count:
                    break
                
                if abs(int(original_img[i, j, channel])) > d:
                    if stego_img[i, j, channel] > original_img[i, j, channel]:
                        extracted_bits += '1'
                    else:
                        extracted_bits += '0'
                    bit_index += 1
            
            if bit_index >= bits_count:
                break
        
        if bit_index >= bits_count:
            break

    return bits_to_text(extracted_bits)

def calculate_psnr(original, stego):
    mse = np.mean((original - stego) ** 2)
    if mse == 0:
        return float('inf')
    max_pixel = 255.0
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
    return psnr

def main():
    input_image = "input.bmp"
    message = "Hahahaha."
    d = 200 # Пороговое значение

    # Встраивание сообщения
    bits_embedded = embed_message(input_image, message, d)
    print(f"Количество встроенных бит: {bits_embedded}")

    # Извлечение сообщения
    extracted_message = extract_message("stego_output.bmp", input_image, d, bits_embedded)
    print(f"Извлеченное сообщение: {extracted_message}")

    # Расчет PSNR
    original_img = np.array(Image.open(input_image))
    stego_img = np.array(Image.open("stego_output.bmp"))

    psnr_values = []
    for channel in range(3):
        psnr = calculate_psnr(original_img[:,:,channel], stego_img[:,:,channel])
        psnr_values.append(psnr)
        print(f"PSNR для канала {channel}: {psnr} dB")

    # Проверка стойкости к сжатию
    stego_image = Image.open("stego_output.bmp")
    stego_image.save("compressed_stego.jpg", quality=95)
    compressed_stego = Image.open("compressed_stego.jpg")
    compressed_stego.save("decompressed_stego.bmp")

    # Извлечение сообщения из сжатого изображения
    extracted_compressed = extract_message("decompressed_stego.bmp", input_image, d, bits_embedded)
    print(f"Извлеченное сообщение после сжатия: {extracted_compressed}")

    # Подсчет ошибок
    original_bits = text_to_bits(message)
    compressed_bits = text_to_bits(extracted_compressed)
    errors = sum(a != b for a, b in zip(original_bits, compressed_bits))
    print(f"Количество ошибок после сжатия: {errors} из {bits_embedded} бит")

if __name__ == "__main__":
    main()