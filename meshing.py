from pathlib import Path
import gmsh
import math


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

