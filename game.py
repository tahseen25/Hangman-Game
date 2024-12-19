import pygame
import random
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE
from hints import get_hints  # Import hints

# Initialize Pygame
pygame.init()

# Constants
INITIAL_SCREEN_WIDTH, INITIAL_SCREEN_HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (2, 75, 48)
FONT_SIZE = 24
WORD_FONT_SIZE = FONT_SIZE * 2  # Double the font size for the word display
LETTER_FONT = pygame.font.SysFont('Arial', 25)
HANGMAN_SIZE = (200, 200)
BACKGROUND_COLOR_TOP = (196, 228, 255)  # Light Blue
BACKGROUND_COLOR_BOTTOM = (215, 208, 255)  # Light Pink

# Initialize mixer for music
pygame.mixer.init()
pygame.mixer.music.load('background_music.wav')  # Load your background music
pygame.mixer.music.play(-1)  # Play music in a loop


# Screen setup (resizable)
screen = pygame.display.set_mode((INITIAL_SCREEN_WIDTH, INITIAL_SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Hangman Game')

# Fonts
font = pygame.font.Font(None, FONT_SIZE)
word_font = pygame.font.Font(None, WORD_FONT_SIZE)  # Font for the word display

# Load images
def load_images():
    images = []
    for i in range(7):
        image = pygame.image.load(f'hangman{i}.png')
        image = pygame.transform.scale(image, HANGMAN_SIZE)
        images.append(image)
    return images

# Draw gradient background
def draw_gradient_background():
    for y in range(screen.get_height()):
        color = (
            BACKGROUND_COLOR_TOP[0] * (screen.get_height() - y) // screen.get_height() + BACKGROUND_COLOR_BOTTOM[0] * y // screen.get_height(),
            BACKGROUND_COLOR_TOP[1] * (screen.get_height() - y) // screen.get_height() + BACKGROUND_COLOR_BOTTOM[1] * y // screen.get_height(),
            BACKGROUND_COLOR_TOP[2] * (screen.get_height() - y) // screen.get_height() + BACKGROUND_COLOR_BOTTOM[2] * y // screen.get_height()
        )
        pygame.draw.line(screen, color, (0, y), (screen.get_width(), y))

# Display feedback message
def display_feedback(message, duration=2000):
    feedback_text = font.render(message, True, BLACK)
    screen.blit(feedback_text, (screen.get_width() // 2 - feedback_text.get_width() // 2, screen.get_height() // 2))
    pygame.display.flip()
    pygame.time.delay(duration)  # Pause for the specified duration

# Draw game screen
def draw_screen(word, guessed_letters, attempts_left, hints, score, hint_index, message=""):
    draw_gradient_background()

    # Display word with underscores for unguessed letters
    display_word = ' '.join([letter.upper() if letter in guessed_letters else '_' for letter in word])
    word_text = word_font.render(display_word, True, BLACK)
    word_x = (screen.get_width() - word_text.get_width()) // 2
    screen.blit(word_text, (word_x, int(screen.get_height() * 0.1)))  # 10% from the top

    # Draw guessed letters
    guessed_text = LETTER_FONT.render("Guessed Letters: " + " ".join(letter.upper() for letter in guessed_letters), 1, BLACK)
    screen.blit(guessed_text, (20, int(screen.get_height() * 0.8)))  # 80% from the top

    # Display remaining attempts
    attempts_text = font.render(f'Remaining Attempts: {attempts_left}', True, BLACK)
    screen.blit(attempts_text, (screen.get_width() - attempts_text.get_width() - 20, 20))

    # Display score
    score_text = font.render(f'Score: {score}', True, BLACK)
    screen.blit(score_text, (20, 20))

    # Display hints in green color only if at least one wrong guess was made
    if hint_index > 0 and hint_index <= len(hints):
        hint_text = font.render(f'Hint: {hints[hint_index - 1]}', True, GREEN)
        screen.blit(hint_text, (screen.get_width() // 2 - hint_text.get_width() // 2, int(screen.get_height() * 0.2)))  # 15% from the top

# Game loop
def game_loop(word_list, category, images, max_attempts, score):
    used_words = []  # Track used words
    word = random.choice(word_list[category])
    hints = get_hints(word)
    guessed_letters = []
    attempts_left = max_attempts
    hint_index = 0
    running = True

    while running:
        draw_screen(word, guessed_letters, attempts_left, hints, score, hint_index)

        # Show corresponding hangman image
        hangman_image = images[max_attempts - attempts_left]
        screen.blit(hangman_image, (screen.get_width() // 2 - hangman_image.get_width() // 2, int(screen.get_height() * 0.3)))  # 30% from the top

        # Display switch button
        switch_text = font.render("Switch ->", True, BLACK)
        switch_button = pygame.Rect(screen.get_width() - switch_text.get_width() - 20, screen.get_height() - switch_text.get_height() - 20, switch_text.get_width(), switch_text.get_height())
        screen.blit(switch_text, (screen.get_width() - switch_text.get_width() - 20, screen.get_height() - switch_text.get_height() - 20))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, score
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if switch_button.collidepoint(event.pos):
                    return True, score
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False, score
                elif event.unicode.isalpha():
                    letter = event.unicode.lower()
                    if letter not in guessed_letters:
                        guessed_letters.append(letter)
                        if letter not in word:
                            attempts_left -= 1
                            if hint_index < len(hints):
                                hint_index += 1

                    # Check if the player has guessed the word
                    if all(letter in guessed_letters for letter in word):
                        draw_screen(word, guessed_letters, attempts_left, hints, score, hint_index)
                        pygame.display.flip()
                        pygame.time.delay(500)

                        score += max(6 - hint_index, 0)
                        display_feedback("Correct! You guessed it right!")
                        used_words.append(word)  # Add word to used list

                        # Choose a new word ensuring it's not already used
                        if len(used_words) >= len(word_list[category]):
                            used_words = []  # Reset used words if all have been used
                        word = random.choice([w for w in word_list[category] if w not in used_words])
                        hints = get_hints(word)
                        guessed_letters = []
                        attempts_left = max_attempts
                        hint_index = 0

                    # Check if the player has run out of attempts
                    if attempts_left == 0:
                        draw_screen(word, guessed_letters, attempts_left, hints, score, hint_index)
                        screen.blit(images[max_attempts - attempts_left], (screen.get_width() // 2 - hangman_image.get_width() // 2, screen.get_height() // 2 - hangman_image.get_height() // 2))
                        pygame.display.flip()
                        pygame.time.delay(1000)
                        display_feedback(f"The word was '{word.capitalize()}'. Better luck next time!")
                        used_words.append(word)  # Add word to used list

                        # Choose a new word ensuring it's not already used
                        if len(used_words) >= len(word_list[category]):
                            used_words = []  # Reset used words if all have been used
                        word = random.choice([w for w in word_list[category] if w not in used_words])
                        hints = get_hints(word)
                        guessed_letters = []
                        attempts_left = max_attempts
                        hint_index = 0

        pygame.time.delay(100)

    return False, score



# Main game function
def main_game(category, score):
    word_list = {

        'flower': ["rose", "tulip", "sunflower", "lily", "lotus", "jasmine", "hibiscus", "daisy", "gazania", "aster", "marigold","orchid", "carnation", "dahlia", "anemone", "chrysanthemum", "cactus", "poppy", "iris", "periwinkle"],
        
        'animal': ["lion", "tiger", "elephant", "giraffe", "zebra", "kangaroo", "panda", "penguin", "koala", "wolf", "bear", "shark", "whale", "eagle", "cheetah", "rhinoceros", "hippopotamus", "jaguar", "leopard", "octopus", "platypus", "hedgehog", "otter", "peacock", "sealion", "walrus", "coyote", "dolphin", "falcon", "jellyfish", "hawk", "starfish", "fox", "camel", "vulture", "tortoise", "porcupine", "crocodile", "alligator"],
        
        'fruit': ["apple", "banana", "orange","grape","kiwi","mango","strawberry","watermelon","pineapple","pear","peach","cherry","plum","coconut","broccoli","potato","onion","garlic","lettuce","cauliflower","eggplant","zucchini","blueberry","raspberry","papaya","blackberry","pomegranate","lemon","lime","apricot","fig","grapes","dragonfruit","tamarind","spinach","beetroot","greenbeans", "cabbage","radish","peas","tomato","cucumber"]
    }

    images = load_images()
    max_attempts = len(images) - 1

    return game_loop(word_list, category, images, max_attempts, score)

is_music_playing = True  # Music is playing by default

def main_menu():
    global is_music_playing
    running = True
    score = 0
    while running:
        draw_gradient_background()

        # Centering text for the main menu title
        title_text = font.render("Hangman Game", True, BLACK)
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        title_x = screen_width * 0.5 - title_text.get_width() * 0.5
        screen.blit(title_text, (title_x, screen_height * 0.05))  # Positioned 5% down from the top

        # Centered buttons
        flower_text = font.render("Flower Edition", True, BLACK)
        flower_img = pygame.transform.scale(pygame.image.load('flowers.jpg'), (200, 200))  # Adjust size as needed
        screen.blit(flower_img, (screen_width * 0.30 - flower_img.get_width() * 0.5, screen_height * 0.15))  # Positioned at 20% down
        screen.blit(flower_text, (screen_width * 0.30 - flower_text.get_width() * 0.5, screen_height * 0.15 + 210))  # Below image

        # Animal button
        animal_text = font.render("Animal Edition", True, BLACK)
        animal_img = pygame.transform.scale(pygame.image.load('animals.jpg'), (200, 200))  # Adjust size as needed
        screen.blit(animal_img, (screen_width * 0.70 - animal_img.get_width() * 0.5, screen_height * 0.15))  # Centered
        screen.blit(animal_text, (screen_width * 0.70 - animal_text.get_width() * 0.5, screen_height * 0.15 + 210))  # Below image

        # Fruit button
        fruit_text = font.render("Fruit Edition", True, BLACK)
        fruit_img = pygame.transform.scale(pygame.image.load('fruits.jpg'), (200, 200))  # Adjust size as needed
        screen.blit(fruit_img, (screen_width * 0.50 - fruit_img.get_width() * 0.5, screen_height * 0.55))  # Right
        screen.blit(fruit_text, (screen_width * 0.50 - fruit_text.get_width() * 0.5, screen_height * 0.55 + 210))  # Below image

        # Music control button
        music_text = font.render("Mute Music" if is_music_playing else "Play Music", True, BLACK)
        music_button = pygame.Rect(screen_width - music_text.get_width() - 20, screen_height - music_text.get_height() - 20, music_text.get_width(), music_text.get_height())
        screen.blit(music_text, (screen_width - music_text.get_width() - 20, screen_height - music_text.get_height() - 20))


        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                # Check which button was clicked
                if music_button.collidepoint(event.pos):
                    if is_music_playing:
                        pygame.mixer.music.pause()  # Mute music
                    else:
                        pygame.mixer.music.unpause()  # Play music
                    is_music_playing = not is_music_playing 
                if (screen_width * 0.30 - 100 <= mouse_x <= screen_width * 0.30 + 100) and (screen_height * 0.15 <= mouse_y <= screen_height * 0.35):
                    # Unpack the returned values
                    switch, score = main_game('flower', score)
                elif (screen_width * 0.70 - 100 <= mouse_x <= screen_width * 0.70 + 100) and (screen_height * 0.15 <= mouse_y <= screen_height * 0.35):
                    switch, score = main_game('animal', score)
                elif (screen_width * 0.50 - 100 <= mouse_x <= screen_width * 0.50 + 100) and (screen_height * 0.55 <= mouse_y <= screen_height * 0.75):
                    switch, score = main_game('fruit', score)

    pygame.quit()


if __name__ == "__main__":
    main_menu()
