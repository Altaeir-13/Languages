import cv2
import sys
import numpy as np
import random
import os

def gerar_mascaras_logo(logo_img):
    """
    Gera as máscaras para remover o fundo branco da logomarca.
    Retorna a logo processada, a máscara do fundo (invertida) e a máscara do logo.
    """
    # Converte para tons de cinza para facilitar a limiarização
    gray_logo = cv2.cvtColor(logo_img, cv2.COLOR_BGR2GRAY)
    
    # Cria uma máscara onde pixels brancos (ou muito claros, > 240) se tornam 255
    _, mask_white = cv2.threshold(gray_logo, 240, 255, cv2.THRESH_BINARY)
    
    # Inverte a máscara: a logo fica branca (255) e o fundo fica preto (0)
    mask_logo = cv2.bitwise_not(mask_white)
    
    # Extrai apenas as cores da logo, zerando o fundo branco
    logo_fg = cv2.bitwise_and(logo_img, logo_img, mask=mask_logo)
    
    return logo_fg, mask_white, mask_logo

def processar_video(caminho_video, caminho_logo, caminho_saida):
    """
    Executa o pipeline de renderização da marca d'água no vídeo.
    """
    if not os.path.exists(caminho_video) or not os.path.exists(caminho_logo):
        print("Erro: Arquivo de vídeo ou logo não encontrado. Verifique os caminhos.")
        sys.exit(1)

    video = cv2.VideoCapture(caminho_video)
    logo_original = cv2.imread(caminho_logo, cv2.IMREAD_COLOR)

    if not video.isOpened() or logo_original is None:
        print("Erro crítico ao decodificar os arquivos fornecidos.")
        sys.exit(1)

    # Obtenção das propriedades originais do vídeo
    video_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # Requisito A: Redimensionamento mantendo a proporção (20% do comprimento)
    logo_width = int(video_width * 0.20)
    aspect_ratio = logo_original.shape[0] / logo_original.shape[1]
    logo_height = int(logo_width * aspect_ratio)
    
    logo_resized = cv2.resize(logo_original, (logo_width, logo_height), interpolation=cv2.INTER_AREA)

    # Requisito B: Descartar fundo branco
    logo_fg, mask_white, mask_logo = gerar_mascaras_logo(logo_resized)

    # Configuração do escritor de vídeo
    codec = cv2.VideoWriter_fourcc(*'mp4v')
    output = cv2.VideoWriter(caminho_saida, codec, fps, (video_width, video_height))

    frame_count = 0
    pos_x, pos_y = 0, 0
    alpha = 0.7  # Transparência da marca d'água (70% logo, 30% vídeo)

    print(f"Iniciando processamento de {total_frames} frames...")

    while True:
        ret, frame = video.read()
        if not ret:
            break  # Fim do vídeo

        # Requisito C: Mudar a posição aleatoriamente a cada 100 frames
        if frame_count % 100 == 0:
            pos_x = random.randint(0, video_width - logo_width)
            pos_y = random.randint(0, video_height - logo_height)

        # Extrai a Região de Interesse (ROI) do frame atual com base nas coordenadas
        roi = frame[pos_y:pos_y + logo_height, pos_x:pos_x + logo_width]

        # Apaga o local exato onde a logo vai ficar na ROI do vídeo (usando a máscara do fundo branco)
        roi_bg = cv2.bitwise_and(roi, roi, mask=mask_white)

        # Adiciona os pixels da logo na ROI apagada
        # Para que não seja uma colagem bruta, usamos blend na área específica
        # Primeiro, somamos diretamente para obter a sobreposição exata
        roi_sobreposta = cv2.add(roi_bg, logo_fg)

        # Aplica a transparência final misturando com a ROI original (somente na área da logo)
        roi_final = cv2.addWeighted(roi_sobreposta, alpha, roi, 1 - alpha, 0)

        # Substitui a ROI processada de volta no frame principal
        frame[pos_y:pos_y + logo_height, pos_x:pos_x + logo_width] = roi_final

        output.write(frame)
        frame_count += 1

        # Feedback visual no terminal
        if frame_count % 50 == 0:
            print(f"Processado: {frame_count}/{total_frames} frames", end='\r')

    print("\nProcessamento concluído com sucesso. Vídeo salvo em:", caminho_saida)

    # Liberação rigorosa de recursos
    video.release()
    output.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Defina os caminhos dos arquivos aqui
    CAMINHO_VIDEO = 'avaliacao passada 2/IFMA Campus Caxias.mp4'
    CAMINHO_LOGO = 'avaliacao passada 2/logo-if.jpg'
    CAMINHO_SAIDA = 'avaliacao passada 2/output_video.mp4'
    
    processar_video(CAMINHO_VIDEO, CAMINHO_LOGO, CAMINHO_SAIDA)