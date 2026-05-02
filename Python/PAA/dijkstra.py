import heapq
import sys

def carregar_grafo(nome_arquivo):
    grafo = {}
    origem_global = None

    with open(nome_arquivo, 'r') as f:
        # 1. Ler a primeira linha (Origem)
        linhas = f.readlines()
        origem_global = linhas[0].strip()

        # 2. Ler as arestas
        for linha in linhas[1:]:
            partes = linha.split()
            if len(partes) < 3: continue # Pula linhas vazias
            
            u, v, peso = partes[0], partes[1], int(partes[2])

            # Adiciona u e v ao grafo se não existirem
            if u not in grafo: grafo[u] = {}
            if v not in grafo: grafo[v] = {}

            # Cria a aresta (Grafo Direcionado)
            grafo[u][v] = peso
            
    return grafo, origem_global

def dijkstra(grafo, inicio):
    # Inicialização
    # distancias: guarda o menor custo encontrado até agora
    distancias = {no: float('inf') for no in grafo}
    distancias[inicio] = 0
    
    # anteriores: guarda "de onde eu vim" para reconstruir o caminho
    anteriores = {no: None for no in grafo}
    
    # Fila de prioridade: guarda tuplas (distancia_atual, vertice)
    fila = [(0, inicio)]

    while fila:
        # 1. Escolha Gulosa: Pega o vértice com menor distância da fila
        dist_atual, u = heapq.heappop(fila)

        # Se já achamos um caminho melhor antes, ignora esse processamento antigo
        if dist_atual > distancias[u]:
            continue

        # 2. Relaxamento: Verifica todos os vizinhos de 'u'
        for v, peso_aresta in grafo[u].items():
            nova_dist = dist_atual + peso_aresta

            # Se achou um atalho melhor para 'v'
            if nova_dist < distancias[v]:
                distancias[v] = nova_dist
                anteriores[v] = u # Anota que viemos de 'u'
                heapq.heappush(fila, (nova_dist, v))

    return distancias, anteriores

def reconstruir_caminho(anteriores, destino):
    caminho = []
    atual = destino
    while atual is not None:
        caminho.append(atual)
        atual = anteriores[atual]
    
    # O caminho foi montado do fim pro começo, então invertemos
    return " -> ".join(caminho[::-1])

# --- BLOCO PRINCIPAL ---
if __name__ == "__main__":
    # Crie um arquivo 'entrada.txt' com o conteúdo do exemplo da prova antes de rodar
    # Conteúdo exemplo:
    # A(inicio)
    # A B 6(oruigem, destino, peso)
    # A D 1
    # D B 2
    # D E 1
    # B C 5
    # E B 2
    # E C 5

    try:
        grafo, origem = carregar_grafo('entrada.txt')
        distancias, anteriores = dijkstra(grafo, origem)

        print(f"Menores distâncias a partir do vértice {origem}")
        print(f"{'Destino':<8} | {'Distância':<10} | {'Caminho'}")
        print("-" * 40)

        # Ordena a saída para ficar bonitinho
        for destino in sorted(grafo.keys()):
            dist = distancias[destino]
            path_str = reconstruir_caminho(anteriores, destino)
            
            # Formata infinito como "inf"
            dist_str = str(dist) if dist != float('inf') else "inf"
            
            print(f"{destino:<8} | {dist_str:<10} | {path_str}")

    except FileNotFoundError:
        print("Erro: Crie o arquivo 'entrada.txt' primeiro!")