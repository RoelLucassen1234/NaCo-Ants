import pygame
import Nest
from foodV1.Food import Food


class SpatialHashGrid:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.grid = {}

        self.type_index = {}  # Additional index for objects by type

    def add_object(self, obj):
        # Convert pygame.Vector2 object to a format compatible with spatial hash grid
        try:
            min_x = int(obj.position[0] / self.cell_size)
            min_y = int(obj.position[1] / self.cell_size)
            max_x = int((obj.position[0] + obj.width) / self.cell_size)
            max_y = int((obj.position[1] + obj.height) / self.cell_size)
        except AttributeError:  # Assuming obj is a dictionary with 'x', 'y', 'width', and 'height'
            min_x = int(obj['x'] / self.cell_size)
            min_y = int(obj['y'] / self.cell_size)
            max_x = int((obj['x'] + obj['width']) / self.cell_size)
            max_y = int((obj['y'] + obj['height']) / self.cell_size)

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                cell_key = (x, y)
                if cell_key not in self.grid:
                    self.grid[cell_key] = []
                self.grid[cell_key].append(obj)

        # Update type index
        obj_type = type(obj)
        if obj_type not in self.type_index:
            self.type_index[obj_type] = []
        self.type_index[obj_type].append(obj)

    def get_objects_in_cell(self, cell_key):
        return self.grid.get(cell_key, [])

    def get_objects_nearby(self, obj, width=15):
        try:

            min_x = int(obj.position[0] / self.cell_size)
            min_y = int(obj.position[1] / self.cell_size)
            max_x = int((obj.position[0] + width) / self.cell_size)
            max_y = int((obj.position[1] + width) / self.cell_size)
        except:
            obj_data = {
                'x': obj.x,
                'y': obj.y,
                'width': width,  # Assuming width and height of 1 for pygame.Vector2 objects
                'height': width

            }
            min_x = int(obj_data['x'] / self.cell_size)
            min_y = int(obj_data['y'] / self.cell_size)
            max_x = int((obj_data['x'] + obj_data['width']) / self.cell_size)
            max_y = int((obj_data['y'] + obj_data['height']) / self.cell_size)

        nearby_objects = []
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                nearby_objects.extend(self.grid.get((x, y), []))
        nearby_objects.extend(self.get_objects_of_type(Nest))
        nearby_objects.extend(self.get_objects_of_type(Food))
        # Convert the list of dictionaries to a list of pygame.Vector2 objects
        # nearby_objects = [pygame.Vector2(obj['x'], obj['y']) for obj in nearby_objects]
        return nearby_objects

    def get_all_objects(self):
        all_objects = []
        for cell_objects in self.grid.values():
            all_objects.extend(cell_objects)
        return all_objects

    def remove_object(self, obj):
        try:
            min_x = int(obj.position[0] / self.cell_size)
            min_y = int(obj.position[1] / self.cell_size)
            max_x = int((obj.position[0] + obj.width) / self.cell_size)
            max_y = int((obj.position[1] + obj.height) / self.cell_size)
        except AttributeError:  # Assuming obj is a dictionary with 'x', 'y', 'width', and 'height'
            min_x = int(obj['x'] / self.cell_size)
            min_y = int(obj['y'] / self.cell_size)
            max_x = int((obj['x'] + obj['width']) / self.cell_size)
            max_y = int((obj['y'] + obj['height']) / self.cell_size)

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                cell_key = (x, y)
                if cell_key in self.grid:
                    if obj in self.grid[cell_key]:
                        self.grid[cell_key].remove(obj)

        # Update type index
        obj_type = type(obj)
        if obj_type in self.type_index:
            if obj in self.type_index[obj_type]:
                self.type_index[obj_type].remove(obj)

    def get_objects_of_type(self, obj_type):
        return self.type_index.get(obj_type, [])

    def detect_collision(self, position):
        """
        Detect collision with food at a given position.
        Returns True if collision is detected, False otherwise.
        """
        cell_x = int(position[0] / self.cell_size)
        cell_y = int(position[1] / self.cell_size)
        nearby_objects = self.get_objects_in_cell((cell_x, cell_y))
        for obj in nearby_objects:
            # Assuming obj has a 'type' attribute to identify it as food
            if obj.get('type') == 'food' and obj.get('position') == position:
                return True
        return False