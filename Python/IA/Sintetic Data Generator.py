qimport pandas as pd
import random
import numpy as np
import os
import unicodedata

# --- 1. Configurações & Reprodutibilidade ---
INPUT_FILE = 'Dataset/All Organic Data.csv'
OUTPUT_FILE = 'Nivel de Competicao/Hail to the Rainbow.csv'

# SEED FIXA
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Alvo: Tudo nivelado pela classe majoritária
ALVO_MAXIMO = 85549

TARGETS = {
    "anger": ALVO_MAXIMO,
    "disgust": ALVO_MAXIMO,
    "fear": ALVO_MAXIMO,
    "joy": ALVO_MAXIMO,
    "sadness": ALVO_MAXIMO,
    "surprise": ALVO_MAXIMO
}

# --- 2. Vocabulário Expandido (Cotidiano Brasileiro) ---

giras_inicio = [
    "mano", "vei", "mds", "putz", "nossa", "aff", "caraca", "gente", "na moral", 
    "pqp", "jesuss", "vixe", "eita", "ave maria", "oxe", "cruz credo", "meu deus", 
    "senhor amado", "bicho", "rapaz", "olha", "nossa senhora"
]

giras_fim = [
    "slk", "tenso", "bizarro", "foda", "demais", "serio", "real", "intankavel", 
    "me poupe", "inacreditavel", "socorro", "fala serio", "tlgd", "ta maluco", 
    "sinistro", "surreal", "sem base", "de cria", "mancada", "sacagem", "absurdo"
]

mapa_intensificadores = {
    "muito": ["mt", "pra caramba", "demais", "super", "mega", "horrores", "pra dedeu", "pacas", "absurdamente"],
    "demais": ["mt", "pra krl", "muito", "exagerado", "infinim", "demasiado", "num nivel hard"],
    "pouco": ["meio", "quase nada", "tipo nada", "so um tico", "migalha"]
}

# Novos Slots de Variedade
lugares = [
    "na rua", "no onibus", "no metro", "em casa", "no trabalho", "na faculdade", "no uber", 
    "na fila do banco", "no shopping", "na loterica", "no posto de saude", "na praia", 
    "no bar", "na balada", "no supermercado", "na calcada", "no terminal", "no almoco",
    "na reuniao", "no transito", "no quarto", "na cozinha", "na sala", "no boteco"
]

parentes = [
    "minha mae", "meu pai", "meu irmao", "o vizinho", "o motorista", "esse povo", 
    "meu chefe", "minha tia", "a vizinha", "meu namorado", "minha namorada", "o porteiro",
    "o atendente", "o professor", "minha avo", "meu avo", "meu primo", "a sogra", 
    "o entregador", "o motoboy", "a crianca", "aquele cara"
]

objetos = [
    "o celular", "a carteira", "o boleto", "a comida", "o lanche", "o computador", 
    "a internet", "o wifi", "a tv", "o carro", "a moto", "o cartao", "o pix", 
    "a encomenda", "a prova", "o salario", "a mensagem", "o audio", "a foto"
]

# --- TEMPLATES MASSIVOS (Com foco em situações reais do BR) ---

templates_medo = [
    # Violência Urbana / Segurança
    "quase fui assaltado {lugar}", "tem um cara estranho me olhando fixo", 
    "ouvindo barulho de tiro aqui perto", "dois caras numa moto passaram devagar",
    "o {parente} nao atende o telefone e ja ta tarde", "sensação ruim de que algo vai acontecer", 
    "meu coracao ta disparado de susto", "travei totalmente na hora que vi", 
    "medo de andar a noite {lugar}", "vi um vulto passando {lugar}",
    "achei que ia morrer hoje slk", "fiquei gelado quando a luz acabou",
    "esse beco aqui me da arrepios", "medo de bala perdida", 
    # Fobias / Saúde / Sobrenatural
    "minha mao ta suando frio de nervoso", "sinto que to sendo seguido na rua", 
    "gelou minha espinha agora", "nao consigo nem respirar de pavor", 
    "pernas tremendo horrores com isso", "ta me dando falta de ar esse lugar fechado",
    "meu estomago ta embrulhado de medo", "coracao saindo pela boca literalmente",
    "pavor de ficar sozinho {lugar}", "sonhei que estava caindo num abismo",
    "sensacao de morte iminente credo", "ansiedade a milhao com essa noticia", 
    "medo do que vai acontecer amanha no trampo", "trauma disso pra sempre", 
    "nao passo la nem pagando depois do que houve", "cagaço monstro de altura",
    "tenho fobia disso mds tira daqui", "fiquei branco igual papel",
    "barata voou na minha cara socorro", "medo desse cachorro solto"
]

templates_nojo = [
    # Higiene / Sujeira
    "encontrei um cabelo enorme na comida", "cheiro de podre vindo {lugar}", 
    "vi uma barata saindo do ralo", "ansia de vomito com esse video", 
    "o {parente} mastiga de boca aberta que nojo", "que estomago embrulhado me deu",
    "gente que cospe no chao na minha frente", "banheiro publico imundo ninguem merece", 
    "verme na fruta q eu ia comer eca", "me sinto sujo so de encostar nisso", 
    "vontade de lavar os olhos com candida depois de ver isso", "revirou meu estomago real",
    "cheiro de morte e lixo nesse lugar", "agua parada com larva da dengue credo", 
    "grudento e nojento credo tira isso", "tem gosto de azedo isso aqui", 
    "parece vomito essa comida da cantina", "quase gorfei no meio da rua",
    # Moral / Comportamento
    "que lixo de atitude desse cara", "nojo fisico dessa pessoa mentirosa", 
    "ranço eterno disso e de quem faz isso", "repulsa total por gente falsa", 
    "me da asco ver gente tratando mal os outros", "podridao humana sem limites",
    "falsidade me enjoa num nivel", "gente porca me irrita demais", 
    "imundo demais slk como consegue viver assim", "cheiro de suor insuportavel {lugar}",
    "a casa tava uma imundice so", "pisei num negocio mole eca"
]

templates_raiva = [
    # Cotidiano / Serviços
    "que odio desse {parente} que nao cala a boca", "internet caindo toda hora que odio", 
    "vontade de quebrar tudo agora", "o {parente} me tira do serio facil", 
    "atendimento lixo desse lugar nunca mais volto", "indignado com essa cobranca indevida",
    "paguei caro e veio estragado palhacada", "fura fila na minha frente na cara dura", 
    "nao tenho paciencia pra gente burra", "esse governo so faz merda incrivel", 
    "transito infernal {lugar} nao anda nada", "meu sangue ferve com injustica",
    "quero matar um hoje de tanta raiva", "povo folgado do caramba no onibus",
    # Tecnologia / Trabalho / Pessoal
    "o {objeto} travou bem na hora importante", "meu chefe é um imbecil completo",
    "vizinho com som alto as 3 da manha", "acabou a luz no meio da partida",
    "perdi o onibus por um minuto que raiva", "o {objeto} quebrou do nada",
    "fizeram fofoca com meu nome", "levaram meu credito e nao resolveram",
    "tomar banho gelado no inverno ninguem merece", "pisaram no meu tenis novo",
    "a encomenda foi extraviada to puto", "nao caiu o pix ate agora"
]

templates_tristeza = [
    # Pessoal / Emocional
    "saudade de quem ja se foi e nao volta", "vontade de chorar do nada hoje", 
    "me sentindo um lixo inutil", "o {parente} me decepcionou profundamente", 
    "noticia ruim logo cedo pra acabar com o dia", "dia cinza e sem graça nenhuma",
    "ninguem lembra de mim no meu aniversario", "sensação de vazio no peito que doi", 
    "queria sumir um pouco desse lugar", "coração partido com essa historia", 
    "depre batendo forte nessa chuva", "lagrima descendo sozinha sem controle",
    # Fracasso / Solidão
    "reprovei na materia que mais estudei", "sem dinheiro pra nada esse mes",
    "me sinto sozinho mesmo acompanhado", "perdi {objetos} que eu amava",
    "o filme acabou comigo to mal", "vendo fotos antigas e sofrendo",
    "queria voltar no tempo e corrigir isso", "desanimo total de levantar da cama",
    "mundo injusto demais com as pessoas boas", "saudade da minha terra"
]

templates_surpresa = [
    # Choque / Inesperado
    "nao esperava por essa nem em mil anos", "chocado com essa noticia bombastica", 
    "mentira que isso aconteceu na minha frente", "como assim o {parente} fez isso?", 
    "fiquei de boca aberta agora sem reação", "surreal o que eu vi {lugar} hoje",
    "nem nos meus sonhos imaginava um plot desse", "caraca que reviravolta maluca", 
    "jamais pensaria nisso vindo dele", "to passado com essa fofoca", 
    "bugou minha mente agora total", "ganhei o sorteio nem acredito",
    "o {objeto} voltou a funcionar do nada", "olha o tamanho disso gente",
    "encontrei {parente} depois de anos", "o preço disso ta muito barato",
    "achava que era mentira mas é real", "o final desse filme me quebrou"
]

perguntas_retoricas = [
    "serio que vcs acham isso normal?", "como tem gente que aguenta isso?",
    "ate quando a gente vai aceitar isso calado?", "sera que so eu fico mal com isso?",
    "alguem me explica pq isso existe?", "onde esse mundo vai parar meu deus?",
    "qual a necessidade disso?", "pra que fazer isso gente?", "quem foi o genio que inventou isso?"
]

respostas_curtas = [
    "simplesmente doentio.", "nao da pra defender.", "que coisa bizarra.",
    "sem condicoes.", "inacreditavel.", "nojo real.", "medo genuino.", "triste demais.", 
    "que raiva mano.", "sem palavras.", "fiquei de cara.", "tomei um susto.",
    "nunca vi isso.", "perdi a fé na humanidade.", "chorei largado.", "gritei alto."
]

emojis_map = {
    "fear": ["😰", "😱", "💀", "😨", "🥶", "🫨", "☠️", "🆘"],
    "disgust": ["🤢", "🤮", "💩", "🦗", "😖", "🗑️", "🤢", "🧟"],
    "sadness": ["😢", "😞", "💔", "🥀", "😩", "🥺", "😭", "😿"],
    "anger": ["😡", "🤬", "😤", "🖕", "🙄", "🔥", "👿", "💢"],
    "surprise": ["😲", "😮", "🤯", "😶", "wdym", "👀", "🎉", "😱"]
}

# --- 3. Funções Otimizadas ---

def normalizar_unicode(txt):
    return unicodedata.normalize("NFKC", txt)

def sujar_texto(txt, intensidade):
    """Aplica ruído controlado."""
    txt = txt.lower()

    # Repetição enfática (Diversidade)
    if intensidade > 0.7 and random.random() < 0.15:
        palavras = txt.split()
        if len(palavras) > 2:
            idx = random.randint(0, len(palavras)-1)
            palavras.insert(idx, palavras[idx]) 
            txt = " ".join(palavras)

    # Pontuação e Caixa Alta (Raiva/Surpresa)
    if random.random() < 0.3 * intensidade:
        txt = txt.upper()
    
    if random.random() < 0.4 * intensidade:
        txt = txt.replace(".", "").replace(",", "").replace("?", "??").replace("!", "!!")

    # Internetês
    if random.random() < 0.5 * intensidade:
        replaces = {
            "voce": "vc", "porque": "pq", "muito": "mt", "que": "q", 
            "tambem": "tbm", "hoje": "hj", "beijo": "bj", "comigo": "cmg",
            "quando": "qnd", "beleza": "blz", "favor": "pfv"
        }
        for k, v in replaces.items():
            txt = txt.replace(k, v)

    # Typos (Erros de digitação comuns)
    if random.random() < 0.2 * intensidade:
        vizinhos = {'a': 's', 'e': 'r', 'o': 'p', 'm': 'n', 'b':'v', 'c':'x', 'l':'k'}
        lista_chars = list(txt)
        if lista_chars:
            idx = random.randint(0, len(lista_chars)-1)
            char_alvo = lista_chars[idx]
            if char_alvo in vizinhos:
                lista_chars[idx] = vizinhos[char_alvo]
            txt = "".join(lista_chars)
    
    return normalizar_unicode(txt)

def mutar_frase_real(frase_original, intensidade):
    palavras = frase_original.split()
    nova_frase = palavras.copy()

    for i, word in enumerate(palavras):
        if word.lower() in mapa_intensificadores and random.random() < 0.5:
            nova_frase[i] = random.choice(mapa_intensificadores[word.lower()])

    if intensidade > 0.6:
        if random.random() < 0.3: nova_frase.insert(0, random.choice(giras_inicio))
        if random.random() < 0.3: nova_frase.append(random.choice(giras_fim))

    texto_final = " ".join(nova_frase)
    return sujar_texto(texto_final, intensidade)

def gerar_via_template(emotion, intensidade):
    base = "erro"
    if emotion == "fear": base = random.choice(templates_medo)
    elif emotion == "disgust": base = random.choice(templates_nojo)
    elif emotion == "anger": base = random.choice(templates_raiva)
    elif emotion == "sadness": base = random.choice(templates_tristeza)
    elif emotion == "surprise": base = random.choice(templates_surpresa)

    if base == "erro": return "frase generica"

    # Substituição de Slots
    while "{lugar}" in base: base = base.replace("{lugar}", random.choice(lugares), 1)
    while "{parente}" in base: base = base.replace("{parente}", random.choice(parentes), 1)
    while "{objeto}" in base: base = base.replace("{objeto}", random.choice(objetos), 1) # Novo slot

    # Enriquecimento
    roll = random.random()
    if roll < 0.15:
        base = f"{random.choice(perguntas_retoricas)} {base}"
    elif roll < 0.30:
        base = f"{base} {random.choice(respostas_curtas)}"
    elif roll > 0.85: # Inserção de gíria no inicio
        base = f"{random.choice(giras_inicio)} {base}"

    frase = sujar_texto(base, intensidade)

    if intensidade > 0.3 and random.random() < 0.40:
        emoji_list = emojis_map.get(emotion, [])
        if emoji_list:
            # Adiciona 1 a 3 emojis
            emojis_escolhidos = "".join(random.choices(emoji_list, k=random.randint(1, 3)))
            frase += f" {emojis_escolhidos}"

    return frase

# --- 4. Execução Principal ---

print(f"--- Balanceamento V9 EXPANDIDO (Alvo: {ALVO_MAXIMO}) ---")

if not os.path.exists(INPUT_FILE):
    print("❌ Arquivo original não encontrado!")
    exit()

df = pd.read_csv(INPUT_FILE)

# 1. LIMPEZA OBRIGATÓRIA 
df = df.dropna(subset=['text'])
cols_labels = list(TARGETS.keys())
df['total_labels'] = df[cols_labels].sum(axis=1)
original_len = len(df)
df = df[df['total_labels'] > 0] 
filtered_len = len(df)
print(f"🧹 Limpeza realizada: {original_len - filtered_len} linhas inúteis removidas.")
df = df.drop(columns=['total_labels'])

# Prepara amostras reais
amostras_reais = {}
for emo in TARGETS.keys():
    textos = df[df[emo] == 1]['text'].tolist()
    amostras_reais[emo] = textos

frases_geradas = {emo: set() for emo in TARGETS}
current_counts = df[list(TARGETS.keys())].sum()
new_rows = []

for emotion, target in TARGETS.items():
    current = current_counts.get(emotion, 0)
    needed = max(0, int(target - current))

    print(f"\n[{emotion.upper()}] Atual: {current} | Meta: {target} | Gerando: {needed}")

    if needed > 0:
        checkpoint = max(1, needed // 10)
        qtd_reais = len(amostras_reais.get(emotion, []))
        
        # Ajuste dinâmico de estratégia
        if qtd_reais > 5000: prob_mutacao = 0.7
        elif qtd_reais > 500: prob_mutacao = 0.5
        else: prob_mutacao = 0.3 # Com templates ricos, podemos depender mais deles

        count_gerados = 0
        for i in range(needed):
            if i % checkpoint == 0 and i > 0: print(".", end="", flush=True)

            intensidade = random.random()
            tentativas = 0
            texto_final = ""

            while True:
                tentativas += 1
                usar_mutacao = (qtd_reais > 0) and (random.random() < prob_mutacao)

                if usar_mutacao:
                    frase_base = random.choice(amostras_reais[emotion])
                    texto_final = mutar_frase_real(frase_base, intensidade)
                else:
                    texto_final = gerar_via_template(emotion, intensidade)

                if texto_final not in frases_geradas[emotion]:
                    frases_geradas[emotion].add(texto_final)
                    break
                
                # Fallback se demorar para achar frase única
                if tentativas > 10:
                    texto_final = gerar_via_template(emotion, intensidade) + str(random.randint(0,9))
                    break 
            
            # Validação mínima de tamanho
            if len(texto_final.split()) < 2:
                 texto_final = gerar_via_template(emotion, intensidade)

            row = {
                "text": texto_final,
                "anger": 0, "disgust": 0, "fear": 0,
                "joy": 0, "sadness": 0, "surprise": 0
            }
            row[emotion] = 1
            new_rows.append(row)
            count_gerados += 1

        print(f" Concluído! ({count_gerados})")
        diversidade = len(frases_geradas[emotion]) / max(1, count_gerados)
        print(f"Diversidade Única: {diversidade:.2f}")

# --- 5. Salvamento ---
print("\nCriando DataFrame final...")
synthetic_df = pd.DataFrame(new_rows)

if not synthetic_df.empty:
    synthetic_df['id'] = [f'sintetico_v9_{i}' for i in range(len(synthetic_df))]

cols_order = ['id', 'text', 'anger', 'disgust', 'fear', 'joy', 'sadness', 'surprise']
cols_finais = [c for c in cols_order if c in df.columns or c in synthetic_df.columns]

if not synthetic_df.empty:
    synthetic_df = synthetic_df[cols_finais]

final_df = pd.concat([df, synthetic_df], ignore_index=True)
final_df = final_df.sample(frac=1, random_state=SEED).reset_index(drop=True)

final_df.to_csv(OUTPUT_FILE, index=False)

print("="*50)
print(f"✅ DATASET FINAL V9 PRONTO: {OUTPUT_FILE}")
print(f"Total de linhas: {len(final_df)}")
print("\n--- Distribuição Final ---")
print(final_df[["anger", "disgust", "fear", "joy", "sadness", "surprise"]].sum())
print("="*50)