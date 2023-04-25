#! /bin/python

from PIL import Image

# Header
char_4_magic = "qoif"
uint_32_t_width = 0
uint_32_t_height = 0
uint_8_t_channels = 3 | 4
uint_8_t_colorspace = 1 | 2

# End
STREAM_END_P1 = 0x00
STREAM_END_P2 = 0x01

# Each chunk starts with a 2- or 8-bit tag
QOI_OP_RGB = b'11111110'  # tag
QOI_OP_RGBA = b'11111111'
QOI_OP_INDEX = b'00'
QOI_OP_DIFF = b'01'
QOI_OP_LUMA = b'10'
QOI_OP_RUN = b'11'

# Running array of previously seen pixel
arr = [None] * 64


def get_hash_pos(r, g, b, a=None):
    if a == None:
        return (r * 3 + g * 5 + b * 7) % 64
    return (r * 3 + g * 5 + b * 7 + a*11) % 64


def encode(image="sample.png"):

    result = []

    with Image.open(image) as img:  # open in bytes
        width, height = img.size

        # prev_pixel = (b'11111111',b'11111111',b'11111111',b'11111111') # big number
        prev_pixel = (512, 512, 512, 512)  # big number
        run_length = 0

        for x in range(height):
            for y in range(width):
                pixel = img.getpixel((y, x))
                print(f"pixel: {y+1} {pixel}")
                r, g, b, a = pixel

                # run length
                if pixel == prev_pixel:
                    run_length += 1
                    if run_length < 61:  # not 63, because it will indicate that its of type rg or rgba
                        if y+1 == width and x + 1 == height:  # if this is the last pixel and we are at run continue to the next condition
                            pass
                        else:
                            continue

                if run_length:
                    result.append((QOI_OP_RUN, run_length))
                    print(result)
                    print("-----------------------")
                    run_length = 0
                    prev_pixel = pixel
                    continue

                # diff from the previous pixel
                pr, pg, pb, pa = prev_pixel

                # difference pixel
                dr = pr - r
                dg = pg - g
                db = pb - b
                if (dr >= -2 and dr <= 1) and (dg >= -2 and dg <= 1) and (db >= -2 and db <= 1):
                    result.append((QOI_OP_DIFF, dr, dg, db))
                    print(result)
                    print("-----------------------")
                    prev_pixel = pixel
                    continue

                # luma pixel
                lg = dg
                lr = (pr - r) - lg
                lb = (pb - b) - lg
                if (lr >= -32 and lr <= 31) and (lg >= -8 and lg <= 7) and (lb >= -8 and lb <= 7):
                    result.append((QOI_OP_LUMA, lr, lg, lb))
                    print(result)
                    print("-----------------------")
                    prev_pixel = pixel
                    continue

                pos = get_hash_pos(r, g, b)

                # index
                if arr[pos] != None and arr[pos] == pixel:
                    result.append((QOI_OP_INDEX, pos))
                    print(result)
                    print("-----------------------")
                    prev_pixel = pixel
                    continue

                result.append((QOI_OP_RGB, r, g, b))
                print(result)
                print("-----------------------")
                prev_pixel = pixel
                if arr[pos] == None:
                    arr[pos] = pixel
    return result


def decode(image):
    pass


if __name__ == "__main__":
    encode("sample_line.png")
