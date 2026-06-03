from barcode import Code128
from barcode.writer import ImageWriter
import os


def generate_barcode(stock_number):

    folder = "static/barcodes"

    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, stock_number)

    Code128(
        stock_number,
        writer=ImageWriter()
    ).save(filepath)

    return f"barcodes/{stock_number}.png"