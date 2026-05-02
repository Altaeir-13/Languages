# coding=utf-8
import cv2
from matplotlib import pyplot as plt
import sys

imagem = cv2.imread('ifma-caxias.jpg')

if imagem is None:
    print("Erro: não foi possível carregar 'ifma-caxias.jpg'")
    sys.exit(1)

imagem_pb = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

cv2.imshow('Escala de Cinza', imagem_pb)

hist = cv2.calcHist([imagem_pb], [0], None, [256], [0, 256])
plt.plot(hist)
plt.xlim([0, 256])
plt.show()

cv2.waitKey(0)
cv2.destroyAllWindows()