import random
import pickle
import os

try:
    from oyun import HUCRE_BOYUT, GENISLIK, YUKSEKLIK
except ImportError:
    HUCRE_BOYUT = 20
    GENISLIK = 480
    YUKSEKLIK = 480

class SnakeAI:
    
    def __init__(self, learning_rate=0.1, discount_factor=0.95, epsilon=1.0):
        self.q_table = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        
        self.training_data = {
            'scores': [],
            'epsilons': [],
            'avg_scores': []
        }
    
    def get_state(self, game):
        snake_head = game.snake.body[0]
        food_pos = game.food.position
        
        dx = food_pos[0] - snake_head[0]
        dy = food_pos[1] - snake_head[1]
        
        food_dir = self._get_food_direction(dx, dy)
        danger_straight = self._is_danger(game, game.snake.direction)
        danger_left = self._is_danger(game, self._turn_left(game.snake.direction))
        danger_right = self._is_danger(game, self._turn_right(game.snake.direction))
        length_category = self._get_length_category(len(game.snake.body))
        
        return (food_dir, danger_straight, danger_left, danger_right, game.snake.direction, length_category)
    
    def _get_food_direction(self, dx, dy):
        if dx > 0 and dy == 0:
            return 'E'
        elif dx > 0 and dy < 0:
            return 'NE'
        elif dx == 0 and dy < 0:
            return 'N'
        elif dx < 0 and dy < 0:
            return 'NW'
        elif dx < 0 and dy == 0:
            return 'W'
        elif dx < 0 and dy > 0:
            return 'SW'
        elif dx == 0 and dy > 0:
            return 'S'
        return 'SE'
    
    def _get_length_category(self, length):
        if length <= 5:
            return 'short'
        elif length <= 15:
            return 'medium'
        return 'long'
    
    def _is_danger(self, game, direction):
        head = game.snake.body[0].copy()
        
        moves = {'UP': (0, -HUCRE_BOYUT), 'DOWN': (0, HUCRE_BOYUT),
                'LEFT': (-HUCRE_BOYUT, 0), 'RIGHT': (HUCRE_BOYUT, 0)}
        
        dx, dy = moves[direction]
        head[0] += dx
        head[1] += dy
        
        if head[0] < 0 or head[0] >= GENISLIK or head[1] < 0 or head[1] >= YUKSEKLIK:
            return True
        return head in game.snake.body[1:]
    
    def _turn_left(self, direction):
        turns = {'UP': 'LEFT', 'LEFT': 'DOWN', 'DOWN': 'RIGHT', 'RIGHT': 'UP'}
        return turns[direction]
    
    def _turn_right(self, direction):
        turns = {'UP': 'RIGHT', 'RIGHT': 'DOWN', 'DOWN': 'LEFT', 'LEFT': 'UP'}
        return turns[direction]
    
    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(['STRAIGHT', 'LEFT', 'RIGHT'])
        
        if state not in self.q_table:
            self.q_table[state] = {'STRAIGHT': 0, 'LEFT': 0, 'RIGHT': 0}
        
        q_values = self.q_table[state]
        max_q = max(q_values.values())
        best_actions = [action for action, q in q_values.items() if q == max_q]
        return random.choice(best_actions)
    
    def action_to_direction(self, action, current_direction):
        if action == 'STRAIGHT':
            return current_direction
        elif action == 'LEFT':
            return self._turn_left(current_direction)
        return self._turn_right(current_direction)
    
    def learn(self, state, action, reward, next_state, done):
        if state not in self.q_table:
            self.q_table[state] = {'STRAIGHT': 0, 'LEFT': 0, 'RIGHT': 0}
        if next_state not in self.q_table:
            self.q_table[next_state] = {'STRAIGHT': 0, 'LEFT': 0, 'RIGHT': 0}
        
        current_q = self.q_table[state][action]
        max_next_q = 0 if done else max(self.q_table[next_state].values())
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        
        self.q_table[state][action] = new_q
    
    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def save_model(self, filename='snake_ai_model.pkl'):
        data = {
            'q_table': self.q_table,
            'epsilon': self.epsilon,
            'training_data': self.training_data
        }
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, filename)
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        print(f"Model kaydedildi: {path}")
    
    def load_model(self, filename='snake_ai_model.pkl'):  
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, filename)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                data = pickle.load(f)
            self.q_table = data.get('q_table', {})
            self.epsilon = data.get('epsilon', self.epsilon)
            self.training_data = data.get('training_data', {'scores': [], 'epsilons': [], 'avg_scores': []})
            print(f"Model yüklendi: {path}")
            print(f"Q-table boyutu: {len(self.q_table)}")
            print(f"Epsilon: {self.epsilon:.4f}")
            return True
        else:
            print(f"Model bulunamadı: {path}")
            return False