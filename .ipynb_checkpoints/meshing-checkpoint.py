from pathlib import Path
import gmsh
import math

def create_rectangle_mesh(
    filepath: Path,
    width: float,
    height: float,
    mesh_size: float,
    center_z: float = 0.0
) -> None:

    gmsh.initialize()
    gmsh.option.setNumber("General.Verbosity", 0)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size)
    gmsh.model.add(filepath.stem)

    z = center_z

    p1 = gmsh.model.occ.addPoint(0.0,    z + height/2, 0.0, mesh_size)
    p2 = gmsh.model.occ.addPoint(width,  z + height/2, 0.0, mesh_size)
    p3 = gmsh.model.occ.addPoint(width,  z - height/2, 0.0, mesh_size)
    p4 = gmsh.model.occ.addPoint(0.0,    z - height/2, 0.0, mesh_size)
    gmsh.model.occ.synchronize()

    l1 = gmsh.model.occ.addLine(p2, p1)
    l2 = gmsh.model.occ.addLine(p1, p4)
    l3 = gmsh.model.occ.addLine(p4, p3)
    l4 = gmsh.model.occ.addLine(p3, p2)
    gmsh.model.occ.synchronize()

    cl   = gmsh.model.occ.addCurveLoop([l1, l2, l3, l4])
    surf = gmsh.model.occ.addPlaneSurface([cl])
    gmsh.model.occ.synchronize()

    pg_domain = gmsh.model.addPhysicalGroup(2, [surf])
    gmsh.model.setPhysicalName(2, pg_domain, "domain")
    bcs = [("top", l1), ("left", l2), ("bottom", l3), ("right", l4)]
    for name, line in bcs:
        pg = gmsh.model.addPhysicalGroup(1, [line])
        gmsh.model.setPhysicalName(1, pg, name)

    gmsh.model.mesh.generate(2)
    gmsh.write(str(filepath.with_suffix(".msh")))
    gmsh.finalize()

def create_rectangle_frac_mesh(
    filepath: Path,
    width: float,
    height: float,
    mesh_size: float,
    center_z: float = 0.0,
    mode="domain",
) -> None:

    gmsh.initialize()
    gmsh.option.setNumber("General.Verbosity", 0)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size)
    gmsh.model.add(filepath.stem)
    
    z = center_z
    
    p1 = gmsh.model.occ.addPoint(0.0, z + height / 2, 0.0, mesh_size)
    p2 = gmsh.model.occ.addPoint(width, z + height / 2, 0.0, mesh_size)
    p3 = gmsh.model.occ.addPoint(width, z - height / 2, 0.0, mesh_size)
    p4 = gmsh.model.occ.addPoint(0.0, z - height / 2, 0.0, mesh_size)
    
    angle_rad = math.radians(30.0)
    p5_x = 0.0
    p6_x = width
    p5_y = z - width * math.tan(angle_rad) / 2
    p6_y = z + width * math.tan(angle_rad) / 2
    
    p5 = gmsh.model.occ.addPoint(p5_x, p5_y, 0.0, mesh_size)
    p6 = gmsh.model.occ.addPoint(p6_x, p6_y, 0.0, mesh_size)
    gmsh.model.occ.synchronize()
    
    l1 = gmsh.model.occ.addLine(p2, p1)
    l2 = gmsh.model.occ.addLine(p1, p5)
    l3 = gmsh.model.occ.addLine(p5, p4)
    l4 = gmsh.model.occ.addLine(p4, p3)
    l5 = gmsh.model.occ.addLine(p3, p6)
    l6 = gmsh.model.occ.addLine(p6, p2)
    l7 = gmsh.model.occ.addLine(p6, p5)
    gmsh.model.occ.synchronize()
    
    cl1 = gmsh.model.occ.addCurveLoop([l1, l2, -l7, l6])
    surf1 = gmsh.model.occ.addPlaneSurface([cl1])
    cl2 = gmsh.model.occ.addCurveLoop([l4, l5, l7, l3])
    surf2 = gmsh.model.occ.addPlaneSurface([cl2])
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(2)

    if mode == "BC":
        bcs = [("top", l1), ("bottom", l4)]
        for name, line in bcs:
            pg = gmsh.model.addPhysicalGroup(1, [line])
            gmsh.model.setPhysicalName(1, pg, name)
        gmsh.model.addPhysicalGroup(1, [l5, l6], name="right")
        gmsh.model.addPhysicalGroup(1, [l2, l3], name="left")
        gmsh.model.addPhysicalGroup(0, [p4], name="p4")
        gmsh.model.addPhysicalGroup(0, [p3], name="p3")
      
    elif mode == "domain":
        gmsh.model.addPhysicalGroup(2, [surf1], name="top_surf")
        gmsh.model.addPhysicalGroup(2, [surf2], name="bot_surf")
        gmsh.model.addPhysicalGroup(1, [l7], name="fracture")
      
    gmsh.write(str(filepath.with_suffix(".msh")))
    gmsh.finalize()

def create_cube_mesh(
    filepath: Path,
    width: float,
    height: float,
    thickness: float,
    mesh_size: float,
    center_z: float = 0.0
) -> None:
    gmsh.initialize()
    gmsh.option.setNumber("General.Verbosity", 0)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size)
    gmsh.model.add(filepath.stem)

    z0 = center_z - thickness/2.0
    z1 = center_z + thickness/2.0

    # 1) Create corner points
    coords = [
        (0.0,     0.0,     z0),  
        (width,   0.0,     z0),  
        (width,   height,  z0),  
        (0.0,     height,  z0),  
        (0.0,     0.0,     z1),  
        (width,   0.0,     z1),  
        (width,   height,  z1),  
        (0.0,     height,  z1)   
    ]
    pts = [gmsh.model.occ.addPoint(x, y, z, mesh_size) for x, y, z in coords]
    gmsh.model.occ.synchronize()

    l1  = gmsh.model.occ.addLine(pts[0], pts[1])
    l2  = gmsh.model.occ.addLine(pts[1], pts[2])
    l3  = gmsh.model.occ.addLine(pts[2], pts[3])
    l4  = gmsh.model.occ.addLine(pts[3], pts[0])
    l5  = gmsh.model.occ.addLine(pts[4], pts[5])
    l6  = gmsh.model.occ.addLine(pts[5], pts[6])
    l7  = gmsh.model.occ.addLine(pts[6], pts[7])
    l8  = gmsh.model.occ.addLine(pts[7], pts[4])
    l9  = gmsh.model.occ.addLine(pts[0], pts[4])
    l10 = gmsh.model.occ.addLine(pts[1], pts[5])
    l11 = gmsh.model.occ.addLine(pts[2], pts[6])
    l12 = gmsh.model.occ.addLine(pts[3], pts[7])
    gmsh.model.occ.synchronize()

    cl_bot   = gmsh.model.occ.addCurveLoop([ l1,  l2,  l3,  l4])
    cl_top   = gmsh.model.occ.addCurveLoop([ l5,  l6,  l7,  l8])
    cl_front = gmsh.model.occ.addCurveLoop([ l1,  l10, -l5,  -l9])
    cl_back  = gmsh.model.occ.addCurveLoop([-l3,  l11,  l7, -l12])
    cl_left  = gmsh.model.occ.addCurveLoop([ l9,  -l8, -l12,  l4])
    cl_right = gmsh.model.occ.addCurveLoop([ l10, l6,  -l11, -l2])
    gmsh.model.occ.synchronize()

    s_bot   = gmsh.model.occ.addPlaneSurface([cl_bot])
    s_top   = gmsh.model.occ.addPlaneSurface([cl_top])
    s_back = gmsh.model.occ.addPlaneSurface([cl_front])
    s_front  = gmsh.model.occ.addPlaneSurface([cl_back])
    s_left  = gmsh.model.occ.addPlaneSurface([cl_left])
    s_right = gmsh.model.occ.addPlaneSurface([cl_right])
    gmsh.model.occ.synchronize()

    sl  = gmsh.model.occ.addSurfaceLoop([s_bot, s_top, s_back, s_front, s_left, s_right])
    vol = gmsh.model.occ.addVolume([sl])
    gmsh.model.occ.synchronize()

    pg0 = gmsh.model.addPhysicalGroup(0, pts)
    gmsh.model.setPhysicalName(0, pg0, "points")

    all_edges = [l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12]
    pg1 = gmsh.model.addPhysicalGroup(1, all_edges)
    gmsh.model.setPhysicalName(1, pg1, "edges")

    face_map = {
        "bottom": s_bot,
        "top":    s_top,
        "back":  s_back,
        "front":   s_front,
        "left":   s_left,
        "right":  s_right,
    }
    for name, surf_tag in face_map.items():
        pg = gmsh.model.addPhysicalGroup(2, [surf_tag])
        gmsh.model.setPhysicalName(2, pg, name)

    pg3 = gmsh.model.addPhysicalGroup(3, [vol])
    gmsh.model.setPhysicalName(3, pg3, "volume")

    gmsh.model.mesh.generate(3)
    gmsh.write(str(filepath.with_suffix(".msh")))
    gmsh.finalize()




from pathlib import Path
import math
import gmsh


def create_fractured_cube(
    filepath: Path | str,
    lc: float = 0.5,
    lc_frac: float = 0.1,
    L: float = 4.0,
    H: float = 4.0,
    T: float = 4.0,
    theta_deg: float = 30.0,
    b: float = 0.2,
    center_z: float = 0.0,  # e.g., -100.0 to place cube center at depth -100
):
    """
    Exact Python port of your .geo with IDs/topology preserved.
    All Z-coordinates are written explicitly with center_z applied.
    """

    filepath = Path(filepath)
    theta = math.radians(theta_deg)
    dy = (L / 2.0) * math.tan(theta)
    r_b = b / (2.0 * math.cos(theta))

    # Explicit Z levels
    z_bot      = center_z - T / 2.0
    z_top      = center_z + T / 2.0
    z_mid_mdy  = center_z - dy
    z_mid_pdy  = center_z + dy
    z_btm_m    = center_z - dy - r_b  # fracture "bottom" surface (−rb)
    z_btm_p    = center_z + dy - r_b
    z_top_m    = center_z - dy + r_b  # fracture "top" surface (+rb)
    z_top_p    = center_z + dy + r_b
    z_center   = center_z

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Verbosity", 1)
        gmsh.model.add(filepath.stem)

        geo = gmsh.model.geo
        mgeo = gmsh.model.geo.mesh

        # -------------------- Points (explicit Z) --------------------
        # Cube corners
        geo.addPoint(-L/2,  H/2, z_bot, lc, tag=1)
        geo.addPoint( L/2,  H/2, z_bot, lc, tag=2)
        geo.addPoint( L/2, -H/2, z_bot, lc, tag=3)
        geo.addPoint(-L/2, -H/2, z_bot, lc, tag=4)
        geo.addPoint(-L/2,  H/2, z_top, lc, tag=5)
        geo.addPoint( L/2,  H/2, z_top, lc, tag=6)
        geo.addPoint( L/2, -H/2, z_top, lc, tag=7)
        geo.addPoint(-L/2, -H/2, z_top, lc, tag=8)

        # Fracture mid-plane
        geo.addPoint(-L/2,  H/2, z_mid_mdy, lc_frac, tag=9)
        geo.addPoint( L/2,  H/2, z_mid_pdy, lc_frac, tag=12)
        geo.addPoint(-L/2, -H/2, z_mid_mdy, lc_frac, tag=15)
        geo.addPoint( L/2, -H/2, z_mid_pdy, lc_frac, tag=18)

        # Fracture bottom surface (−rb)
        geo.addPoint(-L/2,  H/2, z_btm_m, lc_frac, tag=10)
        geo.addPoint( L/2,  H/2, z_btm_p, lc_frac, tag=13)
        geo.addPoint(-L/2, -H/2, z_btm_m, lc_frac, tag=16)
        geo.addPoint( L/2, -H/2, z_btm_p, lc_frac, tag=19)

        # Fracture top surface (+rb)
        geo.addPoint(-L/2,  H/2, z_top_m, lc_frac, tag=11)
        geo.addPoint( L/2,  H/2, z_top_p, lc_frac, tag=14)
        geo.addPoint(-L/2, -H/2, z_top_m, lc_frac, tag=17)
        geo.addPoint( L/2, -H/2, z_top_p, lc_frac, tag=20)

        # Source point at cube center
        geo.addPoint(0.0, 0.0, z_center, lc_frac, tag=1000)

        # -------------------- Lines --------------------
        # Fracture Bottom
        geo.addLine(10, 13, tag=101); geo.addLine(13, 19, tag=102)
        geo.addLine(19, 16, tag=103); geo.addLine(16, 10, tag=104)
        # Fracture Top
        geo.addLine(11, 14, tag=105); geo.addLine(14, 20, tag=106)
        geo.addLine(20, 17, tag=107); geo.addLine(17, 11, tag=108)
        # Fracture Mid
        geo.addLine(9, 12, tag=109);  geo.addLine(12, 18, tag=110)
        geo.addLine(18, 15, tag=111); geo.addLine(15, 9,  tag=112)

        # Cube Bottom
        geo.addLine(1, 2, tag=1); geo.addLine(2, 3, tag=2)
        geo.addLine(3, 4, tag=3); geo.addLine(4, 1, tag=4)
        # Cube Top
        geo.addLine(5, 6, tag=5); geo.addLine(6, 7, tag=6)
        geo.addLine(7, 8, tag=7); geo.addLine(8, 5, tag=8)

        # Cube vertical edges via fracture
        geo.addLine(1, 10, tag=9);  geo.addLine(10, 9,  tag=10)
        geo.addLine(9, 11,  tag=11); geo.addLine(11, 5,  tag=12)

        geo.addLine(2, 13, tag=13); geo.addLine(13, 12, tag=14)
        geo.addLine(12, 14, tag=15); geo.addLine(14, 6,  tag=16)

        geo.addLine(4, 16, tag=17); geo.addLine(16, 15, tag=18)
        geo.addLine(15, 17, tag=19); geo.addLine(17, 8,  tag=20)

        geo.addLine(3, 19, tag=21); geo.addLine(19, 18, tag=22)
        geo.addLine(18, 20, tag=23); geo.addLine(20, 7,  tag=24)

        # -------------------- Surfaces --------------------
        def add_plane(cl_id, curves, surf_id):
            geo.addCurveLoop(curves, cl_id)
            geo.addPlaneSurface([cl_id], tag=surf_id)

        add_plane(1,  [9, 101, -13, -1],           1)
        add_plane(2,  [101, 14, -109, -10],        2)
        add_plane(3,  [11, 105, -15, -109],        3)
        add_plane(4,  [16, -5, -12, 105],          4)

        add_plane(5,  [3, 17, -103, -21],          5)
        add_plane(6,  [103, 18, -111, -22],        6)
        add_plane(7,  [19, -107, -23, 111],        7)
        add_plane(8,  [24, 7, -20, -107],          8)

        add_plane(9,  [13, 102, -21, -2],          9)
        add_plane(10, [102, 22, -110, -14],        10)
        add_plane(11, [23, -106, -15, 110],        11)
        add_plane(12, [16, 6, -24, -106],          12)

        add_plane(13, [17, 104, -9, -4],           13)
        add_plane(14, [10, -112, -18, 104],        14)
        add_plane(15, [19, 108, -11, -112],        15)
        add_plane(16, [12, -8, -20, 108],          16)

        add_plane(17, [8, 5, 6, 7],                17)
        add_plane(18, [3, 4, 1, 2],                18)
        add_plane(19, [105, 106, 107, 108],        19)
        add_plane(20, [109, 110, 111, 112],        20)
        add_plane(21, [101, 102, 103, 104],        21)

        # -------------------- Volumes --------------------
        def add_volume(sl_id, surfaces, vol_id):
            geo.addSurfaceLoop(surfaces, sl_id)
            geo.addVolume([sl_id], tag=vol_id)

        add_volume(101, [4, 16, 17, 12, 8, 19], 1)
        add_volume(102, [3, 11, 7, 15, 19, 20], 2)
        add_volume(103, [20, 21, 10, 6, 2, 14], 3)
        add_volume(104, [21, 13, 1, 9, 5, 18], 4)

        # -------------------- Transfinite / Recombine (GEO-level, before sync) --------------------
        tf_surfs = [2, 3, 6, 7, 10, 11, 14, 15, 19, 20, 21]
        for s in tf_surfs:
            mgeo.setTransfiniteSurface(s)
            mgeo.setRecombine(2, s)
        for v in [2, 3]:
            mgeo.setTransfiniteVolume(v)

        # Sync CAD → mesh
        geo.synchronize()

        # -------------------- Physical Groups --------------------
        gmsh.model.addPhysicalGroup(0, [1000], tag=1000)
        gmsh.model.setPhysicalName(0, 1000, "Source_Point")

        pg_mid = gmsh.model.addPhysicalGroup(2, [20])
        gmsh.model.setPhysicalName(2, pg_mid, "Fracture_MidPlane")

        gmsh.model.setPhysicalName(3, gmsh.model.addPhysicalGroup(3, [1]), "Top_Left")
        gmsh.model.setPhysicalName(3, gmsh.model.addPhysicalGroup(3, [2]), "Top_Right")
        gmsh.model.setPhysicalName(3, gmsh.model.addPhysicalGroup(3, [3]), "Bottom_Right")
        gmsh.model.setPhysicalName(3, gmsh.model.addPhysicalGroup(3, [4]), "Bottom_Left")

        # -------------------- Mesh --------------------
        gmsh.model.mesh.generate(3)
        gmsh.write(str(filepath if filepath.suffix == ".msh" else filepath.with_suffix(".msh")))
    finally:
        gmsh.finalize()



def create_fractured_cube_centered(
    filepath: str | Path,
    lc: float = 1.0,          # matrix target h
    lc_frac: float = 0.2,     # fracture band target h
    L: float = 4.0,
    H: float = 4.0,
    T: float = 4.0,
    theta_deg: float = 0.0,   # your input (e.g., 0 or 30)
    b: float = 0.2,           # total band thickness (~2*r_b)
    center_z: float = 0.0,    # shift the whole sample along Z (e.g., -100.0)
    generate_mesh: bool = True,
) -> Path:
    filepath = Path(filepath)
    model_name = filepath.stem

    theta = math.radians(theta_deg)
    dy = (L / 2.0) * math.tan(theta)
    r_b = b / (2.0 * math.cos(theta)) if math.cos(theta) != 0 else 0.0

    z_bot = center_z - T / 2.0
    z_top = center_z + T / 2.0

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Verbosity", 2)
        gmsh.option.setNumber("Mesh.RecombineAll", 1)
        gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)

        gmsh.model.add(model_name)
        geo = gmsh.model.geo
        mgeo = gmsh.model.geo.mesh

        # ---------------------------
        # POINTS 
        # ---------------------------
        # Cube corners
        geo.addPoint(-L/2,  H/2, z_bot, lc, tag=1)
        geo.addPoint( L/2,  H/2, z_bot, lc, tag=2)
        geo.addPoint( L/2, -H/2, z_bot, lc, tag=3)
        geo.addPoint(-L/2, -H/2, z_bot, lc, tag=4)
        geo.addPoint(-L/2,  H/2, z_top, lc, tag=5)
        geo.addPoint( L/2,  H/2, z_top, lc, tag=6)
        geo.addPoint( L/2, -H/2, z_top, lc, tag=7)
        geo.addPoint(-L/2, -H/2, z_top, lc, tag=8)

        # Fracture mid-plane and bands (y varies with ±dy)
        geo.addPoint(-L/2, -dy,        z_top, lc_frac, tag=9)
        geo.addPoint( L/2,  dy,        z_top, lc_frac, tag=12)
        geo.addPoint(-L/2, -dy,        z_bot, lc_frac, tag=15)
        geo.addPoint( L/2,  dy,        z_bot, lc_frac, tag=18)

        # Bottom (-rb)
        geo.addPoint(-L/2, -dy - r_b,  z_top, lc_frac, tag=10)
        geo.addPoint( L/2,  dy - r_b,  z_top, lc_frac, tag=13)
        geo.addPoint(-L/2, -dy - r_b,  z_bot, lc_frac, tag=16)
        geo.addPoint( L/2,  dy - r_b,  z_bot, lc_frac, tag=19)

        # Top (+rb)
        geo.addPoint(-L/2, -dy + r_b,  z_top, lc_frac, tag=11)
        geo.addPoint( L/2,  dy + r_b,  z_top, lc_frac, tag=14)
        geo.addPoint(-L/2, -dy + r_b,  z_bot, lc_frac, tag=17)
        geo.addPoint( L/2,  dy + r_b,  z_bot, lc_frac, tag=20)

        # Center point
        geo.addPoint(0.0, 0.0, center_z, lc, tag=100)

        # ---------------------------
        # LINES 
        # ---------------------------
        geo.addLine(7, 8, tag=1)
        geo.addLine(7, 3, tag=2)
        geo.addLine(3, 4, tag=3)
        geo.addLine(4, 8, tag=4)
        geo.addLine(2, 1, tag=5)
        geo.addLine(1, 5, tag=6)
        geo.addLine(5, 6, tag=7)
        geo.addLine(6, 2, tag=8)
        geo.addLine(7, 13, tag=9)
        geo.addLine(13, 12, tag=10)
        geo.addLine(12, 14, tag=11)
        geo.addLine(14, 6, tag=12)
        geo.addLine(5, 11, tag=13)
        geo.addLine(11, 9, tag=14)
        geo.addLine(9, 10, tag=15)
        geo.addLine(10, 8, tag=16)
        geo.addLine(3, 19, tag=17)
        geo.addLine(19, 18, tag=18)
        geo.addLine(18, 20, tag=19)
        geo.addLine(20, 2, tag=20)
        geo.addLine(1, 17, tag=21)
        geo.addLine(17, 15, tag=22)
        geo.addLine(15, 16, tag=23)
        geo.addLine(16, 4, tag=24)
        geo.addLine(10, 13, tag=25)
        geo.addLine(9, 12, tag=26)
        geo.addLine(11, 14, tag=27)
        geo.addLine(10, 16, tag=28)
        geo.addLine(9, 15, tag=29)
        geo.addLine(11, 17, tag=30)
        geo.addLine(16, 19, tag=31)
        geo.addLine(15, 18, tag=32)
        geo.addLine(17, 20, tag=33)
        geo.addLine(19, 13, tag=34)
        geo.addLine(12, 18, tag=35)
        geo.addLine(14, 20, tag=36)

        # ---------------------------
        # SURFACES 
        # ---------------------------
        def plane(loop_id: int, edges: list[int], surf_id: int):
            geo.addCurveLoop(edges, loop_id)
            geo.addPlaneSurface([loop_id], surf_id)

        plane(1,  [8, 5, 6, 7],                     1)   # Front
        plane(2,  [3, 4, -1, 2],                    2)   # Back
        plane(3,  [13, 30, -21, 6],                 3)   # Left upper
        plane(4,  [30, 22, -29, -14],               4)   # Left mid
        plane(5,  [15, 28, -23, -29],               5)   # Left lower
        plane(6,  [24, 4, -16, 28],                 6)   # Left bottom
        plane(7,  [8, -20, -36, 12],                7)   # Right upper
        plane(8,  [36, -19, -35, 11],               8)   # Right mid
        plane(9,  [35, -18, 34, 10],                9)   # Right lower
        plane(10, [17, 34, -9, 2],                  10)  # Right bottom
        plane(11, [7, -12, -27, -13],               11)  # Top top
        plane(12, [27, -11, -26, -14],              12)  # Top mid
        plane(13, [15, 25, 10, -26],                13)  # Top lower
        plane(14, [9, -25, 16, -1],                 14)  # Top bottom
        plane(15, [3, -24, 31, -17],                15)  # Bottom top
        plane(16, [31, 18, -32, 23],                16)  # Bottom mid
        plane(17, [19, -33, 22, 32],                17)  # Bottom lower
        plane(18, [21, 33, 20, 5],                  18)  # Bottom bottom
        plane(19, [33, -36, -27, 30],               19)  # Frac upper
        plane(20, [29, 32, -35, -26],               20)  # Frac mid
        plane(21, [25, -34, -31, -28],              21)  # Frac lower

        # ---------------------------
        # VOLUMES 
        # ---------------------------
        def add_volume(sl_id: int, srf_ids: list[int], vol_id: int):
            geo.addSurfaceLoop(srf_ids, sl_id)
            geo.addVolume([sl_id], vol_id)

        add_volume(1, [18, 3, 11, 1, 7, 19], 1)   # matrix block
        add_volume(2, [15, 2, 6, 14, 10, 21], 2)  # matrix block
        add_volume(3, [8, 17, 4, 12, 19, 20], 3)  # fracture upper
        add_volume(4, [20, 21, 16, 9, 13, 5], 4)  # fracture lower

        # ---------------------------
        # TRANSFINITE + RECOMBINE
        # ---------------------------
        trans_surf = {8, 17, 4, 12, 19, 20, 21, 16, 9, 13, 5}
        for s in trans_surf:
            mgeo.setTransfiniteSurface(s)
            mgeo.setRecombine(1, s)

        # Volumes 3 and 4 set as transfinite
        for v in [3, 4]:
            mgeo.setTransfiniteVolume(v)

        geo.synchronize()

        # ---------------------------
        # PHYSICAL GROUPS (names preserved)
        # ---------------------------
        pg = gmsh.model.addPhysicalGroup
        pn = gmsh.model.setPhysicalName

        # Volumes
        pg(3, [1]); pn(3, gmsh.model.getPhysicalGroups(3)[-1][1], "MATRIX_TOP")
        pg(3, [2]); pn(3, gmsh.model.getPhysicalGroups(3)[-1][1], "MATRIX_BOTTOM")
        pg(3, [3,4]); pn(3, gmsh.model.getPhysicalGroups(3)[-1][1], "FRAC")
        #pg(3, [4]); pn(3, gmsh.model.getPhysicalGroups(3)[-1][1], "FRAC_LOWER")
        #pg(3, [3,4]); pn(3, gmsh.model.getPhysicalGroups(3)[-1][1], "FRAC_UPPER")

        # Surfaces
        pg(2, [1]); pn(2, gmsh.model.getPhysicalGroups(2)[-1][1], "F_FRONT")
        pg(2, [2]); pn(2, gmsh.model.getPhysicalGroups(2)[-1][1], "F_BACK")
        pg(2, [3, 4, 5, 6]);   pn(2, gmsh.model.getPhysicalGroups(2)[-1][1], "F_LEFT")
        pg(2, [7, 8, 9, 10]);  pn(2, gmsh.model.getPhysicalGroups(2)[-1][1], "F_RIGHT")
        pg(2, [11, 12, 13, 14]); pn(2, gmsh.model.getPhysicalGroups(2)[-1][1], "F_TOP")
        pg(2, [15, 16, 17, 18]); pn(2, gmsh.model.getPhysicalGroups(2)[-1][1], "F_BOTTOM")
        pg(2, [19]); pn(2, gmsh.model.getPhysicalGroups(2)[-1][1], "F_FRAC_U")
        pg(2, [20]); pn(2, gmsh.model.getPhysicalGroups(2)[-1][1], "F_FRAC_M")
        pg(2, [21]); pn(2, gmsh.model.getPhysicalGroups(2)[-1][1], "F_FRAC_L")

        # Lines
        pg(1, [5]);               pn(1, gmsh.model.getPhysicalGroups(1)[-1][1], "L_BOT_FRONT")
        pg(1, [3]);               pn(1, gmsh.model.getPhysicalGroups(1)[-1][1], "L_BOT_BACK")
        pg(1, [17, 18, 19, 20]);  pn(1, gmsh.model.getPhysicalGroups(1)[-1][1], "L_BOT_RIGHT")
        pg(1, [21, 22, 23, 24]);  pn(1, gmsh.model.getPhysicalGroups(1)[-1][1], "L_BOT_LEFT")



     
        # Center point
        pg(0, [100]); pn(0, gmsh.model.getPhysicalGroups(0)[-1][1], "CENTER")

        # Bottom corner points
        pg(0, [1]); pn(0, gmsh.model.getPhysicalGroups(0)[-1][1], "P_BOT_FL")
        pg(0, [2]); pn(0, gmsh.model.getPhysicalGroups(0)[-1][1], "P_BOT_FR")
        pg(0, [3]); pn(0, gmsh.model.getPhysicalGroups(0)[-1][1], "P_BOT_BR")
        pg(0, [4]); pn(0, gmsh.model.getPhysicalGroups(0)[-1][1], "P_BOT_BL")


        # ---------------------------
        # MESH
        # ---------------------------
        if generate_mesh:
            gmsh.model.mesh.generate(3)

        out = filepath if filepath.suffix == ".msh" else filepath.with_suffix(".msh")
        gmsh.write(str(out))
        return out

    finally:
        gmsh.finalize()

