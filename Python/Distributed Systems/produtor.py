import threading
import time
import random
import signal
import sys
from collections import deque


class BufferCompartilhado:
    # Classe responsável por armazenar itens em um buffer limitado e sincronizado.
    def __init__(self, capacidade):
        # Define o número máximo de itens que o buffer pode guardar.
        self.capacidade = capacidade
        # Estrutura de fila eficiente para inserir/remover itens nas extremidades.
        self.itens = deque()
        # Condition coordena espera/acordo entre produtores e consumidores.
        self.condicao = threading.Condition()

    def produzir(self, item, produtor_id):
        # Entra na região crítica protegida pela condition.
        with self.condicao:
            # Enquanto o buffer estiver cheio, o produtor espera.
            while len(self.itens) >= self.capacidade:
                print(f"[Produtor {produtor_id}] Buffer cheio. Aguardando...")
                # Libera o lock e dorme até ser notificado.
                self.condicao.wait()

            # Adiciona o novo item ao buffer.
            self.itens.append(item)
            # Mostra o item produzido e o estado atual do buffer.
            print(f"[Produtor {produtor_id}] Produziu: {item} | Buffer: {list(self.itens)}")
            # Acorda todas as threads esperando (produtoras/consumidoras).
            self.condicao.notify_all()

    def consumir(self, consumidor_id):
        # Entra na região crítica protegida pela condition.
        with self.condicao:
            # Enquanto o buffer estiver vazio, o consumidor espera.
            while len(self.itens) == 0:
                print(f"[Consumidor {consumidor_id}] Buffer vazio. Aguardando...")
                # Libera o lock e dorme até ser notificado.
                self.condicao.wait()

            # Remove e obtém o item mais antigo do buffer (FIFO).
            item = self.itens.popleft()
            # Mostra o item consumido e o estado atual do buffer.
            print(f"[Consumidor {consumidor_id}] Consumiu: {item} | Buffer: {list(self.itens)}")
            # Acorda as threads esperando, pois houve mudança no buffer.
            self.condicao.notify_all()
            # Retorna o item consumido para quem chamou o método.
            return item


class SimulacaoProdutorConsumidor:
    # Controla criação de produtores/consumidores e ciclo de execução.
    def __init__(self, produtores=1, consumidores=1, capacidade=5):
        # Cria o buffer compartilhado com capacidade definida.
        self.buffer = BufferCompartilhado(capacidade)
        # Quantidade de threads produtoras.
        self.produtores = produtores
        # Quantidade de threads consumidoras.
        self.consumidores = consumidores
        # Flag usada para manter/interromper os loops das threads.
        self.rodando = True
        # Lista para armazenar referência das threads criadas.
        self.threads = []

    def ciclo_produtor(self, produtor_id):
        # Loop principal do produtor enquanto a simulação estiver ativa.
        while self.rodando:
            # Gera um item aleatório para produzir.
            item = random.randint(1, 100)
            # Tenta inserir o item no buffer.
            self.buffer.produzir(item, produtor_id)
            # Simula tempo de produção.
            time.sleep(random.uniform(0.5, 1.5))

    def ciclo_consumidor(self, consumidor_id):
        # Loop principal do consumidor enquanto a simulação estiver ativa.
        while self.rodando:
            # Tenta consumir um item do buffer.
            self.buffer.consumir(consumidor_id)
            # Simula tempo de processamento/consumo.
            time.sleep(random.uniform(1.0, 2.5))

    def iniciar(self):
        # Exibe resumo inicial da simulação.
        print(
            f"Iniciando simulação. "
            f"{self.produtores}P / {self.consumidores}C. Ctrl+C para parar."
        )

        # Cria e inicia todas as threads produtoras.
        for i in range(self.produtores):
            thread = threading.Thread(
                # Função executada pela thread.
                target=self.ciclo_produtor,
                # ID do produtor passado para a função.
                args=(i,),
                # Thread daemon encerra junto com o processo principal.
                daemon=True
            )
            # Guarda referência da thread.
            self.threads.append(thread)
            # Inicia execução da thread.
            thread.start()

        # Cria e inicia todas as threads consumidoras.
        for i in range(self.consumidores):
            thread = threading.Thread(
                # Função executada pela thread.
                target=self.ciclo_consumidor,
                # ID do consumidor passado para a função.
                args=(i,),
                # Thread daemon encerra junto com o processo principal.
                daemon=True
            )
            # Guarda referência da thread.
            self.threads.append(thread)
            # Inicia execução da thread.
            thread.start()

    def parar(self):
        # Sinaliza para os loops das threads finalizarem.
        self.rodando = False
        # Mensagem de encerramento da simulação.
        print("\nFinalizando threads e encerrando...")


def main():
    # Cria a simulação com 2 produtores, 2 consumidores e buffer de capacidade 5.
    simulacao = SimulacaoProdutorConsumidor(produtores=2, consumidores=2, capacidade=5)

    def encerrar(_sig, _frame):
        # Handler de sinal: para a simulação...
        simulacao.parar()
        # ...e encerra o processo com código de sucesso.
        sys.exit(0)

    # Registra o handler para Ctrl+C (SIGINT).
    signal.signal(signal.SIGINT, encerrar)
    # Inicia as threads de produção/consumo.
    simulacao.iniciar()

    try:
        # Mantém a thread principal viva enquanto a simulação roda.
        while True:
            # Pequena pausa para não ocupar CPU sem necessidade.
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        # Ignora exceções de encerramento, pois o fluxo de saída já foi tratado.
        pass

# Ponto de entrada do script quando executado diretamente.
if __name__ == "__main__":
    # Chama a função principal da aplicação.
    main()

# Instruções para explicar este código ao professor:
# 1) Objetivo geral:
#    - Mostrar que é uma simulação do problema produtor-consumidor com buffer limitado
#      e sincronização entre threads usando threading.Condition.
#
# 2) Componentes principais:
#    - BufferCompartilhado(capacidade): estrutura FIFO (collections.deque) com
#      uma Condition para coordenar produtores e consumidores.
#      * produzir(item, produtor_id): obtém o lock da condition, espera enquanto
#        o buffer estiver cheio (while len >= capacidade), insere o item, faz
#        notify_all() e libera o lock.
#      * consumir(consumidor_id): obtém o lock da condition, espera enquanto o
#        buffer estiver vazio (while len == 0), remove um item (popleft), faz
#        notify_all() e retorna o item.
#      - O uso de while evita problemas com wakeups espúrios.
#
# 3) SimulacaoProdutorConsumidor:
#    - Mantém o buffer, número de produtores/consumidores, lista de threads e
#      a flag self.rodando para controlar loops.
#    - ciclo_produtor: gera um inteiro aleatório, chama buffer.produzir(...) e
#      dorme um tempo aleatório para simular produção.
#    - ciclo_consumidor: chama buffer.consumir(...) e dorme para simular consumo.
#    - iniciar(): cria e inicia as threads (daemon=True) para produtores e
#      consumidores, salvando referências em self.threads.
#    - parar(): define rodando = False e imprime mensagem.
#
# 4) Execução e encerramento:
#    - main() instancia a simulação (ex.: 2 produtores, 2 consumidores, cap=5),
#      registra um handler para SIGINT que chama simulacao.parar() e encerra o
#      processo com sys.exit(0), e mantém a thread principal viva em loop.
#    - As threads são daemon: quando o processo principal termina, elas são
#      finalizadas automaticamente; por isso não há join explícito.
#
# 5) Pontos a destacar ao explicar ao professor:
#    - Como Condition garante exclusão mútua e coordenação (wait libera o lock
#      e bloqueia até notify; notify_all acorda todas as threads esperando).
#    - Por que usar while em vez de if (protege contra wakeups espúrios e
#      mudanças de estado entre o notify e a aquisição do lock).
#    - Efeito de usar daemon=True (simples, mas não permite limpeza ordenada).
#    - Possíveis melhorias: usar queue.Queue (já thread-safe) ou implementar
#      um mecanismo de parada que notifique (condicao.notify_all()) após
#      setar rodando = False e fazer join() nas threads para encerramento limpo.
#
# 6) Roteiro de apresentação curto (mensagens que pode dizer):
#    - "Este programa simula produtores e consumidores que compartilham um
#      buffer limitado. A sincronização é feita com threading.Condition para
#      coordenar espera e notificação. Producers esperam quando o buffer está
#      cheio; consumers esperam quando está vazio. Usei while nos waits para
#      robustez contra wakeups espúrios. O encerramento é tratado por SIGINT,
#      que seta a flag de parada e termina o processo." 
#