import pygame
import numpy as np
from sklearn.cluster import DBSCAN

# Евклидово расстояние. Позволяет найти расстояние между двумя точками
def dist(A, B):
    return np.sqrt((A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2)

# генерирует k рандомных цветов
def generate_colors(k):
    colors = []
    for i in range(k + 1):
        colors.append((np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)))
    return colors

def brush(pos):
    near_points = []
    for i in range(np.random.randint(1, 7)):
        x = pos[0] + np.random.randint(-20, 20)
        y = pos[1] + np.random.randint(-20, 20)
        near_points.append((x, y))
    return near_points

# получаем соседей точки
def get_neighbors(point, points, epsilon):
    return [p for p in points if dist(p, point) <= epsilon]

def custom_dbscan(points, epsilon, minPts):
    visited = set()
    clusters = []
    potential_outliers = set()
    edge_points = set()

    for point in points:
        if point in visited:
            continue
        visited.add(point)

        neighbors = get_neighbors(point, points, epsilon)

        # если соседей слишком мало, то это ПОТЕНЦИАЛЬНЫЙ отшельник
        if len(neighbors) < minPts:
            potential_outliers.add(point)

        # иначе это зеленая точка
        else:
            cluster = [point]  # создаем на ее основе новый кластер
            clusters.append(cluster)

            # обходим всех ее соседей
            for neighbor in neighbors:
                # если точку не посещали
                if neighbor not in visited:
                    visited.add(neighbor)
                    neighbor_neighbors = get_neighbors(neighbor, points, epsilon)

                    # если у точки достаточно соседей - это зеленая точка
                    if len(neighbor_neighbors) >= minPts:
                        # значит ее соседей мы тоже должны обойти, добавляем в список обхода
                        neighbors.extend(neighbor_neighbors)
                    # иначе это краевая точка
                    else:
                        edge_points.add(neighbor)
                        if neighbor in potential_outliers:
                            potential_outliers.remove(neighbor) # если была отшельником, теперь она больше не такая

                    cluster.append(neighbor) # добавляем в кластер в любом случае

                # если точка не в кластере, но ее посещали - значит она отшельник
                if neighbor not in cluster:
                    # тогда добавляем ее в текущий кластер как краевую
                    cluster.append(neighbor)
                    edge_points.add(neighbor)
                    # и убираем из отшельников
                    if neighbor in potential_outliers:
                        potential_outliers.remove(neighbor)

    return clusters, potential_outliers, edge_points

epsilon = 15
minPts = 3 # минимальное количество соседей
radius = 3 # радиус точки
points = []

pygame.init()
screen = pygame.display.set_mode((600, 400), pygame.RESIZABLE)
screen.fill("#FFFFFF")
pygame.display.update()
is_pressed = False
labels = []
clusters = []
potential_outliers = []

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.WINDOWRESIZED:
            screen.fill("#FFFFFF")
            for i in range(len(points)):
                pygame.draw.circle(screen, "black", point, radius)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                is_pressed = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_pressed = False
            elif event.button == 3:  # правая кнопка мыши
                pos = event.pos
                pygame.draw.circle(screen, "black", pos, radius)
                points.append(pos)

        if event.type == pygame.MOUSEMOTION and is_pressed:
            pos = event.pos
            if len(points) == 0 or dist(pos, points[-1]) > 20:
                near_points = brush(pos)
                for point in near_points:
                    pygame.draw.circle(screen, "black", point, radius)
                    points.append(point)
                pygame.draw.circle(screen, "black", pos, radius)
                points.append(pos)
        if event.type == pygame.KEYDOWN:

            # на SPACE запускается библиотечный DBSCAN (просто для сравнения)
            if event.key == pygame.K_SPACE:
                dbscan = DBSCAN(eps=epsilon, min_samples=minPts)
                dbscan.fit(points)
                labels = dbscan.labels_
                k = np.max(labels)
                colors = generate_colors(k)
                screen.fill("#FFFFFF")
                for i in range(len(points)):
                    color = colors[labels[i]] if labels[i] != -1 else (0, 0, 0)
                    pygame.draw.circle(screen, color, points[i], radius)
                print(k)

            # на ENTER запускается кастомный DBSCAN
            if event.key == pygame.K_RETURN:
                clusters, potential_outliers, edge_points = custom_dbscan(points, epsilon, minPts)
                screen.fill("#FFFFFF")

                # Раскрашиваем отшельников в красный
                for point in potential_outliers:
                    pygame.draw.circle(screen, (255, 0, 0), point, radius)  # красный цвет

                # Раскрашиваем кластеры
                for cluster in clusters:
                    for point in cluster:
                        if point in edge_points:
                            pygame.draw.circle(screen, (255, 255, 0), point, radius)  # желтый цвет для краевых точек
                        else:
                            pygame.draw.circle(screen, (0, 255, 0), point, radius)  # зеленый цвет для групп

                # рисуем круги вокруг краевых точек (просто чтобы посмотреть )
                for edge_point in edge_points:
                    pygame.draw.circle(screen, (0, 0, 255), edge_point, epsilon, 1)  # Синий цвет для кругов

            # на k кластеры раскрашиваются в разные цвета
            if event.key == pygame.K_k:

                # Получаем количество кластеров
                k = len(clusters)  # Количество кластеров
                colors = generate_colors(k)

                # Рисуем точки с цветами кластеров
                screen.fill("#FFFFFF")
                for cluster_index, cluster in enumerate(clusters):
                    color = colors[cluster_index]
                    for point in cluster:
                        pygame.draw.circle(screen, color, point, radius)

                # отдельно раскрашиваем отшельников
                for point in potential_outliers:
                    pygame.draw.circle(screen, (0, 0, 0), point, radius)  # черный цвет

                pygame.display.flip()
        pygame.display.flip()