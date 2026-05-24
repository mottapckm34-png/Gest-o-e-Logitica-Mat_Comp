WIDTH = 600
HEIGHT = 400

# Physics parameters
DT = 0.03
G = 100.0          # constant downward force per unit mass
DRAG = 2.0         # viscous damping coefficient
REP_STRENGTH = 2000.0
OBSTACLE_R = 35.0

# Ball state
ball_r = 10
x = WIDTH / 2.0
y = ball_r + 2
vx = 0.0
vy = 0.0

# Obstacle at lower middle, slightly right
ox = 1.01 * WIDTH / 2.0
oy = 285.0

running = True

def obstacle_force(px, py):
    dx = px - ox
    dy = py - oy
    r = math.sqrt(dx * dx + dy * dy)

    if r < 1e-6:
        return (0.0, 0.0)

    if r < OBSTACLE_R:
        r = OBSTACLE_R

    # Exponential decay: at 2R, exp(-4) ~ 1.8%
    # If you want even steeper, increase 4.0.
    mag = REP_STRENGTH * math.exp(-4.0 * (r / OBSTACLE_R - 1.0))

    return (mag * dx / r, mag * dy / r)

def total_force(px, py, vx, vy):
    fx_rep, fy_rep = obstacle_force(px, py)
    fx_drag = -DRAG * vx
    fy_drag = -DRAG * vy
    fy_const = G
    return (fx_rep + fx_drag, fy_rep + fy_drag + fy_const)

def update():
    global x, y, vx, vy

    fx, fy = total_force(x, y, vx, vy)

    # Explicit Euler
    vx += fx * DT
    vy += fy * DT
    x += vx * DT
    y += vy * DT

    # Soft walls
    if x < ball_r:
        x = ball_r
        vx = -0.6 * vx
    if x > WIDTH - ball_r:
        x = WIDTH - ball_r
        vx = -0.6 * vx
    if y < ball_r:
        y = ball_r
        vy = -0.6 * vy
    if y > HEIGHT - ball_r:
        y = HEIGHT - ball_r
        vy = -0.6 * vy

def draw_arrow(canvas, p1, p2, color, width=2):
    canvas.draw_line(p1, p2, width, color)
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    ang = math.atan2(dy, dx)
    head = 8
    a1 = ang + math.pi * 0.8
    a2 = ang - math.pi * 0.8
    p3 = (p2[0] + head * math.cos(a1), p2[1] + head * math.sin(a1))
    p4 = (p2[0] + head * math.cos(a2), p2[1] + head * math.sin(a2))
    canvas.draw_line(p2, p3, width, color)
    canvas.draw_line(p2, p4, width, color)

def field_vector(px, py):
    fx, fy = total_force(px, py, 0.0, 0.0)
    return fx, fy

def draw(canvas):
    canvas.draw_line((0, 0), (WIDTH, 0), 2, "Black")
    canvas.draw_line((0, 0), (0, HEIGHT), 2, "Black")
    canvas.draw_line((WIDTH - 1, 0), (WIDTH - 1, HEIGHT), 2, "Black")
    canvas.draw_line((0, HEIGHT - 1), (WIDTH, HEIGHT - 1), 2, "Black")

    canvas.draw_circle((ox, oy), OBSTACLE_R, 2, "Red", "Pink")
    canvas.draw_circle((ox, oy), 4, 1, "Red", "Red")

    # Force field arrows on a coarse grid
    scale = 0.015
    for gx in range(60, WIDTH - 60, 30):
        for gy in range(60, HEIGHT - 60, 30):
            fx, fy = field_vector(gx, gy)
            mag = math.sqrt(fx * fx + fy * fy)
            if mag > 1e-6:
                l = max(10.0, min(28.0, mag * scale))
                ux = fx / mag
                uy = fy / mag
                p1 = (gx, gy)
                p2 = (gx + ux * l, gy + uy * l)
                draw_arrow(canvas, p1, p2, "Blue", 1)

    canvas.draw_circle((x, y), ball_r, 2, "Green", "Orange")
    canvas.draw_text("Euler + gravity + viscous drag + repulsive obstacle", (10, 20), 18, "Black")
    canvas.draw_text("Ball starts at rest, at top center", (10, 40), 14, "Black")

def tick():
    if running:
        update()

frame = simplegui.create_frame("Ball in Force Field", WIDTH, HEIGHT)
frame.set_canvas_background("Teal")
frame.set_draw_handler(draw)
timer = simplegui.create_timer(int(DT * 1000), tick)
timer.start()
frame.start()