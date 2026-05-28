import pygame
import sys
import os
import random
import json

# 1. Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Настройки окна
WIDTH, HEIGHT = 1000, 750  
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Обучающее приложение «Знай-ка»")

# Цвета (RGB)
WHITE = (255, 255, 255)
LIGHT_BLUE = (220, 240, 250) 
GREEN = (144, 238, 144)
ORANGE = (255, 165, 0)
DARK_GRAY = (50, 50, 50)
YELLOW = (255, 220, 100)
PINK = (255, 182, 193)
RED = (255, 100, 100)
SOFT_PURPLE = (200, 180, 240)
DARK_BLUE = (40, 80, 120)

font = pygame.font.SysFont("Arial", 36)
small_font = pygame.font.SysFont("Arial", 24)
sub_font = pygame.font.SysFont("Arial", 28, bold=True) 

# Загрузка фоновой картинки для главного меню
menu_bg_loaded = False
menu_background = None
if os.path.exists("images/menu_bg.jpg"):
    try:
        menu_background = pygame.image.load("images/menu_bg.jpg")
        menu_background = pygame.transform.scale(menu_background, (WIDTH, HEIGHT))
        menu_bg_loaded = True
    except Exception as e:
        print(f"Ошибка загрузки красивого фона: {e}")

# БАЗА ДАННЫХ - источник истины 
CATEGORIES = {
    "animals": [
        {"name": "Кот", "file": "cat", "ext": "png", "type": "домашние"},
        {"name": "Корова", "file": "cow", "ext": "png", "type": "домашние"},
        {"name": "Собака", "file": "dog", "ext": "png", "type": "домашние"},
        {"name": "Курица", "file": "hen", "ext": "png", "type": "домашние"},
        {"name": "Медведь", "file": "bear", "ext": "png", "type": "дикие"},
        {"name": "Лиса", "file": "fox", "ext": "png", "type": "дикие"},
        {"name": "Волк", "file": "wolf", "ext": "png", "type": "дикие"},
        {"name": "Бегемот", "file": "begemot", "ext": "png", "type": "экзотические"},
        {"name": "Жираф", "file": "giraffe", "ext": "png", "type": "экзотические"},
        {"name": "Обезьяна", "file": "monkey", "ext": "png", "type": "экзотические"}
    ],
    "colors": [
        {"name": "Синий", "file": "blue", "ext": "jpg"},
        {"name": "Зеленый", "file": "green", "ext": "jpg"},
        {"name": "Красный", "file": "red", "ext": "jpg"},
        {"name": "Желтый", "file": "yellow", "ext": "jpg"}
    ],
    "vegetables": [
        {"name": "Капуста", "file": "cabbage", "ext": "jpg"},
        {"name": "Огурец", "file": "cucumber", "ext": "png"},
        {"name": "Картошка", "file": "potato", "ext": "jpg"},
        {"name": "Помидор", "file": "tomato", "ext": "jpg"}
    ],
    "fruits": [
        {"name": "Яблоко", "file": "apple", "ext": "jpg"},
        {"name": "Банан", "file": "banana", "ext": "jpg"},
        {"name": "Клубника", "file": "strawberry", "ext": "jpg"},
        {"name": "Апельсин", "file": "orange", "ext": "jpg"} 
    ]
}

# Статистика для родителей — сохраняется в файл stats.json
STATS_FILE = "stats.json"

DEFAULT_STATS = {
    "animals":    {"correct": 0, "wrong": 0, "ru": "Животные"},
    "colors":     {"correct": 0, "wrong": 0, "ru": "Цвета"},
    "vegetables": {"correct": 0, "wrong": 0, "ru": "Овощи"},
    "fruits":     {"correct": 0, "wrong": 0, "ru": "Фрукты"}
}

def load_stats():
    """Загружает статистику из stats.json. Если файла нет — возвращает дефолтную."""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Убеждаемся, что все ключи на месте 
            for key, default in DEFAULT_STATS.items():
                if key not in data:
                    data[key] = default
            return data
        except Exception as e:
            print(f"Ошибка чтения stats.json, сброс статистики: {e}")
    return {k: v.copy() for k, v in DEFAULT_STATS.items()}

def save_stats():
    """Сохраняет текущую статистику в stats.json."""
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(parent_stats, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения stats.json: {e}")

parent_stats = load_stats()
#загрузка карточек
def load_card_images():
    loaded = {}
    all_flat_list = []
    for cat_name, items in CATEGORIES.items():
        loaded[cat_name] = []
        for item in items:
            img_path = f"images/{item['file']}.{item['ext']}"
            if os.path.exists(img_path):
                img = pygame.image.load(img_path)
                img_learn = pygame.transform.scale(img, (110, 110))
                img_option = pygame.transform.scale(img, (120, 120)) 
                
                card_info = {
                    "name": item["name"],
                    "category": cat_name,
                    "image_learn": img_learn,
                    "image_option": img_option,
                    "sound_file": f"sound/{item['file']}.mp3",
                    "type": item.get("type", "") 
                }
                loaded[cat_name].append(card_info)
                all_flat_list.append(card_info)
            else:
                print(f"Внимание: Картинка {img_path} не найдена!")
    return loaded, all_flat_list

CARD_DATA, ALL_ITEMS = load_card_images()

screen_state = 'MENU'
current_category = ""
test_current_item = None
test_options = [] 
test_feedback = ""
feedback_color = DARK_GRAY

def generate_new_test_question():
    global test_current_item, test_options, test_feedback
    if not ALL_ITEMS: return
    test_feedback = ""
    test_current_item = random.choice(ALL_ITEMS)
    
    wrong_candidates = [item for item in ALL_ITEMS if item["name"] != test_current_item["name"]]
    chosen_wrong = random.sample(wrong_candidates, min(3, len(wrong_candidates)))
    
    test_options = chosen_wrong + [test_current_item]
    random.shuffle(test_options)
    

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if screen_state == 'MENU':
                if button_learn.collidepoint(mouse_pos): screen_state = 'LEARN_MENU'
                elif button_test.collidepoint(mouse_pos): generate_new_test_question(); screen_state = 'TEST'
                elif button_parents.collidepoint(mouse_pos): screen_state = 'PARENTS'
                elif button_info.collidepoint(mouse_pos): screen_state = 'INFO'
                    
            elif screen_state in ['LEARN_MENU', 'PARENTS', 'INFO']:
                if button_back.collidepoint(mouse_pos): screen_state = 'MENU'
                if screen_state == 'LEARN_MENU':
                    if btn_animals.collidepoint(mouse_pos): current_category = "animals"; screen_state = 'LEARN_CARDS'
                    elif btn_colors.collidepoint(mouse_pos): current_category = "colors"; screen_state = 'LEARN_CARDS'
                    elif btn_veg.collidepoint(mouse_pos): current_category = "vegetables"; screen_state = 'LEARN_CARDS'
                    elif btn_fruits.collidepoint(mouse_pos): current_category = "fruits"; screen_state = 'LEARN_CARDS'
                    
            elif screen_state == 'LEARN_CARDS':
                if button_back.collidepoint(mouse_pos): screen_state = 'LEARN_MENU'
                for card_rect, sound_path in current_cards_rects:
                    if card_rect.collidepoint(mouse_pos):
                        if os.path.exists(sound_path):
                            pygame.mixer.stop() 
                            pygame.mixer.Sound(sound_path).play()

            elif screen_state == 'TEST':
                if button_back.collidepoint(mouse_pos): screen_state = 'MENU'
                
                # Клик по кнопке "СЛУШАТЬ" — теперь это главный источник звука задания
                if button_speaker.collidepoint(mouse_pos) and test_current_item:
                    if os.path.exists(test_current_item["sound_file"]):
                        pygame.mixer.stop() 
                        pygame.mixer.Sound(test_current_item["sound_file"]).play()
                
                # Клик по 4 картинкам-вариантам
                for i, btn_rect in enumerate(test_buttons_rects):
                    if btn_rect.collidepoint(mouse_pos) and test_feedback != "correct":
                        cat = test_current_item["category"]
                        
                        if test_options[i]["name"] == test_current_item["name"]:
                            test_feedback = "correct"; feedback_color = (30, 156, 16)
                            parent_stats[cat]["correct"] += 1
                            save_stats()
                            
                            
                            pygame.mixer.stop() 
                            
                            molodec_path = "sound/correct_molodec.mp3"
                            if os.path.exists(molodec_path):
                                pygame.mixer.Sound(molodec_path).play()
                            else:
                                if os.path.exists(test_current_item["sound_file"]):
                                    pygame.mixer.Sound(test_current_item["sound_file"]).play()
                            
                            # Перелистываем вопрос через 1.5 секунды (теперь он загрузится тихо!)
                            pygame.time.set_timer(pygame.USEREVENT, 1500)
                        else:
                            test_feedback = "wrong"; feedback_color = (255, 0 ,0)
                            parent_stats[cat]["wrong"] += 1
                            save_stats()
                            
                            pygame.mixer.stop() 
                            try_again_path = "sound/try_again.mp3"
                            if os.path.exists(try_again_path):
                                pygame.mixer.Sound(try_again_path).play()
                            
        if event.type == pygame.USEREVENT:
            generate_new_test_question()
            pygame.time.set_timer(pygame.USEREVENT, 0)

    # 3. ОТРИСОВКА ЭКРАНОВ
    if screen_state == 'MENU' and menu_bg_loaded:
        screen.blit(menu_background, (0, 0)) 
    else:
        screen.fill(LIGHT_BLUE) 
    
    if screen_state == 'MENU':
        title_text = font.render("Развивающее приложение «Знай-ка»", True, DARK_BLUE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 60))
        
        button_learn = pygame.Rect(320, 180, 360, 90); pygame.draw.rect(screen, GREEN, button_learn, border_radius=20)
        text = font.render(" Обучение", True, DARK_GRAY); screen.blit(text, (button_learn.centerx - text.get_width()//2, button_learn.centery - 20))
        
        button_test = pygame.Rect(320, 300, 360, 90); pygame.draw.rect(screen, ORANGE, button_test, border_radius=20)
        text = font.render(" Проверка", True, DARK_GRAY); screen.blit(text, (button_test.centerx - text.get_width()//2, button_test.centery - 20))
        
        button_parents = pygame.Rect(320, 420, 360, 90); pygame.draw.rect(screen, SOFT_PURPLE, button_parents, border_radius=20)
        text = font.render(" Родителям", True, DARK_GRAY); screen.blit(text, (button_parents.centerx - text.get_width()//2, button_parents.centery - 20))
        
        button_info = pygame.Rect(900, 660, 60, 60); pygame.draw.rect(screen, WHITE, button_info, border_radius=30)
        text_i = font.render("?", True, DARK_BLUE); screen.blit(text_i, (button_info.centerx - text_i.get_width()//2, button_info.centery - 22))

    elif screen_state == 'INFO':
        title_text = font.render("О приложении", True, DARK_BLUE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
        
        instructions = [
            "Добро пожаловать в интерактивное приложение «Знай-ка»!",
            "Оно создано специально для малышей в возрасте 2-3 лет.",
            "",
            " Режим 'Обучение': Позволяет ребенку нажимать на карточки,",
            "   рассматривать яркие картинки и слушать правильное произношение слов.",
            "",
            " Режим 'Проверка': Тестовая часть полностью адаптирована для малышей.",
            "   Программа озвучивает слово, а ребенку нужно выбрать правильную картинку.",
            "",
            " Раздел 'Родителям': Содержит аналитику успеваемости ребенка,",
            "   подсказывая, какие темы усвоены, а на какие стоит обратить внимание."
        ]
        y_pos = 150
        for line in instructions:
            inst_lbl = small_font.render(line, True, DARK_GRAY)
            screen.blit(inst_lbl, (80, y_pos))
            y_pos += 35
            
        button_back = pygame.Rect(50, 660, 150, 50); pygame.draw.rect(screen, WHITE, button_back, border_radius=10)
        t = small_font.render("Назад", True, DARK_GRAY); screen.blit(t, (button_back.centerx - t.get_width()//2, button_back.centery - 12))

    elif screen_state == 'PARENTS':
        title_text = font.render("Панель успеваемости для родителей", True, DARK_BLUE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 40))
        
        start_y = 150
        for cat_key, data in parent_stats.items():
            cat_lbl = sub_font.render(f"Категория: {data['ru']}", True, DARK_GRAY)
            screen.blit(cat_lbl, (100, start_y))
            
            score_text = f"Правильно: {data['correct']} | Ошибок: {data['wrong']}"
            score_lbl = small_font.render(score_text, True, DARK_GRAY)
            screen.blit(score_lbl, (100, start_y + 30))
            
            if data['correct'] == 0 and data['wrong'] == 0:
                rec_text = "Ребенок еще не проходил тесты по этой теме."
                rec_color = DARK_GRAY
            elif data['wrong'] == 0:
                rec_text = "Великолепно! Тема усвоена без ошибок."
                rec_color = (30, 150, 20)
            elif data['correct'] >= data['wrong'] * 2:
                rec_text = "Хороший прогресс. Материал зафиксирован успешно."
                rec_color = DARK_BLUE
            else:
                rec_text = "Обратите внимание: малыш путает предметы. Стоит повторить тему в обучении."
                rec_color = (200, 50, 50)
                
            rec_lbl = small_font.render(f"Рекомендация: {rec_text}", True, rec_color)
            screen.blit(rec_lbl, (100, start_y + 55))
            
            pygame.draw.line(screen, SOFT_PURPLE, (100, start_y + 90), (900, start_y + 90), 2)
            start_y += 120
            
        button_back = pygame.Rect(50, 660, 150, 50); pygame.draw.rect(screen, WHITE, button_back, border_radius=10)
        t = small_font.render("Назад", True, DARK_GRAY); screen.blit(t, (button_back.centerx - t.get_width()//2, button_back.centery - 12))

    elif screen_state == 'LEARN_MENU':
        title_text = font.render("Выберите категорию", True, DARK_GRAY)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
        btn_animals = pygame.Rect(150, 180, 320, 100); pygame.draw.rect(screen, YELLOW, btn_animals, border_radius=15)
        t = font.render("Животные", True, DARK_GRAY); screen.blit(t, (btn_animals.centerx - t.get_width()//2, btn_animals.centery - 20))
        btn_colors = pygame.Rect(530, 180, 320, 100); pygame.draw.rect(screen, PINK, btn_colors, border_radius=15)
        t = font.render("Цвета", True, DARK_GRAY); screen.blit(t, (btn_colors.centerx - t.get_width()//2, btn_colors.centery - 20))
        btn_veg = pygame.Rect(150, 330, 320, 100); pygame.draw.rect(screen, GREEN, btn_veg, border_radius=15)
        t = font.render("Овощи", True, DARK_GRAY); screen.blit(t, (btn_veg.centerx - t.get_width()//2, btn_veg.centery - 20))
        btn_fruits = pygame.Rect(530, 330, 320, 100); pygame.draw.rect(screen, ORANGE, btn_fruits, border_radius=15)
        t = font.render("Фрукты", True, DARK_GRAY); screen.blit(t, (btn_fruits.centerx - t.get_width()//2, btn_fruits.centery - 20))
        button_back = pygame.Rect(50, 660, 150, 50); pygame.draw.rect(screen, WHITE, button_back, border_radius=10)
        t = small_font.render("Назад", True, DARK_GRAY); screen.blit(t, (button_back.centerx - t.get_width()//2, button_back.centery - 12))

    elif screen_state == 'LEARN_CARDS':
        ru_names = {"animals": "Животные", "colors": "Цвета", "vegetables": "Овощи", "fruits": "Фрукты"}
        title_text = font.render(f"Изучаем: {ru_names[current_category]}", True, DARK_GRAY)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 20))
        
        current_cards_rects = [] #координаты всех кнопок, чтобы потом прога знала по какой кнопке кликнул ребенок
        
        if current_category == "animals":
            subtypes = [("Домашние животные", "домашние"), ("Дикие животные", "дикие"), ("Экзотические животные", "экзотические")]
            current_y = 80
            
            for title, sub_type in subtypes:
                sub_lbl = sub_font.render(title, True, DARK_GRAY)
                screen.blit(sub_lbl, (50, current_y))
                current_y += 40
                
                filtered_animals = [a for a in CARD_DATA["animals"] if a["type"] == sub_type]
                for col, item in enumerate(filtered_animals):
                    x = 50 + col * 170
                    card_rect = pygame.Rect(x, current_y, 140, 150)
                    pygame.draw.rect(screen, WHITE, card_rect, border_radius=10)
                    screen.blit(item["image_learn"], (x + 15, current_y + 10))
                    lbl = small_font.render(item["name"], True, DARK_GRAY)
                    screen.blit(lbl, (card_rect.centerx - lbl.get_width()//2, current_y + 120))
                    current_cards_rects.append((card_rect, item["sound_file"])) # если мы попали по карточке, вкл звук
                
                current_y += 170
        else:
            start_x, start_y = 80, 120
            x_offset, y_offset = 180, 190
            for i, item in enumerate(CARD_DATA[current_category]):
                row = i // 5; col = i % 5
                x = start_x + col * x_offset; y = start_y + row * y_offset
                card_rect = pygame.Rect(x, y, 150, 170)
                pygame.draw.rect(screen, WHITE, card_rect, border_radius=10)
                screen.blit(item["image_learn"], (x + 20, y + 15))
                lbl = small_font.render(item["name"], True, DARK_GRAY)
                screen.blit(lbl, (card_rect.centerx - lbl.get_width()//2, y + 140))
                current_cards_rects.append((card_rect, item["sound_file"]))
            
        button_back = pygame.Rect(50, 695, 150, 50); pygame.draw.rect(screen, WHITE, button_back, border_radius=10)
        t = small_font.render("Назад", True, DARK_GRAY); screen.blit(t, (button_back.centerx - t.get_width()//2, button_back.centery - 12))

    elif screen_state == 'TEST':
        title_text = font.render("Послушай звук и выбери картинку!", True, DARK_GRAY)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 40))
        
        test_buttons_rects = []
        if test_current_item:
            # Кнопка "Слушать"
            button_speaker = pygame.Rect(WIDTH//2 - 150, 160, 300, 80)
            pygame.draw.rect(screen, YELLOW, button_speaker, border_radius=15)
            speaker_lbl = font.render(" СЛУШАТЬ", True, DARK_GRAY)
            screen.blit(speaker_lbl, (button_speaker.centerx - speaker_lbl.get_width()//2, button_speaker.centery - 20))

            # Эффекты успеха/ошибки
            if test_feedback:
                if test_feedback == "correct":
                    feed_text = "Правильно! Молодец!"
                    feed_lbl = font.render(feed_text, True, feedback_color)
                    fx = WIDTH//2 - feed_lbl.get_width()//2
                    screen.blit(feed_lbl, (fx, 280))
                    
                else:
                    feed_text = "Попробуй еще раз!"
                    feed_lbl = font.render(feed_text, True, feedback_color)
                    fx = WIDTH//2 - feed_lbl.get_width()//2
                    screen.blit(feed_lbl, (fx, 280))
                    
            # Четыре карточки-варианта в ряд
            btn_w, btn_h = 160, 160
            coords = [(140, 440), (340, 440), (540, 440), (740, 440)]
            for i, opt_item in enumerate(test_options):
                bx, by = coords[i]
                btn_rect = pygame.Rect(bx, by, btn_w, btn_h)
                
                pygame.draw.rect(screen, WHITE, btn_rect, border_radius=15)
                screen.blit(opt_item["image_option"], (bx + 20, by + 20))
                test_buttons_rects.append(btn_rect)
                
        button_back = pygame.Rect(50, 660, 150, 50); pygame.draw.rect(screen, WHITE, button_back, border_radius=10)
        t = small_font.render("Назад", True, DARK_GRAY); screen.blit(t, (button_back.centerx - t.get_width()//2, button_back.centery - 12))

    pygame.display.flip() 

pygame.quit()
sys.exit()