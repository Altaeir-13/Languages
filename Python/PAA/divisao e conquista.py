def encontrar_ponto_fixo(arr, inicio, fim):
    # Caso Base: Se a lista acabou e não achamos
    if inicio > fim:
        return -1 # Não existe

    # 1. Passo da Divisão: Achar o meio
    meio = (inicio + fim) // 2

    # 2. Conquista: Testar o meio
    if arr[meio] == meio:
        return meio # ACHAMOS! O valor é igual ao índice

    # 3. Decidir para onde ir (Recursão)
    if arr[meio] > meio:
        # Valor é muito alto, o "match" só pode estar na esquerda
        return encontrar_ponto_fixo(arr, inicio, meio - 1)
    else:
        # Valor é muito baixo, o "match" só pode estar na direita
        return encontrar_ponto_fixo(arr, meio + 1, fim)

# Exemplo de uso
vetor = [-10, -5, 2, 7, 9]
resultado = encontrar_ponto_fixo(vetor, 0, 4)
# O resultado será 2