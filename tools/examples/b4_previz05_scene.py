# -*- coding: utf-8 -*-
# ★ 본보기(원본 경로 상수 그대로) — 실행을 보장하지 않는다. 베껴 쓰지 말고 «이런 식으로 짠다»를 본다.
# 보여 주는 것: 블렌더 프리비즈 장면(클라우드 블렌더에 그대로 넣는 bpy 코드): 단순 도형으로 단지·숲·강·사람을 깔고 카메라를 atan2 로 목표를 보게 프레임마다 계산
# 원본: D:/영상제작/도구/광고편집/b4_previz05_scene.py (통과/반려 이력은 references/feedback-log.md)
# 모듈 대응: bisa_web_vs_instant → ae_scene · bisa_meta_sfx / bisa_toc_cards.by_name → sfx · rf3_ae·rule_check·lec_xml·design_layers → tools/ 같은 이름.
# 이 폴더에 없는 모듈(bisa_ab_setup 1판, bisa_toc_cards 노트 틀 등)을 import 하는 줄은 원본을 읽어 대응한다.
# 분양4 05 프리비즈 장면 — 힉스필드 클라우드 블렌더(3D Jutsu) scene_builder_3d_run_python 에 그대로 넣는 코드.
# 프로젝트 ID 생략. 30fps 1~217프레임 = 시퀀스 14.915~22.139.
#   r 0~0.82   한강공원 앞에: 강변 숲 안, 살짝 전진(북쪽 = 한강)
#   r 0.82~2.45 서울의 초근접한 택지지구인: 수직 급상승, 한강·서울 스카이라인 → 고개 돌려 단지
#   r 2.45~4.685 ○○단지 단지안에 ~ 무려 2,432세대: 단지 내려다봄(HUD 는 후반 합성), 4.33·4.48·4.62 디지털 줌 단
#   r 4.685~    대단지 아파트를 공급하기 시작했어: 눈높이 중앙 정원, 사람들 오감
import bpy, math, random

random.seed(5)
S = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

def mat(name, rgb):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = (*rgb, 1)
    return m

M = dict(land=mat("land", (0.30, 0.45, 0.22)), water=mat("water", (0.22, 0.42, 0.62)),
         seoul=mat("seoul", (0.55, 0.60, 0.68)), trunk=mat("trunk", (0.30, 0.22, 0.15)),
         leaf=mat("leaf", (0.12, 0.38, 0.12)), leaf2=mat("leaf2", (0.20, 0.48, 0.16)),
         tower=mat("tower", (0.86, 0.86, 0.84)), towertop=mat("towertop", (0.20, 0.32, 0.33)),
         lawn=mat("lawn", (0.42, 0.62, 0.30)), path=mat("path", (0.80, 0.74, 0.62)),
         pond=mat("pond", (0.30, 0.55, 0.75)), skin=mat("skin", (0.85, 0.68, 0.55)))
PEOPLE = [mat(f"cloth{i}", c) for i, c in enumerate([(0.85, 0.25, 0.20), (0.15, 0.25, 0.60), (0.95, 0.85, 0.75),
                                                      (0.20, 0.20, 0.22), (0.90, 0.60, 0.20), (0.45, 0.65, 0.80)])]

def mesh_obj(name, op, m, loc, scale=(1, 1, 1), rot=(0, 0, 0), **kw):
    op(location=loc, **kw)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    o.rotation_euler = rot
    o.data.materials.append(m)
    return o

def inst(name, src, loc, scale=(1, 1, 1), rot=(0, 0, 0)):
    o = bpy.data.objects.new(name, src.data)
    o.location, o.scale, o.rotation_euler = loc, scale, rot
    S.collection.objects.link(o)
    return o

# 땅·강·서울
mesh_obj("Land", bpy.ops.mesh.primitive_plane_add, M["land"], (0, 0, 0), size=8000)
mesh_obj("HanRiver", bpy.ops.mesh.primitive_plane_add, M["water"], (0, 420, 0.05), scale=(1, 0.09, 1), size=8000)
sb = mesh_obj("SeoulSrc", bpy.ops.mesh.primitive_cube_add, M["seoul"], (0, 0, -500), size=1)
for i in range(90):
    x, y = random.uniform(-400, 2200), random.uniform(1300, 2600)
    h = random.uniform(30, 180) * (1.4 if 600 < x < 1400 else 1)
    inst(f"Seoul_{i}", sb, (x, y, h / 2), (random.uniform(25, 60), random.uniform(25, 60), h))

# 강변 숲(한강공원)
tr = mesh_obj("TrunkSrc", bpy.ops.mesh.primitive_cylinder_add, M["trunk"], (0, 0, -500), vertices=8, radius=0.3, depth=1)
cn = mesh_obj("CanopySrc", bpy.ops.mesh.primitive_ico_sphere_add, M["leaf"], (0, 0, -500), subdivisions=2, radius=1)
cn2 = mesh_obj("CanopySrc2", bpy.ops.mesh.primitive_ico_sphere_add, M["leaf2"], (0, 0, -500), subdivisions=2, radius=1)
k = 0
for i in range(420):
    x, y = random.uniform(-90, 90), random.uniform(-60, 52)
    if abs(x) < 2.8 and -9 < y < 4:
        continue                                     # 카메라 자리
    h = random.uniform(6, 11)
    inst(f"Trunk_{k}", tr, (x, y, h / 2), (1, 1, h))
    r = random.uniform(2.8, 4.8)
    inst(f"Canopy_{k}", random.choice([cn, cn2]), (x, y, h + r * 0.4), (r, r, r * 0.85))
    k += 1

# ○○단지 단지 — 중앙 정원 C 둘레 2겹 고리
C = (300.0, -80.0)
tw = mesh_obj("TowerSrc", bpy.ops.mesh.primitive_cube_add, M["tower"], (0, 0, -500), size=1)
tt = mesh_obj("TowerTopSrc", bpy.ops.mesh.primitive_cube_add, M["towertop"], (0, 0, -500), size=1)
n = 0
for ring, cnt, hh in ((105, 10, (78, 96)), (165, 14, (70, 90))):
    for j in range(cnt):
        a = 2 * math.pi * j / cnt + (0.2 if ring > 120 else 0)
        x, y = C[0] + ring * math.cos(a), C[1] + ring * math.sin(a)
        h = random.uniform(*hh)
        rot = (0, 0, a + math.pi / 2)
        inst(f"Tower_{n}", tw, (x, y, h / 2), (34, 15, h), rot)
        inst(f"TowerTop_{n}", tt, (x, y, h + 2), (34, 15, 4), rot)
        n += 1
mesh_obj("GardenLawn", bpy.ops.mesh.primitive_cylinder_add, M["lawn"], (C[0], C[1], 0.1), vertices=64, radius=80, depth=0.2)
mesh_obj("GardenPond", bpy.ops.mesh.primitive_cylinder_add, M["pond"], (C[0] + 12, C[1] + 8, 0.25), vertices=48, radius=16, depth=0.2)
for i, ang in enumerate((0, 1.2, 2.4)):
    mesh_obj(f"GardenPath_{i}", bpy.ops.mesh.primitive_cube_add, M["path"], (C[0], C[1], 0.22), (160, 4, 0.1), (0, 0, ang), size=1)
for i in range(40):
    a, rr = random.uniform(0, 2 * math.pi), random.uniform(25, 75)
    x, y = C[0] + rr * math.cos(a), C[1] + rr * math.sin(a)
    if abs(y - (C[1] - 6)) < 5 and x < C[0] + 10:
        continue                                     # 정원 걷는 카메라 길
    h = random.uniform(4, 6)
    inst(f"GTrunk_{i}", tr, (x, y, h / 2), (1, 1, h))
    r = random.uniform(2, 3.2)
    inst(f"GCanopy_{i}", cn2, (x, y, h + r * 0.4), (r, r, r))

# 사람들 — 정원 카메라 앞에서 오감
body = mesh_obj("BodySrc", bpy.ops.mesh.primitive_cylinder_add, PEOPLE[0], (0, 0, -500), vertices=10, radius=0.24, depth=1.25)
head = mesh_obj("HeadSrc", bpy.ops.mesh.primitive_uv_sphere_add, M["skin"], (0, 0, -500), segments=12, ring_count=8, radius=0.12)
F0, F1 = 142, 217
for i in range(22):
    x0 = C[0] - 50 + random.uniform(4, 32)
    y0 = C[1] - 6 + random.choice([-1, 1]) * random.uniform(1.4, 7)
    ang = random.uniform(0, 2 * math.pi)
    sp = random.uniform(0.9, 1.4) / 30
    b = bpy.data.objects.new(f"Person_{i}", body.data.copy())
    b.data.materials[0] = PEOPLE[i % len(PEOPLE)]
    S.collection.objects.link(b)
    hd = inst(f"PersonHead_{i}", head, (0, 0, 0.78))
    hd.parent = b
    for f in (F0, F1):
        d = (f - F0) * sp
        b.location = (x0 + d * math.cos(ang), y0 + d * math.sin(ang), 0.82)
        b.keyframe_insert("location", frame=f)
for o in (sb, tr, cn, cn2, tw, tt, body, head):
    o.hide_render = o.hide_viewport = True

# 빛
bpy.ops.object.light_add(type="SUN", location=(0, 0, 100))
sun = bpy.context.active_object
sun.name = "KeySun"
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(50), 0, math.radians(35))
bpy.ops.object.light_add(type="SUN", location=(0, 0, 100))
fill = bpy.context.active_object
fill.name = "FillSun"
fill.data.energy = 0.8
fill.rotation_euler = (math.radians(60), 0, math.radians(-150))

# 카메라 — 프레임마다 위치·목표 계산(atan2)
bpy.ops.object.camera_add()
cam = bpy.context.active_object
cam.name = "DeliveryCam"
cam.data.lens = 24
cam.data.clip_end = 8000
S.camera = cam
S.render.fps = 30
S.frame_start, S.frame_end = 1, F1
S.render.resolution_x, S.render.resolution_y = 432, 768

def ss(u):
    u = min(max(u, 0), 1)
    return u * u * (3 - 2 * u)

def look(p, q):
    dx, dy, dz = q[0] - p[0], q[1] - p[1], q[2] - p[2]
    return math.atan2(-dx, dy), math.atan2(dz, math.hypot(dx, dy))

TOP = (150.0, -55.0, 270.0)   # 단지 정원을 가파르게 내려다봄(앞 동에 안 가리게)
yN, pN = 0.0, math.radians(3)
yS, pS = look(TOP, (900, 1900, 40))
yC, pC = look(TOP, (C[0], C[1], 0))
def pose(r):
    if r < 0.82:
        return (0, -6 + 2.0 * r, 1.7), yN, pN
    if r < 2.45:
        u = (r - 0.82) / 1.63
        e = ss(u)
        p = (TOP[0] * e ** 2, -4.4 + (TOP[1] + 4.4) * e, 1.7 + (TOP[2] - 1.7) * e)
        if u < 0.5:
            v = ss(u / 0.5); yw, pt = yN + (yS - yN) * v, pN + (math.radians(-6) - pN) * v
        else:
            v = ss((u - 0.5) / 0.5); yw, pt = yS + (yC - yS) * v, math.radians(-6) + (pC - math.radians(-6)) * v
        return p, yw, pt
    if r < 4.685:
        d = (r - 2.45) * 3.0
        dirx, diry = C[0] - TOP[0], C[1] - TOP[1]
        L = math.hypot(dirx, diry)
        p = (TOP[0] + dirx / L * d, TOP[1] + diry / L * d, TOP[2])
        yw, pt = look(p, (C[0] + 12, C[1] + 8, 0))
        return p, yw, pt
    d = (r - 4.685) * 1.1
    p = (C[0] - 55 + d, C[1] - 6, 1.6)
    yw, pt = look(p, (C[0] + 60, C[1] - 6, 9))
    return p, yw, pt

prev = None
for f in range(1, F1 + 1):
    r = (f - 1) / 30
    p, yw, pt = pose(r)
    if prev is not None:
        while yw - prev > math.pi: yw -= 2 * math.pi
        while yw - prev < -math.pi: yw += 2 * math.pi
    prev = yw
    cam.location = p
    cam.rotation_euler = (math.pi / 2 + pt, 0, yw)
    cam.keyframe_insert("location", frame=f)
    cam.keyframe_insert("rotation_euler", frame=f)
bpy.context.preferences.edit.keyframe_new_interpolation_type = "CONSTANT"
for f, lens in ((1, 24), (round(4.33 * 30) + 1, 45), (round(4.48 * 30) + 1, 85), (round(4.62 * 30) + 1, 150), (142, 24)):
    cam.data.lens = lens
    cam.data.keyframe_insert("lens", frame=f)
bpy.context.preferences.edit.keyframe_new_interpolation_type = "BEZIER"

S.world = S.world or bpy.data.worlds.new("World")
S.world.color = (0.55, 0.72, 0.92)
result = {"objects": len(bpy.data.objects), "towers": n, "frames": F1}
