import threading
import time
import signal
import sys


class JantarDosFilosofos:
    def __init__(self, quantidade):
        self.quantidade = quantidade
        self.garfos = [threading.Lock() for _ in range(quantidade)]
        self.ativo = True
        self.threads = []

    def garfos_do_filosofo(self, filosofo):
        
        esquerdo = filosofo
        direito = (filosofo + 1) % self.quantidade
        return tuple(sorted((esquerdo, direito)))

    def pensar(self, filosofo):
        
        print(f"Filósofo {filosofo} está pensando...")
        time.sleep(1)

    def comer(self, filosofo, primeiro_garfo, segundo_garfo):
        
        print(f"Filósofo {filosofo} está com fome e tentando pegar os garfos.")
        with self.garfos[primeiro_garfo]:
            with self.garfos[segundo_garfo]:
                print(
                    f"Filósofo {filosofo} ESTÁ COMENDO "
                    f"(usando garfos {primeiro_garfo} e {segundo_garfo})"
                )
                time.sleep(2)
        print(f"Filósofo {filosofo} terminou de comer e voltou a pensar.")

    def ciclo_do_filosofo(self, filosofo):
        
        primeiro_garfo, segundo_garfo = self.garfos_do_filosofo(filosofo)

        while self.ativo:
            self.pensar(filosofo)
            self.comer(filosofo, primeiro_garfo, segundo_garfo)

    def iniciar(self):
        
        print(
            f"Iniciando jantar com {self.quantidade} filósofos. "
            f"Pressione Ctrl+C para encerrar."
        )

        for filosofo in range(self.quantidade):
            thread = threading.Thread(
                target=self.ciclo_do_filosofo,
                args=(filosofo,),
                daemon=True
            )
            self.threads.append(thread)
            thread.start()

    def parar(self):
        
        self.ativo = False
        print("\nEncerrando o jantar...")


def main():
    
    jantar = JantarDosFilosofos(5)

    def encerrar(_sig, _frame):
        
        jantar.parar()
        sys.exit(0)

    signal.signal(signal.SIGINT, encerrar)

    jantar.iniciar()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()