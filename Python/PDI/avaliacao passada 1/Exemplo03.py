# coding=utf-8
from pathlib import Path
import cv2
import sys

base_dir = Path(__file__).resolve().parent
caminho = base_dir / 'logo-if.jpg'

img = cv2.imread(str(caminho))

if img is None:
    print(f'Erro: não foi possível carregar a imagem em {caminho}', file=sys.stderr)
    sys.exit(1)

# Redimensiona imagem
img = cv2.resize(img, (200, 100), interpolation=cv2.INTER_AREA)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, mask_inv = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
mask = cv2.bitwise_not(mask_inv)

cv2.imshow('Original', img)
cv2.imshow('Grayscale', gray)
cv2.imshow('Threshold', mask)
cv2.imshow('Mask Inv', mask_inv)

cv2.waitKey(0)
cv2.destroyAllWindows()