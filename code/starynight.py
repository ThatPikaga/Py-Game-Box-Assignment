import pygame
import random


class StarfieldBackground:
    def __init__(self, width, height, star_count=150):
        self.width = width
        self.height = height
        self.stars = []

        for _ in range(star_count):
            self.stars.append(self._create_star(random_y=True))

    def _create_star(self, random_y=True):
        layer = random.choice([1,2,3])

        return {
            "x": random.randint(0, self.width),
            "y": random.randint(0, self.height) if random_y else 0,
            "speed": layer * 0.1,
            "radius": layer,
            "color": self._get_color(layer),
        }

    def _get_color(self, layer):
        if layer == 1:
            return (100, 100, 150)
        if layer == 2:
            return (180, 180, 220)
        return (255, 255, 255)

    def update(self):
        for star in self.stars:
            star["y"] += star["speed"]

            if star["y"] > self.height:
                fresh_star = self._create_star(random_y=False)
                star["x"] = fresh_star["x"]
                star["y"] = fresh_star["y"]
                star["speed"] = fresh_star["speed"]
                star["radius"] = fresh_star["radius"]
                star["color"] = fresh_star["color"]

    def draw(self, screen):
        screen.fill((5, 5, 15))

        for star in self.stars:
            pygame.draw.circle(
                screen, star["color"],
                (int(star["x"]), int(star["y"])),
                star["radius"],
            )


if __name__ == "__main__":
    pygame.init()

    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Starfield")

    clock = pygame.time.Clock()
    background = StarfieldBackground(WIDTH, HEIGHT, star_count=200)


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        background.update()
        background.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()