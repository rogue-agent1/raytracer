#!/usr/bin/env python3
"""raytracer - ASCII ray tracer with spheres, planes, lighting, and shadows."""

import sys, math

class V3:
    __slots__ = ('x','y','z')
    def __init__(self, x=0,y=0,z=0): self.x=x;self.y=y;self.z=z
    def __add__(s,o): return V3(s.x+o.x,s.y+o.y,s.z+o.z)
    def __sub__(s,o): return V3(s.x-o.x,s.y-o.y,s.z-o.z)
    def __mul__(s,t): return V3(s.x*t,s.y*t,s.z*t)
    def dot(s,o): return s.x*o.x+s.y*o.y+s.z*o.z
    def length(s): return math.sqrt(s.dot(s))
    def norm(s):
        l=s.length()
        return V3(s.x/l,s.y/l,s.z/l) if l>0 else V3()

class Sphere:
    def __init__(self, center, radius, brightness=0.8):
        self.center=center;self.radius=radius;self.brightness=brightness
    def intersect(self, origin, direction):
        oc=origin-self.center
        b=2*oc.dot(direction)
        c=oc.dot(oc)-self.radius**2
        d=b*b-4*c
        if d<0: return None
        t=(-b-math.sqrt(d))/2
        if t>0.001: return t
        t=(-b+math.sqrt(d))/2
        return t if t>0.001 else None
    def normal(self, point):
        return (point-self.center).norm()

class Plane:
    def __init__(self, point, normal, brightness=0.5):
        self.point=point;self.normal_v=normal.norm();self.brightness=brightness
    def intersect(self, origin, direction):
        denom=self.normal_v.dot(direction)
        if abs(denom)<1e-6: return None
        t=(self.point-origin).dot(self.normal_v)/denom
        return t if t>0.001 else None
    def normal(self, point):
        return self.normal_v

def render(width=80, height=30, fov=60):
    objects = [
        Sphere(V3(0, 0, 5), 1, 0.9),
        Sphere(V3(2, 0.5, 4), 0.7, 0.7),
        Sphere(V3(-1.5, -0.3, 6), 1.2, 0.6),
        Plane(V3(0, -1, 0), V3(0, 1, 0), 0.4),
    ]
    light = V3(2, 3, -1).norm()
    aspect = width / height * 0.5
    fov_rad = math.radians(fov)
    chars = ' .:-=+*#%@'

    lines = []
    for row in range(height):
        line = ''
        for col in range(width):
            u = (2 * col / width - 1) * math.tan(fov_rad/2) * aspect
            v = (1 - 2 * row / height) * math.tan(fov_rad/2)
            direction = V3(u, v, 1).norm()
            origin = V3(0, 0, 0)

            closest_t = float('inf')
            hit_obj = None
            for obj in objects:
                t = obj.intersect(origin, direction)
                if t is not None and t < closest_t:
                    closest_t = t
                    hit_obj = obj

            if hit_obj:
                hit_point = origin + direction * closest_t
                normal = hit_obj.normal(hit_point)
                # diffuse lighting
                diffuse = max(0, normal.dot(light))
                # shadow check
                shadow = False
                shadow_origin = hit_point + normal * 0.001
                for obj in objects:
                    if obj is hit_obj: continue
                    if obj.intersect(shadow_origin, light) is not None:
                        shadow = True; break
                if shadow: diffuse *= 0.3
                # checkerboard for plane
                if isinstance(hit_obj, Plane):
                    cx = int(math.floor(hit_point.x)) + int(math.floor(hit_point.z))
                    if cx % 2 == 0: diffuse *= 0.6
                intensity = diffuse * hit_obj.brightness
                idx = min(len(chars)-1, int(intensity * (len(chars)-1)))
                line += chars[idx]
            else:
                line += ' '
        lines.append(line)
    return '\n'.join(lines)

def cmd_render(args):
    w = int(args[0]) if args else 80
    h = int(args[1]) if len(args) > 1 else 30
    print(f"Ray Tracer ({w}x{h})")
    print("Scene: 3 spheres + checkerboard plane + directional light + shadows\n")
    print(render(w, h))

def cmd_bench(args):
    import time
    w, h = 80, 30
    t0 = time.perf_counter()
    render(w, h)
    elapsed = time.perf_counter() - t0
    pixels = w * h
    print(f"\n{w}x{h} = {pixels} pixels in {elapsed:.3f}s ({pixels/elapsed:,.0f} pixels/s)")

CMDS = {
    'render': (cmd_render, '[W] [H] — render scene'),
    'bench': (cmd_bench, '— benchmark rendering'),
}

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print("Usage: raytracer <command> [args...]")
        for n, (_, d) in sorted(CMDS.items()):
            print(f"  {n:8s} {d}")
        sys.exit(0)
    cmd = sys.argv[1]
    if cmd not in CMDS: print(f"Unknown: {cmd}", file=sys.stderr); sys.exit(1)
    CMDS[cmd][0](sys.argv[2:])

if __name__ == '__main__':
    main()
