import pygame
import sys
import random

# ウィンドウサイズ
WINDOW_WIDTH = 320
WINDOW_HEIGHT = 480

# グリッドの設定
GRID_SIZE = 32
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# 色の定義
WHITE = (255, 255, 255)


class Puyo(pygame.sprite.Sprite):
  def __init__(self, x, y, color):
    super().__init__()
    self.color = color
    self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
    self.image.fill(color)
    self.rect = self.image.get_rect()
    self.rect.x = x * GRID_SIZE
    self.rect.y = y * GRID_SIZE

  def move(self, dx, dy, grid):
    new_x = self.rect.x // GRID_SIZE + dx
    new_y = self.rect.y // GRID_SIZE + dy
    if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and not grid[new_y][new_x]:
      self.rect.x += dx * GRID_SIZE
      self.rect.y += dy * GRID_SIZE
      return True
    return False

  def rotate(self, grid, pivot):
    dx = self.rect.x // GRID_SIZE - pivot.rect.x // GRID_SIZE
    dy = self.rect.y // GRID_SIZE - pivot.rect.y // GRID_SIZE
    new_x = pivot.rect.x // GRID_SIZE - dy
    new_y = pivot.rect.y // GRID_SIZE + dx

    if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and not grid[new_y][new_x]:
      self.rect.x = new_x * GRID_SIZE
      self.rect.y = new_y * GRID_SIZE
      return True
    return False


def check_for_matches(x, y, grid, visited):
  color = grid[y][x].color
  visited[y][x] = True
  matches = [(x, y)]

  for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
    new_x, new_y = x + dx, y + dy
    if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and
            not visited[new_y][new_x] and grid[new_y][new_x] is not None and grid[new_y][new_x].color == color):
      matches.extend(check_for_matches(new_x, new_y, grid, visited))

  return matches


def remove_matches(matches, grid, all_sprites):
  for x, y in matches:
    all_sprites.remove(grid[y][x])
    grid[y][x] = None

  for x in range(GRID_WIDTH):
    for y in range(GRID_HEIGHT - 1, -1, -1):
      if grid[y][x] is None:
        continue

      new_y = y
      while new_y < GRID_HEIGHT - 1 and grid[new_y + 1][x] is None:
        grid[new_y][x].move(0, 1, grid)
        grid[new_y + 1][x] = grid[new_y][x]
        grid[new_y][x] = None
        new_y += 1


def main():
  pygame.init()
  screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
  pygame.display.set_caption("Puyo Puyo Sample")

  clock = pygame.time.Clock()
  all_sprites = pygame.sprite.Group()
  grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

  def generate_new_puyos():
    pivot_color = random.choice([pygame.Color("red"), pygame.Color(
        "green"), pygame.Color("blue"), pygame.Color("yellow")])
    satellite_color = random.choice([pygame.Color("red"), pygame.Color(
        "green"), pygame.Color("blue"), pygame.Color("yellow")])
    pivot = Puyo(GRID_WIDTH // 2, 0, pivot_color)
    satellite = Puyo(GRID_WIDTH // 2 + 1, 0, satellite_color)
    all_sprites.add(pivot, satellite)
    return pivot, satellite

  pivot, satellite = generate_new_puyos()
  fall_speed = 1
  counter = 0

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
      pivot.move(-1, 0, grid)
      satellite.move(-1, 0, grid)
    if keys[pygame.K_RIGHT]:
      pivot.move(1, 0, grid)
      satellite.move(1, 0, grid)
    if keys[pygame.K_DOWN]:
      fall_speed = 10
    else:
      fall_speed = 1
    if keys[pygame.K_UP]:
      satellite.rotate(grid, pivot)

    counter += 1
    if counter >= 60 // fall_speed:
      counter = 0
      if not pivot.move(0, 1, grid) or not satellite.move(0, 1, grid):
        grid[pivot.rect.y // GRID_SIZE][pivot.rect.x // GRID_SIZE] = pivot
        grid[satellite.rect.y //
             GRID_SIZE][satellite.rect.x //
                        GRID_SIZE] = satellite
        visited = [[False for _ in range(GRID_WIDTH)]
                   for _ in range(GRID_HEIGHT)]
        matches = []
        for y in range(GRID_HEIGHT):
          for x in range(GRID_WIDTH):
            if grid[y][x] is not None and not visited[y][x]:
              match = check_for_matches(x, y, grid, visited)
              if len(match) >= 4:
                matches.extend(match)
        if matches:
          remove_matches(matches, grid, all_sprites)
        pivot, satellite = generate_new_puyos()
        if not pivot.move(0, 0, grid) or not satellite.move(0, 0, grid):
          pygame.quit()
          sys.exit()

    screen.fill(WHITE)
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(60)


if __name__ == "__main__":
  main()
