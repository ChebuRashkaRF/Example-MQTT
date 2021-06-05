from influxdb import InfluxDBClient
import pygame


WIDTH, HEIGHT = 626, 417
fps = 60
ball_radius = 5

# Подключение к БД
client = InfluxDBClient("127.0.0.1", 8086)
client.switch_database('arconoid')


pygame.init()
sc = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
    result_cart = client.query('SELECT "cart_x", "cart_y" FROM "cart" WHERE time > now()-3s')

    # Траектория движения тележки
    points_cart = result_cart.get_points(measurement='cart')
    if bool(result_cart):
        for point_cart in points_cart:
            if point_cart['cart_x'] and point_cart['cart_y']:
                center_cart = point_cart['cart_x'], point_cart['cart_y']
                # print(center)
                pygame.draw.circle(sc, (209, 157, 24), center_cart, ball_radius+3)
                pygame.display.update()
    result_ball = client.query('SELECT "ball_x", "ball_y" FROM "ball" WHERE time > now()-3s')

    # Траектория движения шарика
    points_ball = result_ball.get_points(measurement='ball')
    if bool(result_ball):
        for point_ball in points_ball:
            if point_ball['ball_x'] and point_ball['ball_y']:
                center_ball = point_ball['ball_x'], point_ball['ball_y']
                print(center_ball)
                pygame.draw.circle(sc, (192, 0, 219), center_ball, ball_radius)
                pygame.display.update()

    clock.tick(fps)
