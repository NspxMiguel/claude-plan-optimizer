"""Os sinais que separam trabalho caro de trabalho barato.

Cada padrão aqui saiu de um corpus de 811 pedidos reais, não de intuição: as
palavras foram tiradas por frequência do que o usuário de fato digita, em
português informal e sem acento ("pq", "n", "tbm", "vdd"), e depois recortadas
manualmente entre as que mudam o custo e as que só enchem linguiça.

Duas famílias de idioma convivem no mesmo padrão de propósito. Quem escreve
"muda a cor do botao" e quem escreve "change the button colour" pede a mesma
coisa, e separar em dois arquivos só criaria a chance de um ficar para trás.
"""

import re


def _p(*alternativas):
    """Compila alternativas como padrão de palavra inteira, sem acento exigido."""
    return re.compile(r"(?<![a-zà-ú])(?:" + "|".join(alternativas) + r")(?![a-zà-ú])",
                      re.IGNORECASE)


# --------------------------------------------------------------- continuação ---
# 22% dos pedidos do corpus. Não descrevem trabalho: mandam seguir. O texto não
# diz nada sobre o custo — quem sabe é a tarefa que já estava rodando.
CONTINUACAO = _p(
    r"continu[ae]", r"continua[r]?", r"segue", r"seguir", r"prossegue", r"prossiga",
    r"dale", r"daleee*", r"vai+", r"vaii+", r"bora", r"manda", r"mandar? ver",
    r"ok", r"okay", r"blz", r"beleza", r"isso", r"isso ai", r"isso mesmo",
    r"pode", r"pode fazer", r"pode ir", r"pode sim", r"faz ai", r"faz isso",
    r"sim", r"aham", r"uhum", r"certo", r"perfeito", r"boa", r"show",
    r"continue", r"go ahead", r"go on", r"proceed", r"keep going", r"yes", r"yep",
    r"sounds good", r"do it", r"lgtm",
)

# Sozinhas não são continuação — "ok, agora refaz o backend" é trabalho novo.
# Por isso a continuação só vale quando o pedido é curto e não traz verbo de obra.

SAUDACAO = _p(
    r"oi+", r"ola", r"olá", r"eae", r"e ai", r"salve", r"bom dia", r"boa tarde",
    r"boa noite", r"hi", r"hey", r"hello", r"yo", r"valeu", r"vlw", r"obrigado",
    r"obg", r"thanks", r"thank you", r"tks",
)

# ------------------------------------------------------------------ trivial ---
# Edição mecânica: a resposta está dentro do próprio pedido.
MECANICO = _p(
    r"cor", r"cores", r"colour", r"color", r"renomeia", r"renomear", r"rename",
    r"typo", r"erro de digita[çc][ãa]o", r"acento", r"emoji", r"[íi]cone", r"icon",
    r"tamanho da fonte", r"font size", r"negrito", r"bold", r"it[áa]lico",
    r"maiuscul", r"minuscul", r"uppercase", r"lowercase",
    r"apaga", r"apagar", r"deleta", r"deletar", r"remove", r"remover", r"delete",
    r"comenta", r"descomenta", r"espa[çc]amento", r"padding", r"margin",
    r"troca o nome", r"muda o nome", r"muda o texto", r"change the text",
)

# ------------------------------------------------------------------ amplitude ---
# "tudo" aparece em 173 dos 811 pedidos. É o marcador de escopo aberto dele, e
# quase sempre significa varredura — o oposto de mudança pontual.
AMPLITUDE = _p(
    r"tudo", r"tudo isso", r"inteiro", r"inteira", r"todos", r"todas",
    r"completo", r"completa", r"geral", r"por completo", r"do zero",
    r"de ponta a ponta", r"ponta a ponta", r"em todos", r"em todas",
    r"o app todo", r"o site todo", r"o projeto todo", r"cada um", r"um por um",
    r"everything", r"the whole", r"entire", r"end to end", r"from scratch",
    r"across the", r"every single", r"all of",
)

VARREDURA = _p(
    r"revisa", r"revisar", r"revis[ãa]o", r"audita", r"auditar", r"auditoria",
    r"vasculha", r"varre", r"varrer", r"varredura", r"confere tudo", r"checa tudo",
    r"procura problemas", r"acha os bugs", r"caça", r"ca[çc]ar",
    r"review", r"audit", r"sweep", r"go through", r"comb through", r"inspect",
)

# ---------------------------------------------------------------- causa oculta ---
# Defeito relatado sem causa. Ninguém sabe onde está o problema até procurar, e
# procurar é o trabalho caro — o conserto em si costuma ser uma linha.
CAUSA_OCULTA = _p(
    r"pq", r"pq n", r"por que", r"porque", r"porqu[êe]", r"por qu[êe]",
    r"n funciona", r"nao funciona", r"não funciona", r"n ta funcionando",
    r"nao ta funcionando", r"parou de funcionar", r"deixou de funcionar",
    r"ta bugado", r"bugado", r"buga", r"bugando", r"bug", r"bugs",
    r"quebra", r"quebrou", r"quebrado", r"trava", r"travando", r"travou",
    r"crash", r"crasha", r"fecha sozinho", r"nao abre", r"n abre",
    r"n foi", r"nao foi", r"nao deu", r"n deu", r"deu erro", r"da erro",
    r"erro", r"error", r"falha", r"falhou", r"nao aparece", r"n aparece",
    r"sumiu", r"desapareceu", r"estranho", r"esquisito",
    r"why", r"doesn.?t work", r"not working", r"broken", r"crashes", r"fails",
    r"stopped working", r"weird", r"unexpected",
    r"crasho[u]?", r"fudido", r"fudida", r"confuso", r"confusa", r"pior",
    r"ainda n", r"ainda nao", r"ainda não", r"continua sem", r"segue sem",
)

# A forma como ele relata defeito no corpus: negação colada num verbo de estado.
# "n foi", "nao apareceu", "nao ta subindo", "n carrega", "nao acha". Escrever
# cada uma à mão deixaria metade de fora — o padrão é a negação, não o verbo.
NEGACAO_DEFEITO = re.compile(
    r"(?<![a-zà-ú])n(?:ao|ão)?\s+"
    r"(?:ta|tá|est[áa]|vai|foi|deu|da|dá|abre|sobe|sub[ei]|acha|achou|carrega|"
    r"salva|salvou|funciona|funcionou|funcionando|aparec\w*|toca|tocou|tocando|"
    r"mostra|mostrou|roda|rodou|conecta|conectou|responde|respondeu|atualiza\w*|"
    r"sincroniza\w*|consegue|consegui|deixa|permite|pega|pegou|entra|entrou)"
    r"(?![a-zà-ú])",
    re.IGNORECASE)

# ------------------------------------------------------------- decisão de peso ---
DECISAO = _p(
    r"arquitetura", r"arquitetural", r"refatora", r"refatorar", r"refactor",
    r"redesenha", r"reescreve", r"reescrever", r"rewrite",
    # Refazer é reescrever, não editar: quem refaz joga fora o que existia.
    r"refaz", r"refazer", r"refa[çc]a", r"redo", r"remake", r"do over", r"migra", r"migrar",
    r"migration", r"reestrutura", r"decide", r"decidir", r"escolhe", r"escolher",
    r"qual (?:e|é|eh) melhor", r"melhor (?:jeito|forma|caminho|op[çc][ãa]o)",
    r"vale a pena", r"compara", r"comparar", r"trade.?off", r"design",
    r"planeja", r"planejar", r"estrategia", r"estratégia", r"abordagem",
    r"which is better", r"should i", r"approach", r"architecture", r"strategy",
    r"analisa", r"analise", r"analize", r"analisar", r"an[áa]lise", r"avalia",
    r"avaliar", r"viabilidade", r"feasibility", r"porta", r"portar", r"port",
    r"unifica", r"unificar", r"junta", r"juntar", r"merge", r"consolida",
    r"melhora", r"melhorar", r"aprimora", r"refina", r"refinar", r"repensa",
    r"generaliza", r"abstrai", r"padroniza", r"improve", r"rethink",
)

RISCO = _p(
    r"seguran[çc]a", r"security", r"senha", r"password", r"chave", r"api key",
    r"token", r"secret", r"segredo", r"credencial", r"vaza", r"vazar", r"vazamento",
    r"leak", r"exposto", r"permiss[ãa]o", r"permission", r"auth", r"autentica",
    r"lgpd", r"gdpr", r"privacidade", r"privacy", r"criptografia", r"encrypt",
    r"producao", r"produ[çc][ãa]o", r"production", r"irrevers[íi]vel", r"destrutiv",
    r"dinheiro", r"pagamento", r"payment", r"cobran[çc]a", r"billing",
)

DESEMPENHO = _p(
    r"otimiza", r"otimizar", r"otimiza[çc][ãa]o", r"performance", r"desempenho",
    r"lento", r"lentid[ãa]o", r"devagar", r"pesado", r"pesa", r"trava tudo",
    r"memoria", r"mem[óo]ria", r"vazamento de mem", r"memory leak", r"cpu",
    r"optimize", r"slow", r"heavy", r"faster", r"speed up", r"bottleneck",
)

# ------------------------------------------------------------ obra de verdade ---
# Verbos que abrem trabalho. Sem um deles, um pedido curto é conversa.
CONSTRUIR = _p(
    r"faz", r"faça", r"faca", r"fazer", r"refaz", r"refazer", r"refaça", r"cria", r"criar", r"crie", r"monta",
    r"montar", r"implementa", r"implementar", r"constr[oóu]i?", r"construir",
    r"desenvolve", r"desenvolver", r"escreve", r"escrever", r"adiciona",
    r"adicionar", r"coloca", r"colocar", r"poe", r"põe", r"por", r"bota",
    r"arruma", r"arrumar", r"conserta", r"consertar", r"corrige", r"corrigir",
    r"ajusta", r"ajustar", r"muda", r"mudar", r"troca", r"trocar", r"altera",
    r"atualiza", r"atualizar", r"instala", r"instalar", r"configura", r"configurar",
    r"integra", r"integrar", r"publica", r"publicar", r"sobe", r"subir", r"lan[çc]a",
    r"testa", r"testar", r"documenta", r"documentar", r"traduz", r"traduzir",
    r"build", r"create", r"make", r"implement", r"write", r"add", r"fix",
    r"change", r"update", r"install", r"configure", r"deploy", r"publish",
    r"test", r"document", r"translate", r"set up", r"setup",
    r"tira", r"tirar", r"baixa", r"baixar", r"download", r"gera", r"gerar",
    r"roda", r"rodar", r"executa", r"executar", r"ativa", r"desativa", r"liga",
    r"desliga", r"habilita", r"desabilita", r"exibe", r"mostra", r"esconde",
    r"renomeia", r"move", r"mover", r"copia", r"copiar", r"exporta", r"importa",
    r"remove", r"run", r"generate", r"enable", r"disable", r"show", r"hide",
    r"move", r"copy", r"export", r"import", r"upload",
)

# Áreas distintas do produto. Duas ou mais num pedido só quase sempre significa
# que ele encomendou várias frentes na mesma frase.
DOMINIOS = (
    ("frontend", _p(r"tela", r"telas", r"ui", r"interface", r"front", r"frontend",
                    r"css", r"layout", r"design", r"componente", r"botao", r"bot[ãa]o",
                    r"pagina", r"p[áa]gina", r"view", r"screen")),
    ("backend",  _p(r"backend", r"back", r"servidor", r"server", r"api", r"endpoint",
                    r"rota", r"route", r"servi[çc]o", r"daemon", r"worker")),
    ("dados",    _p(r"banco", r"database", r"db", r"schema", r"migration", r"sql",
                    r"firestore", r"supabase", r"tabela", r"query", r"cache")),
    ("teste",    _p(r"teste", r"testes", r"test", r"tests", r"cobertura",
                    r"coverage", r"suite", r"e2e", r"unit")),
    ("docs",     _p(r"documenta[çc][ãa]o", r"docs", r"readme", r"manual",
                    r"changelog", r"coment[áa]rio")),
    ("infra",    _p(r"deploy", r"ci", r"pipeline", r"docker", r"vercel", r"github "
                    r"actions", r"dns", r"dom[íi]nio", r"servidor", r"cloudflare",
                    r"homebrew", r"instalador", r"install")),
    ("mobile",   _p(r"ios", r"android", r"app de celular", r"swift", r"xcode",
                    r"simulador", r"react native", r"expo")),
    ("i18n",     _p(r"idioma", r"tradu[çc][ãa]o", r"traduz", r"i18n", r"ingl[êe]s",
                    r"portugu[êe]s", r"locale", r"language")),
)

# Emenda: ele encomenda várias coisas numa frase só, e a emenda é o sinal.
EMENDA = _p(
    r"e tbm", r"e tamb[ée]m", r"e outra", r"e ai", r"e dps", r"e depois",
    r"alem disso", r"al[ée]m disso", r"junto", r"de quebra", r"aproveita",
    r"aproveitando", r"ja que", r"j[áa] que", r"and also", r"also", r"plus",
    r"while you.?re at it", r"on top of that",
)

# Pedido preciso é barato: quem já disse o arquivo e a linha tirou a busca do meio.
PRECISAO = re.compile(
    r"[\w./-]+\.(?:py|js|jsx|ts|tsx|swift|sh|rb|go|rs|c|h|cpp|java|kt|json|ya?ml|"
    r"toml|md|html|css|scss|sql|plist|xml|txt)\b"
    r"|:[0-9]{1,5}\b"
    r"|\blinha [0-9]+|\bline [0-9]+"
    r"|\b(?:fun[çc][ãa]o|function|metodo|m[ée]todo|method|classe|class|"
    r"componente|component|variavel|vari[áa]vel)\s+"
    # O trecho do camelCase precisa ignorar o IGNORECASE do padrão inteiro:
    # com ele ligado, [A-Z] casa minúscula, e "funcao la" passava por símbolo —
    # dando desconto de precisão justamente ao pedido que não diz onde é.
    r"[`\"']?(?=\w*[_.(]|(?-i:\w*[a-z]\w*[A-Z]|[A-Z]\w))\w+"
    r"|`[^`]{2,60}`",
    re.IGNORECASE)

# Pergunta factual: resposta curta, sem obra.
CONSULTA = _p(
    r"kd", r"cad[êe]", r"onde", r"onde ta", r"onde est[áa]", r"qual", r"quais",
    r"quanto", r"quantos", r"quantas", r"quando", r"quem", r"o que (?:e|é|eh)",
    r"ja", r"j[áa]", r"terminou", r"acabou", r"deu certo", r"foi", r"funcionou",
    r"status", r"como ta", r"como est[áa]",
    r"where", r"which", r"how many", r"how much", r"when", r"who", r"what is",
    r"did it", r"is it done", r"done yet",
)
