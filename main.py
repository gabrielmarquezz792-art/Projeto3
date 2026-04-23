from steampy import SteamPy, ARQ_DATASET


def menu():
    plataforma = SteamPy()

    # ── Carregamento inicial ───────────────────
    print('╔══════════════════════════════════════╗')
    print('║           SteamPy  v1.0              ║')
    print('╚══════════════════════════════════════╝')
    plataforma.carregar_jogos(ARQ_DATASET)
    plataforma.carregar_backlog()
    plataforma.carregar_recentes()
    plataforma.carregar_historico()

    opcoes = {
        '1':  'Carregar / recarregar catálogo',
        '2':  'Listar jogos',
        '3':  'Buscar jogo por nome',
        '4':  'Filtrar por gênero',
        '5':  'Filtrar por console',
        '6':  'Filtrar por nota mínima',
        '7':  'Filtrar por vendas mínimas',
        '8':  'Filtrar por publisher',
        '9':  'Ordenar catálogo',
        '10': 'Adicionar jogo ao backlog',
        '11': 'Ver backlog',
        '12': 'Jogar próximo do backlog',
        '13': 'Ver jogos recentes',
        '14': 'Retomar último jogo',
        '15': 'Registrar tempo de jogo (avulso)',
        '16': 'Ver histórico completo',
        '17': 'Ver recomendações',
        '18': 'Ver ranking pessoal',
        '19': 'Ver dashboard',
        '20': 'Salvar backlog',
        '0':  'Sair',
    }

    while True:
        print('\n' + '─'*42)
        print('  MENU PRINCIPAL')
        print('─'*42)
        for k, v in opcoes.items():
            print(f'  {k:>2}. {v}')
        print('─'*42)

        escolha = input('Opção: ').strip()

        # ── 1 ─ Carregar catálogo ──────────────
        if escolha == '1':
            plataforma.carregar_jogos(ARQ_DATASET)

        # ── 2 ─ Listar jogos ──────────────────
        elif escolha == '2':
            plataforma.listar_jogos()

        # ── 3 ─ Busca por nome ────────────────
        elif escolha == '3':
            termo = input('Nome (ou parte): ')
            plataforma.buscar_jogo_por_nome(termo)

        # ── 4 ─ Filtrar por gênero ────────────
        elif escolha == '4':
            genero = input('Gênero: ')
            plataforma.filtrar_por_genero(genero)

        # ── 5 ─ Filtrar por console ───────────
        elif escolha == '5':
            console = input('Console: ')
            plataforma.filtrar_por_console(console)

        # ── 6 ─ Filtrar por nota ──────────────
        elif escolha == '6':
            try:
                nota = float(input('Nota mínima (0-10): '))
                plataforma.filtrar_por_nota(nota)
            except ValueError:
                print('Valor inválido.')

        # ── 7 ─ Filtrar por vendas ────────────
        elif escolha == '7':
            try:
                vendas = float(input('Vendas mínimas (em milhões): '))
                plataforma.filtrar_por_vendas(vendas)
            except ValueError:
                print('Valor inválido.')

        # ── 8 ─ Filtrar por publisher ─────────
        elif escolha == '8':
            pub = input('Publisher: ')
            plataforma.filtrar_por_publisher(pub)

        # ── 9 ─ Ordenar catálogo ──────────────
        elif escolha == '9':
            print('  1. Título\n  2. Nota\n  3. Vendas\n  4. Data\n  5. Console\n  6. Gênero')
            crit = input('Critério: ')
            plataforma.ordenar_jogos(crit)

        # ── 10 ─ Adicionar ao backlog ──────────
        elif escolha == '10':
            print('Busque o jogo que deseja adicionar:')
            termo = input('Nome (ou parte): ')
            resultado = plataforma.buscar_jogo_por_nome(termo)
            if resultado:
                jogo = plataforma._selecionar_jogo(resultado)
                if jogo:
                    plataforma.adicionar_ao_backlog(jogo)

        # ── 11 ─ Ver backlog ───────────────────
        elif escolha == '11':
            plataforma.mostrar_backlog()

        # ── 12 ─ Jogar próximo do backlog ──────
        elif escolha == '12':
            plataforma.jogar_proximo()

        # ── 13 ─ Ver recentes ──────────────────
        elif escolha == '13':
            plataforma.mostrar_recentes()

        # ── 14 ─ Retomar último jogo ───────────
        elif escolha == '14':
            plataforma.retomar_ultimo_jogo()

        # ── 15 ─ Registrar sessão avulsa ───────
        elif escolha == '15':
            print('Busque o jogo que jogou:')
            termo = input('Nome (ou parte): ')
            resultado = plataforma.buscar_jogo_por_nome(termo)
            if resultado:
                jogo = plataforma._selecionar_jogo(resultado)
                if jogo:
                    try:
                        tempo = float(input(f'Horas jogadas em "{jogo.titulo}": '))
                        plataforma.registrar_sessao(jogo, tempo)
                    except ValueError:
                        print('Valor inválido.')

        # ── 16 ─ Histórico completo ────────────
        elif escolha == '16':
            plataforma.mostrar_historico()

        # ── 17 ─ Recomendações ─────────────────
        elif escolha == '17':
            plataforma.recomendar_jogos()

        # ── 18 ─ Ranking pessoal ───────────────
        elif escolha == '18':
            plataforma.gerar_ranking_pessoal()

        # ── 19 ─ Dashboard ─────────────────────
        elif escolha == '19':
            plataforma.exibir_dashboard()

        # ── 20 ─ Salvar backlog ────────────────
        elif escolha == '20':
            plataforma.salvar_backlog()

        # ── 0 ─ Sair ───────────────────────────
        elif escolha == '0':
            plataforma.salvar_backlog()
            plataforma.salvar_recentes()
            plataforma.salvar_historico()
            print('\nDados salvos. Até logo!')
            break

        else:
            print('Opção inválida. Tente novamente.')


if __name__ == '__main__':
    menu()