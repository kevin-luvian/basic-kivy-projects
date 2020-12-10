import const


def generate_kdtree(boids):
    boids.sort(key=lambda boid: boid.pos[0])
    return KDTree(0, boids)


def create_boid_visibility_radius(boid):
    x = boid.pos[0] - const.BOID_VISIBILITY_RADIUS
    y = boid.pos[1] - const.BOID_VISIBILITY_RADIUS
    r = const.BOID_VISIBILITY_RADIUS * 2
    return [x, y, r, r]


def rectangle_contain_pos(rect, pos):
    check_horizontal = rect[0] < pos[0] < rect[0] + rect[2]
    check_vertical = rect[1] < pos[1] < rect[1] + rect[3]
    return check_horizontal and check_vertical


class KDTree:
    def __init__(self, align, boids):
        self.alignment = align
        self.median_pos = None
        self.boids = None
        self.left = None
        self.right = None
        self.create(boids)

    def create(self, boids):
        if len(boids) <= const.KD_MAX_BOID:
            self.boids = boids
        else:
            self.subdivide(boids)

    def subdivide(self, boids):
        # sorted_boids = sorted(boids, key=lambda boid: boid.pos[1])
        boids.sort(key=lambda boid: boid.pos[self.alignment])
        mid = len(boids) // 2
        self.set_median_pos(boids, mid)
        self.left = KDTree((self.alignment + 1) % 2, boids[:mid])
        self.right = KDTree((self.alignment + 1) % 2, boids[mid:])
        # print("align", self.alignment, "Med", self.median_pos)
        # print("boid 0", boids[0].pos, "last", boids[len(boids) - 1].pos)

    def set_median_pos(self, boids, mid):
        median = boids[mid].pos[self.alignment]

        if len(boids) % 2 == 0:
            median_2 = boids[mid - 1].pos[self.alignment]
            median = (median + median_2) / 2
            # print(median_2)
        # print("Median", median)

        self.median_pos = median

    def query(self, target_rectangle):
        query = []
        # print("this boids", self.boids)
        # print("this left", self.left)
        # print("this right", self.right)
        if self.median_pos is None or self.intersect(target_rectangle, self.alignment):
            if self.boids is not None:
                query += self.get_intersected_boids(target_rectangle)
        if self.left is not None and not self.check_target_is_right(target_rectangle):
            query += self.left.query(target_rectangle)
        if self.right is not None and not self.check_target_is_left(target_rectangle):
            query += self.right.query(target_rectangle)
        # print("final query", query)
        return query

    def check_target_is_left(self, target_rectangle):
        right_side = target_rectangle[self.alignment] + target_rectangle[self.alignment + 2]
        return right_side < self.median_pos

    def check_target_is_right(self, target_rectangle):
        left_side = target_rectangle[self.alignment]
        return left_side >= self.median_pos

    def get_intersected_boids(self, target_rectangle):
        res = []
        for boid in self.boids:
            if rectangle_contain_pos(target_rectangle, boid.pos):
                res.append(boid)
        return res

    def intersect(self, target_rectangle, pos_idx):
        is_intersected = target_rectangle[pos_idx] < self.median_pos < target_rectangle[pos_idx] + target_rectangle[
            pos_idx + 2]
        return is_intersected

# class Leaf:
#     def __init__(self, boids):
#         self.boids = boids
