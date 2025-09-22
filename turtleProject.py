# Elizabeth Elden, 9/21/2025, Turtle Planet Generator

#Import all the fun things you need
import turtle
import random
import math

#Global stuff
WIDTH, HEIGHT = 900, 700
PLANET_RADIUS = 260
STAR_COUNT = random.randint(250, 1000)

#Set up the turtle, screen, etc...
screen = turtle.Screen()
screen.setup(WIDTH, HEIGHT)
screen.bgcolor("black")
screen.tracer(0)
t = turtle.Turtle()
t.hideturtle()
t.speed(0)
t.penup()

#Useful functions


def polar_to_cart(cx, cy, r, ang):
    #Polar to cartesan cords
    return cx + r * math.cos(ang), cy + r * math.sin(ang)

def point_in_poly(x, y, poly):
    #Determines whether something is a point in a polygon
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i] #End points of the current edge
        x2, y2 = poly[(i + 1) % n] #End points of the current edge
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1): #Checks if the ray passes
            inside = not inside
    return inside

#Draw stars
def draw_starfield(rng, count=STAR_COUNT):
    t.color("white")
    t.penup()
    for i in range(count):
        x = rng.randint(-WIDTH//2, WIDTH//2)
        y = rng.randint(-HEIGHT//2, HEIGHT//2)
        t.goto(x, y) #Go to random point
        size = rng.choice([1, 2, 3, 4]) #Choose random star size
        t.dot(size, "white")

#Base planet
def basePlanet(cx, cy, radius, water_hex, shading):
    t.color(water_hex) #Draws the basic circle
    t.penup()
    t.goto(cx, cy - radius)
    t.pendown()
    t.begin_fill()
    t.circle(radius)
    t.end_fill()
    t.penup()

    def hex_to_rgb(h):
        #Changes hexadecimal into rgb
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) #Does the cool math stuff

    def darker(rgb, factor):
        #Darkens an rgb number by the factor
        return tuple(max(0, int(c * factor)) for c in rgb)

    screen.colormode(255) #Uses RBG to 255
    base_rgb = hex_to_rgb(water_hex)
    rings = 18 #Number of different colors on planet
    for i in range(1, rings + 1):
        f = i / (rings + 1)
        factor = 1 - 0.55 * f #How much darker each ring should be
        c = darker(base_rgb, factor) #Darken color
        t.color(c)
        t.penup()
        t.goto(cx, cy - radius + i * (radius * 0.01)) #Go to the ring poisition
        t.pendown()
        t.begin_fill()
        t.circle(radius - i * (radius * 0.01)) #Draw circle
        t.end_fill()
        t.penup()
    screen.colormode(1.0) #Go back to normal RGB

#Creates continent base
def make_contour_local(rng, avg_radius=80, points=28, jitter=0.5, smoothing=2):
    angles = [i * 2 * math.pi / points for i in range(points)] #Create angles for the circle and draw points
    vals = []
    r = avg_radius
    for _ in range(points): #Jitter the base.
        r = max(6, r + rng.uniform(-jitter * avg_radius, jitter * avg_radius))
        vals.append(r)
    for _ in range(smoothing): #Smooth the base
        vals = [(vals[i-1] + vals[i] + vals[(i+1) % points]) / 3 for i in range(points)]
    return [(vals[i] * math.cos(angles[i]), vals[i] * math.sin(angles[i])) for i in range(points)]

#Make planet base longitude and latitude
def transform_to_planet(contour, cx, cy, planet_r, lon, lat, sx, sy, rot, clamp_margin=6):
    lat_factor = math.cos(lat * math.pi / 2)
    tx = planet_r * 0.4 * math.cos(lon) * lat_factor
    ty = planet_r * 0.4 * math.sin(lon) * lat_factor * (1 - 0.2 * lat)
    max_r = planet_r - clamp_margin
    transformed = []
    for (x, y) in contour:
        # scale, rotate, translate
        x *= sx; y *= sy
        xr = x * math.cos(rot) - y * math.sin(rot)
        yr = x * math.sin(rot) + y * math.cos(rot)
        X = cx + xr + tx
        Y = cy + yr + ty
        
        dist = math.hypot(X - cx, Y - cy)
        if dist > max_r:
            ratio = max_r / dist
            X = cx + (X - cx) * ratio
            Y = cy + (Y - cy) * ratio
        transformed.append((X, Y))
    return transformed

#Fill continents
def fill_polygon(turtle, poly, color_hex):
    if not poly: return
    turtle.penup()
    turtle.color(color_hex)
    turtle.goto(poly[0])
    turtle.pendown()
    turtle.begin_fill()
    for p in poly[1:]:  #go to each point and fill it in
        turtle.goto(p)
    turtle.goto(poly[0])
    turtle.end_fill()
    turtle.penup()

#Add details to the land
def add_blobs_inside(turtle, poly, rng, cx, cy, planet_r,
                     blob_count=(18,60), blob_radius=(3,18), avoid_rim=6, land_color="#1d5212"):
    turtle.color(land_color)
    turtle.penup()
    minx = max(min(p[0] for p in poly), cx - planet_r + avoid_rim) #range for circles
    maxx = min(max(p[0] for p in poly), cx + planet_r - avoid_rim)
    miny = max(min(p[1] for p in poly), cy - planet_r + avoid_rim)
    maxy = min(max(p[1] for p in poly), cy + planet_r - avoid_rim)
    count = rng.randint(*blob_count)
    for _ in range(count):
        for i in range(200):
            bx = rng.uniform(minx, maxx)
            by = rng.uniform(miny, maxy)
            if not point_in_poly(bx, by, poly):
                continue
            rblob = rng.uniform(blob_radius[0], blob_radius[1])
            if math.hypot(bx - cx, by - cy) + rblob > planet_r - avoid_rim:
                continue
            turtle.goto(bx, by)
            turtle.pendown()
            turtle.begin_fill()
            turtle.circle(rblob)
            turtle.end_fill()
            turtle.penup()
            break

#Add le clouds
def draw_clouds(cx, cy, radius, rng, count=10):
    t.penup()
    for _ in range(count): #How many clouds you want
        lon = rng.uniform(0, 2*math.pi)
        rpos = radius * rng.uniform(0.12, 0.75)
        x, y = polar_to_cart(cx, cy, rpos, lon)
        blobs = rng.randint(3,6)
        for _ in range(blobs):
            bx = x + rng.uniform(-26, 26)
            by = y + rng.uniform(-18, 18)
            rblob = rng.uniform(6, 14)
            if math.hypot(bx - cx, by - cy) + rblob > radius - 2:
                continue
            t.goto(bx, by)
            t.color("#ffffff")
            t.pendown()
            t.begin_fill()
            t.circle(rblob)
            t.end_fill()
            t.penup()

#Draw the scene onto the screen
def draw_scene(seed=None): #Can change seed to make it the same DOESNT WORK??
    if seed is None:
        seed = random.randint(0, 1_000_000)
    rng = random.Random(seed)

    draw_starfield(rng, STAR_COUNT)

    water_hex = rng.choice(["#2b6fd6", "#1b4f8b", "#1a5aa1"])
    land_choices = ["#1d5212", "#2e7b3b", "#6a5a2a"]

    basePlanet(0, 0, PLANET_RADIUS, water_hex, shading=True)

    continents = []
    attempts = 0
    target_continents = random.randint(1, 4)  # number of distinct large continents
    while len(continents) < target_continents and attempts < 200:
        attempts += 1
        subseed = rng.randint(0, 2_000_000)
        subrng = random.Random(subseed)
        avg_rad = rng.uniform(60, 110)  # size of continent
        points = int(rng.uniform(14, 30))
        contour_local = make_contour_local(subrng, avg_radius=avg_rad, points=points, jitter=0.7, smoothing=3)
        lon = rng.uniform(0, 2*math.pi)
        lat = rng.uniform(-0.6, 0.6)
        sx = rng.uniform(0.6, 1.4)
        sy = rng.uniform(0.6, 1.2)
        rot = rng.uniform(0, 2*math.pi)
        poly = transform_to_planet(contour_local, 0, 0, PLANET_RADIUS, lon, lat, sx, sy, rot, clamp_margin=8)

        cx_mean = sum(p[0] for p in poly)/len(poly)
        cy_mean = sum(p[1] for p in poly)/len(poly)
        max_dist = max(math.hypot(px - cx_mean, py - cy_mean) for (px, py) in poly)
        too_close = False
        for (ocx, ocy, orad) in continents:
            if math.hypot(cx_mean - ocx, cy_mean - ocy) < (max_dist + orad + 40): 
                too_close = True
                break
        if math.hypot(cx_mean, cy_mean) > PLANET_RADIUS * 0.30:
            too_close = True
        if not too_close:
            continents.append((cx_mean, cy_mean, max_dist))
            fill_polygon(t, poly, rng.choice(land_choices))
            add_blobs_inside(t, poly, rng, 0, 0, PLANET_RADIUS,
                             blob_count=(12, 40), blob_radius=(3, 14), avoid_rim=8,
                             land_color=rng.choice(land_choices))

    island_clusters = 5 + rng.randint(0, 6)
    clusters = 0
    attempts = 0
    while clusters < island_clusters and attempts < 300:
        attempts += 1
        subrng = random.Random(rng.randint(0, 3_000_000))
        contour_local = make_contour_local(subrng, avg_radius=rng.uniform(8, 32),
                                           points=int(rng.uniform(8, 18)),
                                           jitter=1.0, smoothing=2)
        lon = rng.uniform(0, 2*math.pi)
        lat = rng.uniform(-0.8, 0.8)
        sx = rng.uniform(0.5, 1.2)
        sy = rng.uniform(0.5, 1.2)
        rot = rng.uniform(0, 2*math.pi)
        poly = transform_to_planet(contour_local, 0, 0, PLANET_RADIUS, lon, lat, sx, sy, rot, clamp_margin=8)
        cx_mean = sum(p[0] for p in poly)/len(poly)
        cy_mean = sum(p[1] for p in poly)/len(poly)
        dist_to_any = min(math.hypot(cx_mean - ocx, cy_mean - ocy) - orad for (ocx, ocy, orad) in continents) if continents else 9999
        if dist_to_any < 30:  # too close to continent, skip to keep oceans
            continue
        fill_polygon(t, poly, rng.choice(land_choices))
        add_blobs_inside(t, poly, rng, 0, 0, PLANET_RADIUS,
                         blob_count=(6, 20), blob_radius=(2, 8), avoid_rim=8,
                         land_color=rng.choice(land_choices))
        clusters += 1

    #Clouds
    draw_clouds(0, 0, PLANET_RADIUS, rng, count=8 + rng.randint(0, 8))

    screen.update()

seed_arg = None
draw_scene(seed_arg)
turtle.done()