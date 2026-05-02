import cv2
import numpy as np
import random
import sys

def process_watermark_video(video_path, logo_path, output_path):
    # 1. Carregamento de Recursos
    cap = cv2.VideoCapture('/home/grey_rat/Code/Languages/Python/PDI/avaliacao passada 2/IFMA Campus Caxias.mp4')
    logo = cv2.imread('/home/grey_rat/Code/Languages/Python/PDI/avaliacao passada 2/logo-if.jpg')

    if not cap.isOpened() or logo is None:
        print("Erro: Não foi possível carregar o vídeo ou a logo.")
        sys.exit(1)

    # 2. Obtenção de Metadados do Vídeo
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Prevenção contra FPS nulo/inválido
    if fps <= 0: fps = 30.0

    # 3. Preparação da Logo (Proporção de 20% do comprimento)
    target_width = int(width * 0.20)
    original_h, original_w = logo.shape[:2]
    aspect_ratio = original_h / original_w
    target_height = int(target_width * aspect_ratio)
    
    logo_res = cv2.resize(logo, (target_width, target_height), interpolation=cv2.INTER_AREA)

    # 4. Criação da Máscara para descartar fundo branco
    # Convertemos para escala de cinza e criamos uma máscara onde o que não é branco (255) é mantido
    logo_gray = cv2.cvtColor(logo_res, cv2.COLOR_BGR2GRAY)
    # Criamos máscara: pixels menores que 250 (não brancos)
    _, mask = cv2.threshold(logo_gray, 250, 255, cv2.THRESH_BINARY_INV)
    
    # Extraímos apenas a parte colorida da logo usando a máscara
    logo_fg = cv2.bitwise_and(logo_res, logo_res, mask=mask)

    # 5. Configuração do Vídeo de Saída
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # 6. Loop de Processamento
    frame_count = 0
    pos_x, pos_y = 0, 0

    print(f"Iniciando processamento: {total_frames} frames...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Atualiza posição aleatória a cada 100 frames
        if frame_count % 100 == 0:
            pos_x = random.randint(0, width - target_width)
            pos_y = random.randint(0, height - target_height)

        # Define a Região de Interesse (ROI) no frame
        roi = frame[pos_y:pos_y+target_height, pos_x:pos_x+target_width]

        # b. Somar os pixels da logo com os pixels do vídeo (onde a máscara permite)
        # Primeiro, limpamos a área da logo na ROI do vídeo (opcional, mas garante soma limpa)
        mask_inv = cv2.bitwise_not(mask)
        roi_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        
        # Somamos o fundo da ROI com o foreground da logo
        # Usamos cv2.add para garantir o clipping em 255 (evitar overflow)
        dst = cv2.add(roi_bg, logo_fg)

        # Recola a ROI processada de volta no frame
        frame[pos_y:pos_y+target_height, pos_x:pos_x+target_width] = dst

        # Grava o frame
        out.write(frame)
        
        frame_count += 1
        if frame_count % 500 == 0:
            print(f"Progresso: {frame_count}/{total_frames} frames processados.")

    # 7. Finalização
    cap.release()
    out.release()
    print(f"Sucesso! Vídeo salvo em: {output_path}")

if __name__ == "__main__":
    # Caminhos baseados no seu exemplo
    VIDEO_INPUT = 'IFMA Campus Caxias.mp4'
    LOGO_INPUT = 'logo-if.jpg'
    VIDEO_OUTPUT = 'video_final_watermark.mp4'
    
    process_watermark_video(VIDEO_INPUT, LOGO_INPUT, VIDEO_OUTPUT)