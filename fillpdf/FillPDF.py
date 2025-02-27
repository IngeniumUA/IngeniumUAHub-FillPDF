import io
import math
from decimal import Decimal
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def round_half_up(number, decimals=2):
    multiplier = Decimal(10 ** decimals)
    return math.floor(number * multiplier + Decimal(0.5)) / multiplier
