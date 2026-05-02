import cv2
import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent
img1 = cv2.imread(str(base_dir / 'ifma-caxias.jpg'))
logo = cv2.imread(str(base_dir / 'logo-if.jpg'))

if img1 is None or logo is None:
    sys.exit(1)

logo = cv2.resize(logo, (200, 100), interpolation=cv2.INTER_AREA)
h, w = logo.shape[:2]

_, mask = cv2.threshold(cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY), 200, 255, cv2.THRESH_BINARY_INV)

img1[:h, :w][mask > 0] = logo[mask > 0]

cv2.imshow('Resultado', img1)
cv2.waitKey(0)
cv2.destroyAllWindows()