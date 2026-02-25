import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import sympy as sp

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


# ----------------------------
# Math helpers (Unit 3)
# ----------------------------

def xy_to_polar(x, y):
    r = float(np.hypot(x, y))
    theta = float(np.arctan2(y, x))  # radians
    return r, theta

def polar_to_xy(r, theta_rad):
    x = float(r * np.cos(theta_rad))
    y = float(r * np.sin(theta_rad))
    return x, y

def _safe_theta_expr(expr_str: str):
    """
    Parse an expression in theta using sympy.
    Supports: sin, cos, tan, sqrt, abs, exp, pi, etc.
    """
    theta = sp.Symbol("theta", real=True)

    local = {
        "theta": theta,
        "pi": sp.pi,
        "e": sp.E,
        "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
        "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
        "sqrt": sp.sqrt, "abs": sp.Abs,
        "ln": sp.log, "log": sp.log, "exp": sp.exp,
    }

    s = expr_str.strip()
    if not s:
        raise ValueError("Expression is empty.")
    # allow user to type "r = ..." casually
    s = s.replace("r=", "").replace("r =", "").strip()

    expr = sp.sympify(s, locals=local)
    expr = sp.simplify(expr)
    f = sp.lambdify(theta, expr, "numpy")
    return f

def polygon_area_shoelace(x, y):
    """Area of a closed polygon given by vertices (x,y)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size < 3:
        return 0.0
    # close polygon
    if x[0] != x[-1] or y[0] != y[-1]:
        x = np.append(x, x[0])
        y = np.append(y, y[0])
    return float(0.5 * np.abs(np.dot(x[:-1], y[1:]) - np.dot(y[:-1], x[1:])))

def polyline_length(x, y):
    """Sum of chord lengths along a polyline (x,y)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size < 2:
        return 0.0
    dx = np.diff(x)
    dy = np.diff(y)
    return float(np.sum(np.sqrt(dx * dx + dy * dy)))


# ----------------------------
# GUI App
# ----------------------------

class SDL3NewCoordinatesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SDL 3 — New Coordinates (Polar) Visualizer")
        self.geometry("1280x760")

        self._build_ui()

    def _build_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_convert = ttk.Frame(self.notebook, padding=10)
        self.tab_plot = ttk.Frame(self.notebook, padding=10)
        self.tab_area = ttk.Frame(self.notebook, padding=10)
        self.tab_arc = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_convert, text="Convert Points")
        self.notebook.add(self.tab_plot, text="Polar Plot")
        self.notebook.add(self.tab_area, text="Polar Area")
        self.notebook.add(self.tab_arc, text="Arc Length")

        self._build_convert_tab()
        self._build_plot_tab()
        self._build_area_tab()
        self._build_arc_tab()

    # ---------- shared plot maker ----------
    def _make_figure(self, parent, title):
        fig = Figure(figsize=(7.6, 6.2), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title(title)
        ax.grid(True)
        ax.set_aspect("equal", adjustable="box")

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()

        return fig, ax, canvas

    def _parse_angle(self, value_str: str, is_degrees: bool) -> float:
        v = float(value_str)
        return float(np.deg2rad(v) if is_degrees else v)

    def _format_angle(self, theta_rad: float, out_degrees: bool) -> float:
        return float(np.rad2deg(theta_rad) if out_degrees else theta_rad)

    def _eval_theta_bound(self, s):
        theta = sp.Symbol("theta", real=True)
        local = {"pi": sp.pi, "e": sp.E, "theta": theta}
        return float(sp.N(sp.sympify(s.strip(), locals=local)))

    # =========================
    # Tab 1: Convert Points
    # =========================
    def _build_convert_tab(self):
        left = ttk.Frame(self.tab_convert)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        right = ttk.Frame(self.tab_convert)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.figC, self.axC, self.canvasC = self._make_figure(
            right, "Point Conversion (showing both coordinate systems)"
        )

        ttk.Label(left, text="Angle mode").pack(anchor="w")
        self.ang_mode = tk.StringVar(value="Radians")
        mode_box = ttk.Combobox(
            left, textvariable=self.ang_mode, values=["Radians", "Degrees"],
            state="readonly", width=10
        )
        mode_box.pack(anchor="w", pady=(0, 10))

        # Rect -> Polar
        ttk.Label(left, text="Rectangular → Polar").pack(anchor="w", pady=(10, 2))
        self.x_var = tk.StringVar(value="3")
        self.y_var = tk.StringVar(value="4")
        row1 = ttk.Frame(left); row1.pack(anchor="w", pady=2)
        ttk.Label(row1, text="x").pack(side=tk.LEFT)
        ttk.Entry(row1, textvariable=self.x_var, width=8).pack(side=tk.LEFT, padx=6)
        ttk.Label(row1, text="y").pack(side=tk.LEFT)
        ttk.Entry(row1, textvariable=self.y_var, width=8).pack(side=tk.LEFT, padx=6)

        ttk.Button(left, text="Convert x,y → r,θ", command=self.convert_xy_to_polar).pack(anchor="w", pady=(4, 10))

        self.r_out = tk.StringVar(value="r = ")
        self.t_out = tk.StringVar(value="θ = ")
        ttk.Label(left, textvariable=self.r_out).pack(anchor="w")
        ttk.Label(left, textvariable=self.t_out).pack(anchor="w")

        # Polar -> Rect
        ttk.Label(left, text="Polar → Rectangular").pack(anchor="w", pady=(16, 2))
        self.r_in_var = tk.StringVar(value="5")
        self.t_in_var = tk.StringVar(value="0.9273")  # approx atan2(4,3)
        row2 = ttk.Frame(left); row2.pack(anchor="w", pady=2)
        ttk.Label(row2, text="r").pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.r_in_var, width=8).pack(side=tk.LEFT, padx=6)
        ttk.Label(row2, text="θ").pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.t_in_var, width=8).pack(side=tk.LEFT, padx=6)

        ttk.Button(left, text="Convert r,θ → x,y", command=self.convert_polar_to_xy).pack(anchor="w", pady=(4, 10))

        self.x_out = tk.StringVar(value="x = ")
        self.y_out = tk.StringVar(value="y = ")
        ttk.Label(left, textvariable=self.x_out).pack(anchor="w")
        ttk.Label(left, textvariable=self.y_out).pack(anchor="w")

        ttk.Separator(left).pack(fill=tk.X, pady=10)
        ttk.Button(left, text="Clear Plot", command=self._clear_convert_plot).pack(anchor="w")

        self.statusC = tk.StringVar(value="Ready.")
        ttk.Label(left, textvariable=self.statusC, foreground="#005").pack(anchor="w", pady=(10, 0))

        self._clear_convert_plot()

    def _clear_convert_plot(self):
        self.axC.clear()
        self.axC.set_title("Point Conversion (showing both coordinate systems)")
        self.axC.grid(True)
        self.axC.set_aspect("equal", adjustable="box")
        self.axC.set_xlim(-8, 8)
        self.axC.set_ylim(-8, 8)
        self.axC.axhline(0, linewidth=1)
        self.axC.axvline(0, linewidth=1)
        self.canvasC.draw()

    def convert_xy_to_polar(self):
        try:
            x = float(self.x_var.get())
            y = float(self.y_var.get())
            r, theta = xy_to_polar(x, y)
            out_deg = (self.ang_mode.get() == "Degrees")
            theta_disp = self._format_angle(theta, out_deg)

            self.r_out.set(f"r = {r:.6g}")
            self.t_out.set(f"θ = {theta_disp:.6g} ({'deg' if out_deg else 'rad'})")

            # plot point and vector
            self._clear_convert_plot()
            self.axC.scatter([x], [y], s=45)
            self.axC.text(x, y, f"({x:.3g},{y:.3g})", fontsize=9)
            self.axC.quiver(0, 0, x, y, angles="xy", scale_units="xy", scale=1)
            self.axC.set_title("Rect → Polar (arrow is position vector)")
            self.canvasC.draw()
            self.statusC.set("Converted x,y → r,θ.")
        except Exception as e:
            self.statusC.set("Error.")
            messagebox.showerror("Conversion Error", str(e))

    def convert_polar_to_xy(self):
        try:
            r = float(self.r_in_var.get())
            in_deg = (self.ang_mode.get() == "Degrees")
            theta = self._parse_angle(self.t_in_var.get(), in_deg)
            x, y = polar_to_xy(r, theta)

            self.x_out.set(f"x = {x:.6g}")
            self.y_out.set(f"y = {y:.6g}")

            # plot point
            self._clear_convert_plot()
            self.axC.scatter([x], [y], s=45)
            self.axC.text(x, y, f"({x:.3g},{y:.3g})", fontsize=9)
            self.axC.quiver(0, 0, x, y, angles="xy", scale_units="xy", scale=1)
            self.axC.set_title("Polar → Rect (arrow is position vector)")
            self.canvasC.draw()
            self.statusC.set("Converted r,θ → x,y.")
        except Exception as e:
            self.statusC.set("Error.")
            messagebox.showerror("Conversion Error", str(e))

    # =========================
    # Tab 2: Polar Plot
    # =========================
    def _build_plot_tab(self):
        left = ttk.Frame(self.tab_plot)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        right = ttk.Frame(self.tab_plot)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.figP, self.axP, self.canvasP = self._make_figure(right, "Polar Curve in the xy-plane")

        ttk.Label(left, text="Polar curve: r = f(theta)").pack(anchor="w")
        self.r_expr_plot = tk.StringVar(value="2 + cos(theta)")
        ttk.Entry(left, textvariable=self.r_expr_plot, width=34).pack(anchor="w", pady=(0, 10))

        ttk.Label(left, text="theta range").pack(anchor="w")
        self.theta_min_plot = tk.StringVar(value="0")
        self.theta_max_plot = tk.StringVar(value="2*pi")
        row = ttk.Frame(left); row.pack(anchor="w", pady=(0, 10))
        ttk.Entry(row, textvariable=self.theta_min_plot, width=10).pack(side=tk.LEFT)
        ttk.Label(row, text=" to ").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.theta_max_plot, width=10).pack(side=tk.LEFT)

        ttk.Label(left, text="samples").pack(anchor="w")
        self.n_plot = tk.StringVar(value="1200")
        ttk.Entry(left, textvariable=self.n_plot, width=10).pack(anchor="w", pady=(0, 10))

        ttk.Label(left, text="xy plot range (for viewing)").pack(anchor="w")
        self.range_plot = tk.StringVar(value="6")
        ttk.Entry(left, textvariable=self.range_plot, width=10).pack(anchor="w", pady=(0, 10))

        ttk.Button(left, text="Plot Curve", command=self.plot_polar_curve).pack(anchor="w")

        ttk.Separator(left).pack(fill=tk.X, pady=10)

        ttk.Label(left, text="Quick examples").pack(anchor="w")
        ex_row = ttk.Frame(left); ex_row.pack(anchor="w", pady=(4, 0))
        ttk.Button(ex_row, text="Rose", command=lambda: self._load_plot_example("2*sin(3*theta)", "0", "2*pi")).pack(side=tk.LEFT)
        ttk.Button(ex_row, text="Cardioid", command=lambda: self._load_plot_example("2 + 2*cos(theta)", "0", "2*pi")).pack(side=tk.LEFT, padx=6)
        ttk.Button(ex_row, text="Spiral", command=lambda: self._load_plot_example("theta/2", "0", "6*pi")).pack(side=tk.LEFT)

        self.statusP = tk.StringVar(value="Ready.")
        ttk.Label(left, textvariable=self.statusP, foreground="#005").pack(anchor="w", pady=(10, 0))

        self.plot_polar_curve()

    def _load_plot_example(self, expr, tmin, tmax):
        self.r_expr_plot.set(expr)
        self.theta_min_plot.set(tmin)
        self.theta_max_plot.set(tmax)
        self.plot_polar_curve()

    def plot_polar_curve(self):
        try:
            f = _safe_theta_expr(self.r_expr_plot.get())
            tmin = self._eval_theta_bound(self.theta_min_plot.get())
            tmax = self._eval_theta_bound(self.theta_max_plot.get())
            n = int(float(self.n_plot.get()))
            view = float(self.range_plot.get())
            if n < 50:
                n = 50

            theta = np.linspace(tmin, tmax, n)
            r = np.asarray(f(theta), dtype=float)

            if not np.all(np.isfinite(r)):
                raise ValueError("r(theta) produced NaN/inf over this interval. Try a different theta range.")

            x = r * np.cos(theta)
            y = r * np.sin(theta)

            self.axP.clear()
            self.axP.grid(True)
            self.axP.set_aspect("equal", adjustable="box")
            self.axP.plot(x, y, linewidth=2)
            self.axP.set_xlim(-view, view)
            self.axP.set_ylim(-view, view)
            self.axP.set_xlabel("x")
            self.axP.set_ylabel("y")
            self.axP.set_title("Polar Curve in the xy-plane")
            self.canvasP.draw()
            self.statusP.set("Plotted polar curve.")
        except Exception as e:
            self.statusP.set("Error.")
            messagebox.showerror("Plot Error", str(e))

    # =========================
    # Tab 4: Polar Area
    # =========================
    def _build_area_tab(self):
        left = ttk.Frame(self.tab_area)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        right = ttk.Frame(self.tab_area)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.figA, self.axA, self.canvasA = self._make_figure(right, "Polar Region (shaded) + Area")

        ttk.Label(left, text="Region in polar: r1(theta) ≤ r ≤ r2(theta)").pack(anchor="w", pady=(0, 4))

        self.r1_expr = tk.StringVar(value="0")
        self.r2_expr = tk.StringVar(value="2 + cos(theta)")

        ttk.Label(left, text="r1(theta) =").pack(anchor="w")
        ttk.Entry(left, textvariable=self.r1_expr, width=34).pack(anchor="w", pady=(0, 8))

        ttk.Label(left, text="r2(theta) =").pack(anchor="w")
        ttk.Entry(left, textvariable=self.r2_expr, width=34).pack(anchor="w", pady=(0, 10))

        ttk.Label(left, text="theta range").pack(anchor="w")
        self.theta_min_area = tk.StringVar(value="0")
        self.theta_max_area = tk.StringVar(value="2*pi")
        row = ttk.Frame(left); row.pack(anchor="w", pady=(0, 10))
        ttk.Entry(row, textvariable=self.theta_min_area, width=10).pack(side=tk.LEFT)
        ttk.Label(row, text=" to ").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.theta_max_area, width=10).pack(side=tk.LEFT)

        ttk.Label(left, text="samples").pack(anchor="w")
        self.n_area = tk.StringVar(value="1200")
        ttk.Entry(left, textvariable=self.n_area, width=10).pack(anchor="w", pady=(0, 10))

        ttk.Label(left, text="xy plot range (for viewing)").pack(anchor="w")
        self.range_area = tk.StringVar(value="6")
        ttk.Entry(left, textvariable=self.range_area, width=10).pack(anchor="w", pady=(0, 10))

        ttk.Button(left, text="Shade + Compute Area", command=self.compute_area).pack(anchor="w")

        self.area_setup = tk.StringVar(
            value="A = ∫(θ=a→b) ∫(r=r1→r2) r dr dθ  =  ∫ 0.5*(r2(θ)^2 - r1(θ)^2) dθ"
        )
        ttk.Label(left, textvariable=self.area_setup, wraplength=280).pack(anchor="w", pady=(10, 0))

        ttk.Separator(left).pack(fill=tk.X, pady=10)

        ttk.Label(left, text="Quick examples").pack(anchor="w")
        ex_row = ttk.Frame(left); ex_row.pack(anchor="w", pady=(4, 0))
        ttk.Button(ex_row, text="Cardioid area", command=self._ex_area_cardioid).pack(side=tk.LEFT)
        ttk.Button(ex_row, text="Rose petal", command=self._ex_area_rose_petal).pack(side=tk.LEFT, padx=6)
        ttk.Button(ex_row, text="Annulus sector", command=self._ex_area_annulus_sector).pack(side=tk.LEFT)

        self.area_out = tk.StringVar(value="Area (polar integral) = ")
        ttk.Label(left, textvariable=self.area_out).pack(anchor="w", pady=(10, 0))

        self.area_out2 = tk.StringVar(value="Check (xy polygon) = ")
        ttk.Label(left, textvariable=self.area_out2).pack(anchor="w", pady=(4, 0))

        self.neg_warn = tk.StringVar(value="")
        ttk.Label(left, textvariable=self.neg_warn, wraplength=280).pack(anchor="w", pady=(4, 0))

        self.statusA = tk.StringVar(value="Ready.")
        ttk.Label(left, textvariable=self.statusA, foreground="#005").pack(anchor="w", pady=(6, 0))

        self.compute_area()

    def _ex_area_cardioid(self):
        self.r1_expr.set("0")
        self.r2_expr.set("2 + 2*cos(theta)")
        self.theta_min_area.set("0")
        self.theta_max_area.set("2*pi")
        self.range_area.set("6")
        self.compute_area()

    def _ex_area_rose_petal(self):
        # Single petal for r = 2*sin(3θ) occurs over θ in [0, pi/3] where sin(3θ) >= 0
        self.r1_expr.set("0")
        self.r2_expr.set("2*sin(3*theta)")
        self.theta_min_area.set("0")
        self.theta_max_area.set("pi/3")
        self.range_area.set("3")
        self.compute_area()

    def _ex_area_annulus_sector(self):
        # ring sector: 2 ≤ r ≤ 4, 0 ≤ θ ≤ pi/2
        self.r1_expr.set("2")
        self.r2_expr.set("4")
        self.theta_min_area.set("0")
        self.theta_max_area.set("pi/2")
        self.range_area.set("5")
        self.compute_area()

    def compute_area(self):
        try:
            self.neg_warn.set("")
            r1f = _safe_theta_expr(self.r1_expr.get())
            r2f = _safe_theta_expr(self.r2_expr.get())
            tmin = self._eval_theta_bound(self.theta_min_area.get())
            tmax = self._eval_theta_bound(self.theta_max_area.get())
            n = int(float(self.n_area.get()))
            view = float(self.range_area.get())
            if n < 200:
                n = 200

            theta = np.linspace(tmin, tmax, n)
            r1 = np.asarray(r1f(theta), dtype=float)
            r2 = np.asarray(r2f(theta), dtype=float)

            if not (np.all(np.isfinite(r1)) and np.all(np.isfinite(r2))):
                raise ValueError("r1(θ) or r2(θ) produced NaN/inf. Try a smaller θ interval or a different function.")

            # Ensure r1 <= r2 pointwise by swapping where needed
            r_low = np.minimum(r1, r2)
            r_high = np.maximum(r1, r2)

            # Warn if negative r values exist (still plotting, but conceptually tricky)
            if np.any(r_low < 0) or np.any(r_high < 0):
                self.neg_warn.set("Note: negative r values detected. The graph may fold across the origin. "
                                  "For clean “region area” examples, try intervals where r ≥ 0.")

            # Polar area:
            # A = ∫_{tmin}^{tmax} ∫_{r_low}^{r_high} r dr dθ
            #   = ∫ 0.5*(r_high^2 - r_low^2) dθ
            integrand = 0.5 * (r_high**2 - r_low**2)
            area_polar = float(np.trapezoid(integrand, theta))

            # Shade region boundaries in xy
            x_outer = r_high * np.cos(theta)
            y_outer = r_high * np.sin(theta)
            x_inner = r_low * np.cos(theta)
            y_inner = r_low * np.sin(theta)

            # Polygon check (approx)
            poly_x = np.concatenate([x_outer, x_inner[::-1]])
            poly_y = np.concatenate([y_outer, y_inner[::-1]])
            area_xy = polygon_area_shoelace(poly_x, poly_y)

            self.area_out.set(f"Area (polar integral) ≈ {area_polar:.6g}")
            self.area_out2.set(f"Check (xy polygon) ≈ {area_xy:.6g}")

            self.axA.clear()
            self.axA.grid(True)
            self.axA.set_aspect("equal", adjustable="box")
            self.axA.set_title("Polar Region (shaded) + Area")

            self.axA.fill(poly_x, poly_y, alpha=0.35)
            self.axA.plot(x_outer, y_outer, linewidth=2, label="r2 boundary")
            self.axA.plot(x_inner, y_inner, linewidth=2, linestyle="--", label="r1 boundary")

            self.axA.set_xlim(-view, view)
            self.axA.set_ylim(-view, view)
            self.axA.set_xlabel("x")
            self.axA.set_ylabel("y")
            self.axA.legend(loc="upper right")

            self.canvasA.draw()
            self.statusA.set("Shaded region and computed area (with check).")
        except Exception as e:
            self.statusA.set("Error.")
            messagebox.showerror("Area Error", str(e))

    # =========================
    # Tab 5: Arc Length
    # =========================
    def _build_arc_tab(self):
        left = ttk.Frame(self.tab_arc)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        right = ttk.Frame(self.tab_arc)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.figL, self.axL, self.canvasL = self._make_figure(right, "Polar Curve + Arc Length Approximation")

        ttk.Label(left, text="Arc length of polar curve r = f(theta)").pack(anchor="w")
        self.r_expr_len = tk.StringVar(value="2 + cos(theta)")
        ttk.Entry(left, textvariable=self.r_expr_len, width=34).pack(anchor="w", pady=(0, 10))

        ttk.Label(left, text="theta range").pack(anchor="w")
        self.theta_min_len = tk.StringVar(value="0")
        self.theta_max_len = tk.StringVar(value="2*pi")
        row = ttk.Frame(left); row.pack(anchor="w", pady=(0, 10))
        ttk.Entry(row, textvariable=self.theta_min_len, width=10).pack(side=tk.LEFT)
        ttk.Label(row, text=" to ").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.theta_max_len, width=10).pack(side=tk.LEFT)

        ttk.Label(left, text="samples").pack(anchor="w")
        self.n_len = tk.StringVar(value="2000")
        ttk.Entry(left, textvariable=self.n_len, width=10).pack(anchor="w", pady=(0, 10))

        ttk.Label(left, text="xy plot range (for viewing)").pack(anchor="w")
        self.range_len = tk.StringVar(value="6")
        ttk.Entry(left, textvariable=self.range_len, width=10).pack(anchor="w", pady=(0, 10))

        ttk.Button(left, text="Plot + Compute Arc Length", command=self.compute_arc_length).pack(anchor="w")

        self.len_setup = tk.StringVar(value="L = ∫ sqrt( r(θ)^2 + (dr/dθ)^2 ) dθ")
        ttk.Label(left, textvariable=self.len_setup, wraplength=280).pack(anchor="w", pady=(10, 0))

        ttk.Separator(left).pack(fill=tk.X, pady=10)

        ttk.Label(left, text="Quick examples").pack(anchor="w")
        ex_row = ttk.Frame(left); ex_row.pack(anchor="w", pady=(4, 0))
        ttk.Button(ex_row, text="Cardioid", command=lambda: self._load_len_example("2 + 2*cos(theta)", "0", "2*pi", "6")).pack(side=tk.LEFT)
        ttk.Button(ex_row, text="Rose", command=lambda: self._load_len_example("2*sin(3*theta)", "0", "2*pi", "3")).pack(side=tk.LEFT, padx=6)
        ttk.Button(ex_row, text="Spiral", command=lambda: self._load_len_example("theta/2", "0", "6*pi", "10")).pack(side=tk.LEFT)

        self.len_out = tk.StringVar(value="Arc length (polar formula) = ")
        ttk.Label(left, textvariable=self.len_out).pack(anchor="w", pady=(10, 0))

        self.len_out2 = tk.StringVar(value="Check (xy chord sum) = ")
        ttk.Label(left, textvariable=self.len_out2).pack(anchor="w", pady=(4, 0))

        self.dr_out = tk.StringVar(value="max |dr/dθ| = ")
        ttk.Label(left, textvariable=self.dr_out).pack(anchor="w", pady=(4, 0))

        self.statusL = tk.StringVar(value="Ready.")
        ttk.Label(left, textvariable=self.statusL, foreground="#005").pack(anchor="w", pady=(6, 0))

        self.compute_arc_length()

    def _load_len_example(self, expr, tmin, tmax, view):
        self.r_expr_len.set(expr)
        self.theta_min_len.set(tmin)
        self.theta_max_len.set(tmax)
        self.range_len.set(view)
        self.compute_arc_length()

    def compute_arc_length(self):
        try:
            f = _safe_theta_expr(self.r_expr_len.get())
            tmin = self._eval_theta_bound(self.theta_min_len.get())
            tmax = self._eval_theta_bound(self.theta_max_len.get())
            n = int(float(self.n_len.get()))
            view = float(self.range_len.get())
            if n < 300:
                n = 300

            theta = np.linspace(tmin, tmax, n)
            r = np.asarray(f(theta), dtype=float)

            if not np.all(np.isfinite(r)):
                raise ValueError("r(theta) produced NaN/inf over this interval. Try a different theta range.")

            # Polar arc length:
            # L = ∫ sqrt( r^2 + (dr/dθ)^2 ) dθ
            dr = np.gradient(r, theta)
            integrand = np.sqrt(r * r + dr * dr)
            L_polar = float(np.trapezoid(integrand, theta))

            x = r * np.cos(theta)
            y = r * np.sin(theta)

            # Sanity check: sum of chord lengths in xy plane
            L_xy = polyline_length(x, y)

            self.len_out.set(f"Arc length (polar formula) ≈ {L_polar:.6g}")
            self.len_out2.set(f"Check (xy chord sum) ≈ {L_xy:.6g}")
            self.dr_out.set(f"max |dr/dθ| ≈ {float(np.max(np.abs(dr))):.6g}")

            self.axL.clear()
            self.axL.grid(True)
            self.axL.set_aspect("equal", adjustable="box")
            self.axL.plot(x, y, linewidth=2)
            self.axL.set_xlim(-view, view)
            self.axL.set_ylim(-view, view)
            self.axL.set_xlabel("x")
            self.axL.set_ylabel("y")
            self.axL.set_title("Polar Curve + Arc Length Approximation")
            self.canvasL.draw()
            self.statusL.set("Computed arc length (with check).")
        except Exception as e:
            self.statusL.set("Error.")
            messagebox.showerror("Arc Length Error", str(e))


if __name__ == "__main__":
    app = SDL3NewCoordinatesApp()
    app.mainloop()