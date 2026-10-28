import math, os

OUT = os.path.dirname(os.path.abspath(__file__))

def sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def write_stl(name, tris):
    with open(os.path.join(OUT, name), "w") as f:
        f.write("solid %s\n" % name[:-4])
        n_ok = 0
        for a, b, c in tris:
            n = cross(sub(b, a), sub(c, a))
            L = math.sqrt(n[0]**2 + n[1]**2 + n[2]**2)
            if L < 1e-15:
                continue
            n = (n[0]/L, n[1]/L, n[2]/L)
            f.write("facet normal %e %e %e\n outer loop\n" % n)
            for v in (a, b, c):
                f.write("  vertex %e %e %e\n" % v)
            f.write(" endloop\nendfacet\n")
            n_ok += 1
        f.write("endsolid %s\n" % name[:-4])
    xs = [v[0] for t in tris for v in t]
    ys = [v[1] for t in tris for v in t]
    zs = [v[2] for t in tris for v in t]
    print("%-18s %3d tris   size mm: %.1f x %.1f x %.1f" % (
        name, n_ok, (max(xs)-min(xs))*1000, (max(ys)-min(ys))*1000, (max(zs)-min(zs))*1000))
    return (max(xs)-min(xs))*1000, (max(ys)-min(ys))*1000, (max(zs)-min(zs))*1000

def box(cx, cy, cz, sx, sy, sz):
    p = lambda i, j, k: (cx + (i-0.5)*sx, cy + (j-0.5)*sy, cz + (k-0.5)*sz)
    faces = [((1,0,0),(1,1,0),(1,1,1),(1,0,1)), ((0,0,0),(0,0,1),(0,1,1),(0,1,0)),
             ((0,1,0),(0,1,1),(1,1,1),(1,1,0)), ((0,0,0),(1,0,0),(1,0,1),(0,0,1)),
             ((0,0,1),(1,0,1),(1,1,1),(0,1,1)), ((0,0,0),(0,1,0),(1,1,0),(1,0,0))]
    t = []
    for q in faces:
        a, b, c, d = [p(*i) for i in q]
        t += [(a, b, c), (a, c, d)]
    return t

def cyl_z(r, h, zc=0.0, n=48):
    t = []
    for i in range(n):
        a0, a1 = 2*math.pi*i/n, 2*math.pi*(i+1)/n
        b0 = (r*math.cos(a0), r*math.sin(a0), zc-h/2); b1 = (r*math.cos(a1), r*math.sin(a1), zc-h/2)
        t0 = (b0[0], b0[1], zc+h/2);                   t1 = (b1[0], b1[1], zc+h/2)
        t += [(b0, b1, t1), (b0, t1, t0)]
        t.append(((0, 0, zc+h/2), t0, t1))
        t.append(((0, 0, zc-h/2), b1, b0))
    return t

def sphere(r, nlat=16, nlon=32):
    v = lambda i, j: (r*math.sin(math.pi*i/nlat)*math.cos(2*math.pi*j/nlon),
                      r*math.sin(math.pi*i/nlat)*math.sin(2*math.pi*j/nlon),
                      r*math.cos(math.pi*i/nlat))
    t = []
    for i in range(nlat):
        for j in range(nlon):
            t.append((v(i, j), v(i+1, j), v(i+1, j+1)))
            t.append((v(i, j), v(i+1, j+1), v(i, j+1)))
    return t

def to_y(tris, dy=0.0):
    m = lambda p: (p[0], p[2] + dy, -p[1])
    return [tuple(m(v) for v in t) for t in tris]

# 1. chassis plate 145 x 120 x 4 mm
c = write_stl("flat_chasis.stl", box(0.0192, 0.0043, 0.002, 0.145, 0.12, 0.004))

# 2. caster: ball + post
write_stl("caster_wheel.stl", sphere(0.0095) + cyl_z(0.004, 0.012, zc=0.006, n=24))

# 3. wheels: r 25.5 mm, width 30 mm, axis along Y
for n in ("left_wheel.stl", "right_wheel.stl"):
    write_stl(n, to_y(cyl_z(0.0255, 0.03, n=64)))

# 4. axles: r 4 mm, length 45 mm
write_stl("left_axle.stl",  to_y(cyl_z(0.004, 0.045, n=24), dy=+0.0225))
write_stl("right_axle.stl", to_y(cyl_z(0.004, 0.045, n=24), dy=-0.0225))

print("Chassis within 150x150x40 mm limit:", c[0] <= 150 and c[1] <= 150 and c[2] <= 40)