import cv2
import sys

video = cv2.VideoCapture('avaliacao passada 1/bomb.mp4')
logo_original = cv2.imread('avaliacao passada 1/OpenCV_logo.png', cv2.IMREAD_UNCHANGED)

if not video.isOpened() or logo_original is None:
    sys.exit(1)

largura = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
altura = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 30
codec = cv2.VideoWriter_fourcc(*'mp4v')
saida = cv2.VideoWriter('output_video.mp4', codec, fps, (largura, altura))

tamanho = 200
logo_redimensionada = cv2.resize(logo_original, (tamanho, tamanho))

if logo_redimensionada.shape[2] == 4:
    canal_alpha = logo_redimensionada[:, :, 3]
    logo_colorida = logo_redimensionada[:, :, :3]
else:
    logo_cinza = cv2.cvtColor(logo_redimensionada, cv2.COLOR_BGR2GRAY)
    _, canal_alpha = cv2.threshold(logo_cinza, 200, 255, cv2.THRESH_BINARY_INV)
    logo_colorida = logo_redimensionada

pos_x = largura // 2
pos_y = altura // 2
vel_x = 15
vel_y = 15
angulo = 0
contagem_frames = 0

cv2.namedWindow('Video', cv2.WINDOW_NORMAL)

while True:
    sucesso, frame = video.read()
    if not sucesso:
        break

    pos_x = pos_x + vel_x
    pos_y = pos_y + vel_y

    if pos_x <= 0 or pos_x + tamanho >= largura:
        vel_x = vel_x * -1
        if pos_x < 0: pos_x = 0
        if pos_x + tamanho > largura: pos_x = largura - tamanho

    if pos_y <= 0 or pos_y + tamanho >= altura:
        vel_y = vel_y * -1
        if pos_y < 0: pos_y = 0
        if pos_y + tamanho > altura: pos_y = altura - tamanho

    angulo = (angulo + 12) % 360
    contagem_frames = contagem_frames + 1

    if (contagem_frames // 15) % 2 != 0:
        centro_logo = (tamanho / 2, tamanho / 2)
        matriz_rotacao = cv2.getRotationMatrix2D(centro_logo, angulo, 1)
        
        logo_rotacionada = cv2.warpAffine(logo_colorida, matriz_rotacao, (tamanho, tamanho))
        mascara_rotacionada = cv2.warpAffine(canal_alpha, matriz_rotacao, (tamanho, tamanho))

        regiao_video = frame[pos_y : pos_y + tamanho, pos_x : pos_x + tamanho]
        regiao_video[mascara_rotacionada > 0] = logo_rotacionada[mascara_rotacionada > 0]

    cv2.imshow('Video', frame)
    saida.write(frame)

    if cv2.waitKey(33) == ord('q'):
        break

video.release()
saida.release()
cv2.destroyAllWindows()
