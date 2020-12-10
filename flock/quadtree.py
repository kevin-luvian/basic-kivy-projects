import const


def generate_quadtree(boids, width, height):
    quadtree = QuadTree([0, 0, width, height])
    for boid in boids:
        quadtree.insert(boid)
    return quadtree


def create_boid_visibility_radius(boid):
    x = boid.pos[0] - const.BOID_VISIBILITY_RADIUS
    y = boid.pos[1] - const.BOID_VISIBILITY_RADIUS
    r = const.BOID_VISIBILITY_RADIUS * 2
    return [x, y, r, r]


def intersect_rectangles(rect_a, rect_b):
    check_left_false = rect_a[0] > rect_b[0] + rect_b[2]
    check_right_false = rect_a[0] + rect_a[2] < rect_b[0]
    check_bottom_false = rect_a[1] > rect_b[1] + rect_b[3]
    check_top_false = rect_a[1] + rect_a[3] < rect_b[1]
    return not (check_left_false or check_right_false or check_bottom_false or check_top_false)


def rectangle_contain_pos(rect, pos):
    check_horizontal = rect[0] < pos[0] < rect[0] + rect[2]
    check_vertical = rect[1] < pos[1] < rect[1] + rect[3]
    return check_horizontal and check_vertical


class QuadTree:
    def __init__(self, bound):
        self.boundary = bound
        self.isDivided = False
        self.boids = []
        self.qt_ul = None
        self.qt_ur = None
        self.qt_bl = None
        self.qt_br = None

    def insert(self, boid):
        if rectangle_contain_pos(self.boundary, boid.pos):
            if len(self.boids) < const.QT_MAX_BOID:
                self.boids.append(boid)
            else:
                self.insert_to_sub_quadtree(boid)

    def insert_to_sub_quadtree(self, boid):
        if not self.isDivided:
            self.subdivide()
        self.qt_ul.insert(boid)
        self.qt_ur.insert(boid)
        self.qt_bl.insert(boid)
        self.qt_br.insert(boid)

    def subdivide(self):
        sub_h = self.boundary[3] / 2
        sub_w = self.boundary[2] / 2
        rect_ul = [self.boundary[0], self.boundary[1] + sub_h, sub_w, sub_h]
        rect_ur = [self.boundary[0] + sub_w, self.boundary[1] + sub_h, sub_w, sub_h]
        rect_bl = [self.boundary[0], self.boundary[1], sub_w, sub_h]
        rect_br = [self.boundary[0] + sub_w, self.boundary[1], sub_w, sub_h]

        self.qt_ul = QuadTree(rect_ul)
        self.qt_ur = QuadTree(rect_ur)
        self.qt_bl = QuadTree(rect_bl)
        self.qt_br = QuadTree(rect_br)

        self.isDivided = True

    def query(self, target_rectangle):
        boids_arr = []
        if not intersect_rectangles(self.boundary, target_rectangle):
            return boids_arr
        for boid in self.boids:
            if rectangle_contain_pos(target_rectangle, boid.pos):
                boids_arr.append(boid)
        if self.isDivided:
            boids_arr += self.qt_ul.query(target_rectangle)
            boids_arr += self.qt_ur.query(target_rectangle)
            boids_arr += self.qt_bl.query(target_rectangle)
            boids_arr += self.qt_br.query(target_rectangle)
        return boids_arr

# class Rectangle:
#     def __init__(self, x, y, w, h):
#         self.x = x
#         self.y = y
#         self.w = w
#         self.h = h
#
#     def contains(self, boid):
#         # print("boid x", boid.pos[0], "y", boid.pos[1])
#         # print("boundary", self.to_string())
#         return self.x < boid.pos[0] < (self.x + self.w) and self.y < boid.pos[1] < (self.y + self.h)
#
#     def intersect(self, target):
#         check_left_false = self.x > target.x + target.w
#         check_right_false = self.x + self.w < target.x
#         check_bottom_false = self.y > target.y + target.h
#         check_top_false = self.y + self.h < target.y
#         return not (check_left_false or check_right_false or check_bottom_false or check_top_false)
#
#     def to_string(self):
#         return "x", self.x, "y", self.y, "w", self.w, "h", self.h
