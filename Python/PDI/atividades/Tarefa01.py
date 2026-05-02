import cv2
import numpy as np

state = {'img': None, 'angle': 0, 'center': (0, 0), 'win': 'PDI - IFMA'}

def render():
    M = cv2.getRotationMatrix2D(state['center'], state['angle'], 1.0)
    res = cv2.warpAffine(state['img'], M, (state['img'].shape[1], state['img'].shape[0]))
    cv2.circle(res, state['center'], 5, (0, 0, 255), -1)
    cv2.imshow(state['win'], res)

def mouse_evt(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        state['center'] = (x, y)
        render()

def main():
    state['img'] = cv2.imread('ifma-caxias.jpg')
    if state['img'] is None: return
    
    h, w = state['img'].shape[:2]
    state['center'] = (w // 2, h // 2)
    
    cv2.namedWindow(state['win'])
    cv2.setMouseCallback(state['win'], mouse_evt)
    render()

    while True:
        k = cv2.waitKey(1) & 0xFF
        if k == 27: break
        if k == ord('r'):
            state['angle'] = (state['angle'] + 5) % 360
            render()
            
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()