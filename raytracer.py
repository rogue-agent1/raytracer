#!/usr/bin/env python3
"""Raytracer — renders spheres with lighting to PPM or ASCII."""
import sys, math

class Vec3:
    def __init__(self, x=0, y=0, z=0): self.x=x; self.y=y; self.z=z
    def __add__(s, o): return Vec3(s.x+o.x, s.y+o.y, s.z+o.z)
    def __sub__(s, o): return Vec3(s.x-o.x, s.y-o.y, s.z-o.z)
    def __mul__(s, t): return Vec3(s.x*t, s.y*t, s.z*t)
    def dot(s, o): return s.x*o.x+s.y*o.y+s.z*o.z
    def norm(s): l=math.sqrt(s.dot(s)); return s*(1/l) if l>0 else s
    def length(s): return math.sqrt(s.dot(s))

class Sphere:
    def __init__(self, center, radius, color):
        self.c=center; self.r=radius; self.color=color
    def intersect(self, origin, direction):
        oc = origin - self.c
        b = 2 * oc.dot(direction)
        c = oc.dot(oc) - self.r**2
        d = b*b - 4*c
        if d < 0: return None
        t = (-b - math.sqrt(d)) / 2
        return t if t > 0.001 else None

def trace(origin, direction, spheres, light):
    closest = None; min_t = float('inf')
    for s in spheres:
        t = s.intersect(origin, direction)
        if t and t < min_t: min_t = t; closest = s
    if not closest: return Vec3(0.1, 0.1, 0.2)  # sky
    hit = origin + direction * min_t
    normal = (hit - closest.c).norm()
    to_light = (light - hit).norm()
    diff = max(0, normal.dot(to_light))
    ambient = 0.15
    spec_dir = (to_light - normal * 2 * normal.dot(to_light) * (-1))
    spec = max(0, direction.dot(spec_dir.norm())) ** 32 * 0.5
    i = ambient + diff * 0.7 + spec
    return Vec3(min(1, closest.color.x*i), min(1, closest.color.y*i), min(1, closest.color.z*i))

def render(w=80, h=40, mode="ascii"):
    spheres = [
        Sphere(Vec3(0, 0, 5), 1.0, Vec3(1, 0.3, 0.3)),
        Sphere(Vec3(-2, 0.5, 6), 1.2, Vec3(0.3, 1, 0.3)),
        Sphere(Vec3(1.5, -0.5, 4), 0.7, Vec3(0.3, 0.3, 1)),
        Sphere(Vec3(0, -101, 5), 100, Vec3(0.8, 0.8, 0.8)),
    ]
    light = Vec3(2, -3, 1)
    cam = Vec3(0, 0, 0)
    aspect = w / h * 0.5
    chars = " .:-=+*#%@"
    lines = []
    for y in range(h):
        row = ""
        for x in range(w):
            u = (x / w - 0.5) * aspect * 2
            v = -(y / h - 0.5) * 2
            d = Vec3(u, v, 1).norm()
            color = trace(cam, d, spheres, light)
            if mode == "ascii":
                brightness = (color.x + color.y + color.z) / 3
                idx = min(len(chars)-1, int(brightness * len(chars)))
                row += chars[idx]
            else:
                row += f"{int(color.x*255)} {int(color.y*255)} {int(color.z*255)} "
        lines.append(row)
    if mode == "ppm":
        print(f"P3\n{w} {h}\n255")
    print("\n".join(lines))

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "ascii"
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    h = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    render(w, h, mode)
