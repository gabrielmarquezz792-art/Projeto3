import os
from datetime import datetime

from jogo        import Jogo
from filabacklog import FilaBacklog
from pilharecentes import PilhaRecentes
from sessaojogo  import SessaoJogo


# ─────────────────────────────────────────────
#  Arquivos de persistência
# ─────────────────────────────────────────────
ARQ_DATASET   = 'dataset.csv'
ARQ_BACKLOG   = 'backlog.txt'
ARQ_HISTORICO = 'historico_jogo.txt'
ARQ_RECENTES  = 'recentes.txt'


class SteamPy:

    def __init__(self):
        self.catalogo   = []          # lista de Jogo
        self.indice     = {}          # dict  id -> Jogo
        self.backlog    = FilaBacklog()
        self.recentes   = PilhaRecentes(limite=20)
        self.historico  = []          # lista de SessaoJogo
        self.tempo_por_jogo = {}      # dict  id -> float (horas acumuladas)
        self.recomendacoes  = []      # lista de Jogo (última geração)

    # ══════════════════════════════════════════
    #  PARTE 1 – CARREGAMENTO DO CATÁLOGO
    # ══════════════════════════════════════════

    def carregar_jogos(self, nome_arquivo=ARQ_DATASET):
        self.catalogo.clear()
        self.indice.clear()
        carregados = 0
        erros = 0

        try:
            with open(nome_arquivo, encoding='utf-8') as f:
                linhas = f.readlines()
        except FileNotFoundError:
            print(f'[ERRO] Arquivo "{nome_arquivo}" não encontrado.')
            return

        for numero, linha in enumerate(linhas[1:], start=2):   # pula cabeçalho
            linha = linha.strip()
            if not linha:
                continue
            partes = linha.split(',')
            if len(partes) < 13:
                erros += 1
                continue

            try:
                id_jogo      = numero - 1          # índice sequencial como id
                titulo       = partes[1].strip()
                console      = partes[2].strip()
                genero       = partes[3].strip()
                publisher    = partes[4].strip()
                developer    = partes[5].strip()
                critic_score = float(partes[6]) if partes[6].strip() else 0.0
                total_sales  = float(partes[7]) if partes[7].strip() else 0.0
                na_sales     = float(partes[8]) if partes[8].strip() else 0.0
                jp_sales     = float(partes[9]) if partes[9].strip() else 0.0
                pal_sales    = float(partes[10]) if partes[10].strip() else 0.0
                other_sales  = float(partes[11]) if partes[11].strip() else 0.0
                release_date = partes[12].strip()
            except (ValueError, IndexError):
                erros += 1
                continue

            jogo = Jogo(id_jogo, titulo, console, genero, publisher, developer,
                        critic_score, total_sales, na_sales, jp_sales,
                        pal_sales, other_sales, release_date)
            self.catalogo.append(jogo)
            self.indice[id_jogo] = jogo
            carregados += 1

        print(f'[OK] {carregados} jogos carregados  |  {erros} linha(s) ignorada(s).')

    # ══════════════════════════════════════════
    #  PARTE 2 – BUSCA, FILTROS E ORDENAÇÃO
    # ══════════════════════════════════════════

    def listar_jogos(self, jogos=None, limite=50):
        lista = jogos if jogos is not None else self.catalogo
        if not lista:
            print('Nenhum jogo encontrado.')
            return
        print(f'\n{"#":>5}  {"Título":<45} {"Console":<8} {"Gênero":<15} {"Nota":>5} {"Vendas":>7}')
        print('─' * 90)
        for i, j in enumerate(lista[:limite], 1):
            nota   = f'{j.critic_score:.1f}' if j.critic_score else '  -'
            vendas = f'{j.total_sales:.2f}M'
            print(f'{i:>5}  {j.titulo:<45} {j.console:<8} {j.genero:<15} {nota:>5} {vendas:>7}')
        if len(lista) > limite:
            print(f'  ... e mais {len(lista) - limite} jogo(s). Refine a busca para ver mais.')

    def buscar_jogo_por_nome(self, termo):
        termo = termo.lower()
        resultado = [j for j in self.catalogo if termo in j.titulo.lower()]
        print(f'\n{len(resultado)} resultado(s) para "{termo}":')
        self.listar_jogos(resultado)
        return resultado

    def filtrar_por_genero(self, genero):
        resultado = [j for j in self.catalogo if j.genero.lower() == genero.lower()]
        print(f'\n{len(resultado)} jogo(s) do gênero "{genero}":')
        self.listar_jogos(resultado)
        return resultado

    def filtrar_por_console(self, console):
        resultado = [j for j in self.catalogo if j.console.lower() == console.lower()]
        print(f'\n{len(resultado)} jogo(s) para "{console}":')
        self.listar_jogos(resultado)
        return resultado

    def filtrar_por_nota(self, nota_minima):
        resultado = [j for j in self.catalogo if j.critic_score >= nota_minima]
        print(f'\n{len(resultado)} jogo(s) com nota ≥ {nota_minima}:')
        self.listar_jogos(resultado)
        return resultado

    def filtrar_por_vendas(self, vendas_minimas):
        resultado = [j for j in self.catalogo if j.total_sales >= vendas_minimas]
        print(f'\n{len(resultado)} jogo(s) com vendas ≥ {vendas_minimas}M:')
        self.listar_jogos(resultado)
        return resultado

    def filtrar_por_publisher(self, publisher):
        resultado = [j for j in self.catalogo if j.publisher.lower() == publisher.lower()]
        print(f'\n{len(resultado)} jogo(s) da publisher "{publisher}":')
        self.listar_jogos(resultado)
        return resultado

    def ordenar_jogos(self, criterio):
        criterios = {
            '1': ('titulo',       False, 'Título (A-Z)'),
            '2': ('critic_score', True,  'Nota (maior primeiro)'),
            '3': ('total_sales',  True,  'Vendas totais (maior primeiro)'),
            '4': ('release_date', False, 'Data de lançamento'),
            '5': ('console',      False, 'Console (A-Z)'),
            '6': ('genero',       False, 'Gênero (A-Z)'),
        }
        if criterio not in criterios:
            print('Critério inválido.')
            return
        attr, rev, nome = criterios[criterio]
        self.catalogo.sort(key=lambda j: getattr(j, attr) or '', reverse=rev)
        print(f'[OK] Catálogo ordenado por: {nome}')

    # ══════════════════════════════════════════
    #  PARTE 3 – BACKLOG (FILA)
    # ══════════════════════════════════════════

    def adicionar_ao_backlog(self, jogo):
        # Verifica duplicata
        for j in self.backlog.dados:
            if j.id == jogo.id:
                print(f'"{jogo.titulo}" já está no backlog.')
                return
        self.backlog.enqueue(jogo)
        print(f'[OK] "{jogo.titulo}" adicionado ao backlog.')

    def mostrar_backlog(self):
        self.backlog.mostrar()

    def jogar_proximo(self):
        jogo = self.backlog.dequeue()
        if not jogo:
            print('Backlog vazio!')
            return None
        print(f'\n▶  Iniciando: {jogo.titulo}  [{jogo.console}]')
        self._iniciar_sessao(jogo)
        return jogo

    def salvar_backlog(self, arquivo=ARQ_BACKLOG):
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write('id;titulo;console\n')
            for jogo in self.backlog.dados:
                f.write(jogo.linha_backlog() + '\n')
        print(f'[OK] Backlog salvo em "{arquivo}".')

    def carregar_backlog(self, arquivo=ARQ_BACKLOG):
        if not os.path.exists(arquivo):
            return
        with open(arquivo, encoding='utf-8') as f:
            linhas = f.readlines()
        for linha in linhas[1:]:
            partes = linha.strip().split(';')
            if len(partes) < 1:
                continue
            try:
                id_jogo = int(partes[0])
                if id_jogo in self.indice:
                    self.backlog.enqueue(self.indice[id_jogo])
            except (ValueError, IndexError):
                continue
        print(f'[OK] Backlog carregado de "{arquivo}" ({self.backlog.tamanho()} jogo(s)).')

    # ══════════════════════════════════════════
    #  PARTE 4 – RECENTES (PILHA)
    # ══════════════════════════════════════════

    def mostrar_recentes(self):
        self.recentes.mostrar()

    def retomar_ultimo_jogo(self):
        jogo = self.recentes.topo()
        if not jogo:
            print('Nenhum jogo recente.')
            return
        print(f'\n▶  Retomando: {jogo.titulo}  [{jogo.console}]')
        self._iniciar_sessao(jogo)

    def salvar_recentes(self, arquivo=ARQ_RECENTES):
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write('id;titulo;console\n')
            for jogo in reversed(self.recentes.dados):   # mais recente primeiro
                f.write(jogo.linha_recentes() + '\n')
        print(f'[OK] Recentes salvos em "{arquivo}".')

    def carregar_recentes(self, arquivo=ARQ_RECENTES):
        if not os.path.exists(arquivo):
            return
        with open(arquivo, encoding='utf-8') as f:
            linhas = f.readlines()
        # inverte para que o push reconstrua a pilha na ordem correta
        for linha in reversed(linhas[1:]):
            partes = linha.strip().split(';')
            if len(partes) < 1:
                continue
            try:
                id_jogo = int(partes[0])
                if id_jogo in self.indice:
                    self.recentes.push(self.indice[id_jogo])
            except (ValueError, IndexError):
                continue
        print(f'[OK] Recentes carregados ({self.recentes.tamanho()} jogo(s)).')

    # ══════════════════════════════════════════
    #  PARTE 5 – SIMULAÇÃO DE TEMPO DE JOGO
    # ══════════════════════════════════════════

    def _iniciar_sessao(self, jogo):
        """Registra uma nova sessão de jogo interativamente."""
        try:
            tempo = float(input(f'Quantas horas você jogou "{jogo.titulo}" nesta sessão? '))
        except ValueError:
            tempo = 0.0
        if tempo <= 0:
            print('Sessão não registrada (tempo inválido).')
            return
        self.registrar_sessao(jogo, tempo)

    def registrar_sessao(self, jogo, tempo):
        sessao = SessaoJogo(jogo, tempo)

        # Acumula tempo total do jogo
        self.tempo_por_jogo[jogo.id] = self.tempo_por_jogo.get(jogo.id, 0.0) + tempo
        total = self.tempo_por_jogo[jogo.id]

        sessao.definir_status(total)
        self.historico.append(sessao)
        self.recentes.push(jogo)

        print(f'\n[OK] Sessão registrada! Total em "{jogo.titulo}": {total:.1f}h  |  Status: {sessao.status}')
        self.salvar_historico()
        self.salvar_recentes()

    # ══════════════════════════════════════════
    #  PARTE 6 – HISTÓRICO COMPLETO
    # ══════════════════════════════════════════

    def mostrar_historico(self):
        if not self.historico:
            print('Nenhuma sessão registrada ainda.')
            return
        print(f'\n{"─"*80}')
        print(f'  HISTÓRICO DE SESSÕES ({len(self.historico)} sessão(ões))')
        print(f'{"─"*80}')
        for s in self.historico:
            s.exibir()

    def salvar_historico(self, arquivo=ARQ_HISTORICO):
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write('titulo;tempo_sessao;tempo_total;status\n')
            for s in self.historico:
                f.write(s.linha_historico() + '\n')

    def carregar_historico(self, arquivo=ARQ_HISTORICO):
        if not os.path.exists(arquivo):
            return
        with open(arquivo, encoding='utf-8') as f:
            linhas = f.readlines()
        for linha in linhas[1:]:
            partes = linha.strip().split(';')
            if len(partes) < 4:
                continue
            titulo, t_sess, t_total, status = partes[0], partes[1], partes[2], partes[3]
            # Reconstrói o tempo acumulado por título (aproximação via busca)
            jogo = next((j for j in self.catalogo if j.titulo == titulo), None)
            if jogo:
                try:
                    self.tempo_por_jogo[jogo.id] = float(t_total)
                except ValueError:
                    pass
                # Recria sessão resumida (sem interação)
                s = SessaoJogo(jogo, float(t_sess) if t_sess else 0.0)
                s.tempo_total = float(t_total) if t_total else 0.0
                s.status = status
                self.historico.append(s)
        print(f'[OK] Histórico carregado ({len(self.historico)} sessão(ões)).')

    # ══════════════════════════════════════════
    #  PARTE 7 – RECOMENDAÇÕES
    # ══════════════════════════════════════════

    def recomendar_jogos(self, quantidade=10):
        if not self.historico:
            print('Jogue pelo menos um jogo para receber recomendações.')
            return []

        # ── Perfil do usuário ──
        contagem_genero  = {}
        contagem_console = {}
        notas_jogadas    = []
        ids_jogados      = set(self.tempo_por_jogo.keys())
        ids_backlog      = {j.id for j in self.backlog.dados}
        ids_muito_jogados = {jid for jid, t in self.tempo_por_jogo.items() if t >= 10}

        for s in self.historico:
            g = s.jogo.genero
            c = s.jogo.console
            contagem_genero[g]  = contagem_genero.get(g, 0)  + 1
            contagem_console[c] = contagem_console.get(c, 0) + 1
            if s.jogo.critic_score:
                notas_jogadas.append(s.jogo.critic_score)

        genero_fav  = max(contagem_genero,  key=contagem_genero.get)  if contagem_genero  else None
        console_fav = max(contagem_console, key=contagem_console.get) if contagem_console else None
        nota_media  = sum(notas_jogadas) / len(notas_jogadas) if notas_jogadas else 0

        print(f'\n  Critérios usados:')
        print(f'    • Gênero favorito  : {genero_fav}')
        print(f'    • Console favorito : {console_fav}')
        print(f'    • Nota média jogada: {nota_media:.1f}')

        # ── Pontuação de candidatos ──
        candidatos = []
        for jogo in self.catalogo:
            if jogo.id in ids_muito_jogados: continue
            if jogo.id in ids_backlog:       continue

            pontos = 0
            if genero_fav  and jogo.genero  == genero_fav:  pontos += 3
            if console_fav and jogo.console == console_fav: pontos += 2
            if nota_media  and jogo.critic_score >= nota_media: pontos += 2
            if jogo.total_sales >= 1.0:                      pontos += 1

            if pontos >= 3:
                candidatos.append((pontos, jogo))

        candidatos.sort(key=lambda x: (-x[0], -x[1].critic_score))
        self.recomendacoes = [j for _, j in candidatos[:quantidade]]

        print(f'\n  {len(self.recomendacoes)} jogo(s) recomendado(s):')
        self.listar_jogos(self.recomendacoes)
        return self.recomendacoes

    # ══════════════════════════════════════════
    #  PARTE 8 – RANKING PESSOAL
    # ══════════════════════════════════════════

    def gerar_ranking_pessoal(self):
        if not self.tempo_por_jogo:
            print('Nenhum dado de jogo registrado ainda.')
            return

        print('\n' + '═'*60)
        print('  RANKING PESSOAL')
        print('═'*60)

        # 1) Jogos mais jogados (por tempo)
        print('\n  🏆 Jogos mais jogados (horas acumuladas):')
        ranking_jogos = sorted(
            [(self.indice[jid], t) for jid, t in self.tempo_por_jogo.items() if jid in self.indice],
            key=lambda x: -x[1]
        )
        for pos, (jogo, tempo) in enumerate(ranking_jogos[:10], 1):
            print(f'    {pos:>2}. {jogo.titulo:<40} {tempo:.1f}h')

        # 2) Gêneros mais jogados
        contagem_genero = {}
        for jid, t in self.tempo_por_jogo.items():
            if jid in self.indice:
                g = self.indice[jid].genero
                contagem_genero[g] = contagem_genero.get(g, 0.0) + t
        print('\n  🎮 Gêneros favoritos (horas totais):')
        for pos, (g, t) in enumerate(sorted(contagem_genero.items(), key=lambda x: -x[1])[:5], 1):
            print(f'    {pos}. {g:<20} {t:.1f}h')

        # 3) Consoles mais jogados
        contagem_console = {}
        for jid, t in self.tempo_por_jogo.items():
            if jid in self.indice:
                c = self.indice[jid].console
                contagem_console[c] = contagem_console.get(c, 0.0) + t
        print('\n  🖥  Consoles mais jogados (horas totais):')
        for pos, (c, t) in enumerate(sorted(contagem_console.items(), key=lambda x: -x[1])[:5], 1):
            print(f'    {pos}. {c:<10} {t:.1f}h')

        # 4) Top jogos por nota dentro do histórico
        jogados_com_nota = [(self.indice[jid], self.indice[jid].critic_score)
                            for jid in self.tempo_por_jogo if jid in self.indice
                            and self.indice[jid].critic_score > 0]
        jogados_com_nota.sort(key=lambda x: -x[1])
        print('\n  ⭐ Jogos com melhor nota que você jogou:')
        for pos, (jogo, nota) in enumerate(jogados_com_nota[:5], 1):
            print(f'    {pos}. {jogo.titulo:<40} nota {nota:.1f}')

    # ══════════════════════════════════════════
    #  PARTE 9 – DASHBOARD
    # ══════════════════════════════════════════

    def exibir_dashboard(self):
        print('\n' + '═'*60)
        print('  ⬛ STEAMPY DASHBOARD')
        print('═'*60)

        # Contadores de status
        status_count = {'iniciado': 0, 'em_andamento': 0,
                        'muito_jogado': 0, 'concluido_simbolicamente': 0}
        for s in self.historico:
            status_count[s.status] = status_count.get(s.status, 0) + 1

        tempo_total   = sum(self.tempo_por_jogo.values())
        total_sessoes = len(self.historico)
        media_sessao  = tempo_total / total_sessoes if total_sessoes else 0

        # Jogo mais jogado
        jogo_mais = None
        if self.tempo_por_jogo:
            jid_mais = max(self.tempo_por_jogo, key=self.tempo_por_jogo.get)
            jogo_mais = self.indice.get(jid_mais)

        # Gênero e console favoritos
        gen_count, con_count, notas = {}, {}, []
        for jid, t in self.tempo_por_jogo.items():
            if jid in self.indice:
                j = self.indice[jid]
                gen_count[j.genero]  = gen_count.get(j.genero, 0)  + t
                con_count[j.console] = con_count.get(j.console, 0) + t
                if j.critic_score: notas.append(j.critic_score)

        genero_fav  = max(gen_count,  key=gen_count.get)  if gen_count  else '-'
        console_fav = max(con_count,  key=con_count.get)  if con_count  else '-'
        nota_media  = sum(notas) / len(notas) if notas else 0

        # Jogo mais popular e melhor nota jogados
        jogados = [(self.indice[jid], self.tempo_por_jogo[jid])
                   for jid in self.tempo_por_jogo if jid in self.indice]
        jogo_popular  = max(jogados, key=lambda x: x[0].total_sales)[0]  if jogados else None
        jogo_melhor_nota = max(jogados, key=lambda x: x[0].critic_score)[0] if jogados else None

        dados = [
            ('Total de jogos no catálogo',          len(self.catalogo)),
            ('Total de jogos no backlog',            self.backlog.tamanho()),
            ('Total de jogos recentes',              self.recentes.tamanho()),
            ('Total de sessões jogadas',             total_sessoes),
            ('Tempo total jogado',                   f'{tempo_total:.1f}h'),
            ('Média de horas por sessão',            f'{media_sessao:.1f}h'),
            ('Jogo mais jogado',                     jogo_mais.titulo if jogo_mais else '-'),
            ('Gênero favorito',                      genero_fav),
            ('Console favorito',                     console_fav),
            ('Nota média dos jogos jogados',         f'{nota_media:.2f}'),
            ('Jogos iniciados',                      status_count.get('iniciado', 0)),
            ('Jogos em andamento',                   status_count.get('em_andamento', 0)),
            ('Jogos muito jogados',                  status_count.get('muito_jogado', 0)),
            ('Jogos concluídos simbolicamente',      status_count.get('concluido_simbolicamente', 0)),
            ('Recomendações disponíveis',            len(self.recomendacoes)),
            ('Jogo mais popular já jogado',          jogo_popular.titulo  if jogo_popular  else '-'),
            ('Jogo com melhor nota já jogado',       jogo_melhor_nota.titulo if jogo_melhor_nota else '-'),
        ]

        for chave, valor in dados:
            print(f'  {chave:<40} {str(valor):>15}')
        print('═'*60)

    # ══════════════════════════════════════════
    #  SELETOR INTERATIVO DE JOGO
    # ══════════════════════════════════════════

    def _selecionar_jogo(self, lista=None):
        """Exibe uma lista e pede ao usuário para escolher um jogo pelo número."""
        alvo = lista if lista is not None else self.catalogo
        if not alvo:
            print('Lista vazia.')
            return None
        self.listar_jogos(alvo)
        try:
            idx = int(input('\nDigite o número do jogo (0 para cancelar): '))
            if idx == 0:
                return None
            if 1 <= idx <= len(alvo):
                return alvo[idx - 1]
        except ValueError:
            pass
        print('Opção inválida.')
        return None