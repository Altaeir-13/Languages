import cv2
import numpy as np
from math import cos, sin, radians

def rotacionar(img, angle, inversa=False):
    h, w, ch = img.shape
    res = np.zeros_like(img)
    theta = radians(-angle if inversa else angle)
    c, s = cos(theta), sin(theta)
    cx, cy = w // 2, h // 2

    for y in range(h):
        for x in range(w):
            tx, ty = x - cx, y - cy
            nx = int(tx * c - ty * s + cx)
            ny = int(tx * s + ty * c + cy)
            
            if 0 <= nx < w and 0 <= ny < h:
                if inversa: res[y, x] = img[ny, nx]
                else: res[ny, nx] = img[y, x]
    return res

def main():
    img = cv2.imread('ifma-caxias.jpg')
    if img is None: return
    
    angle = 0
    while True:
        rd = rotacionar(img, angle, False)
        ri = rotacionar(img, angle, True)
        
        cv2.imshow('Direta', rd)
        cv2.imshow('Inversa', ri)
        
        k = cv2.waitKey(0)
        if k == 27: break
        if k == ord('r'): angle = (angle + 5) % 360

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()