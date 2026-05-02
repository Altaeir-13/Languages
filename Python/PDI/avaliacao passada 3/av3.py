import cv2
import numpy as np

def advanced_flag_wave(image_path, output_video, duration_sec=5, fps=30):
    # Carrega a imagem original
    img = cv2.imread('avaliacao passada 3/logo bandeira.jpg')
    if img is None:
        print("Erro ao carregar a imagem.")
        return
    
    h, w = img.shape[:2]
    
    # Configurações do vídeo
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_video, fourcc, fps, (w, h))
    
    # Parâmetros da ondulação
    amp_x = 10    # Amplitude horizontal
    amp_y = 15    # Amplitude vertical
    freq_x = 0.05 # Frequência no eixo X
    freq_y = 0.03 # Frequência no eixo Y
    speed = 0.2   # Velocidade da animação
    
    # Gera as grades de coordenadas base
    grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
    
    total_frames = duration_sec * fps
    
    for frame_idx in range(total_frames):
        t = frame_idx * speed
        
        # Calcula o deslocamento senoidal para cada pixel [cite: 12, 13]
        map_x = grid_x + amp_x * np.sin(grid_y * freq_x + t)
        map_y = grid_y + amp_y * np.sin(grid_x * freq_y + t)
        
        # Converte para float32 (exigência do cv2.remap)
        map_x = map_x.astype(np.float32)
        map_y = map_y.astype(np.float32)
        
        # Aplica a transformação geométrica 
        waved_img = cv2.remap(img, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        
        # Grava o frame no vídeo 
        video_writer.write(waved_img)
        
    video_writer.release()
    print(f"Vídeo salvo com sucesso: {output_video}")

# Execução
advanced_flag_wave('logo_bandeira.jpg', 'bandeira_animada.mp4')