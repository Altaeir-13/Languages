import threading
import time
import random
import signal
import sys


class MonitorLeituraEscrita:
    def __init__(self):
        self.leitores_ativos = 0
        self.lock_leitores = threading.Lock()
        self.lock_recurso = threading.Lock()

    def iniciar_leitura(self, leitor_id):
        with self.lock_leitores:
            self.leitores_ativos += 1
            if self.leitores_ativos == 1:
                self.lock_recurso.acquire()

        print(f"[Leitor {leitor_id}] Lendo dados...")

    def encerrar_leitura(self, leitor_id):
        with self.lock_leitores:
            self.leitores_ativos -= 1
            if self.leitores_ativos == 0:
                self.lock_recurso.release()

        print(f"[Leitor {leitor_id}] Terminou leitura.")

    def escrever(self, escritor_id):
        with self.lock_recurso:
            print(f"[Escritor {escritor_id}] === INICIANDO ESCRITA CRÍTICA ===")
            time.sleep(random.uniform(2, 3))
            print(f"[Escritor {escritor_id}] === ESCRITA FINALIZADA ===")


class SimulacaoLeitoresEscritores:
    def __init__(self):
        self.monitor = MonitorLeituraEscrita()
        self.rodando = True
        self.threads = []

    def ciclo_leitor(self, leitor_id):
        while self.rodando:
            self.monitor.iniciar_leitura(leitor_id)
            time.sleep(random.uniform(1, 2))
            self.monitor.encerrar_leitura(leitor_id)
            time.sleep(random.uniform(0.5, 1))

    def ciclo_escritor(self, escritor_id):
        while self.rodando:
            self.monitor.escrever(escritor_id)
            time.sleep(random.uniform(2, 4))

    def iniciar(self, leitores=3, escritores=1):
        print(f"Simulação iniciada ({leitores}L/{escritores}E). Ctrl+C para parar.")

        for i in range(leitores):
            thread = threading.Thread(
                target=self.ciclo_leitor,
                args=(i + 1,),
                daemon=True
            )
            self.threads.append(thread)
            thread.start()

        for i in range(escritores):
            thread = threading.Thread(
                target=self.ciclo_escritor,
                args=(i + 1,),
                daemon=True
            )
            self.threads.append(thread)
            thread.start()

    def parar(self):
        self.rodando = False


def main():
    simulacao = SimulacaoLeitoresEscritores()

    def encerrar(_sig, _frame):
        simulacao.parar()
        print("\nEncerrando simulação com segurança...")
        sys.exit(0)

    signal.signal(signal.SIGINT, encerrar)
    simulacao.iniciar(leitores=4, escritores=2)

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()