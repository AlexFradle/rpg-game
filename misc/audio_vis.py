import pygame
import pyaudio
import time
import colour
pygame.init()

width, height = 1650, 720
display = pygame.display.set_mode((width, height), pygame.SRCALPHA)
clock = pygame.time.Clock()

WIDTH = 2
CHANNELS = 2
RATE = 44100

p = pyaudio.PyAudio()
data = []
purple = colour.Color("purple")
colours = [list(map(lambda z: z * 255, i.rgb)) for i in list(purple.range_to(colour.Color("red"), 255 * 2))]


def callback(in_data, frame_count, time_info, status):
    global data
    data = in_data
    return in_data, pyaudio.paContinue


stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=False,
                stream_callback=callback)

stream.start_stream()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    display.fill((0, 0, 0))

    x = 0
    for d in data:
        if d != 255:
            pygame.draw.line(display, colours[d * 2], (x, height), (x, height - (d * 2)))
        x += 0.4

    pygame.display.update()
    clock.tick(60)


stream.stop_stream()
stream.close()
p.terminate()

pygame.quit()
