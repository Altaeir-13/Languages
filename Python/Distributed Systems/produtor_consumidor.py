import threading
import time
import random
import signal
import sys
from collections import deque


class BufferCompartilhado:
    def __init__(self, capacidade):
        self.capacidade = capacidade
        self.itens = deque()
        self.condicao = threading.Condition()

    def produzir(self, item, produtor_id):
        with self.condicao:
            while len(self.itens) >= self.capacidade:
                print(f"[Produtor {produtor_id}] Buffer cheio. Aguardando...")
                self.condicao.wait()

            self.itens.append(item)
            print(f"[Produtor {produtor_id}] Produziu: {item} | Buffer: {list(self.itens)}")
            self.condicao.notify_all()

    def consumir(self, consumidor_id):
        with self.condicao:
            while len(self.itens) == 0:
                print(f"[Consumidor {consumidor_id}] Buffer vazio. Aguardando...")
                self.condicao.wait()

            item = self.itens.popleft()
            print(f"[Consumidor {consumidor_id}] Consumiu: {item} | Buffer: {list(self.itens)}")
            self.condicao.notify_all()
            return item


class SimulacaoProdutorConsumidor:
    def __init__(self, produtores, consumidores, capacidade):
        self.buffer = BufferCompartilhado(capacidade)
        self.produtores = produtores
        self.consumidores = consumidores
        self.rodando = True
        self.threads = []

    def ciclo_produtor(self, produtor_id):
        while self.rodando:
            item = random.randint(1, 100)
            self.buffer.produzir(item, produtor_id)
            time.sleep(random.uniform(0.5, 1.5))

    def ciclo_consumidor(self, consumidor_id):
        while self.rodando:
            self.buffer.consumir(consumidor_id)
            time.sleep(random.uniform(1.0, 2.5))

    def iniciar(self):
        print(
            f"Iniciando simulação. "
            f"{self.produtores}P / {self.consumidores}C. Ctrl+C para parar."
        )

        for i in range(self.produtores):
            thread = threading.Thread(
                target=self.ciclo_produtor,
                args=(i,),
                daemon=True
            )
            self.threads.append(thread)
            thread.start()

        for i in range(self.consumidores):
            thread = threading.Thread(
                target=self.ciclo_consumidor,
                args=(i,),
                daemon=True
            )
            self.threads.append(thread)
            thread.start()

    def parar(self):
        self.rodando = False
        print("\nFinalizando threads e encerrando...")


def main():
    simulacao = SimulacaoProdutorConsumidor(produtores=3, consumidores=5, capacidade=15)

    def encerrar(_sig, _frame):
        simulacao.parar()
        sys.exit(0)

    signal.signal(signal.SIGINT, encerrar)
    simulacao.iniciar()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    main()