class Jogo:
    def __init__(self, id_jogo, titulo, console, genero, publisher, developer, critic_score, total_sales, na_sales, jp_sales, pal_sales, other_sales, release_date):
        self.id                    = id_jogo
        self.titulo                = titulo
        self.console               = console
        self.genero                = genero
        self.publisher             = publisher
        self.developer             = developer
        self.critic_score          = critic_score
        self.total_sales           = total_sales
        self.na_sales              = na_sales
        self.jp_sales              = jp_sales
        self.pal_sales             = pal_sales
        self.other_sales           = other_sales
        self.release_date          = release_date

    def exibir(self):
        print(f'{self.id}, {self.titulo}, {self.console}, {self.genero}, {self.publisher}, {self.developer}, {self.critic_score}, {self.total_sales}, {self.na_sales}, {self.jp_sales}, { self.pal_sales}, {self.other_sales}, {self.release_date}')
    
    def linha_backlog(self):
        return f'{self.id};{self.titulo};{self.console}'
    
    def linha_recentes(self):
        return f'{self.id};{self.titulo};{self.console}'
