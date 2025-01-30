import pygame
import sounddevice as sd
import numpy as np
import random

# Initialize pygame
pygame.init()

# Set fixed window size
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Frequency Guesser")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.Font(None, 30)

# Frequency settings
min_frequency = 20
max_frequency = 20000
target_frequency = random.randint(min_frequency, max_frequency)
guessed_frequency = (min_frequency + max_frequency) // 2
volume_level = 50  # Percentage
message = ""
score = 0  # Score counter

# Sliders
guessed_frequency_slider = {"x": 100, "y": 200, "length": 800, "value": guessed_frequency, "min_value": min_frequency,
                            "max_value": max_frequency}
volume_slider = {"x": 100, "y": 250, "length": 800, "value": volume_level, "min_value": 0, "max_value": 100}
frequency_range_slider = {"x": 100, "y": 300, "length": 800, "min_value": min_frequency, "max_value": max_frequency,
                          "left_value": min_frequency, "right_value": max_frequency}
display_target_frequency = None  # Will be shown after Guess is clicked


# Function to generate a tone
def generate_tone(frequency, duration=1.0, volume=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 0.5 * (volume / 100) * np.sin(2 * np.pi * frequency * t)
    return wave


# Function to play a tone
def play_tone():
    global target_frequency
    tone = generate_tone(target_frequency, duration=1.0, volume=volume_slider["value"])
    sd.play(tone, samplerate=44100)


# Function to start a new round
def new_round():
    global target_frequency, guessed_frequency, message, display_target_frequency
    target_frequency = random.randint(int(frequency_range_slider["left_value"]),
                                      int(frequency_range_slider["right_value"]))
    guessed_frequency = (frequency_range_slider["left_value"] + frequency_range_slider["right_value"]) // 2
    display_target_frequency = None  # Hide target frequency at start of a new round
    message = ""


# Function to calculate and display feedback
def calculate_feedback():
    global message, score, display_target_frequency
    difference = abs(target_frequency - guessed_frequency)
    display_target_frequency = target_frequency  # Show target frequency after guess

    if difference <= 399:
        message = "Incredible! You nailed it!"
        score += 100
    elif difference <= 900:
        message = "So close! You're on fire!"
        score += 75
    elif difference <= 3000:
        message = "Not bad, keep practicing!"
        score += 50
    elif difference <= 5000:
        message = "Meh... Could be better."
        score += 25
    else:
        message = "Way off! Try again!"
        score += 0


# Function to draw a slider
def draw_slider(slider, label, is_percentage=False, dual_knob=False):
    pygame.draw.rect(screen, BLACK, (slider["x"], slider["y"], slider["length"], 5), 2)
    if dual_knob:
        left_pos = int(
            slider["x"] + (slider["left_value"] - slider["min_value"]) / (slider["max_value"] - slider["min_value"]) *
            slider["length"])
        right_pos = int(
            slider["x"] + (slider["right_value"] - slider["min_value"]) / (slider["max_value"] - slider["min_value"]) *
            slider["length"])
        pygame.draw.circle(screen, BLACK, (left_pos, slider["y"] + 3), 10)
        pygame.draw.circle(screen, BLACK, (right_pos, slider["y"] + 3), 10)
        display_value = f"{int(slider['left_value'])} Hz - {int(slider['right_value'])} Hz"
    else:
        pos = int(slider["x"] + (slider["value"] - slider["min_value"]) / (slider["max_value"] - slider["min_value"]) *
                  slider["length"])
        pygame.draw.circle(screen, BLACK, (pos, slider["y"] + 3), 10)
        display_value = f"{int(slider['value'])}{'%' if is_percentage else ' Hz'}"
    label_text = font.render(f"{label}: {display_value}", True, BLACK)
    screen.blit(label_text, (slider["x"], slider["y"] - 20))


# Buttons
buttons = [
    {"label": "Play Tone", "x": 100, "y": 400, "action": play_tone},
    {"label": "Guess!", "x": 300, "y": 400, "action": calculate_feedback},
    {"label": "New Round", "x": 500, "y": 400, "action": new_round},
]

dragging = None
dragging_knob = None
running = True

try:
    while running:
        screen.fill(WHITE)

        # Display message at the top
        if message:
            message_text = font.render(message, True, BLACK)
            screen.blit(message_text, (WIDTH // 2 - 150, 50))

        # Display Target Frequency between message and sliders
        if display_target_frequency:
            target_text = font.render(f"Target Frequency: {display_target_frequency} Hz", True, BLACK)
            screen.blit(target_text, (WIDTH // 2 - 150, 80))  # Positioned below message

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x_pos, y_pos = event.pos
                for button in buttons:
                    if button["x"] <= x_pos <= button["x"] + 150 and button["y"] <= y_pos <= button["y"] + 40:
                        button["action"]()
                if guessed_frequency_slider["y"] - 10 <= y_pos <= guessed_frequency_slider["y"] + 10:
                    dragging = "guessed_frequency"
                elif volume_slider["y"] - 10 <= y_pos <= volume_slider["y"] + 10:
                    dragging = "volume"
                elif frequency_range_slider["y"] - 10 <= y_pos <= frequency_range_slider["y"] + 10:
                    if abs(x_pos - (frequency_range_slider["x"] +
                                   (frequency_range_slider["left_value"] - min_frequency) /
                                   (max_frequency - min_frequency) * frequency_range_slider["length"])) < 10:
                        dragging_knob = "left"
                    elif abs(x_pos - (frequency_range_slider["x"] +
                                      (frequency_range_slider["right_value"] - min_frequency) /
                                      (max_frequency - min_frequency) * frequency_range_slider["length"])) < 10:
                        dragging_knob = "right"
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = None
                dragging_knob = None
            elif event.type == pygame.MOUSEMOTION:
                x_pos, _ = event.pos
                if dragging == "guessed_frequency":
                    guessed_frequency_slider["value"] = max(min_frequency, min(max_frequency,
                        int(min_frequency + (x_pos - guessed_frequency_slider["x"]) / guessed_frequency_slider["length"] * (max_frequency - min_frequency))))
                elif dragging == "volume":
                    volume_slider["value"] = max(0, min(100, int((x_pos - volume_slider["x"]) / volume_slider["length"] * 100)))
                elif dragging_knob == "left":
                    frequency_range_slider["left_value"] = max(min_frequency,
                        min(frequency_range_slider["right_value"] - 100,
                            int(min_frequency + (x_pos - frequency_range_slider["x"]) /
                                frequency_range_slider["length"] * (max_frequency - min_frequency))))
                elif dragging_knob == "right":
                    frequency_range_slider["right_value"] = min(max_frequency,
                        max(frequency_range_slider["left_value"] + 100,
                            int(min_frequency + (x_pos - frequency_range_slider["x"]) /
                                frequency_range_slider["length"] * (max_frequency - min_frequency))))

        for button in buttons:
            pygame.draw.rect(screen, BLACK, (button["x"], button["y"], 150, 40))
            text = font.render(button["label"], True, WHITE)
            screen.blit(text, (button["x"] + 20, button["y"] + 10))

        draw_slider(guessed_frequency_slider, "Guessed Frequency")
        draw_slider(volume_slider, "Volume", is_percentage=True)
        draw_slider(frequency_range_slider, "Frequency Range", dual_knob=True)

        pygame.display.flip()
except Exception as e:
    print("Error:", e)
finally:
    pygame.quit()
