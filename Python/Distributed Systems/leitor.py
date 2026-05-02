import threading  # Biblioteca para criar e controlar threads (execução concorrente)
import time  # Biblioteca para trabalhar com pausas e tempo
import random  # Biblioteca para gerar valores aleatórios
import signal  # Biblioteca para capturar sinais do sistema (ex.: Ctrl+C)
import sys  # Biblioteca com funções do interpretador (ex.: finalizar programa)


class MonitorLeituraEscrita:
    def __init__(self):
        self.leitores_ativos = 0  # Contador de leitores que estão lendo neste momento
        self.lock_leitores = threading.Lock()  # Lock para proteger acesso ao contador de leitores
        self.lock_recurso = threading.Lock()  # Lock do recurso compartilhado (bloqueia escrita/leitura crítica)

    def iniciar_leitura(self, leitor_id):
        with self.lock_leitores:  # Entra em seção crítica para alterar leitores_ativos com segurança
            self.leitores_ativos += 1  # Incrementa quantidade de leitores ativos
            if self.leitores_ativos == 1:  # Se este for o primeiro leitor...
                self.lock_recurso.acquire()  # ...bloqueia o recurso para impedir escritores durante leitura

        print(f"[Leitor {leitor_id}] Lendo dados...")  # Mensagem de status da leitura

    def encerrar_leitura(self, leitor_id):
        with self.lock_leitores:  # Entra em seção crítica para alterar leitores_ativos com segurança
            self.leitores_ativos -= 1  # Decrementa quantidade de leitores ativos
            if self.leitores_ativos == 0:  # Se era o último leitor...
                self.lock_recurso.release()  # ...libera o recurso para permitir escrita

        print(f"[Leitor {leitor_id}] Terminou leitura.")  # Mensagem de status de fim da leitura

    def escrever(self, escritor_id):
        with self.lock_recurso:  # Garante exclusão mútua: apenas 1 escritor e nenhum leitor durante escrita
            print(f"[Escritor {escritor_id}] === INICIANDO ESCRITA CRÍTICA ===")  # Início da escrita
            time.sleep(random.uniform(2, 3))  # Simula tempo de escrita entre 2 e 3 segundos
            print(f"[Escritor {escritor_id}] === ESCRITA FINALIZADA ===")  # Fim da escrita


class SimulacaoLeitoresEscritores:
    def __init__(self):
        self.monitor = MonitorLeituraEscrita()  # Instância do monitor que controla leitura/escrita
        self.rodando = True  # Flag para manter os loops das threads ativos
        self.threads = []  # Lista para guardar referências das threads criadas

    def ciclo_leitor(self, leitor_id):
        while self.rodando:  # Loop contínuo do leitor enquanto simulação estiver ativa
            self.monitor.iniciar_leitura(leitor_id)  # Solicita início da leitura ao monitor
            time.sleep(random.uniform(1, 2))  # Simula tempo lendo dados (1 a 2 segundos)
            self.monitor.encerrar_leitura(leitor_id)  # Informa ao monitor que terminou de ler
            time.sleep(random.uniform(0.5, 1))  # Pausa antes de tentar nova leitura

    def ciclo_escritor(self, escritor_id):
        while self.rodando:  # Loop contínuo do escritor enquanto simulação estiver ativa
            self.monitor.escrever(escritor_id)  # Solicita operação de escrita ao monitor
            time.sleep(random.uniform(2, 4))  # Pausa antes da próxima escrita

    def iniciar(self, leitores=3, escritores=1):
        print(f"Simulação iniciada ({leitores}L/{escritores}E). Ctrl+C para parar.")  # Exibe configuração inicial

        for i in range(leitores):  # Cria a quantidade definida de leitores
            thread = threading.Thread(  # Cria uma nova thread
                target=self.ciclo_leitor,  # Função que a thread executará
                args=(i + 1,),  # ID do leitor passado como argumento
                daemon=True  # Thread daemon encerra junto com o processo principal
            )
            self.threads.append(thread)  # Guarda referência da thread criada
            thread.start()  # Inicia execução da thread

        for i in range(escritores):  # Cria a quantidade definida de escritores
            thread = threading.Thread(  # Cria uma nova thread
                target=self.ciclo_escritor,  # Função que a thread executará
                args=(i + 1,),  # ID do escritor passado como argumento
                daemon=True  # Thread daemon encerra junto com o processo principal
            )
            self.threads.append(thread)  # Guarda referência da thread criada
            thread.start()  # Inicia execução da thread

    def parar(self):
        self.rodando = False  # Sinaliza para os loops das threads encerrarem


def main():
    simulacao = SimulacaoLeitoresEscritores()  # Cria objeto principal da simulação

    def encerrar(_sig, _frame):
        simulacao.parar()  # Muda flag para interromper os ciclos de leitores/escritores
        print("\nEncerrando simulação com segurança...")  # Mensagem de encerramento
        sys.exit(0)  # Finaliza o programa com código de sucesso

    signal.signal(signal.SIGINT, encerrar)  # Associa Ctrl+C (SIGINT) à função de encerramento
    simulacao.iniciar(leitores=4, escritores=2)  # Inicia simulação com 4 leitores e 2 escritores

    try:
        while True:  # Mantém thread principal viva enquanto as threads daemon executam
            time.sleep(1)  # Dorme para não consumir CPU desnecessariamente
    except (KeyboardInterrupt, SystemExit):
        pass  # Ignora exceções de saída, pois o encerramento já foi tratado


if __name__ == "__main__":
    main()  # Executa programa apenas quando arquivo for chamado diretamente

# ========================
# ROTEIRO PARA EXPLICAR AO PROFESSOR
# ========================
# 1) Objetivo do programa:
#    "Este código simula o problema clássico Leitores-Escritores em sistemas distribuídos/
#    concorrentes, garantindo acesso seguro a um recurso compartilhado."
#
# 2) Estrutura principal:
#    - MonitorLeituraEscrita: controla sincronização (quem pode ler/escrever).
#    - SimulacaoLeitoresEscritores: cria e executa as threads de leitores e escritores.
#    - main(): inicializa a simulação e trata encerramento com Ctrl+C.
#
# 3) Como a sincronização funciona (parte mais importante):
#    - lock_leitores protege o contador leitores_ativos.
#    - lock_recurso protege o recurso compartilhado.
#    - Quando um leitor entra:
#         a) incrementa leitores_ativos com lock_leitores.
#         b) se for o primeiro leitor, adquire lock_recurso.
#      Isso bloqueia escritores enquanto existir pelo menos um leitor.
#    - Quando um leitor sai:
#         a) decrementa leitores_ativos com lock_leitores.
#         b) se for o último leitor, libera lock_recurso.
#      Assim, escritores só escrevem quando não há leitores ativos.
#
# 4) Escritor:
#    - O método escrever() usa "with self.lock_recurso".
#    - Isso garante exclusão mútua: apenas um escritor por vez e nenhum leitor durante escrita.
#
# 5) Threads e simulação:
#    - iniciar() cria N threads leitoras e M threads escritoras (daemon=True).
#    - Cada leitor/escritor roda em loop enquanto self.rodando for True.
#    - time.sleep(random.uniform(...)) simula tempos reais de leitura, escrita e espera.
#
# 6) Encerramento seguro:
#    - SIGINT (Ctrl+C) chama encerrar().
#    - encerrar() define rodando=False e finaliza com sys.exit(0).
#    - Isso evita deixar a simulação em estado inconsistente.
#
# 7) Observação técnica para comentar na apresentação:
#    - Esta implementação favorece leitores (reader-preference).
#    - Em alta carga de leitura, escritores podem esperar bastante (possível starvation).
#
# 8) Frase de conclusão sugerida:
#    "O código demonstra controle de concorrência com locks, separando claramente a lógica
#    de sincronização (monitor) da lógica de execução (simulação com threads)."