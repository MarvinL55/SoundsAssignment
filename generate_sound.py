import pygame
import time
import os
import random
import numpy as np
from pydub import AudioSegment

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Interpretation of Earle Brown's December 1952")

# Trim and save sounds
def trim_sound(input_file, output_file, start_ms=0, duration_ms=3000):
    sound = AudioSegment.from_file(input_file)
    trimmed_sound = sound[start_ms:start_ms + duration_ms]
    sound.export(output_file, format="wav")

os.makedirs("temp_trimmed_sounds", exist_ok=True)

# Trim the sounds and save them
trim_sound("130586__casemundy__wind-chimes.wav", "temp_trimmed_sounds/chimes.wav")
trim_sound("371856__cryanrautha__ganon-mid-tom-drum.wav", "temp_trimmed_sounds/drum.wav")
trim_sound("394905__nikviolinist97__violin-d-string-melody (1).wav", "temp_trimmed_sounds/violin.wav")
trim_sound("435923__luhenriking__high-notes-piano-melody.wav", "temp_trimmed_sounds/piano.wav")
trim_sound("546533__funnyvoices__wind-13km-per-hour-11pm-29-nov-2020-werribee-south-beach.wav", "temp_trimmed_sounds/ambient_wind.wav")
trim_sound("710582__audiocoffee__long-autumn-loop-ver (1).wav", "temp_trimmed_sounds/synth.wav")


chimes_sound = pygame.mixer.Sound("temp_trimmed_sounds/chimes.wav")
drum_sound = pygame.mixer.Sound("temp_trimmed_sounds/drum.wav")
violin_sound = pygame.mixer.Sound("temp_trimmed_sounds/violin.wav")
piano_sound = pygame.mixer.Sound("temp_trimmed_sounds/piano.wav")
ambient_wind_sound = pygame.mixer.Sound("temp_trimmed_sounds/ambient_wind.wav")
synth_sound = pygame.mixer.Sound("temp_trimmed_sounds/synth.wav")

for sound in [chimes_sound, piano_sound, synth_sound, violin_sound, drum_sound, ambient_wind_sound]:
    sound.set_volume(0.3)


# Layout based on the provided image
def generate_score_elements():
    return [
        # Rectangles (x, y, width, height)
        ("rectangle", 240, 20, 5, 55),
        ("rectangle", 370, 410, 10, 40),
        ("rectangle", 280, 190, 40, 10),
        ("rectangle", 830, 310, 60, 5),
        ("rectangle", 490, 420, 8, 20),
        ("rectangle", 720, 150, 30, 10),
        ("rectangle", 200, 600, 40, 5),
        ("rectangle", 190, 870, 50, 7),
        ("rectangle", 50, 790, 6, 60),
        ("rectangle", 560, 600, 40, 8),
        ("rectangle", 740, 630, 10, 60),
        ("rectangle", 690, 370, 60, 5),
        ("rectangle", 585, 720, 60, 5),
        ("rectangle", 620, 740, 60, 5),
        
        ("line", 500 + 50, 150, 440 + 58, 150),
        ("line", 305 - 100, (100 - 40) + 309 - 10, 305 - 100, 100 + 309 - 10),
        ("line", 50, 500, -20, 500),
        ("line", 280, 660, 280, 590),
        ("line", 450, 910, 450, 820),
        ("line", 110, 720, 170, 720),
        ("line", 780, 590, 870, 590),
    ]

all_sounds = [chimes_sound, drum_sound, violin_sound, piano_sound, ambient_wind_sound, synth_sound]

# Assign sounds to elements
def create_sounds_for_elements(elements):
    element_sounds = {}
    sound_cooldowns = {}
    for element in elements:
        sound = random.choice(all_sounds)
        if sound:
            element_sounds[element] = sound
            sound_cooldowns[sound] = 0
    return element_sounds, sound_cooldowns

# Generate visual elements, sounds, and cooldowns
score_elements = generate_score_elements()
element_sounds, sound_cooldowns = create_sounds_for_elements(score_elements)

channels = [pygame.mixer.Channel(i) for i in range(5)]
max_sounds = 3
current_sounds_playing = 0

def play_sound(element):
    global current_sounds_playing
    sound = element_sounds.get(element)
    if sound and current_sounds_playing < max_sounds:  
        current_time = time.time()
        if current_time - sound_cooldowns[sound] > 0.5:
            # Find a free channel
            for channel in channels:
                if not channel.get_busy():
                    channel.play(sound, maxtime=4000)
                    current_sounds_playing += 1
                    channel.set_endevent(pygame.USEREVENT + 1) 
                    break
            sound_cooldowns[sound] = current_time

# Handle sound end events
def handle_sound_end(event):
    global current_sounds_playing
    if event.type == pygame.USEREVENT + 1:
        current_sounds_playing = max(0, current_sounds_playing - 1)

# Draw score elements
def draw_score_elements():
    for element in score_elements:
        if element[0] == "rectangle":
            _, x, y, width, height = element
            pygame.draw.rect(screen, (0, 0, 0), (x, y, width, height))
        elif element[0] == "line":
            _, x1, y1, x2, y2 = element
            pygame.draw.line(screen, (0, 0, 0), (x1, y1), (x2, y2), 2)

# Function to check collision and play sound
def check_collision(ball, element):
    if element[0] == "rectangle":
        x, y, width, height = element[1:]
        if x - ball['radius'] <= ball['pos'][0] <= x + width + ball['radius'] and y - ball['radius'] <= ball['pos'][1] <= y + height + ball['radius']:
            ball['speed'][1] = -ball['speed'][1]
            play_sound(element)
    elif element[0] == "line":
        x1, y1, x2, y2 = element[1:]
        if is_near_line(ball['pos'], (x1, y1), (x2, y2)):
            ball['speed'][1] = -ball['speed'][1]
            ball['speed'][0] = -ball['speed'][0]
            play_sound(element)

# Check if the ball is near a line segment
def is_near_line(ball_pos, line_start, line_end):
    line_vec = np.array([line_end[0] - line_start[0], line_end[1] - line_start[1]])
    ball_vec = np.array([ball_pos[0] - line_start[0], ball_pos[1] - line_start[1]])
    line_len = np.linalg.norm(line_vec)
    proj_len = np.dot(ball_vec, line_vec / line_len)
    if 0 <= proj_len <= line_len:
        perp_dist = np.linalg.norm(ball_vec - proj_len * (line_vec / line_len))
        return perp_dist <= 10
    return False

# Main loop
running = True
clock = pygame.time.Clock()
balls = []

while running:
    screen.fill((255, 255, 255))
    draw_score_elements()

    for ball in balls:
        pygame.draw.circle(screen, (255, 0, 0), ball['pos'], ball['radius'])
        ball['pos'][0] += ball['speed'][0]
        ball['pos'][1] += ball['speed'][1]
        for element in score_elements:
            check_collision(ball, element)
        if ball['pos'][0] <= 0 or ball['pos'][0] >= WIDTH:
            ball['speed'][0] *= -1
        if ball['pos'][1] <= 0 or ball['pos'][1] >= HEIGHT:
            ball['speed'][1] *= -1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x = pygame.mouse.get_pos()[0]
            possible_horizontal_speeds = [-5, -3, 3, 5]
            possible_vertical_speeds = [2, 4, 6, 8, 10]
            balls.append({
                'pos': [mouse_x, 0],
                'radius': 10,
                'speed': [
                    random.choice(possible_horizontal_speeds),
                    random.choice(possible_vertical_speeds)
                ],
            })
        elif event.type == pygame.USEREVENT + 1:
            handle_sound_end(event)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
