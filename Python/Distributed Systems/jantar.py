import threading  # Fornece recursos de concorrência usando threads.
import time  # Permite pausar a execução por alguns segundos.
import signal  # Permite capturar sinais do sistema (ex.: Ctrl+C).
import sys  # Dá acesso a funções do interpretador, como encerrar o programa.


class JantarDosFilosofos:
    # Classe principal que modela a simulação do problema do Jantar dos Filósofos.

    def __init__(self, quantidade):
        # Método construtor: executa quando um objeto da classe é criado.
        self.quantidade = quantidade  # Guarda o número total de filósofos na mesa.
        # Cria um lock para cada garfo; lock garante exclusão mútua (uso por um filósofo de cada vez).
        self.garfos = [threading.Lock() for _ in range(quantidade)]
        self.ativo = True  # Flag de controle: enquanto True, os filósofos continuam em ciclo.
        self.threads = []  # Lista para armazenar as threads criadas para cada filósofo.

    def garfos_do_filosofo(self, filosofo):
        # Define quais garfos pertencem ao filósofo atual.
        esquerdo = filosofo  # Índice do garfo à esquerda (mesmo índice do filósofo).
        # Índice do garfo à direita; o módulo (%) faz o último filósofo apontar para o garfo 0.
        direito = (filosofo + 1) % self.quantidade
        # Retorna os dois índices ordenados para manter uma ordem fixa de aquisição e evitar deadlock.
        return tuple(sorted((esquerdo, direito)))

    def pensar(self, filosofo):
        # Simula o estado de pensamento do filósofo.
        print(f"Filósofo {filosofo} está pensando...")  # Mostra no terminal o estado atual.
        time.sleep(1)  # Espera 1 segundo para simular tempo de pensamento.

    def comer(self, filosofo, primeiro_garfo, segundo_garfo):
        # Simula o ato de comer, pegando os dois garfos necessários com segurança.
        print(f"Filósofo {filosofo} está com fome e tentando pegar os garfos.")
        # Tenta adquirir o primeiro garfo; bloqueia se outro filósofo já estiver usando.
        with self.garfos[primeiro_garfo]:
            # Após pegar o primeiro, tenta adquirir o segundo garfo.
            with self.garfos[segundo_garfo]:
                # Só chega aqui quando os dois garfos estão em posse do filósofo.
                print(
                    f"Filósofo {filosofo} ESTÁ COMENDO "
                    f"(usando garfos {primeiro_garfo} e {segundo_garfo})"
                )
                time.sleep(2)  # Espera 2 segundos para simular o tempo de refeição.
        # Ao sair dos blocos "with", os locks são liberados automaticamente.
        print(f"Filósofo {filosofo} terminou de comer e voltou a pensar.")

    def ciclo_do_filosofo(self, filosofo):
        # Função alvo da thread: define o ciclo contínuo de vida de um filósofo.
        # Descobre, uma única vez, quais são os dois garfos desse filósofo.
        primeiro_garfo, segundo_garfo = self.garfos_do_filosofo(filosofo)

        # Enquanto a simulação estiver ativa, alterna entre pensar e comer.
        while self.ativo:
            self.pensar(filosofo)  # Executa etapa de pensamento.
            self.comer(filosofo, primeiro_garfo, segundo_garfo)  # Executa etapa de refeição.

    def iniciar(self):
        # Inicia a simulação criando e executando uma thread para cada filósofo.
        print(
            f"Iniciando jantar com {self.quantidade} filósofos. "
            f"Pressione Ctrl+C para encerrar."
        )

        # Percorre todos os filósofos (0 até quantidade-1).
        for filosofo in range(self.quantidade):
            # Cria uma nova thread para rodar o ciclo do filósofo correspondente.
            thread = threading.Thread(
                target=self.ciclo_do_filosofo,  # Função que a thread vai executar.
                args=(filosofo,),  # Argumentos passados para a função alvo.
                daemon=True  # Thread daemon encerra automaticamente quando o programa principal termina.
            )
            self.threads.append(thread)  # Guarda referência da thread na lista.
            thread.start()  # Inicia a execução da thread.

    def parar(self):
        # Encerra a simulação alterando a flag de controle do laço principal das threads.
        self.ativo = False
        print("\nEncerrando o jantar...")  # Exibe mensagem de encerramento.


def main():
    # Função principal do programa: configura sinais, inicia e mantém a aplicação viva.
    jantar = JantarDosFilosofos(5)  # Cria a simulação com 5 filósofos.

    def encerrar(_sig, _frame):
        # Handler de sinal chamado ao pressionar Ctrl+C (SIGINT).
        # _sig e _frame são parâmetros exigidos pela assinatura do handler de signal.
        jantar.parar()  # Pede para a simulação parar.
        sys.exit(0)  # Encerra o processo com código de sucesso.

    # Registra a função 'encerrar' para tratar o sinal de interrupção (Ctrl+C).
    signal.signal(signal.SIGINT, encerrar)

    jantar.iniciar()  # Inicia as threads e a simulação.

    try:
        # Laço infinito para manter a thread principal ativa.
        while True:
            time.sleep(1)  # Pequena pausa para evitar uso desnecessário de CPU.
    except (KeyboardInterrupt, SystemExit):
        # Ignora exceções de encerramento, pois o encerramento já é tratado no signal handler.
        pass


if __name__ == "__main__":
    # Garante que main() rode apenas quando este arquivo for executado diretamente.
    main()


# Explicação sugerida para apresentar ao professor:
# 1) Objetivo: simular o problema clássico do Jantar dos Filósofos para mostrar
#    sincronização concorrente e uso de locks em Python.
# 2) Estrutura principal: a classe JantarDosFilosofos contém:
#    - quantidade: número de filósofos/garfos;
#    - garfos: lista de threading.Lock, um por garfo;
#    - ativo: flag para encerrar os ciclos das threads;
#    - threads: referências às threads criadas.
# 3) garfos_do_filosofo(f): retorna índices do garfo esquerdo e direito e os
#    ordena (tuple(sorted(...))) para impor uma ordem fixa de aquisição — isso
#    evita o deadlock circular clássico porque todos os filósofos adquirem
#    locks sempre na mesma ordem.
# 4) pensar/comer: funções que simulam estados com prints e time.sleep (1s e 2s).
# 5) comer(f, g1, g2): usa 'with self.garfos[g1]' e em seguida 'with self.garfos[g2]'
#    garantindo que os locks são adquiridos e liberados de forma segura.
# 6) ciclo_do_filosofo: rotina alvo da thread; calcula os índices dos garfos uma
#    vez e então alterna pensar->comer enquanto self.ativo for True.
# 7) iniciar: cria uma thread daemon por filósofo (threads daemon terminam quando
#    o processo principal encerra) e as inicia.
# 8) parar: seta self.ativo = False para interromper os ciclos das threads e
#    imprime mensagem de encerramento.
# 9) main: cria instância com 5 filósofos, registra handler de SIGINT (Ctrl+C)
#    que chama jantar.parar() e sys.exit(0), inicia a simulação e mantém o loop
#    principal com sleep até sinal de interrupção.
# 10) Propriedades relevantes para discutir:
#    - Evita deadlock pelo ordenamento de aquisição de locks.
#    - Não garante fairness: pode ocorrer starvation (um filósofo nunca conseguir
#      ambos os garfos) dependendo do escalonamento.
#    - Usa primitives simples (threading.Lock); alternativas: semáforos,
#      waiter/arbitrator, ou algoritmos com conteadores/condition variables.
# 11) Demonstração prática: execute o script, mostre os prints de pensar/comer,
#    explique como o ordenamento evita deadlock e comente limitações e possíveis
#    melhorias (ex.: evitar starvation, métricas de desempenho, aumentar nº de
#    filósofos/alterar tempos).
# 12) Pontos para perguntas do professor: por que usamos locks em vez de outros
#    mecanismos, como provar ausência de deadlock no esquema atual, e como
#    modificar para garantir fairness.