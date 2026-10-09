"""Funções puras: geometria e decisão podem ser testadas sem iniciar ROS."""
import math

def wrap(angle):
    return math.atan2(math.sin(angle), math.cos(angle))

def scan_points(ranges, angle_min, increment, rmin, rmax, offset_x):
    """+inf = sem retorno; NaN/valores inválidos não são espaço conhecido."""
    points, valid = [], 0
    for i, r in enumerate(ranges):
        if math.isinf(r) and r > 0:
            valid += 1
        elif math.isfinite(r) and rmin <= r <= rmax:
            valid += 1
            a = angle_min + i * increment
            points.append((offset_x + r * math.cos(a), r * math.sin(a)))
    return points, valid / max(1, len(ranges))

def corridor_clear(points, heading, length, radius):
    """Corredor com margem circular; testa o segmento e sua extremidade."""
    c, s = math.cos(heading), math.sin(heading)
    for x, y in points:
        along, across = x*c + y*s, -x*s + y*c
        nearest = max(0.0, min(length, along))
        if math.hypot(along-nearest, across) < radius:
            return False
    return True

def choose_heading(points, desired, length, radius, previous):
    candidates = [desired] + [math.radians(a) for a in range(-90,90,10)]

    free = []
    free_bool=[]
    for h in candidates:
        if corridor_clear(points,h,length,radius):
            free.append(h)
            free_bool.append(True)
        else:
            free_bool.append(False)

    msg = []
    sector = [free_bool[0:6], free_bool[6:12], free_bool[12:18]]

    for i, s in enumerate(sector):
        if not all(s):
            msg.append(f"SETOR {i}: OCUPADO")
        else:
            msg.append(f"SETOR {i}: LIVRE")

    if not free:
        return None
    # A continuidade reduz alternância esquerda/direita, mas não garante progresso.
    return [min(free, key=lambda h: abs(wrap(h-desired)) + .25*abs(wrap(h-previous))), msg]
