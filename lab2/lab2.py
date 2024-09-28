from PIL import Image
import random

def generate_key(seed, size):
    random.seed(seed)
    return random.sample(range(size), size)


def text_to_bits(text):
    return ''.join(f'{ord(c):08b}' for c in text)

def bits_to_text(bits):
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(char, 2)) for char in chars)

def embed_text(image_path, text, channel, seed, output_path):
    img = Image.open(image_path)
    pixels = img.load()

    bits = text_to_bits(text)
    bit_length = len(bits)

    width, height = img.size
    total_pixels = width * height

    key = generate_key(seed, total_pixels)

    bit_idx = 0
    for i in range(total_pixels):
        x = key[i] % width
        y = key[i] // width
        r, g, b = pixels[x, y]

        if bit_idx < bit_length:
            if channel == 'R':
                r = (r & ~1) | int(bits[bit_idx])
            elif channel == 'G':
                g = (g & ~1) | int(bits[bit_idx])
            elif channel == 'B':
                b = (b & ~1) | int(bits[bit_idx])
            pixels[x, y] = (r, g, b)
            bit_idx += 1

    img.save(output_path)

    return bit_length

def extract_text(image_path, bit_length, channel, seed):
    img = Image.open(image_path)
    pixels = img.load()

    width, height = img.size
    total_pixels = width * height

    key = generate_key(seed, total_pixels)

    bits = []
    bit_idx = 0
    for i in range(total_pixels):
        if bit_idx >= bit_length:
            break

        x = key[i] % width
        y = key[i] // width
        r, g, b = pixels[x, y]

        if channel == 'R':
            bits.append(str(r & 1))
        elif channel == 'G':
            bits.append(str(g & 1))
        elif channel == 'B':
            bits.append(str(b & 1))

        bit_idx += 1
        
    return bits_to_text(''.join(bits))

if __name__ == '__main__':
    # Параметры
    input_image = 'input.bmp'
    output_image = 'output.bmp'
    text_message = "GG("
    seed = 1234 
    channel = 'B' 

    bits_embedded = embed_text(input_image, text_message, channel, seed, output_image)
    print(f'Внедрено {bits_embedded} бит.')
    extracted_message = extract_text(output_image, bits_embedded, channel, seed)
    print(f'Извлеченное сообщение: {extracted_message}')
