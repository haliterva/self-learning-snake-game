import pygame
import sys
import os
import matplotlib.pyplot as plt
from oyun import Game, GENISLIK, YUKSEKLIK, ekran, saat, font_orta, font_kucuk, BEYAZ, SARI, YESIL, KIRMIZI
from ai import SnakeAI

class AITrainer:
    def __init__(self):
        self.ai = SnakeAI()
        self.game = Game()
        self.episode = 0
    
    def train(self, num_episodes=1000, visualize=True, save_every=100):
        self._print_header("AI EĞİTİMİ BAŞLIYOR")
        print(f"Hedef: {num_episodes} oyun")
        print(f"Görselleştirme: {'Açık' if visualize else 'Kapalı'}")
        print(f"{'='*50}\n")
        
        for episode in range(1, num_episodes + 1):
            self.episode = episode
            self.game.reset()
            
            state = self.ai.get_state(self.game)
            total_reward = 0
            steps = 0
            max_steps = 1000
            
            while not self.game.game_over and steps < max_steps:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.save_and_exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.save_and_exit()
                        if event.key == pygame.K_s:
                            self.ai.save_model()
                
                action = self.ai.choose_action(state)
                new_direction = self.ai.action_to_direction(action, self.game.snake.direction)
                self.game.snake.change_direction(new_direction)
                
                old_score = self.game.score
                self.game.update()
                next_state = self.ai.get_state(self.game)
                
                reward = self._calculate_reward(old_score, self.game.score, self.game.game_over)
                total_reward += reward
                
                self.ai.learn(state, action, reward, next_state, self.game.game_over)
                
                state = next_state
                steps += 1
                
                if visualize:
                    self.draw_training()
                    pygame.display.flip()
                    saat.tick(30)
            
            self.ai.decay_epsilon()
            
            self.ai.training_data['scores'].append(self.game.score)
            self.ai.training_data['epsilons'].append(self.ai.epsilon)
            
            if len(self.ai.training_data['scores']) >= 100:
                avg_score = sum(self.ai.training_data['scores'][-100:]) / 100
            else:
                avg_score = sum(self.ai.training_data['scores']) / len(self.ai.training_data['scores'])
            self.ai.training_data['avg_scores'].append(avg_score)
            
            if episode % 10 == 0:
                print(f"Oyun {episode}/{num_episodes} | "
                      f"Skor: {self.game.score} | "
                      f"Ort: {avg_score:.1f} | "
                      f"Epsilon: {self.ai.epsilon:.3f}")
            
            if episode % save_every == 0:
                self.ai.save_model(f'snake_ai_episode_{episode}.pkl')
        
        self._print_header("EĞİTİM TAMAMLANDI!")
        print(f"Toplam oyun: {num_episodes}")
        print(f"Ortalama skor: {avg_score:.1f}")
        print(f"En yüksek skor: {max(self.ai.training_data['scores'])}")
        print(f"{'='*50}\n")
        
        self.ai.save_model('snake_ai_final.pkl')
        self.plot_results()
    
    def _calculate_reward(self, old_score, new_score, game_over):
        if game_over:
            return -10
        if new_score > old_score:
            return 10
        return -0.01
    
    def draw_training(self):
        self.game.draw()
        
        # Sol taraf - Oyun bilgisi (Skorun yanına)
        center_x = GENISLIK // 2 - 80
        episode_text = font_kucuk.render(f'Oyun: {self.episode}', True, BEYAZ)
        ekran.blit(episode_text, (center_x, YUKSEKLIK + 20))
        
        # Sağ taraf - AI bilgileri
        right_x = GENISLIK // 2 + 50
        epsilon_text = font_kucuk.render(f'Epsilon: {self.ai.epsilon:.3f}', True, SARI)
        ekran.blit(epsilon_text, (right_x, YUKSEKLIK + 10))
        
        q_size_text = font_kucuk.render(f'Q-Table: {len(self.ai.q_table)}', True, YESIL)
        ekran.blit(q_size_text, (right_x, YUKSEKLIK + 33))
    
    def test(self, num_games=10, delay=100):
        self._print_header("AI TEST EDİLİYOR")
        
        if not self.ai.load_model('snake_ai_final.pkl'):
            print("Model bulunamadı! Önce eğitim yapmalısınız.")
            return
        
        self.ai.epsilon = 0
        scores = []
        
        for game_num in range(1, num_games + 1):
            self.game.reset()
            state = self.ai.get_state(self.game)
            steps = 0
            max_steps = 1000
            skip_game = False
            
            while not self.game.game_over and steps < max_steps and not skip_game:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return
                        if event.key == pygame.K_SPACE:
                            skip_game = True
                            break
                
                action = self.ai.choose_action(state)
                new_direction = self.ai.action_to_direction(action, self.game.snake.direction)
                self.game.snake.change_direction(new_direction)
                
                self.game.update()
                state = self.ai.get_state(self.game)
                steps += 1
                
                self.game.draw()
                test_text = font_orta.render(f'TEST OYUNU: {game_num}/{num_games}', True, YESIL)
                text_x = GENISLIK // 2 - test_text.get_width() // 2
                ekran.blit(test_text, (text_x, YUKSEKLIK + 15))
                
                skip_hint = font_kucuk.render('SPACE - Sonraki Oyun | ESC - Çıkış', True, BEYAZ)
                hint_x = GENISLIK // 2 - skip_hint.get_width() // 2
                ekran.blit(skip_hint, (hint_x, YUKSEKLIK + 40))
                
                pygame.display.flip()
                saat.tick(delay / 10)
            
            scores.append(self.game.score)
            print(f"Test {game_num}/{num_games} | Skor: {self.game.score}")
            pygame.time.wait(1000)
        
        self._print_header("TEST SONUÇLARI")
        print(f"Ortalama skor: {sum(scores)/len(scores):.1f}")
        print(f"En yüksek: {max(scores)}")
        print(f"En düşük: {min(scores)}")
        print(f"{'='*50}\n")
    
    def plot_results(self):
        scores = self.ai.training_data['scores']
        avg_scores = self.ai.training_data['avg_scores']
        epsilons = self.ai.training_data['epsilons']
        
        if not scores:
            print("Grafik için yeterli veri yok!")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        ax1.plot(scores, alpha=0.3, label='Skor')
        ax1.plot(avg_scores, label='Ortalama (100 oyun)', linewidth=2)
        ax1.set_xlabel('Oyun Sayısı')
        ax1.set_ylabel('Skor')
        ax1.set_title('AI Öğrenme Eğrisi')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(epsilons, color='red', label='Epsilon (Rastgelelik)')
        ax2.set_xlabel('Oyun Sayısı')
        ax2.set_ylabel('Epsilon')
        ax2.set_title('Keşif vs Sömürü')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(script_dir, 'training_results.png')
        plt.savefig(save_path)
        print(f"Grafik kaydedildi: {save_path}")
        plt.show()
    
    def save_and_exit(self):
        self.ai.save_model('snake_ai_backup.pkl')
        print("\nModel kaydedildi. Çıkılıyor...")
        pygame.quit()
        sys.exit()
    
    def _print_header(self, text):
        print(f"\n{'='*50}")
        print(f"{text}")
        print(f"{'='*50}\n")


def main():
    print("\n" + "="*50)
    print("SNAKE AI - Q-LEARNING PROJESI")
    print("="*50)
    print("\n[1] AI Eğit (Yeni)")
    print("[2] AI Eğit (Devam Et)")
    print("[3] AI Test Et")
    print("[4] Grafik Göster")
    print("[5] Çıkış")
    print("\n" + "="*50)
    
    choice = input("\nSeçiminiz (1-5): ").strip()
    
    trainer = AITrainer()
    
    if choice == '1':
        episodes = int(input("Kaç oyun eğitim yapılsın? (önerilen: 100-500): ") or "500")
        visualize = input("Görselleştirme açık olsun mu? (e/h): ").lower() == 'e'
        trainer.train(num_episodes=episodes, visualize=visualize)
    
    elif choice == '2':
        if trainer.ai.load_model('snake_ai_final.pkl'):
            episodes = int(input("Kaç oyun daha eğitim yapılsın?: ") or "500")
            visualize = input("Görselleştirme açık olsun mu? (e/h): ").lower() == 'e'
            trainer.train(num_episodes=episodes, visualize=visualize)
        else:
            print("Model bulunamadı! Seçenek 1'i kullanın.")
    
    elif choice == '3':
        games = int(input("Kaç oyun test edilsin? (önerilen: 5-10): ") or "5")
        trainer.test(num_games=games)
    
    elif choice == '4':
        if trainer.ai.load_model('snake_ai_final.pkl'):
            trainer.plot_results()
        else:
            print("Model bulunamadı! Önce eğitim yapın.")
    
    elif choice == '5':
        print("Çıkılıyor...")
        sys.exit()
    
    else:
        print("Geçersiz seçim!")


if __name__ == '__main__':
    main()