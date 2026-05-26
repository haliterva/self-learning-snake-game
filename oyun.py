import pygame
import random
import sys

pygame.init()

# Renkler
SIYAH = (0, 0, 0)
BEYAZ = (255, 255, 255)
KIRMIZI = (220, 20, 60)
YESIL = (50, 205, 50)
KOYU_YESIL = (34, 139, 34)
MAVI = (70, 130, 180)
SARI = (255, 215, 0)

EKRAN_GENISLIK = 480
HUCRE_BOYUT = 20

GENISLIK = (EKRAN_GENISLIK // HUCRE_BOYUT) * HUCRE_BOYUT
YUKSEKLIK = (EKRAN_GENISLIK // HUCRE_BOYUT) * HUCRE_BOYUT

ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK + 60))
pygame.display.set_caption('Snake Oyunu')
saat = pygame.time.Clock()

font_buyuk = pygame.font.Font(None, 48)
font_orta = pygame.font.Font(None, 32)
font_kucuk = pygame.font.Font(None, 24)

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        baslangic_x = (GENISLIK // 2 // HUCRE_BOYUT) * HUCRE_BOYUT
        baslangic_y = (YUKSEKLIK // 2 // HUCRE_BOYUT) * HUCRE_BOYUT
        
        self.body = [
            [baslangic_x, baslangic_y],
            [baslangic_x - HUCRE_BOYUT, baslangic_y],
            [baslangic_x - 2 * HUCRE_BOYUT, baslangic_y]
        ]
        self.direction = 'RIGHT'
        self.next_direction = 'RIGHT'
        self.grow_pending = False
    
    def change_direction(self, yeni_yon):
        ters_yonler = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}
        if yeni_yon != ters_yonler[self.direction]:
            self.next_direction = yeni_yon
    
    def move(self):
        self.direction = self.next_direction
        bas = self.body[0].copy()
        
        if self.direction == 'UP':
            bas[1] -= HUCRE_BOYUT
        elif self.direction == 'DOWN':
            bas[1] += HUCRE_BOYUT
        elif self.direction == 'LEFT':
            bas[0] -= HUCRE_BOYUT
        elif self.direction == 'RIGHT':
            bas[0] += HUCRE_BOYUT
        
        self.body.insert(0, bas)
        
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False
    
    def grow(self):
        self.grow_pending = True
    
    def check_collision(self):
        bas = self.body[0]
        
        if (bas[0] < 0 or bas[0] >= GENISLIK or 
            bas[1] < 0 or bas[1] >= YUKSEKLIK):
            return True
        
        if bas in self.body[1:]:
            return True
        
        return False
    
    def draw(self, surface):
        for i, segment in enumerate(self.body):
            if i == 0:
                pygame.draw.rect(surface, KOYU_YESIL, 
                               (segment[0], segment[1], HUCRE_BOYUT, HUCRE_BOYUT))
                pygame.draw.rect(surface, YESIL, 
                               (segment[0] + 2, segment[1] + 2, 
                                HUCRE_BOYUT - 4, HUCRE_BOYUT - 4))
                
                eye_positions = {
                    'RIGHT': [(14, 6), (14, 14)],
                    'LEFT': [(6, 6), (6, 14)],
                    'UP': [(6, 6), (14, 6)],
                    'DOWN': [(6, 14), (14, 14)]
                }
                
                for x, y in eye_positions[self.direction]:
                    pygame.draw.circle(surface, SIYAH, (segment[0] + x, segment[1] + y), 2)
            else:
                pygame.draw.rect(surface, KOYU_YESIL, 
                               (segment[0], segment[1], HUCRE_BOYUT, HUCRE_BOYUT))
                pygame.draw.rect(surface, YESIL, 
                               (segment[0] + 1, segment[1] + 1, 
                                HUCRE_BOYUT - 2, HUCRE_BOYUT - 2))

class Food:
    def __init__(self):
        self.position = [0, 0]
        self.spawn()
    
    def spawn(self):
        self.position = [
            random.randint(0, (GENISLIK // HUCRE_BOYUT) - 1) * HUCRE_BOYUT,
            random.randint(0, (YUKSEKLIK // HUCRE_BOYUT) - 1) * HUCRE_BOYUT
        ]
    
    def draw(self, surface):
        pygame.draw.rect(surface, KIRMIZI, 
                        (self.position[0], self.position[1], HUCRE_BOYUT, HUCRE_BOYUT))
        pygame.draw.rect(surface, (255, 100, 100), 
                        (self.position[0] + 3, self.position[1] + 3, 
                         HUCRE_BOYUT - 6, HUCRE_BOYUT - 6))
        pygame.draw.rect(surface, (139, 69, 19), 
                        (self.position[0] + 8, self.position[1] + 2, 4, 5))

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.paused = False
    
    def reset(self):
        self.snake.reset()
        self.food.spawn()
        if self.score > self.high_score:
            self.high_score = self.score
        self.score = 0
        self.game_over = False
        self.paused = False
    
    def update(self):
        if self.game_over or self.paused:
            return
        
        self.snake.move()
        
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.score += 10
            self.food.spawn()
            
            while self.food.position in self.snake.body:
                self.food.spawn()
        
        if self.snake.check_collision():
            self.game_over = True
    
    def draw(self):
        ekran.fill(SIYAH)
        pygame.draw.rect(ekran, (20, 20, 20), (0, 0, GENISLIK, YUKSEKLIK))
        
        for x in range(0, GENISLIK, HUCRE_BOYUT):
            pygame.draw.line(ekran, (30, 30, 30), (x, 0), (x, YUKSEKLIK))
        for y in range(0, YUKSEKLIK, HUCRE_BOYUT):
            pygame.draw.line(ekran, (30, 30, 30), (0, y), (GENISLIK, y))
        
        self.food.draw(ekran)
        self.snake.draw(ekran)
        
        pygame.draw.rect(ekran, (40, 40, 40), (0, YUKSEKLIK, GENISLIK, 60))
        skor_text = font_orta.render(f'Skor: {self.score}', True, BEYAZ)
        ekran.blit(skor_text, (20, YUKSEKLIK + 15))
        rekor_text = font_kucuk.render(f'Rekor: {self.high_score}', True, SARI)
        ekran.blit(rekor_text, (GENISLIK - 150, YUKSEKLIK + 20))
        
        if self.game_over:
            overlay = pygame.Surface((GENISLIK, YUKSEKLIK))
            overlay.set_alpha(200)
            overlay.fill(SIYAH)
            ekran.blit(overlay, (0, 0))
            
            game_over_text = font_buyuk.render('OYUN BİTTİ!', True, KIRMIZI)
            skor_text = font_orta.render(f'Skor: {self.score}', True, BEYAZ)
            devam_text = font_kucuk.render('SPACE - Yeniden Başla', True, YESIL)
            cikis_text = font_kucuk.render('ESC - Çıkış', True, BEYAZ)
            
            texts = [
                (game_over_text, YUKSEKLIK // 2 - 80),
                (skor_text, YUKSEKLIK // 2 - 20),
                (devam_text, YUKSEKLIK // 2 + 40),
                (cikis_text, YUKSEKLIK // 2 + 70)
            ]
            for text, y_pos in texts:
                ekran.blit(text, (GENISLIK // 2 - text.get_width() // 2, y_pos))
        
        if self.paused:
            overlay = pygame.Surface((GENISLIK, YUKSEKLIK))
            overlay.set_alpha(150)
            overlay.fill(SIYAH)
            ekran.blit(overlay, (0, 0))
            
            pause_text = font_buyuk.render('DURAKLADI', True, SARI)
            devam_text = font_kucuk.render('P - Devam Et', True, BEYAZ)
            
            for text, y_offset in [(pause_text, -40), (devam_text, 20)]:
                ekran.blit(text, (GENISLIK // 2 - text.get_width() // 2, YUKSEKLIK // 2 + y_offset))

def main():
    game = Game()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                if event.key == pygame.K_SPACE and game.game_over:
                    game.reset()
                
                if event.key == pygame.K_p and not game.game_over:
                    game.paused = not game.paused
                
                if not game.game_over and not game.paused:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        game.snake.change_direction('UP')
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        game.snake.change_direction('DOWN')
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        game.snake.change_direction('LEFT')
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        game.snake.change_direction('RIGHT')
        
        game.update()
        game.draw()
        pygame.display.flip()
        saat.tick(10)

if __name__ == '__main__':
    main()