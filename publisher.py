import pygame
from random import randrange as rnd
import paho.mqtt.client as mqtt
import time


client = mqtt.Client("Publisher")  # создание клиента


WIDTH, HEIGHT = 626, 417
fps = 60
IsStart = 0
Score = 0

# paddle settings
paddle_w = 200
paddle_h = 15
paddle_speed = 15
paddle = pygame.Rect(WIDTH // 2 - paddle_w // 2, HEIGHT - paddle_h - 10,
                     paddle_w, paddle_h)

# ball settings
ball_radius = 12
ball_speed = 6
ball_rect = int(ball_radius * 2 ** 0.5)
ball = pygame.Rect(rnd(ball_rect, WIDTH - ball_rect), HEIGHT // 2, ball_rect,
                   ball_rect)
dx, dy = 1, -1

# blocks settings
block_list = [pygame.Rect(20 + 60 * i, 15 + 35 * j, 50, 25)
              for i in range(10) for j in range(3)]
color_list = [(rnd(30, 256), rnd(30, 256), rnd(30, 256)) for i in range(10)
              for j in range(3)]

pygame.init()
sc = pygame.display.set_mode((WIDTH, HEIGHT))
# sc2.set_caption("Пример")
clock = pygame.time.Clock()
# background image
img = pygame.image.load('img/fon.jpg').convert()
# legend
front_score = pygame.font.SysFont('Arial', 18, bold=True)
font_end = pygame.font.SysFont('Arial', 66, bold=True)
font_win = pygame.font.SysFont('Arial', 66, bold=True)


def detect_collision(dx, dy, ball, rect):
    if dx > 0:
        delta_x = ball.right - rect.left
    else:
        delta_x = rect.right - ball.left
    if dy > 0:
        delta_y = ball.bottom - rect.top
    else:
        delta_y = rect.bottom - ball.top

    if abs(delta_x - delta_y) < 10:
        dx, dy = -dx, -dy
    elif delta_x > delta_y:
        dy = -dy
    elif delta_y > delta_x:
        dx = -dx

    return dx, dy


client.loop_start()  # start the loop
client.connect("127.0.0.1", 1883, 60)  # подключение к брокеру

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and \
           IsStart == 0:
            IsStart = 1
            ball.x += ball_speed * dx
            ball.y += ball_speed * dy
        if event.type == pygame.QUIT:
            exit()
            run = False
    sc.blit(img, (0, 0))

    # show score
    ScoreText = front_score.render(f'Score: {Score}', 1, (255, 255, 255))
    sc.blit(ScoreText, (10, HEIGHT-paddle_h-40))
    # drawing world
    [pygame.draw.rect(sc, color_list[color], block) for color, block in
     enumerate(block_list)]
    pygame.draw.rect(sc, (209, 157, 24), paddle)
    pygame.draw.circle(sc, (192, 0, 219), ball.center, ball_radius)

    # print(ball.centerx, ball.centery)
    client.publish("arconoid/ball", str(ball.centerx) + ',' +
                   str(ball.centery))

    # ball movement
    if IsStart == 1:
        ball.x += ball_speed * dx
        ball.y += ball_speed * dy
    # collision left right
    if ball.centerx < ball_radius or ball.centerx > WIDTH - ball_radius:
        dx = -dx
    # collision top
    if ball.centery < ball_radius:
        dy = -dy
    # collision paddle
    if ball.colliderect(paddle) and dy > 0:
        dx, dy = detect_collision(dx, dy, ball, paddle)

    # collision blocks
    hit_index = ball.collidelist(block_list)
    if hit_index != -1:
        hit_rect = block_list.pop(hit_index)
        hit_color = color_list.pop(hit_index)
        dx, dy = detect_collision(dx, dy, ball, hit_rect)
        Score += 1
        hit_rect.inflate_ip(ball.width*3, ball.height*3)
        pygame.draw.rect(sc, hit_color, hit_rect)
        fps += 2

    # win, game over
    if ball.bottom > HEIGHT:
        while True:
            render_end = font_end.render('GAME OVER', 1,
                                         pygame.Color('orange'))
            sc.blit(render_end, (WIDTH//2-200, HEIGHT//2-45))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    client.loop_stop()   # Stop loop
                    client.disconnect()  # disconnect
                    exit()
    elif not len(block_list):
        while True:
            render_win = font_win.render('---WIN---', 1,
                                         pygame.Color('green'))
            sc.blit(render_win, (WIDTH//2-120, HEIGHT//2-45))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                    client.loop_stop()   # Stop loop
                    client.disconnect()  # disconnect

    # control
    key = pygame.key.get_pressed()
    if key[pygame.K_LEFT] and paddle.left > 0:
        paddle.left -= paddle_speed
        client.publish("arconoid/cart", str(paddle.centerx) + ',' +
                       str(paddle.centery))
    if key[pygame.K_RIGHT] and paddle.right < WIDTH:
        paddle.right += paddle_speed
        client.publish("arconoid/cart", str(paddle.centerx) + ',' +
                       str(paddle.centery))
    # update screen
    pygame.display.flip()
    clock.tick(fps)
