import heapq # Biblioteca para Fila de Prioridade (Min-Heap)

# --- CLASSE DO NO DA ARVORE ---
class NoHuffman:
    def __init__(self, char, freq):
        self.char = char        # Caractere armazenado (None se for um no interno/pai)
        self.freq = freq        # Frequencia (peso)
        self.esquerda = None    # Filho da esquerda (caminho 0)
        self.direita = None     # Filho da direita (caminho 1)

    # Metodo especial para o heapq saber como comparar dois nos.
    # O algoritmo eh GULOSO: ele precisa sempre pegar o no com MENOR frequencia.
    def __lt__(self, outro):
        return self.freq < outro.freq

# --- FUNCAO PRINCIPAL ---
def algoritmo_huffman(texto):
    
    # PASSO 1: Contagem de Frequencia
    # Cria um dicionario para contar quantas vezes cada letra aparece.
    frequencia = {}
    for caractere in texto:
        if caractere not in frequencia:
            frequencia[caractere] = 0
        frequencia[caractere] += 1
    
    print(f"1. Frequencias calculadas: {frequencia}")

    # PASSO 2: Fila de Prioridade (Min-Heap)
    # Transforma cada caractere em um "No" e joga na fila.
    # O heapq organiza automaticamente para que o menor peso fique no topo.
    fila_prioridade = []
    for char, freq in frequencia.items():
        heapq.heappush(fila_prioridade, NoHuffman(char, freq))

    # PASSO 3: Construcao da Arvore (A logica Gulosa)
    # Enquanto houver mais de 1 no na fila, agrupa os dois menores.
    while len(fila_prioridade) > 1:
        
        # 3.1: Remove os dois nos com MENOR frequencia (Guloso!)
        no_esquerda = heapq.heappop(fila_prioridade)
        no_direita = heapq.heappop(fila_prioridade)
        
        # 3.2: Cria um novo no pai com a soma das frequencias
        soma_freq = no_esquerda.freq + no_direita.freq
        no_pai = NoHuffman(None, soma_freq)
        
        # 3.3: Define os filhos (Esquerda e Direita)
        no_pai.esquerda = no_esquerda
        no_pai.direita = no_direita  # CORRECAO: A linha errada foi removida daqui
        
        # 3.4: Devolve o pai para a fila para ser processado depois
        heapq.heappush(fila_prioridade, no_pai)

    # O no que sobrou na fila eh a Raiz da arvore completa
    raiz_arvore = fila_prioridade[0]

    # PASSO 4: Gerar os Codigos (Percorrer a Arvore)
    # Funcao auxiliar recursiva para montar o codigo de '0' e '1'
    tabela_codigos = {}

    def gerar_codigo_recursivo(no, codigo_atual):
        if no is None:
            return

        # Se for um no folha (tem caractere), salva o codigo
        if no.char is not None:
            tabela_codigos[no.char] = codigo_atual
            return

        # Se nao for folha, continua descendo:
        # Esquerda = adiciona "0"
        gerar_codigo_recursivo(no.esquerda, codigo_atual + "0")
        # Direita = adiciona "1"
        gerar_codigo_recursivo(no.direita, codigo_atual + "1")

    gerar_codigo_recursivo(raiz_arvore, "")

    # PASSO 5: Codificar o Texto Original
    # Substitui cada letra pelo seu codigo binario correspondente
    texto_codificado = ""
    for char in texto:
        texto_codificado += tabela_codigos[char]

    return tabela_codigos, texto_codificado

# --- TESTANDO O CODIGO (Exemplo da Prova) ---
if __name__ == "__main__":
    entrada = "ILOVEYOUNICOLE"
    
    print(f"Entrada: {entrada}\n")
    
    tabela, saida_binaria = algoritmo_huffman(entrada)
    
    print("-" * 30)
    print("Tabela de Codigos Huffman:")
    print(f"{'Char':<5} | {'Codigo'}")
    print("-" * 30)
    
    # Exibe a tabela ordenada para facilitar a leitura
    for char in sorted(tabela):
        print(f"{char:<5} | {tabela[char]}")
        
    print("-" * 30)
    print(f"Sequencia Binaria Gerada:\n{saida_binaria}")
    print("-" * 30)
    
    # Calculo de compressao (Curiosidade para a prova)
    bits_original = len(entrada) * 8 # ASCII usa 8 bits por letra
    bits_huffman = len(saida_binaria)
    print(f"Tamanho Original (ASCII): {bits_original} bits")
    print(f"Tamanho Huffman: {bits_huffman} bits")