# Define Rectangle class
class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def intersects_field_of_view(self, field_of_view):
        for point in field_of_view:
            if self.contains_point(point):
                return True
        return False
    def contains_point(self, point):
        return (self.x <= point[0] <= self.x + self.width and
                self.y <= point[1] <= self.y + self.height)

    def intersects(self, other):
        return not (self.x + self.width < other.x or
                    other.x + other.width < self.x or
                    self.y + self.height < other.y or
                    other.y + other.height < self.y)


# Define QuadTreeNode class
class QuadTreeNode:
    def __init__(self, boundary):
        self.boundary = boundary  # Boundary of the node (rectangle)
        self.objects = []  # Objects contained in this node
        self.children = [None, None, None, None]  # Children nodes (NW, NE, SW, SE)
        self.field_of_view = None  # Field of view polygon

    def insert(self, obj):
        # If the object is not contained in the node's boundary, ignore it
        if not self.boundary.contains_point(obj):
            return False

        # If the node exceeds its capacity and hasn't been subdivided yet, subdivide
        if len(self.objects) >= 10 and not self.children:
            self.subdivide()

        # If the node has children, insert the object into one of them
        if self.children:
            for child in self.children:
                if child is not None:
                    if child.insert(obj):
                        return True

        # Add the object to this node
        self.objects.append(obj)
        return True

    def is_inside_triangle(point, vertices):
        # Calculate barycentric coordinates of the point with respect to the triangle
        v0, v1, v2 = vertices
        total_area = 0.5 * (-v1[1] * v2[0] + v0[1] * (-v1[0] + v2[0]) + v0[0] * (v1[1] - v2[1]) + v1[0] * v2[1])
        barycentric_coordinates = [
            0.5 * (-v1[1] * v2[0] + v0[1] * (-v1[0] + v2[0]) + (v1[0] * v2[1] - v1[1] * v2[0]) * point[0] + v0[0] * (
                        v1[1] - v2[1])) / total_area,
            0.5 * (v0[1] * v2[0] - v0[0] * v2[1] + (v2[1] - v0[1]) * point[0] + (v0[0] - v2[0]) * point[
                1]) / total_area,
            0.5 * (v0[0] * v1[1] - v0[1] * v1[0] + (v0[1] - v1[1]) * point[0] + (v1[0] - v0[0]) * point[1]) / total_area
        ]

        # Check if the barycentric coordinates are within the range [0, 1]
        return all(0 <= coord <= 1 for coord in barycentric_coordinates)
    def query(self, field_of_view):
        objects_in_range = []
        # If the boundary of the node does not intersect with the field of view,
        # no need to search further
        if not self.boundary.intersects_field_of_view(field_of_view):
            return objects_in_range

        # Check if any object in this node is within the field of view
        for obj in self.objects:
            if is_inside_triangle(obj, field_of_view):
                objects_in_range.append(obj)

        # If the node has children, recursively query them
        if self.children:
            for child in self.children:
                objects_in_range.extend(child.query(field_of_view))

        return objects_in_range

    def subdivide(self):
        x, y = self.boundary.x, self.boundary.y
        w, h = self.boundary.width / 2, self.boundary.height / 2

        # Create child nodes (NW, NE, SW, SE)
        self.children[0] = QuadTreeNode(Rectangle(x, y, w, h))  # NW
        self.children[1] = QuadTreeNode(Rectangle(x + w, y, w, h))  # NE
        self.children[2] = QuadTreeNode(Rectangle(x, y + h, w, h))  # SW
        self.children[3] = QuadTreeNode(Rectangle(x + w, y + h, w, h))  # SE

        # Move objects to appropriate child nodes
        for obj in self.objects:
            for child in self.children:
                if child.boundary.contains_point(obj):
                    child.insert(obj)

        # Clear objects from this node after subdivision
        self.objects = []
