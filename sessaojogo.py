from datetime import datetime


class SessaoJogo:
    _contador = 1

    def __init__(self, jogo, tempo_jogado):
        self.jogo               = jogo
        self.tempo_jogado       = tempo_jogado          # horas nesta sessão
        self.data_sessao        = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.numero_sessao      = SessaoJogo._contador
        SessaoJogo._contador   += 1
        self.tempo_total        = 0.0                   # preenchido por SteamPy
        self.percentual_simulado = 0.0
        self.status             = 'iniciado'

    def definir_status(self, tempo_total):
        self.tempo_total = tempo_total
        if tempo_total >= 20:
            self.status = 'concluido_simbolicamente'
            self.percentual_simulado = 100.0
        elif tempo_total >= 10:
            self.status = 'muito_jogado'
            self.percentual_simulado = min(tempo_total * 4, 99.0)
        elif tempo_total >= 2:
            self.status = 'em_andamento'
            self.percentual_simulado = min(tempo_total * 8, 75.0)
        else:
            self.status = 'iniciado'
            self.percentual_simulado = min(tempo_total * 10, 15.0)

    def exibir(self):
        print(f'  Sessão #{self.numero_sessao} | {self.data_sessao} | '
              f'{self.jogo.titulo} | +{self.tempo_jogado}h | '
              f'Total: {self.tempo_total}h | Status: {self.status}')

    def linha_historico(self):
        return (f'{self.jogo.titulo};{self.tempo_jogado};'
                f'{self.tempo_total};{self.status}')