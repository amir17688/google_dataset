class Ball(object):
    # Class variables. These are shared amongst all instances of Ball.
    Spring = 0.05
    Gravity = 0.03
    Friction = -0.9

    def __init__(self, x, y, radius, index, others):
        self.x = x
        self.y = y
        self.radius = radius
        self.index = index
        self.others = others
        self.vx = 0
        self.vy = 0

    def collide(self):
        for other in self.others[self.index:]:
            dx = other.x - self.x
            dy = other.y - self.y
            minDist = other.radius + self.radius
            if dist(other.x, other.y, self.x, self.y) < minDist:
                angle = atan2(dy, dx)
                targetX = self.x + cos(angle) * minDist
                targetY = self.y + sin(angle) * minDist
                ax = (targetX - other.x) * Ball.Spring
                ay = (targetY - other.y) * Ball.Spring
                self.vx -= ax
                self.vy -= ay
                other.vx += ax
                other.vy += ay

    def move(self):
        self.vy += Ball.Gravity
        self.x += self.vx
        self.y += self.vy

        if self.x + self.radius > width:
            self.x = width - self.radius
            self.vx *= Ball.Friction
        elif self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= Ball.Friction
        if self.y + self.radius > height:
            self.y = height - self.radius
            self.vy *= Ball.Friction
        elif self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= Ball.Friction

    def display(self):
        ellipse(self.x, self.y, self.radius, self.radius)
#  rotation expressions. bTemp[0].position.x and
            #  bTemp[0].position.y will initialize automatically to 0.0, which
            #  is what you want since b[1] will rotate around b[0].
            bTemp[1].x = cosine * bVect.x + sine * bVect.y
            bTemp[1].y = cosine * bVect.y - sine * bVect.x

            # Rotate Temporary velocities.
            vTemp = [PVector(), PVector()]
            vTemp[0].x = cosine * self.velocity.x + sine * self.velocity.y
            vTemp[0].y = cosine * self.velocity.y - sine * self.velocity.x
            vTemp[1].x = cosine * other.velocity.x + sine * other.velocity.y
            vTemp[1].y = cosine * other.velocity.y - sine * other.velocity.x

            # Now that velocities are rotated, you can use 1D conservation of
            #  momentum equations to calculate the velocity along the x-
            #  axis.
            vFinal = [PVector(), PVector()]

            # Rotated velocity for b[0].
            vFinal[0].x = (((self.m - other.m) *
                            vTemp[0].x + 2 * other.m * vTemp[1].x) /
                          (self.m + other.m))
            vFinal[0].y = vTemp[0].y

            # Rotated velocity for b[0].
            vFinal[1].x = (((other.m - self.m) *
                            vTemp[1].x + 2 * self.m * vTemp[0].x) /
                          (self.m + other.m))
            vFinal[1].y = vTemp[1].y

            # Hack to avoid clumping.
            bTemp[0].x += vFinal[0].x
            bTemp[1].x += vFinal[1].x

            # Rotate ball positions and velocities back Reverse signs in trig
            #  expressions to rotate in the opposite direction.
            # Rotate balls.
            bFinal = [PVector(), PVector()]
            bFinal[0].x = cosine * bTemp[0].x - sine * bTemp[0].y
            bFinal[0].y = cosine * bTemp[0].y + sine * bTemp[0].x
            bFinal[1].x = cosine * bTemp[1].x - sine * bTemp[1].y
            bFinal[1].y = cosine * bTemp[1].y + sine * bTemp[1].x

            # Update balls to screen position.
            other.position.x = self.position.x + bFinal[1].x
            other.position.y = self.position.y + bFinal[1].y
            self.position.add(bFinal[0])

            # Update velocities.
            self.velocity.x = cosine * vFinal[0].x - sine * vFinal[0].y
            self.velocity.y = cosine * vFinal[0].y + sine * vFinal[0].x
            other.velocity.x = cosine * vFinal[1].x - sine * vFinal[1].y
            other.velocity.y = cosine * vFinal[1].y + sine * vFinal[1].x

    def display(self):
        noStroke()
        fill(204)
        ellipse(self.position.x, self.position.y, self.radius * 2, self.radius * 2)
