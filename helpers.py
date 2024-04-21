import pygame


class SpatialHashGrid:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.grid = {}

    def add_object(self, obj):
        # Convert pygame.Vector2 object to a format compatible with spatial hash grid
        obj_data = {
            'x': obj.x,
            'y': obj.y,
            'width': 1,  # Assuming width and height of 1 for pygame.Vector2 objects
            'height': 1
        }

        min_x = int(obj_data['x'] / self.cell_size)
        min_y = int(obj_data['y'] / self.cell_size)
        max_x = int((obj_data['x'] + obj_data['width']) / self.cell_size)
        max_y = int((obj_data['y'] + obj_data['height']) / self.cell_size)

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                cell_key = (x, y)
                if cell_key not in self.grid:
                    self.grid[cell_key] = []
                self.grid[cell_key].append(obj_data)

    def get_objects_in_cell(self, cell_key):
        return self.grid.get(cell_key, [])

    def get_objects_nearby(self, obj):
        obj_data = {
            'x': obj.x,
            'y': obj.y,
            'width': 1,  # Assuming width and height of 1 for pygame.Vector2 objects
            'height': 1
        }

        min_x = int(obj_data['x'] / self.cell_size)
        min_y = int(obj_data['y'] / self.cell_size)
        max_x = int((obj_data['x'] + obj_data['width']) / self.cell_size)
        max_y = int((obj_data['y'] + obj_data['height']) / self.cell_size)

        nearby_objects = []
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                nearby_objects.extend(self.grid.get((x, y), []))

        # Convert the list of dictionaries to a list of pygame.Vector2 objects
        nearby_objects = [pygame.Vector2(obj['x'], obj['y']) for obj in nearby_objects]
        return nearby_objects

    def get_all_objects(self):
        all_objects = []
        for cell_objects in self.grid.values():
            all_objects.extend(cell_objects)
        return all_objects
