import pygame
import random
import math
import sys

pygame.init()

# Esconde o ponteiro do mouse para desenhar a mira própria
pygame.mouse.set_visible(False)

# Pega o tamanho total da tela do computador
info_tela = pygame.display.Info()
LARGURA, ALTURA = info_tela.current_w, info_tela.current_h

# Abre o jogo ocupando a tela toda
tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
pygame.display.set_caption("InfStar")
relogio = pygame.time.Clock()

fonte = pygame.font.SysFont("Consolas", 22, bold=True)
fonte_pequena = pygame.font.SysFont("Consolas", 16, bold=True)
fonte_grande = pygame.font.SysFont("Consolas", 48, bold=True)

# Gera as estrelas no fundo: [x, y, brilho]
estrelas = [[random.randint(0, LARGURA), random.randint(0, ALTURA), random.randint(1, 3)] for _ in range(150)]


class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Cria a imagem base da nave virada para cima
        self.imagem_base = pygame.Surface((48, 48), pygame.SRCALPHA)
        
        # Desenha o formato da nave
        pygame.draw.polygon(self.imagem_base, (0, 180, 255), [(24, 2), (0, 42), (48, 42)])
        pygame.draw.polygon(self.imagem_base, (220, 235, 255), [(24, 2), (14, 46), (34, 46)])
        pygame.draw.polygon(self.imagem_base, (0, 255, 200), [(6, 38), (0, 46), (12, 42)])
        pygame.draw.polygon(self.imagem_base, (0, 255, 200), [(42, 38), (48, 46), (36, 42)])
        pygame.draw.ellipse(self.imagem_base, (255, 215, 0), (18, 14, 12, 18))
        pygame.draw.polygon(self.imagem_base, (255, 100, 0), [(18, 44), (24, 48), (30, 44)])

        self.image = self.imagem_base
        self.rect = self.image.get_rect(center=(LARGURA // 2, ALTURA // 2))
        
        # Guardamos a posição exata em float para movimentação suave
        self.x, self.y = float(self.rect.centerx), float(self.rect.centery)
        
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.angulo = 0.0
        self.vidas = 3
        self.moedas = 0
        self.espera_tiro = 0
        self.cadencia = 12

    def update(self):
        if self.espera_tiro > 0:
            self.espera_tiro -= 1

        # Mira na direção do mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        diff_x = mouse_x - self.x
        diff_y = mouse_y - self.y
        distancia = math.hypot(diff_x, diff_y)

        # Só gira se o mouse estiver a uma distância mínima (evita tremer)
        if distancia > 10:
            self.angulo = math.degrees(math.atan2(-diff_y, diff_x)) - 90

        # Controles de movimento WASD e Setas
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.vel_x -= 0.4
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.vel_x += 0.4
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            self.vel_y -= 0.4
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            self.vel_y += 0.4

        # Teleporta nas bordas da tela e aplica atrito de parada (0.94)
        self.x = (self.x + self.vel_x) % LARGURA
        self.y = (self.y + self.vel_y) % ALTURA
        self.vel_x *= 0.94
        self.vel_y *= 0.94

        # Rotaciona a nave sem deslocar o centro
        self.image = pygame.transform.rotate(self.imagem_base, self.angulo)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))


class Inimigo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (220, 40, 40), [(20, 38), (0, 8), (40, 8)])
        pygame.draw.polygon(self.image, (80, 20, 60), [(20, 38), (12, 0), (28, 0)])
        pygame.draw.circle(self.image, (255, 215, 0), (20, 16), 6)
        pygame.draw.circle(self.image, (255, 50, 50), (20, 16), 3)

        # Nasce fora das bordas da tela
        if random.random() < 0.5:
            self.x = float(random.choice([-20, LARGURA + 20]))
            self.y = float(random.randint(0, ALTURA))
        else:
            self.x = float(random.randint(0, LARGURA))
            self.y = float(random.choice([-20, ALTURA + 20]))

        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        self.velocidade = random.uniform(1.8, 3.2)

    def update(self, pos_x, pos_y):
        # Persegue as coordenadas do jogador
        diff_x = pos_x - self.x
        diff_y = pos_y - self.y
        distancia = math.hypot(diff_x, diff_y)
        if distancia > 0:
            self.x += (diff_x / distancia) * self.velocidade
            self.y += (diff_y / distancia) * self.velocidade
        self.rect.center = (int(self.x), int(self.y))


class Tiro(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, angulo):
        super().__init__()
        radiano = math.radians(angulo - 90)
        
        # Calcula a saída na ponta do bico da nave (24px do centro)
        tiro_x = pos_x + math.cos(radiano) * 24
        tiro_y = pos_y + math.sin(radiano) * 24

        imagem_tiro = pygame.Surface((4, 16), pygame.SRCALPHA)
        imagem_tiro.fill((40, 240, 120))
        self.image = pygame.transform.rotate(imagem_tiro, angulo)
        self.rect = self.image.get_rect(center=(tiro_x, tiro_y))

        self.vel_x = math.cos(radiano) * 15
        self.vel_y = math.sin(radiano) * 15
        self.x, self.y = float(tiro_x), float(tiro_y)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.center = (int(self.x), int(self.y))
        
        # Apaga se sair da tela
        if not (0 <= self.x <= LARGURA and 0 <= self.y <= ALTURA):
            self.kill()


class Moeda(pygame.sprite.Sprite):
    def __init__(self, posicao):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 215, 0), (6, 6), 6)
        self.rect = self.image.get_rect(center=posicao)
        self.tempo_vida = 450  # Some após 7.5 segundos se ninguém pegar

    def update(self):
        self.tempo_vida -= 1
        if self.tempo_vida <= 0:
            self.kill()


def desenhar_mira(superficie, x, y):
    pygame.draw.circle(superficie, (0, 255, 200), (x, y), 10, 1)
    pygame.draw.line(superficie, (0, 255, 200), (x - 14, y), (x - 4, y), 2)
    pygame.draw.line(superficie, (0, 255, 200), (x + 4, y), (x + 14, y), 2)
    pygame.draw.line(superficie, (0, 255, 200), (x, y - 14), (x, y - 4), 2)
    pygame.draw.line(superficie, (0, 255, 200), (x, y + 4), (x, y + 14), 2)


# Grupos de elementos
todas_sprites = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
tiros = pygame.sprite.Group()
moedas = pygame.sprite.Group()

jogador = Jogador()
todas_sprites.add(jogador)

for _ in range(8):
    inimigo = Inimigo()
    todas_sprites.add(inimigo)
    inimigos.add(inimigo)

pontos = 0
fim_de_jogo = False
na_loja = False

custo_cadencia = 8
custo_vida = 12

# Loop do Jogo
while True:
    relogio.tick(60)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            # Reinicia o jogo no Game Over
            if evento.key == pygame.K_r and fim_de_jogo:
                todas_sprites.empty()
                inimigos.empty()
                tiros.empty()
                moedas.empty()
                jogador = Jogador()
                todas_sprites.add(jogador)
                for _ in range(8):
                    inimigo = Inimigo()
                    todas_sprites.add(inimigo)
                    inimigos.add(inimigo)
                pontos = 0
                custo_cadencia, custo_vida = 8, 12
                fim_de_jogo = False

            elif evento.key == pygame.K_b and not fim_de_jogo:
                na_loja = not na_loja

            # Compras da loja
            if na_loja:
                if evento.key == pygame.K_1 and jogador.moedas >= custo_cadencia and jogador.cadencia > 4:
                    jogador.moedas -= custo_cadencia
                    jogador.cadencia -= 2
                    custo_cadencia += 6
                elif evento.key == pygame.K_2 and jogador.moedas >= custo_vida:
                    jogador.moedas -= custo_vida
                    jogador.vidas += 1
                    custo_vida += 10

    # Clique do mouse ou Espaço para atirar
    botoes_mouse = pygame.mouse.get_pressed()
    teclas = pygame.key.get_pressed()
    if (botoes_mouse[0] or teclas[pygame.K_SPACE]) and not fim_de_jogo and not na_loja and jogador.espera_tiro == 0:
        novo_tiro = Tiro(jogador.x, jogador.y, jogador.angulo)
        todas_sprites.add(novo_tiro)
        tiros.add(novo_tiro)
        jogador.espera_tiro = jogador.cadencia

    if not fim_de_jogo and not na_loja:
        jogador.update()
        tiros.update()
        moedas.update()
        for inimigo in inimigos:
            inimigo.update(jogador.x, jogador.y)

        # Inimigos contínuos baseados na pontuação
        if len(inimigos) < 10 + (pontos // 800) and random.random() < 0.025:
            novo_inimigo = Inimigo()
            todas_sprites.add(novo_inimigo)
            inimigos.add(novo_inimigo)

        # Tiro atinge o Inimigo: gera moeda
        acertos = pygame.sprite.groupcollide(inimigos, tiros, True, True)
        for inimigo_destruido in acertos:
            pontos += 100
            nova_moeda = Moeda(inimigo_destruido.rect.center)
            todas_sprites.add(nova_moeda)
            moedas.add(nova_moeda)

        # Jogador pega a moeda
        for _ in pygame.sprite.spritecollide(jogador, moedas, True):
            jogador.moedas += 1

        # Inimigo atinge o Jogador
        if pygame.sprite.spritecollide(jogador, inimigos, True):
            jogador.vidas -= 1
            if jogador.vidas <= 0:
                fim_de_jogo = True

    # Renderização da tela
    tela.fill((10, 10, 20))

    # Desenha o fundo estrelado
    for estrela in estrelas:
        tela.set_at((estrela[0], estrela[1]), (200, 200, 200) if estrela[2] == 1 else (100, 100, 100))

    todas_sprites.draw(tela)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    desenhar_mira(tela, mouse_x, mouse_y)

    # Interface HUD
    tela.blit(fonte.render(f"PONTOS: {pontos}", True, (255, 255, 255)), (20, 20))
    tela.blit(fonte.render(f"MOEDAS: {jogador.moedas}", True, (255, 215, 0)), (20, 50))
    tela.blit(fonte.render(f"VIDAS: {'♥ ' * jogador.vidas}", True, (240, 60, 60)), (LARGURA - 200, 20))
    tela.blit(fonte.render("[B] LOJA", True, (0, 220, 255)), (LARGURA - 140, 50))
    tela.blit(fonte_pequena.render("CONTROLES: [WASD] Mover | [MOUSE] Mirar | [CLIQUE ESQ. / ESPAÇO] Atirar | [ESC] Sair", True, (160, 160, 180)), (LARGURA - 730, 80))

    # Tela da Loja
    if na_loja:
        fundo_escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        fundo_escuro.fill((0, 0, 0, 210))
        tela.blit(fundo_escuro, (0, 0))

        tela.blit(fonte_grande.render("LOJA", True, (255, 215, 0)), (LARGURA // 2 - 60, ALTURA // 2 - 120))
        tela.blit(fonte.render(f"[1] Cadência de Tiro - {custo_cadencia} moedas", True, (255, 255, 255)), (LARGURA // 2 - 180, ALTURA // 2 - 20))
        tela.blit(fonte.render(f"[2] +1 Vida - {custo_vida} moedas", True, (255, 255, 255)), (LARGURA // 2 - 180, ALTURA // 2 + 30))
        tela.blit(fonte.render("Pressione [B] para fechar", True, (150, 150, 150)), (LARGURA // 2 - 140, ALTURA // 2 + 120))

    # Tela de Game Over
    if fim_de_jogo:
        tela.blit(fonte_grande.render("GAME OVER", True, (240, 60, 60)), (LARGURA // 2 - 130, ALTURA // 2 - 40))
        tela.blit(fonte.render("Pressione [R] para reiniciar", True, (255, 255, 255)), (LARGURA // 2 - 160, ALTURA // 2 + 30))

    pygame.display.flip()