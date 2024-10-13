import numpy as np
import cv2
from scipy.fftpack import dct, idct

def load_image(filepath):
    """Load a BMP image."""
    img = cv2.imread(filepath)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    return img

def save_image(filepath, img):
    """Save the image as BMP."""
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR
    cv2.imwrite(filepath, img_bgr)

def dct_2d(block):
    """Apply 2D Discrete Cosine Transform (DCT) to a block."""
    return dct(dct(block.T, norm='ortho').T, norm='ortho')

def idct_2d(block):
    """Apply 2D Inverse Discrete Cosine Transform (IDCT) to a block."""
    return idct(idct(block.T, norm='ortho').T, norm='ortho')

def embed_message_in_block(block, bit, d):
    """Embed a single bit in the DCT coefficients of the block."""
    block_dct = dct_2d(block)
    # Find a coefficient greater than d
    for i in range(block_dct.shape[0]):
        for j in range(block_dct.shape[1]):
            if abs(block_dct[i, j]) > d:
                if bit == 1:
                    block_dct[i, j] += d
                else:
                    block_dct[i, j] -= d
                return idct_2d(block_dct)
    return block  # If no coefficient is greater than d

def extract_bit_from_block(block, d):
    """Extract a bit from the DCT coefficients of the block."""
    block_dct = dct_2d(block)
    # Find a coefficient greater than d
    for i in range(block_dct.shape[0]):
        for j in range(block_dct.shape[1]):
            if abs(block_dct[i, j]) > d:
                return 1 if block_dct[i, j] > 0 else 0
    return 0  # Default to 0 if no coefficient is greater than d

def embed_message(img, message, d):
    """Embed a binary message into an image."""
    h, w, _ = img.shape
    message_bits = ''.join(format(ord(c), '08b') for c in message)  # Convert message to binary
    bit_idx = 0
    # Split image into 8x8 blocks and embed message bits
    for y in range(0, h, 8):
        for x in range(0, w, 8):
            if bit_idx < len(message_bits):
                for channel in range(3):  # Iterate over R, G, B channels
                    block = img[y:y+8, x:x+8, channel]
                    img[y:y+8, x:x+8, channel] = embed_message_in_block(block, int(message_bits[bit_idx]), d)
                    bit_idx += 1
                    if bit_idx >= len(message_bits):
                        break
    return img

def extract_message(img, message_len, d):
    """Extract a binary message from an image."""
    h, w, _ = img.shape
    message_bits = []
    bit_idx = 0
    # Split image into 8x8 blocks and extract message bits
    for y in range(0, h, 8):
        for x in range(0, w, 8):
            if bit_idx < message_len * 8:
                for channel in range(3):  # Iterate over R, G, B channels
                    block = img[y:y+8, x:x+8, channel]
                    bit = extract_bit_from_block(block, d)
                    message_bits.append(str(bit))
                    bit_idx += 1
                    if bit_idx >= message_len * 8:
                        break
    # Convert binary message to string
    message = ''.join([chr(int(''.join(message_bits[i:i+8]), 2)) for i in range(0, len(message_bits), 8)])
    return message

def psnr(original, modified):
    """Calculate PSNR between two images."""
    mse = np.mean((original - modified) ** 2)
    if mse == 0:
        return float('inf')  # No difference between images
    max_pixel = 255.0
    psnr_value = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr_value

# Пример использования:
if __name__ == "__main__":
    # Параметры
    input_image_path = "input.bmp"
    output_image_path = "output_with_message.bmp"
    d = 10  # Пороговое значение для Podilchuk
    message = "Hidden message"

    # Шаг 1: Загрузка изображения
    img = load_image(input_image_path)

    # Шаг 2: Внедрение сообщения
    img_with_message = embed_message(img, message, d)

    # Шаг 3: Сохранение изображения с внедрённым сообщением
    save_image(output_image_path, img_with_message)

    # Шаг 4: Извлечение сообщения
    extracted_message = extract_message(img_with_message, len(message), d)
    print("Извлечённое сообщение:", extracted_message)

    # Шаг 5: Рассчёт PSNR
    psnr_value = psnr(img, img_with_message)
    print("PSNR:", psnr_value)
