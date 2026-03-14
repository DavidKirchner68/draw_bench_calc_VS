"""
Draw Bench Calculator
Wire Drawing Analysis Tool
Based on proc_draw.prg and Wire Technology by Roger N. Wright
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math


# ─────────────────────────────────────────────────────────────
#  Unit conversion constants
# ─────────────────────────────────────────────────────────────

PSI_TO_MPA   = 6.89476e-3          # 1 psi  = 0.00689476 MPa
MPA_TO_PSI   = 145.038             # 1 MPa  = 145.038 psi
N_TO_LBF     = 0.224809            # 1 N    = 0.224809 lbf
KW_TO_HP     = 1.34102             # 1 kW   = 1.34102 hp
M_S_TO_FT_MIN = 196.850            # 1 m/s  = 196.85 ft/min
PA_TO_PSI    = PSI_TO_MPA * 1e-6   # 1 Pa → psi  (= 1.4504e-4)

def dt_c_to_f(delta_c):
    """Temperature RISE  °C → °F   (ΔF = ΔC × 9/5)"""
    return delta_c * 9.0 / 5.0

def abs_c_to_f(c):
    """Absolute temperature  °C → °F"""
    return c * 9.0 / 5.0 + 32.0


# ─────────────────────────────────────────────────────────────
#  Pure calculation functions  (mirror proc_draw.prg logic)
# ─────────────────────────────────────────────────────────────

def area(d):
    """Cross-sectional area of a round wire."""
    return math.pi * d ** 2 / 4.0

def ra_from_diameters(d0, d1):
    """RA = (D0²−D1²)/D0²"""
    return (d0 ** 2 - d1 ** 2) / d0 ** 2

def d1_from_ra(d0, ra):
    """D1 = D0·√(1−RA)"""
    return d0 * math.sqrt(1.0 - ra)

def true_strain_ra(ra):
    """ε = ln(1/(1−RA))"""
    return math.log(1.0 / (1.0 - ra))

def engineering_strain(a0, a1):
    """e = (A0−A1)/A1"""
    return (a0 - a1) / a1

def length_ratio(ra):
    """L1/L0 = 1/(1−RA)"""
    return 1.0 / (1.0 - ra)

def deformation_zone_length(d0, d1, alpha_rad):
    """Ld = (D0−D1)/(2·tan α)"""
    return (d0 - d1) / (2.0 * math.tan(alpha_rad))

def die_contact_length(d0, d1, alpha_rad):
    """Lc = (D0−D1)/(2·sin α)"""
    return (d0 - d1) / (2.0 * math.sin(alpha_rad))

def delta(alpha_rad, ra):
    """Δ = (α/RA)·(1 + √(1−RA))²"""
    return (alpha_rad / ra) * (1.0 + math.sqrt(1.0 - ra)) ** 2

def redundant_work_factor_delta(delta_val):
    """Φ = (Δ/6) + 1"""
    return (delta_val / 6.0) + 1.0

def redundant_work_factor_delta2(delta_val):
    """Θ = 0.8 + (Δ/4.4)"""
    return 0.8 + (delta_val / 4.4)

def optimum_delta(cof, ra):
    """Δ_opt = 1.89·√(μ/RA)·(1 + √(1−RA))"""
    return 1.89 * math.sqrt(cof / ra) * (1.0 + math.sqrt(1.0 - ra))

def optimum_angle_rad(cof, ra):
    """α_opt (rad) = 1.89·√(μ·RA)·(1 + √(1−RA))"""
    return 1.89 * math.sqrt(cof * ra) * (1.0 + math.sqrt(1.0 - ra))

def draw_stress_MPa(sigma_a_MPa, delta_val, alpha_rad, cof):
    """σ_d = σ_a·[(3.2/Δ)+0.9]·(α+μ)   (MPa in, MPa out)"""
    return sigma_a_MPa * ((3.2 / delta_val) + 0.9) * (alpha_rad + cof)

def drawing_stress_ratio(sigma_d, sigma_a):
    """Σ = σ_d / σ_a"""
    return sigma_d / sigma_a

def draw_force_N(sigma_d_Pa, a1_m2):
    """F = σ_d · A1  (Pa · m² = N)"""
    return sigma_d_Pa * a1_m2

def power_kW(force_N, velocity_m_s):
    """P = F·V  (N·m/s = W → /1000 = kW)"""
    return force_N * velocity_m_s / 1000.0

def velocity_in(v_out, a0, a1):
    """V0 = V1·A1/A0"""
    return v_out * a1 / a0

def work_uniform_MPa(sigma_a_MPa, ra):
    """Wu = σ_a·ln(1/(1−RA))  (MPa)"""
    return sigma_a_MPa * math.log(1.0 / (1.0 - ra))

def work_redundant_MPa(phi, sigma_a_MPa, ra):
    """Wr = (Φ−1)·σ_a·ln(1/(1−RA))  (MPa)"""
    return (phi - 1.0) * sigma_a_MPa * math.log(1.0 / (1.0 - ra))

def work_friction_MPa(cof, phi, sigma_a_MPa, delta_val):
    """Wf = 4·μ·Φ·σ_a / Δ  (MPa)"""
    return 4.0 * cof * phi * sigma_a_MPa / delta_val

def avg_die_pressure_MPa(phi, sigma_a_MPa):
    """P = Φ·σ_a  (MPa)"""
    return phi * sigma_a_MPa

def avg_strain_rate(epsilon_t, v0, v1, ld):
    """ε̇ = ε_t·(V0+V1)/(2·Ld)"""
    return epsilon_t * (v0 + v1) / (2.0 * ld)

# ── Thermal (all SI: Pa, kg/m³, J/(kg·K), W/(m·K), results in °C) ──

def adiabatic_rise_C(sigma_d_Pa, spec_heat, density):
    """ΔT = σ_d/(C·ρ)  °C"""
    return sigma_d_Pa / (spec_heat * density)

def wire_temperature_rise_C(delta_val, sigma_a_Pa, ra, spec_heat, density):
    """Tw = Δ·σ_a·ln(1/(1−RA))/(C·ρ)  °C"""
    return delta_val * sigma_a_Pa * math.log(1.0 / (1.0 - ra)) / (spec_heat * density)

def uniform_temp_rise_C(sigma_a_Pa, ra, spec_heat, density):
    """Tuw = σ_a·ln(1/(1−RA))/(C·ρ)  °C"""
    return sigma_a_Pa * math.log(1.0 / (1.0 - ra)) / (spec_heat * density)

def redundant_temp_rise_C(delta_val, sigma_a_Pa, ra, spec_heat, density):
    """Trw = (Δ−1)·σ_a·ln(1/(1−RA))/(C·ρ)  °C"""
    return (delta_val - 1.0) * sigma_a_Pa * math.log(1.0 / (1.0 - ra)) / (spec_heat * density)

def equilibrated_temp_C(t0_c, sigma_d_Pa, spec_heat, density):
    """Teq = T0 + σ_d/(C·ρ)  °C"""
    return t0_c + sigma_d_Pa / (spec_heat * density)

def frictional_heating_C(cof, delta_val, sigma_a_Pa, velocity_m_s, ld, spec_heat, density, k_thermal):
    """Surface frictional heat = 1.25·μ·Δ·σ_a·√(v·Ld/(C·ρ·K))  °C"""
    return (1.25 * cof * delta_val * sigma_a_Pa *
            math.sqrt((velocity_m_s * ld) / (spec_heat * density * k_thermal)))


# ─────────────────────────────────────────────────────────────
#  Color & style constants
# ─────────────────────────────────────────────────────────────

WARN_COLOR    = "#c0392b"
CAUTION_COLOR = "#e67e22"
OK_COLOR      = "#1a7a3a"
NEUTRAL_COLOR = "#2c3e50"
BG            = "#f4f6f8"
PANEL_BG      = "#ffffff"
HEADER_BG     = "#1a3a5c"
ACCENT        = "#2980b9"
DIV_COLOR     = "#95a5a6"
IMP_BG        = "#fdf6ec"   # warm tint for Imperial column
MET_BG        = "#ecf5fd"   # cool tint for Metric column


# ─────────────────────────────────────────────────────────────
#  Reusable widget classes
# ─────────────────────────────────────────────────────────────

def _bind_tooltip(widget, text):
    tip = [None]
    def show(e):
        x, y = e.widget.winfo_rootx() + 22, e.widget.winfo_rooty() + 20
        tip[0] = tw = tk.Toplevel()
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=text, background="#ffffe0", relief='solid',
                 borderwidth=1, font=("Arial", 9), justify='left').pack()
    def hide(e):
        if tip[0]: tip[0].destroy(); tip[0] = None
    widget.bind("<Enter>", show)
    widget.bind("<Leave>", hide)


class ResultRow:
    """Single-value result row (used in Basic and Die Geometry tabs)."""

    def __init__(self, parent, label, unit="", tooltip="", row=0,
                 label_width=0, label_anchor='w', label_sticky='w'):
        lbl_kwargs = {
            "text": label,
            "font": ("Arial", 9),
            "bg": PANEL_BG,
            "anchor": label_anchor,
        }
        if label_width:
            lbl_kwargs["width"] = label_width
        lbl = tk.Label(parent, **lbl_kwargs)
        lbl.grid(row=row, column=0, sticky=label_sticky, padx=(6, 2), pady=2)
        if tooltip:
            lbl.config(text=label + " ⓘ", cursor="question_arrow")
            _bind_tooltip(lbl, tooltip)

        self.val_lbl = tk.Label(parent, text="—",
                                font=("Courier New", 10, "bold"),
                                bg="#eaf0fb", anchor='e', width=14,
                                relief='groove', padx=4)
        self.val_lbl.grid(row=row, column=1, sticky='e', padx=2, pady=2)

        if unit:
            tk.Label(parent, text=unit, font=("Arial", 9),
                     bg=PANEL_BG, anchor='w').grid(
                row=row, column=2, sticky='w', padx=(0, 6))

    def set(self, value, color=NEUTRAL_COLOR, fmt="{:.6g}"):
        if value is None:
            self.val_lbl.config(text="—", fg=NEUTRAL_COLOR)
        else:
            self.val_lbl.config(text=fmt.format(value), fg=color)

    def clear(self):
        self.val_lbl.config(text="—", fg=NEUTRAL_COLOR)


class DualResultRow:
    """
    Two-value result row showing Imperial | Metric side by side.
    Column layout  (all in parent grid):
      col 0  – row label
      col 1  – imperial value box
      col 2  – imperial unit label
      col 3  – divider  "|"
      col 4  – metric value box
      col 5  – metric unit label
    """

    def __init__(self, parent, label,
                 unit_imp="", unit_met="",
                 tooltip="", row=0, bold_label=False,
                 label_width=0, label_anchor='w', label_sticky='w',
                 metric_first=False):
        font_lbl = ("Arial", 9, "bold") if bold_label else ("Arial", 9)
        lbl_kwargs = {
            "text": label,
            "font": font_lbl,
            "bg": PANEL_BG,
            "anchor": label_anchor,
        }
        if label_width:
            lbl_kwargs["width"] = label_width
        lbl = tk.Label(parent, **lbl_kwargs)
        lbl.grid(row=row, column=0, sticky=label_sticky, padx=(6, 4), pady=2)
        if tooltip:
            lbl.config(text=label + " ⓘ", cursor="question_arrow")
            _bind_tooltip(lbl, tooltip)

        if metric_first:
            self.met_lbl = tk.Label(parent, text="—",
                                    font=("Courier New", 10, "bold"),
                                    bg=MET_BG, anchor='e', width=13,
                                    relief='groove', padx=4)
            self.met_lbl.grid(row=row, column=1, sticky='e', padx=2, pady=2)

            tk.Label(parent, text=unit_met, font=("Arial", 9),
                     bg=PANEL_BG, anchor='w', width=8).grid(
                row=row, column=2, sticky='w')

            tk.Label(parent, text="│", font=("Arial", 10),
                     bg=PANEL_BG, fg=DIV_COLOR).grid(
                row=row, column=3, padx=4)

            self.imp_lbl = tk.Label(parent, text="—",
                                    font=("Courier New", 10, "bold"),
                                    bg=IMP_BG, anchor='e', width=13,
                                    relief='groove', padx=4)
            self.imp_lbl.grid(row=row, column=4, sticky='e', padx=2, pady=2)

            tk.Label(parent, text=unit_imp, font=("Arial", 9),
                     bg=PANEL_BG, anchor='w', width=6).grid(
                row=row, column=5, sticky='w', padx=(0, 6))
        else:
            self.imp_lbl = tk.Label(parent, text="—",
                                    font=("Courier New", 10, "bold"),
                                    bg=IMP_BG, anchor='e', width=13,
                                    relief='groove', padx=4)
            self.imp_lbl.grid(row=row, column=1, sticky='e', padx=2, pady=2)

            tk.Label(parent, text=unit_imp, font=("Arial", 9),
                     bg=PANEL_BG, anchor='w', width=6).grid(
                row=row, column=2, sticky='w')

            tk.Label(parent, text="│", font=("Arial", 10),
                     bg=PANEL_BG, fg=DIV_COLOR).grid(
                row=row, column=3, padx=4)

            self.met_lbl = tk.Label(parent, text="—",
                                    font=("Courier New", 10, "bold"),
                                    bg=MET_BG, anchor='e', width=13,
                                    relief='groove', padx=4)
            self.met_lbl.grid(row=row, column=4, sticky='e', padx=2, pady=2)

            tk.Label(parent, text=unit_met, font=("Arial", 9),
                     bg=PANEL_BG, anchor='w', width=8).grid(
                row=row, column=5, sticky='w', padx=(0, 6))

    def set(self, val_imp, val_met,
            color=NEUTRAL_COLOR,
            fmt_imp="{:,.1f}", fmt_met="{:.2f}"):
        for lbl, val, fmt in ((self.imp_lbl, val_imp, fmt_imp),
                               (self.met_lbl, val_met, fmt_met)):
            if val is None:
                lbl.config(text="—", fg=NEUTRAL_COLOR)
            else:
                lbl.config(text=fmt.format(val), fg=color)

    def set_imp(self, val, color=NEUTRAL_COLOR, fmt="{:,.1f}"):
        if val is None:
            self.imp_lbl.config(text="—", fg=NEUTRAL_COLOR)
        else:
            self.imp_lbl.config(text=fmt.format(val), fg=color)

    def set_met(self, val, color=NEUTRAL_COLOR, fmt="{:.2f}"):
        if val is None:
            self.met_lbl.config(text="—", fg=NEUTRAL_COLOR)
        else:
            self.met_lbl.config(text=fmt.format(val), fg=color)

    def clear(self):
        self.imp_lbl.config(text="—", fg=NEUTRAL_COLOR)
        self.met_lbl.config(text="—", fg=NEUTRAL_COLOR)


def _col_header_row(parent, row, label_text="", imp_text="Imperial", met_text="Metric",
                    label_width=0, label_anchor='w', label_sticky='w',
                    metric_first=False):
    """Inserts column header labels above a DualResultRow block."""
    if label_text:
        hdr_kwargs = {
            "text": label_text,
            "font": ("Arial", 8, "italic"),
            "bg": PANEL_BG,
            "fg": "#555",
            "anchor": label_anchor,
        }
        if label_width:
            hdr_kwargs["width"] = label_width
        tk.Label(parent, **hdr_kwargs).grid(
            row=row, column=0, sticky=label_sticky, padx=6, pady=(6, 0))
    if metric_first:
        hdr_cols = ((1, met_text, MET_BG), (4, imp_text, IMP_BG))
    else:
        hdr_cols = ((1, imp_text, IMP_BG), (4, met_text, MET_BG))

    for col, txt, bg in hdr_cols:
        tk.Label(parent, text=txt, font=("Arial", 8, "bold"),
                 bg=bg, fg=HEADER_BG, anchor='center', width=13,
                 relief='flat').grid(row=row, column=col, padx=2, pady=(4, 0))


# ─────────────────────────────────────────────────────────────
#  Main application
# ─────────────────────────────────────────────────────────────

def safe_float(s, label=""):
    try:
        return float(s.strip())
    except ValueError:
        raise ValueError(f"'{label}' must be a number (got: '{s}')")


class DrawBenchApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Draw Bench Calculator  –  Wire Drawing Analysis")
        self.root.geometry("860x870")
        self.root.minsize(760, 720)
        self.root.configure(bg=BG)
        self._suppress = False
        self._last_unit = "in"
        self._syncing_angle = False
        self._build_ui()

    # ──────────────────────────────────────────────────────────
    #  Top-level layout
    # ──────────────────────────────────────────────────────────

    def _build_ui(self):
        hdr = tk.Frame(self.root, bg=HEADER_BG)
        hdr.pack(fill='x')
        tk.Label(hdr, text="Draw Bench Calculator",
                 font=("Arial", 17, "bold"), bg=HEADER_BG, fg="white",
                 pady=8).pack(side='left', padx=16)
        tk.Label(hdr, text="Wire Drawing Analysis  |  Wright, Wire Technology",
                 font=("Arial", 9), bg=HEADER_BG, fg="#a8c4d8").pack(
            side='left', padx=4)

        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill='both', expand=True, padx=10, pady=8)

        self._build_tab_basic()
        self._build_tab_die()
        self._build_tab_stress()
        self._build_tab_thermal()
        self._build_tab_schedule()

        self.status_var = tk.StringVar(value="Ready – enter values in the Basic tab first.")
        tk.Label(self.root, textvariable=self.status_var,
                 font=("Arial", 9), bg="#dce3ea", relief='sunken',
                 anchor='w', padx=8).pack(fill='x', side='bottom', ipady=3)

    # ──────────────────────────────────────────────────────────
    #  TAB 1 – Basic
    # ──────────────────────────────────────────────────────────

    def _build_tab_basic(self):
        tab = tk.Frame(self.nb, bg=BG)
        self.nb.add(tab, text="  Basic  ")

        inp = tk.LabelFrame(tab, text="  Inputs  ",
                            font=("Arial", 10, "bold"),
                            bg=PANEL_BG, fg=HEADER_BG, padx=10, pady=8)
        inp.pack(fill='x', padx=12, pady=(10, 4))

        # units
        unit_row = tk.Frame(inp, bg=PANEL_BG)
        unit_row.pack(fill='x', pady=(0, 6))
        tk.Label(unit_row, text="Diameter units:", font=("Arial", 10),
                 bg=PANEL_BG).pack(side='left')
        self.unit_var = tk.StringVar(value="in")
        for txt, val in [("Inches (in)", "in"), ("Millimeters (mm)", "mm")]:
            tk.Radiobutton(unit_row, text=txt, variable=self.unit_var, value=val,
                           bg=PANEL_BG, font=("Arial", 10),
                           command=self._update_unit_labels).pack(side='left', padx=8)

        # D0
        d0r = tk.Frame(inp, bg=PANEL_BG)
        d0r.pack(fill='x', pady=3)
        tk.Label(d0r, text="Original Diameter  D₀ :", font=("Arial", 10),
                 bg=PANEL_BG, width=28, anchor='e').pack(side='left')
        self.d0_var = tk.StringVar()
        self.d0_entry = tk.Entry(d0r, textvariable=self.d0_var,
                                 font=("Arial", 12), width=14)
        self.d0_entry.pack(side='left', padx=4)
        self.d0_unit_lbl = tk.Label(d0r, text="in", font=("Arial", 10),
                                    bg=PANEL_BG, width=4, anchor='e')
        self.d0_unit_lbl.pack(side='left')

        tk.Label(inp,
                 text="Enter ONE of the following  (the other will be calculated):",
                 font=("Arial", 9, "italic"), bg=PANEL_BG, fg="#555").pack(
            anchor='w', pady=(8, 2))

        # D1
        d1r = tk.Frame(inp, bg=PANEL_BG)
        d1r.pack(fill='x', pady=3)
        tk.Label(d1r, text="Output Diameter  D₁ :", font=("Arial", 10),
                 bg=PANEL_BG, width=28, anchor='e').pack(side='left')
        self.d1_var = tk.StringVar()
        self.d1_entry = tk.Entry(d1r, textvariable=self.d1_var,
                                 font=("Arial", 12), width=14)
        self.d1_entry.pack(side='left', padx=4)
        self.d1_entry.bind("<FocusOut>", self._on_d1_focus_out)
        self.d1_unit_lbl = tk.Label(d1r, text="in", font=("Arial", 10),
                                    bg=PANEL_BG, width=4, anchor='e')
        self.d1_unit_lbl.pack(side='left')
        tk.Label(d1r, text="← fill this  OR  the RA below →",
                 font=("Arial", 9, "italic"), bg=PANEL_BG, fg="#888").pack(
            side='left', padx=8)

        # CW%
        cwr = tk.Frame(inp, bg=PANEL_BG)
        cwr.pack(fill='x', pady=3)
        tk.Label(cwr, text="Cold Work / Red. of Area  RA :", font=("Arial", 10),
                 bg=PANEL_BG, width=28, anchor='e').pack(side='left')
        self.cw_var = tk.StringVar()
        self.cw_entry = tk.Entry(cwr, textvariable=self.cw_var,
                                 font=("Arial", 12), width=14)
        self.cw_entry.pack(side='left', padx=4)
        tk.Label(cwr, text="%", font=("Arial", 10), bg=PANEL_BG,
                 width=4, anchor='e').pack(side='left')

        # buttons
        bf = tk.Frame(tab, bg=BG)
        bf.pack(pady=6)
        tk.Button(bf, text="  Calculate  ", font=("Arial", 12, "bold"),
                  bg=ACCENT, fg="white", relief='flat', padx=12, pady=6,
                  cursor="hand2", command=self._calc_basic).pack(side='left', padx=6)
        tk.Button(bf, text="  Clear  ", font=("Arial", 11),
                  bg="#95a5a6", fg="white", relief='flat', padx=8, pady=6,
                  cursor="hand2", command=self._clear_all).pack(side='left', padx=6)

        # results
        res = tk.LabelFrame(tab, text="  Results  ",
                            font=("Arial", 10, "bold"),
                            bg=PANEL_BG, fg=HEADER_BG, padx=10, pady=8)
        res.pack(fill='both', expand=True, padx=12, pady=4)

        unit = self.unit_var.get()
        basic_row_opts = dict(label_width=34, label_anchor='e', label_sticky='e')
        self.r_ra_pct      = ResultRow(res, "Reduction of Area (RA)", "%",
                           "RA = (D0²−D1²)/D0² × 100", row=0,
                           **basic_row_opts)
        self.r_ra_frac     = ResultRow(res, "RA Fraction", "",
                           "Fraction form  0.0 – 1.0", row=1,
                           **basic_row_opts)
        self.r_true_strain = ResultRow(res, "True Strain  ε", "",
                           "ε = ln(A0/A1) = ln(1/(1−RA))", row=2,
                           **basic_row_opts)
        self.r_eng_strain  = ResultRow(res, "Engineering Strain  e", "",
                           "e = (A0−A1)/A1", row=3,
                           **basic_row_opts)
        self.r_a0          = ResultRow(res, "Original Area  A₀", "",
                           "Cross-sectional area before drawing", row=4,
                           **basic_row_opts)
        self.r_a1          = ResultRow(res, "Final Area  A₁", "",
                           "Cross-sectional area after drawing", row=5,
                           **basic_row_opts)
        self.r_length_ratio = ResultRow(res, "Length Ratio  L₁/L₀", "",
                        "Volume conservation: L1/L0 = A0/A1", row=6,
                        **basic_row_opts)
        self.r_dia_ratio   = ResultRow(res, "Diameter Ratio  D₁/D₀", "",
                           "", row=7, **basic_row_opts)
        self.r_d1_calc     = ResultRow(res, "Calculated D₁", "", "", row=8,
                           **basic_row_opts)
        self.r_cw_calc     = ResultRow(res, "Calculated RA", "%", "", row=9,
                           **basic_row_opts)

        tk.Label(tab,
                 text="Commercial practice rarely involves reductions above 30% per pass.  "
                      "Drawing limit: draw stress / flow stress < 1.0",
                 font=("Arial", 8, "italic"), bg=BG, fg="#555",
                 wraplength=720, justify='left').pack(anchor='w', padx=14, pady=(0, 6))

    # ──────────────────────────────────────────────────────────
    #  TAB 2 – Die Geometry
    # ──────────────────────────────────────────────────────────

    def _build_tab_die(self):
        tab = tk.Frame(self.nb, bg=BG)
        self.nb.add(tab, text="  Die Geometry  ")

        inp = tk.LabelFrame(
            tab,
            text="  Die Parameters  (requires Basic tab calculation first)  ",
            font=("Arial", 10, "bold"), bg=PANEL_BG, fg=HEADER_BG,
            padx=10, pady=8)
        inp.pack(fill='x', padx=12, pady=(10, 4))

        self.alpha_var = tk.StringVar(value="16")
        self.alpha_var.trace_add("write", self._sync_angle_from_die)
        self._add_input_row(inp, 0, "Die Included Angle  (full) :", self.alpha_var,
                            "degrees",
                            "Full included angle of the die (semi-angle = this ÷ 2)")

        self.cof_var = tk.StringVar(value="0.10")
        self._add_input_row(inp, 1, "Coefficient of Friction  μ :", self.cof_var, "",
                            "Typical: 0.08–0.12 WC dies, good lube;  0.15 = high friction")

        tk.Button(inp, text="  Calculate Die Geometry  ",
                  font=("Arial", 11, "bold"),
                  bg=ACCENT, fg="white", relief='flat', padx=10, pady=5,
                  cursor="hand2", command=self._calc_die).grid(
            row=2, column=0, columnspan=4, pady=10)

        res = tk.LabelFrame(tab, text="  Die Geometry Results  ",
                            font=("Arial", 10, "bold"),
                            bg=PANEL_BG, fg=HEADER_BG, padx=10, pady=8)
        res.pack(fill='both', expand=True, padx=12, pady=4)

        self.r_delta      = ResultRow(res, "Deformation Zone Param  Δ", "",
                                      "Δ = (α/RA)·(1+√(1−RA))²  –  ideal 1–3", row=0)
        self.r_ld         = ResultRow(res, "Deformation Zone Length  Ld", "",
                                      "Ld = (D0−D1)/(2·tan α)", row=1)
        self.r_lc         = ResultRow(res, "Die Contact Length  Lc", "",
                                      "Lc = (D0−D1)/(2·sin α)", row=2)
        self.r_phi        = ResultRow(res, "Redundant Work Factor  Φ", "",
                                      "Φ = (Δ/6)+1", row=3)
        self.r_phi2       = ResultRow(res, "Redundant Work Factor  Θ  (alt.)", "",
                                      "Θ = 0.8 + Δ/4.4", row=4)
        self.r_delta_opt  = ResultRow(res, "Optimum Δ  (for μ, RA)", "",
                                      "Δ_opt = 1.89·√(μ/RA)·(1+√(1−RA))", row=5)
        self.r_alpha_opt  = ResultRow(res, "Optimum Included Angle  (full)", "°",
                                      "Full die angle = 2·α_opt that minimises draw stress", row=6)

        self._die_warn = tk.Label(tab, text="", font=("Arial", 9, "bold"),
                                  bg=BG, fg=WARN_COLOR, wraplength=720, justify='left')
        self._die_warn.pack(anchor='w', padx=14, pady=2)

    # ──────────────────────────────────────────────────────────
    #  TAB 3 – Stress & Force  (DUAL UNITS)
    # ──────────────────────────────────────────────────────────

    def _build_tab_stress(self):
        tab = tk.Frame(self.nb, bg=BG)
        self.nb.add(tab, text="  Stress & Force  ")

        # ── Inputs ──────────────────────────────────────────
        inp = tk.LabelFrame(
            tab,
            text="  Stress Inputs  (requires Die Geometry tab first)  ",
            font=("Arial", 10, "bold"), bg=PANEL_BG, fg=HEADER_BG,
            padx=10, pady=8)
        inp.pack(fill='x', padx=12, pady=(10, 4))

        # Display RA pulled from Basic tab in user-facing Cold Work % format
        self.stress_cw_var = tk.StringVar(value="")
        tk.Label(inp, text="Cold Work :", font=("Arial", 10),
                 bg=PANEL_BG, width=34, anchor='e').grid(
            row=0, column=0, sticky='e', padx=(0, 4), pady=(0, 4))
        tk.Entry(inp, textvariable=self.stress_cw_var,
                 font=("Arial", 11), width=14,
                 state='readonly', readonlybackground="#eef4ff",
                 fg="#1f4e79").grid(
            row=0, column=1, sticky='w', padx=4, pady=(0, 4))
        tk.Label(inp, text="%", font=("Arial", 9), bg=PANEL_BG,
                 width=6, anchor='w').grid(row=0, column=2, sticky='w')

        # Column headers for input section
        tk.Label(inp, text="", bg=PANEL_BG, width=34).grid(row=1, column=0)
        tk.Label(inp, text="psi", font=("Arial", 9, "bold"),
                 bg=IMP_BG, fg=HEADER_BG, width=14, anchor='center',
                 relief='flat').grid(row=1, column=1, padx=2, pady=(2, 4))
        tk.Label(inp, text="", bg=PANEL_BG, width=6).grid(row=1, column=2)
        tk.Label(inp, text="│", fg=DIV_COLOR, bg=PANEL_BG).grid(row=1, column=3)
        tk.Label(inp, text="MPa  (auto-converted)",
                 font=("Arial", 9, "bold"),
                 bg=MET_BG, fg=HEADER_BG, width=20, anchor='center',
                 relief='flat').grid(row=1, column=4, columnspan=2,
                                     padx=2, pady=(2, 4))
        stress_label_opts = dict(label_width=34, label_anchor='e', label_sticky='e')

        # Beginning yield
        self.yield_begin_var = tk.StringVar(value="90,000")
        self.yield_begin_mpa_var = tk.StringVar(value="")
        self.yield_begin_var.trace_add("write", self._format_beginning_yield)
        self._add_dual_input_row(
            inp, 2,
            "Beginning Yield Strength  σ_y₀ :",
            self.yield_begin_var, "psi",
            self.yield_begin_mpa_var, "MPa",
            "Yield strength of wire entering the die",
            psi_trace=True,
            **stress_label_opts)

        # Final (cold worked) yield
        self.yield_final_var = tk.StringVar(value="180,000")
        self.yield_final_mpa_var = tk.StringVar(value="")
        self.yield_final_var.trace_add("write", self._format_final_yield)
        self._add_dual_input_row(
            inp, 3,
            "Final Cold Worked Yield  σ_y₁ :",
            self.yield_final_var, "psi",
            self.yield_final_mpa_var, "MPa",
            "Yield strength of wire after drawing",
            psi_trace=True,
            **stress_label_opts)

        # Speed (metric only – common in wire industry)
        self.v_out_var = tk.StringVar(value="1")
        self._add_input_row(inp, 4, "Exit Drawing Speed  V₁ :",
                    self.v_out_var, "m/s",
                    "Default is 1 m/s. Change as needed for Force and Power.",
                            **stress_label_opts)

        tk.Button(inp, text="  Calculate Stress & Force  ",
                  font=("Arial", 11, "bold"),
                  bg=ACCENT, fg="white", relief='flat', padx=10, pady=5,
                  cursor="hand2", command=self._calc_stress).grid(
            row=5, column=0, columnspan=6, pady=10)

        # ── Results ─────────────────────────────────────────
        # Scrollable frame so results don't clip on small screens
        res_outer = tk.LabelFrame(
            tab, text="  Results  –  Imperial  │  Metric  ",
            font=("Arial", 10, "bold"),
            bg=PANEL_BG, fg=HEADER_BG, padx=6, pady=6)
        res_outer.pack(fill='both', expand=True, padx=12, pady=4)

        res = res_outer   # direct grid in frame (no scroll needed – fits in window)

        stress_row_opts = dict(label_width=34, label_anchor='e', label_sticky='e')
        _col_header_row(res, row=0, label_text="Stress values:", **stress_row_opts)
        r = 1
        self.r_sigma_a = DualResultRow(
            res, "Ave. Flow Stress  σ_a  = (σ_y₀+σ_y₁)/2",
            "psi", "MPa",
            "Arithmetic mean of entry and exit yield strengths", row=r,
            **stress_row_opts); r += 1
        self.r_wu = DualResultRow(
            res, "Uniform Work  Wu",
            "psi", "MPa",
            "Wu = σ_a·ln(1/(1−RA))", row=r,
            **stress_row_opts); r += 1
        self.r_wr = DualResultRow(
            res, "Redundant Work  Wr",
            "psi", "MPa",
            "Wr = (Φ−1)·σ_a·ln(1/(1−RA))", row=r,
            **stress_row_opts); r += 1
        self.r_wf = DualResultRow(
            res, "Friction Work  Wf",
            "psi", "MPa",
            "Wf = 4·μ·Φ·σ_a / Δ", row=r,
            **stress_row_opts); r += 1
        self.r_sigma_d = DualResultRow(
            res, "Drawing Stress  σ_d",
            "psi", "MPa",
            "σ_d = σ_a·[(3.2/Δ)+0.9]·(α+μ)", row=r,
            **stress_row_opts); r += 1

        # Stress ratio – single value (same either way)
        self.r_sigma_ratio = ResultRow(
            res, "Drawing Stress Ratio  Σ = σ_d/σ_a", "",
            "MUST be < 1.0 to draw;  guideline: keep below 0.7", row=r,
            **stress_row_opts); r += 1

        self.r_die_pressure = DualResultRow(
            res, "Avg Die Pressure  P = Φ·σ_a",
            "psi", "MPa", "", row=r,
            **stress_row_opts); r += 1

        _col_header_row(res, row=r,
                        label_text="Force & Power  (requires drawing speed):",
                        **stress_row_opts); r += 1
        self.r_draw_force = DualResultRow(
            res, "Draw Force  F = σ_d · A₁",
            "lbf", "N", "", row=r,
            **stress_row_opts); r += 1
        self.r_power = DualResultRow(
            res, "Power  P = F · V₁",
            "hp", "kW", "", row=r,
            **stress_row_opts); r += 1
        self.r_v0 = DualResultRow(
            res, "Inlet Wire Speed  V₀",
            "ft/min", "m/s",
            "V0 = V1·A1/A0  (volume conservation)", row=r,
            **stress_row_opts); r += 1
        self.r_avg_strain_rate = ResultRow(
            res, "Avg Strain Rate  ε̇", "s⁻¹",
            "ε̇ = ε_t·(V0+V1)/(2·Ld)", row=r,
            **stress_row_opts)

        self._stress_warn = tk.Label(
            tab, text="", font=("Arial", 9, "bold"),
            bg=BG, fg=WARN_COLOR, wraplength=800, justify='left')
        self._stress_warn.pack(anchor='w', padx=14, pady=2)

    # ──────────────────────────────────────────────────────────
    #  TAB 4 – Thermal  (DUAL UNITS)
    # ──────────────────────────────────────────────────────────

    def _build_tab_thermal(self):
        tab = tk.Frame(self.nb, bg=BG)
        self.nb.add(tab, text="  Thermal  ")

        thermal_label_opts = dict(label_width=28, label_anchor='e', label_sticky='e')
        thermal_result_opts = dict(label_width=33, label_anchor='e', label_sticky='e')

        inp = tk.LabelFrame(
            tab,
            text="  Material & Thermal Parameters  (requires Stress & Force tab first)  ",
            font=("Arial", 10, "bold"), bg=PANEL_BG, fg=HEADER_BG,
            padx=10, pady=8)
        inp.pack(fill='x', padx=12, pady=(10, 4))

        # Material preset
        pr = tk.Frame(inp, bg=PANEL_BG)
        pr.grid(row=0, column=0, columnspan=6, sticky='w', pady=(0, 6))
        tk.Label(pr, text="Material preset:", font=("Arial", 10),
                 bg=PANEL_BG).pack(side='left')
        self.material_var = tk.StringVar(value="Stainless Steel")
        cb = ttk.Combobox(pr, textvariable=self.material_var,
                          values=["Carbon Steel", "Stainless Steel",
                                  "Copper", "Aluminum", "Custom"],
                          state='readonly', width=16)
        cb.pack(side='left', padx=8)
        cb.bind("<<ComboboxSelected>>", self._load_material_preset)

        # Column headers for inputs
        tk.Label(inp, text="", bg=PANEL_BG, width=34).grid(row=1, column=0)
        tk.Label(inp, text="Metric  (SI – used for calc)",
                 font=("Arial", 9, "bold"), bg=MET_BG, fg=HEADER_BG,
                 width=22, anchor='center', relief='flat').grid(
            row=1, column=1, columnspan=2, padx=2, pady=(2, 4))
        tk.Label(inp, text="│", fg=DIV_COLOR, bg=PANEL_BG).grid(row=1, column=3)
        tk.Label(inp, text="Imperial  (reference)",
                 font=("Arial", 9, "bold"), bg=IMP_BG, fg=HEADER_BG,
                 width=22, anchor='center', relief='flat').grid(
            row=1, column=4, columnspan=2, padx=2, pady=(2, 4))

        # Density
        self.density_var = tk.StringVar(value="8000")
        self.density_imp_var = tk.StringVar(value="")
        self._add_dual_input_row(
            inp, 2,
            "Density  ρ :",
            self.density_var, "kg/m³",
            self.density_imp_var, "lb/ft³",
            "Steel ≈ 7850 kg/m³  (490 lb/ft³)",
            met_trace=True, met_to_imp=lambda v: v * 0.062428,
            **thermal_label_opts)

        # Specific heat
        self.spec_heat_var = tk.StringVar(value="500")
        self.spec_heat_imp_var = tk.StringVar(value="")
        self._add_dual_input_row(
            inp, 3,
            "Specific Heat  C :",
            self.spec_heat_var, "J/(kg·K)",
            self.spec_heat_imp_var, "BTU/(lb·°F)",
            "Steel ≈ 502 J/(kg·K)  (0.12 BTU/lb·°F)",
            met_trace=True, met_to_imp=lambda v: v * 2.3885e-4,
            **thermal_label_opts)

        # Thermal conductivity
        self.k_therm_var = tk.StringVar(value="16")
        self.k_therm_imp_var = tk.StringVar(value="")
        self._add_dual_input_row(
            inp, 4,
            "Thermal Conductivity  K :",
            self.k_therm_var, "W/(m·K)",
            self.k_therm_imp_var, "BTU/(h·ft·°F)",
            "Steel ≈ 50 W/(m·K)  (28.9 BTU/h·ft·°F)",
            met_trace=True, met_to_imp=lambda v: v * 0.5779,
            **thermal_label_opts)

        # Inlet temperature
        self.t0_c_var = tk.StringVar(value="20")
        self.t0_f_var = tk.StringVar(value=f"{abs_c_to_f(20):.4f}")
        self._add_dual_input_row(
            inp, 5,
            "Inlet Wire Temperature  T₀ :",
            self.t0_c_var, "°C",
            self.t0_f_var, "°F",
            "Wire temperature before entering the die",
            met_trace=True, met_to_imp=lambda v: v * 9.0/5.0 + 32.0,
            **thermal_label_opts)

        # Sync visible defaults to selected material preset at startup.
        self._load_material_preset()

        tk.Button(inp, text="  Calculate Temperatures  ",
                  font=("Arial", 11, "bold"),
                  bg=ACCENT, fg="white", relief='flat', padx=10, pady=5,
                  cursor="hand2", command=self._calc_thermal).grid(
            row=6, column=0, columnspan=6, pady=10)

        # ── Results ─────────────────────────────────────────
        res = tk.LabelFrame(
            tab, text="  Temperature Results  –  Metric (°C)  │  Imperial (°F)  ",
            font=("Arial", 10, "bold"),
            bg=PANEL_BG, fg=HEADER_BG, padx=6, pady=6)
        res.pack(fill='both', expand=True, padx=12, pady=4)

        _col_header_row(res, row=0,
                        label_text="Temperature RISES (ΔT)  –  ΔF = ΔC × 9/5 :",
                        imp_text="Imperial (°F)", met_text="Metric (°C)",
                        metric_first=True)
        r = 1
        self.r_tw_uniform = DualResultRow(
            res, "Uniform Work Rise  Tuw",
            "°F rise", "°C rise",
            "Tuw = σ_a·ln(1/(1−RA))/(C·ρ)", row=r,
            metric_first=True,
            **thermal_result_opts); r += 1
        self.r_tw_redundant = DualResultRow(
            res, "Redundant Work Rise  Trw",
            "°F rise", "°C rise",
            "Trw = (Δ−1)·σ_a·ln(1/(1−RA))/(C·ρ)", row=r,
            metric_first=True,
            **thermal_result_opts); r += 1
        self.r_tw_total = DualResultRow(
            res, "Total Wire Rise  Tw  (= Tuw + Trw)",
            "°F rise", "°C rise",
            "Tw = Δ·σ_a·ln(1/(1−RA))/(C·ρ)", row=r,
            metric_first=True,
            **thermal_result_opts); r += 1
        self.r_adiabatic = DualResultRow(
            res, "Adiabatic Heat Rise  ΔT  (from σ_d)",
            "°F rise", "°C rise",
            "ΔT = σ_d/(C·ρ) – total bulk rise using draw stress", row=r,
            metric_first=True,
            **thermal_result_opts); r += 1
        self.r_frict_heat = DualResultRow(
            res, "Surface Frictional Heating",
            "°F rise", "°C rise",
            "1.25·μ·Δ·σ_a·√(v·Ld/(C·ρ·K)) – needs drawing speed", row=r,
            metric_first=True,
            **thermal_result_opts); r += 1

        _col_header_row(res, row=r,
                        label_text="ABSOLUTE temperatures  (T₀ + rises) :",
                        imp_text="Imperial (°F)", met_text="Metric (°C)",
                        metric_first=True); r += 1
        self.r_teq = DualResultRow(
            res, "Equilibrated Wire Temp  Teq",
            "°F", "°C",
            "Teq = T0 + σ_d/(C·ρ)", row=r,
            metric_first=True,
            **thermal_result_opts); r += 1
        self.r_tmax = DualResultRow(
            res, "Max Surface Temp at Die Exit  Tmax",
            "°F", "°C",
            "Tmax = T₀ + Tw + Frictional heating  (needs speed)", row=r,
            metric_first=True,
            **thermal_result_opts)

        tk.Label(
            tab,
            text="Note: stress values are converted to Pa internally for SI-correct thermal results.  "
                 "Temperature rises use ΔF = ΔC×9/5; absolute temps use F = C×9/5 + 32.",
            font=("Arial", 8, "italic"), bg=BG, fg="#555",
            wraplength=820, justify='left').pack(anchor='w', padx=14, pady=(0, 6))

    # ──────────────────────────────────────────────────────────
    #  Input-row helpers
    # ──────────────────────────────────────────────────────────

    def _add_input_row(self, parent, row, label, var, unit, tooltip="",
                       label_width=34, label_anchor='w', label_sticky='w',
                       entry_width=14, unit_width=28, unit_colspan=4,
                       tip_col=6, tip_sticky='w', tip_padx=(0, 0),
                       unit_padx=(0, 0)):
        tk.Label(parent, text=label, font=("Arial", 10), bg=PANEL_BG,
                 width=label_width, anchor=label_anchor).grid(
            row=row, column=0, sticky=label_sticky, padx=(0, 4), pady=3)
        tk.Entry(parent, textvariable=var,
                 font=("Arial", 11), width=entry_width).grid(
            row=row, column=1, sticky='w', padx=4, pady=3)
        unit_lbl = tk.Label(parent, text=unit, font=("Arial", 9), bg=PANEL_BG,
                            width=unit_width, anchor='w')
        unit_lbl.grid(row=row, column=2, columnspan=unit_colspan, sticky='w',
                  padx=unit_padx)
        if tooltip:
            tip_lbl = tk.Label(parent, text="ⓘ", font=("Arial", 10),
                               bg=PANEL_BG, fg=ACCENT, cursor="question_arrow")
            tip_lbl.grid(row=row, column=tip_col, sticky=tip_sticky, padx=tip_padx)
            _bind_tooltip(tip_lbl, tooltip)
        return unit_lbl

    def _add_dual_input_row(self, parent, row, label,
                            var_a, unit_a, var_b, unit_b,
                            tooltip="",
                            psi_trace=False,
                            met_trace=False, met_to_imp=None,
                            label_width=34, label_anchor='w', label_sticky='w'):
        """
        Two-entry input row. Supports auto-conversion in one direction.
        psi_trace=True  → var_a is psi; var_b shows MPa (read-only, auto-updated)
        met_trace=True  → var_a is metric; var_b shows imperial (read-only, auto-updated)
        """
        tk.Label(parent, text=label, font=("Arial", 10), bg=PANEL_BG,
                  width=label_width, anchor=label_anchor).grid(
              row=row, column=0, sticky=label_sticky, padx=(0, 4), pady=3)

        tk.Entry(parent, textvariable=var_a,
                 font=("Arial", 11), width=14).grid(
            row=row, column=1, sticky='w', padx=4, pady=3)
        tk.Label(parent, text=unit_a, font=("Arial", 9),
                 bg=PANEL_BG, width=6, anchor='w').grid(
            row=row, column=2, sticky='w')

        tk.Label(parent, text="│", font=("Arial", 10),
                 bg=PANEL_BG, fg=DIV_COLOR).grid(row=row, column=3, padx=4)

        conv_bg = MET_BG
        if psi_trace:
            # psi -> MPa: converted field is metric
            conv_bg = MET_BG
        elif met_trace:
            # metric -> imperial: converted field is imperial
            conv_bg = IMP_BG

        conv_entry = tk.Entry(parent, textvariable=var_b,
                              font=("Arial", 11), width=14,
                              state='readonly',
                              readonlybackground=conv_bg,
                              fg="#444")
        conv_entry.grid(row=row, column=4, sticky='w', padx=4, pady=3)
        tk.Label(parent, text=unit_b, font=("Arial", 9),
                 bg=PANEL_BG, width=8, anchor='w').grid(
            row=row, column=5, sticky='w')

        if tooltip:
            tip_lbl = tk.Label(parent, text="ⓘ", font=("Arial", 10),
                               bg=PANEL_BG, fg=ACCENT, cursor="question_arrow")
            tip_lbl.grid(row=row, column=6, sticky='w')
            _bind_tooltip(tip_lbl, tooltip)

        if psi_trace:
            def _update_mpa(*_):
                try:
                    v = float(var_a.get().strip().replace(",", ""))
                    var_b.set(f"{v * PSI_TO_MPA:.4f}")
                except Exception:
                    var_b.set("")
            var_a.trace_add("write", _update_mpa)
            _update_mpa()

        if met_trace and met_to_imp:
            def _update_imp(*_, fn=met_to_imp):
                try:
                    v = float(var_a.get().strip())
                    var_b.set(f"{fn(v):.4f}")
                except Exception:
                    var_b.set("")
            var_a.trace_add("write", _update_imp)
            _update_imp()

    # ──────────────────────────────────────────────────────────
    #  Calculation methods
    # ──────────────────────────────────────────────────────────

    def _calc_basic(self):
        try:
            d0_s = self.d0_var.get().strip()
            d1_s = self.d1_var.get().strip()
            cw_s = self.cw_var.get().strip()

            if not d0_s:
                raise ValueError("Original Diameter D₀ is required.")
            d0 = safe_float(d0_s, "D₀")
            if d0 <= 0:
                raise ValueError("D₀ must be positive.")

            have_d1 = bool(d1_s)
            have_cw = bool(cw_s)

            if have_d1 and have_cw:
                d1  = safe_float(d1_s, "D₁")
                cw  = safe_float(cw_s, "RA%")
                ra_d1 = ra_from_diameters(d0, d1)
                ra_cw = cw / 100.0
                if abs(ra_d1 - ra_cw) > 0.0005:
                    raise ValueError(
                        f"D₁ and RA% are inconsistent.\n"
                        f"D₁ = {d1} implies RA = {ra_d1*100:.4f}%,  "
                        f"but you entered RA = {cw:.4f}%.\nClear one field."
                    )
                ra = ra_d1
            elif have_d1:
                d1 = safe_float(d1_s, "D₁")
                if d1 <= 0 or d1 >= d0:
                    raise ValueError("D₁ must be > 0 and < D₀.")
                ra = ra_from_diameters(d0, d1)
                self._suppress = True
                self.cw_var.set(f"{ra*100:.6g}")
                self._suppress = False
            elif have_cw:
                cw = safe_float(cw_s, "RA%")
                if not (0 < cw < 100):
                    raise ValueError("Cold Work % must be between 0 and 100.")
                ra = cw / 100.0
                d1 = d1_from_ra(d0, ra)
                self._suppress = True
                self.d1_var.set(f"{d1:.6g}")
                self._suppress = False
            else:
                raise ValueError("Enter Output Diameter D₁  OR  Cold Work / RA %.")

            self._d0 = d0
            self._d1 = d1
            self._ra = ra
            if hasattr(self, 'stress_cw_var'):
                self.stress_cw_var.set(f"{ra*100:.4f}")

            unit = self.unit_var.get()
            a0  = area(d0)
            a1  = area(d1)
            eps = true_strain_ra(ra)
            e_e = engineering_strain(a0, a1)
            Lr  = length_ratio(ra)

            ra_color = WARN_COLOR if ra > 0.30 else OK_COLOR
            self.r_ra_pct.set(ra * 100, color=ra_color, fmt="{:.4f}")
            self.r_ra_frac.set(ra, fmt="{:.6f}")
            self.r_true_strain.set(eps, fmt="{:.6f}")
            self.r_eng_strain.set(e_e, fmt="{:.6f}")
            self.r_a0.set(a0, fmt=f"{{:.6g}} {unit}²")
            self.r_a1.set(a1, fmt=f"{{:.6g}} {unit}²")
            self.r_length_ratio.set(Lr, fmt="{:.4f}")
            self.r_dia_ratio.set(d1 / d0, fmt="{:.6f}")
            self.r_d1_calc.set(d1, fmt=f"{{:.6g}} {unit}")
            self.r_cw_calc.set(ra * 100, color=ra_color, fmt="{:.4f}")

            warn = ("  ⚠ RA > 30% – exceeds typical commercial limit per pass."
                    if ra > 0.30 else "")
            self.status_var.set(
                f"D₀ = {d0} {unit}  →  D₁ = {d1:.6g} {unit}   "
                f"RA = {ra*100:.4f}%   ε = {eps:.4f}{warn}"
            )
            self._calc_die()
            self._sync_schedule_from_basic()
        except ValueError as exc:
            messagebox.showerror("Input Error", str(exc))
            self.status_var.set(f"Error: {exc}")

    def _calc_die(self):
        try:
            if not hasattr(self, '_d0'):
                raise ValueError("Run the Basic tab first.")
            d0, d1, ra = self._d0, self._d1, self._ra

            alpha_full = safe_float(self.alpha_var.get(), "Die included angle")
            cof        = safe_float(self.cof_var.get(), "CoF")
            if not (0 < alpha_full < 90):
                raise ValueError("Die included angle must be between 0° and 90°.")
            if not (0 < cof < 1):
                raise ValueError("CoF must be between 0 and 1.")

            alpha_deg = alpha_full / 2.0          # semi-angle for all formulas
            alpha_rad = math.radians(alpha_deg)
            D         = delta(alpha_rad, ra)
            Ld        = deformation_zone_length(d0, d1, alpha_rad)
            Lc        = die_contact_length(d0, d1, alpha_rad)
            phi       = redundant_work_factor_delta(D)
            phi2      = redundant_work_factor_delta2(D)
            D_opt     = optimum_delta(cof, ra)
            aopt_deg  = math.degrees(optimum_angle_rad(cof, ra))

            self._delta     = D
            self._ld        = Ld
            self._phi       = phi
            self._alpha_rad = alpha_rad
            self._cof       = cof

            d_color = WARN_COLOR if D > 3.0 else (CAUTION_COLOR if D > 1.3 else OK_COLOR)
            self.r_delta.set(D, color=d_color, fmt="{:.4f}")
            self.r_ld.set(Ld, fmt="{:.6g}")
            self.r_lc.set(Lc, fmt="{:.6g}")
            self.r_phi.set(phi, fmt="{:.4f}")
            self.r_phi2.set(phi2, fmt="{:.4f}")
            self.r_delta_opt.set(D_opt, fmt="{:.4f}")
            self.r_alpha_opt.set(aopt_deg * 2.0, fmt="{:.2f}")

            warns = []
            if D > 3.0:
                warns.append(f"⚠  Δ={D:.2f} > 3 → high redundant work.")
            if D > 1.3:
                warns.append(f"⚠  Δ={D:.2f} > 1.3 → centerline stress is TENSILE – risk of center bursts.")
            if alpha_deg < 4:
                warns.append("⚠  Very low semi-angle – friction risk.")
            self._die_warn.config(text="   ".join(warns))
            self.status_var.set(
                f"Full angle = {alpha_full:.1f}°  (semi = {alpha_deg:.1f}°)   "
                f"Δ = {D:.4f}   Ld = {Ld:.4g}   Φ = {phi:.4f}   "
                f"Optimum full angle = {aopt_deg*2:.2f}°"
            )
        except ValueError as exc:
            messagebox.showerror("Input Error", str(exc))
            self.status_var.set(f"Error: {exc}")

    def _calc_stress(self):
        try:
            if not hasattr(self, '_delta'):
                raise ValueError("Run the Die Geometry tab first.")
            d0, d1, ra = self._d0, self._d1, self._ra
            D, phi, alpha_rad, cof = self._delta, self._phi, self._alpha_rad, self._cof
            Ld = self._ld

            # ── Read psi inputs ──────────────────────────────
            sy0_psi = safe_float(self.yield_begin_var.get().replace(",", ""), "Beginning Yield")
            sy1_psi = safe_float(self.yield_final_var.get().replace(",", ""), "Final CW Yield")
            if sy0_psi <= 0 or sy1_psi <= 0:
                raise ValueError("Yield strengths must be positive.")
            if sy0_psi > 1_000_000:
                raise ValueError("Beginning Yield must be ≤ 1,000,000 psi.")
            if sy1_psi > 1_000_000:
                raise ValueError("Final Cold Worked Yield must be ≤ 1,000,000 psi.")

            # Average flow stress
            sa_psi = (sy0_psi + sy1_psi) / 2.0
            sa_MPa = sa_psi * PSI_TO_MPA

            # Optional speed
            v_s = self.v_out_var.get().strip()
            v_out = safe_float(v_s, "Exit Speed") if v_s else None

            # ── Work components (MPa) ────────────────────────
            Wu_MPa = work_uniform_MPa(sa_MPa, ra)
            Wr_MPa = work_redundant_MPa(phi, sa_MPa, ra)
            Wf_MPa = work_friction_MPa(cof, phi, sa_MPa, D)
            sd_MPa = draw_stress_MPa(sa_MPa, D, alpha_rad, cof)
            P_MPa  = avg_die_pressure_MPa(phi, sa_MPa)
            ratio  = drawing_stress_ratio(sd_MPa, sa_MPa)

            # Cache for thermal tab
            self._sigma_a_MPa = sa_MPa
            self._sigma_d_MPa = sd_MPa

            def m2p(mpa): return mpa * MPA_TO_PSI   # MPa → psi

            # ── Fill stress rows ─────────────────────────────
            self.r_sigma_a.set(m2p(sa_MPa), sa_MPa, fmt_imp="{:,.1f}", fmt_met="{:.3f}")
            self.r_wu.set(m2p(Wu_MPa), Wu_MPa, fmt_imp="{:,.1f}", fmt_met="{:.3f}")
            self.r_wr.set(m2p(Wr_MPa), Wr_MPa, fmt_imp="{:,.1f}", fmt_met="{:.3f}")
            self.r_wf.set(m2p(Wf_MPa), Wf_MPa, fmt_imp="{:,.1f}", fmt_met="{:.3f}")

            r_color = (WARN_COLOR    if ratio >= 1.0 else
                       CAUTION_COLOR if ratio >= 0.7 else OK_COLOR)
            self.r_sigma_d.set(m2p(sd_MPa), sd_MPa,
                               color=r_color,
                               fmt_imp="{:,.1f}", fmt_met="{:.3f}")
            self.r_sigma_ratio.set(ratio, color=r_color, fmt="{:.4f}")
            self.r_die_pressure.set(m2p(P_MPa), P_MPa,
                                    fmt_imp="{:,.1f}", fmt_met="{:.3f}")

            # ── Force & Power (need area in m² and speed in m/s) ──
            # Convert diameters to metres (assumes inches or mm entered in Basic)
            unit = self.unit_var.get()
            if unit == "in":
                d1_m = d1 * 0.0254
                d0_m = d0 * 0.0254
            else:
                d1_m = d1 * 0.001
                d0_m = d0 * 0.001
            a1_m2 = area(d1_m)
            a0_m2 = area(d0_m)

            if v_out is not None:
                sd_Pa = sd_MPa * 1e6
                F_N   = draw_force_N(sd_Pa, a1_m2)
                F_lbf = F_N * N_TO_LBF
                kW    = power_kW(F_N, v_out)
                hp    = kW * KW_TO_HP
                v_in  = velocity_in(v_out, a0_m2, a1_m2)
                v_in_ftmin = v_in * M_S_TO_FT_MIN

                eps_t = true_strain_ra(ra)
                sr = avg_strain_rate(eps_t, v_in, v_out, Ld) if Ld > 0 else None

                self._v_out = v_out
                self._v_in  = v_in
                self.r_draw_force.set(F_lbf, F_N,
                                      color=NEUTRAL_COLOR,
                                      fmt_imp="{:,.1f}", fmt_met="{:,.1f}")
                self.r_power.set(hp, kW,
                                 fmt_imp="{:.3f}", fmt_met="{:.3f}")
                self.r_v0.set(v_in_ftmin, v_in,
                              fmt_imp="{:.2f}", fmt_met="{:.4f}")
                self.r_avg_strain_rate.set(sr, fmt="{:.2f}") if sr else \
                    self.r_avg_strain_rate.clear()
            else:
                for r in (self.r_draw_force, self.r_power, self.r_v0):
                    r.clear()
                self.r_avg_strain_rate.clear()
                self._v_out = None

            warns = []
            if ratio >= 1.0:
                warns.append("⚠  σ_d ≥ σ_a  – wire WILL BREAK.")
            elif ratio >= 0.7:
                warns.append(f"⚠  σ_d/σ_a = {ratio:.3f} – near drawing limit (0.7 guideline).")
            self._stress_warn.config(text="   ".join(warns))
            self.status_var.set(
                f"σ_a = {sa_psi:,.0f} psi ({sa_MPa:.1f} MPa)   "
                f"σ_d = {m2p(sd_MPa):,.0f} psi ({sd_MPa:.1f} MPa)   "
                f"Σ = {ratio:.4f}"
            )

            # Keep downstream tabs current from a single Stress calculation action.
            self._calc_thermal()
            self._calc_schedule()
        except ValueError as exc:
            messagebox.showerror("Input Error", str(exc))
            self.status_var.set(f"Error: {exc}")

    def _calc_thermal(self):
        try:
            if not hasattr(self, '_sigma_d_MPa'):
                raise ValueError("Run the Stress & Force tab first.")
            ra       = self._ra
            D        = self._delta
            sa_MPa   = self._sigma_a_MPa
            sd_MPa   = self._sigma_d_MPa
            cof      = self._cof
            Ld       = self._ld

            rho   = safe_float(self.density_var.get(),   "Density ρ")
            C     = safe_float(self.spec_heat_var.get(), "Specific Heat C")
            K     = safe_float(self.k_therm_var.get(),   "Thermal Conductivity K")
            T0_C  = safe_float(self.t0_c_var.get(),      "Inlet Temperature T₀")

            # Convert MPa → Pa for SI-correct thermal results
            sa_Pa = sa_MPa * 1e6
            sd_Pa = sd_MPa * 1e6

            # ── Temperature rises (°C) ───────────────────────
            Tuw_C = uniform_temp_rise_C(sa_Pa, ra, C, rho)
            Trw_C = redundant_temp_rise_C(D, sa_Pa, ra, C, rho)
            Tw_C  = wire_temperature_rise_C(D, sa_Pa, ra, C, rho)
            dT_C  = adiabatic_rise_C(sd_Pa, C, rho)
            Teq_C = equilibrated_temp_C(T0_C, sd_Pa, C, rho)

            # ── Fill rises (ΔF = ΔC × 9/5) ──────────────────
            def dr(row, c_val):
                row.set(dt_c_to_f(c_val), c_val, fmt_imp="{:.2f}", fmt_met="{:.2f}")

            dr(self.r_tw_uniform,   Tuw_C)
            dr(self.r_tw_redundant, Trw_C)
            dr(self.r_tw_total,     Tw_C)
            dr(self.r_adiabatic,    dT_C)

            # ── Absolute temperatures ────────────────────────
            def ar(row, c_val):
                row.set(abs_c_to_f(c_val), c_val,
                        fmt_imp="{:.1f}", fmt_met="{:.1f}")

            ar(self.r_teq, Teq_C)

            # Frictional heating needs speed
            if hasattr(self, '_v_out') and self._v_out:
                Tf_C   = frictional_heating_C(cof, D, sa_Pa, self._v_out, Ld, C, rho, K)
                Tmax_C = T0_C + Tw_C + Tf_C
                dr(self.r_frict_heat, Tf_C)
                ar(self.r_tmax, Tmax_C)
            else:
                self.r_frict_heat.clear()
                self.r_frict_heat.imp_lbl.config(text="Need speed")
                self.r_frict_heat.met_lbl.config(text="Need speed")
                self.r_tmax.clear()
                self.r_tmax.imp_lbl.config(text="Need speed")
                self.r_tmax.met_lbl.config(text="Need speed")

            self.status_var.set(
                f"Tuw = {Tuw_C:.2f}°C ({dt_c_to_f(Tuw_C):.2f}°F rise)   "
                f"Tw total = {Tw_C:.2f}°C ({dt_c_to_f(Tw_C):.2f}°F rise)   "
                f"Teq = {Teq_C:.1f}°C ({abs_c_to_f(Teq_C):.1f}°F)"
            )
        except ValueError as exc:
            messagebox.showerror("Input Error", str(exc))
            self.status_var.set(f"Error: {exc}")

    # ──────────────────────────────────────────────────────────
    #  Material presets
    # ──────────────────────────────────────────────────────────

    _MATERIALS = {
        "Carbon Steel":    (7850, 502, 50),
        "Stainless Steel": (8000, 500, 16),
        "Copper":          (8960, 385, 401),
        "Aluminum":        (2700, 900, 205),
        "Custom":          (None, None, None),
    }

    def _load_material_preset(self, _event=None):
        rho, C, K = self._MATERIALS.get(self.material_var.get(), (None, None, None))
        if rho is not None:
            self.density_var.set(str(rho))
            self.spec_heat_var.set(str(C))
            self.k_therm_var.set(str(K))

    def _format_beginning_yield(self, *_):
        if getattr(self, "_suppress", False):
            return
        s = self.yield_begin_var.get().strip()
        if not s:
            return
        cleaned = s.replace(",", "")
        try:
            v = float(cleaned)
        except ValueError:
            return
        # Beginning yield is displayed as whole psi and capped for sanity.
        v_int = max(0, min(1_000_000, int(round(v))))
        formatted = f"{v_int:,}"
        if formatted != s:
            self._suppress = True
            self.yield_begin_var.set(formatted)
            self._suppress = False

    def _format_final_yield(self, *_):
        if getattr(self, "_suppress", False):
            return
        s = self.yield_final_var.get().strip()
        if not s:
            return
        cleaned = s.replace(",", "")
        try:
            v = float(cleaned)
        except ValueError:
            return
        # Final CW yield is displayed as whole psi and capped for sanity.
        v_int = max(0, min(1_000_000, int(round(v))))
        formatted = f"{v_int:,}"
        if formatted != s:
            self._suppress = True
            self.yield_final_var.set(formatted)
            self._suppress = False

    # ──────────────────────────────────────────────────────────
    #  Unit-label sync
    # ──────────────────────────────────────────────────────────

    def _update_unit_labels(self):
        u = self.unit_var.get()

        # Convert entered diameters when toggling units so field values stay meaningful.
        if self._last_unit != u:
            self._convert_diameter_vars(self._last_unit, u)
            self._last_unit = u

        self.d0_unit_lbl.config(text=u)
        self.d1_unit_lbl.config(text=u)
        if hasattr(self, "sched_d_start_unit_lbl"):
            self.sched_d_start_unit_lbl.config(text=u)
        if hasattr(self, "sched_d_target_unit_lbl"):
            self.sched_d_target_unit_lbl.config(text=u)

    def _convert_diameter_vars(self, from_unit, to_unit):
        if from_unit == to_unit:
            return
        factor = 25.4 if from_unit == "in" and to_unit == "mm" else (1.0 / 25.4)

        def _convert_var(var):
            s = var.get().strip()
            if not s:
                return
            try:
                v = float(s)
            except ValueError:
                return
            var.set(f"{v * factor:.6g}")

        # Basic tab diameters
        for var in (self.d0_var, self.d1_var):
            _convert_var(var)

        # Pass Schedule diameters (if tab already built)
        if hasattr(self, "sched_d_start_var"):
            _convert_var(self.sched_d_start_var)
        if hasattr(self, "sched_d_target_var"):
            _convert_var(self.sched_d_target_var)

    def _sync_angle_from_die(self, *_):
        if self._syncing_angle or not hasattr(self, "sched_angle_var"):
            return
        self._syncing_angle = True
        try:
            self.sched_angle_var.set(self.alpha_var.get())
        finally:
            self._syncing_angle = False

    def _sync_angle_from_schedule(self, *_):
        if self._syncing_angle or not hasattr(self, "alpha_var"):
            return
        self._syncing_angle = True
        try:
            self.alpha_var.set(self.sched_angle_var.get())
        finally:
            self._syncing_angle = False

    def _sync_schedule_from_basic(self):
        if not hasattr(self, "sched_d_start_var"):
            return
        self.sched_d_start_var.set(f"{self._d0:.6g}")
        self.sched_d_target_var.set(f"{self._d1:.6g}")
        self.sched_strategy.set("n_passes")
        self.sched_param_var.set("1")
        self._update_unit_labels()

    def _on_d1_focus_out(self, _event=None):
        if self._suppress:
            return
        if self.d0_var.get().strip() and self.d1_var.get().strip():
            self._calc_basic()

    # ──────────────────────────────────────────────────────────
    #  Clear
    # ──────────────────────────────────────────────────────────

    def _clear_all(self):
        for v in (self.d0_var, self.d1_var, self.cw_var):
            v.set("")
        if hasattr(self, 'stress_cw_var'):
            self.stress_cw_var.set("")
        for attr in ('_d0', '_d1', '_ra', '_delta', '_phi', '_ld',
                     '_alpha_rad', '_cof', '_sigma_d_MPa', '_sigma_a_MPa',
                     '_v_out', '_v_in'):
            if hasattr(self, attr):
                delattr(self, attr)
        for r in (self.r_ra_pct, self.r_ra_frac, self.r_true_strain,
                  self.r_eng_strain, self.r_a0, self.r_a1,
                  self.r_length_ratio, self.r_dia_ratio,
                  self.r_d1_calc, self.r_cw_calc):
            r.clear()
        self.status_var.set("Cleared.")

    # ──────────────────────────────────────────────────────────
    #  TAB 5 – Pass Schedule
    # ──────────────────────────────────────────────────────────

    def _build_tab_schedule(self):
        tab = tk.Frame(self.nb, bg=BG)
        self.nb.add(tab, text="  Pass Schedule  ")

        # ── Inputs ──────────────────────────────────────────
        inp = tk.LabelFrame(
            tab, text="  Pass Schedule Inputs  ",
            font=("Arial", 10, "bold"), bg=PANEL_BG, fg=HEADER_BG,
            padx=10, pady=8)
        inp.pack(fill='x', padx=12, pady=(10, 4))

        # Diameter units (linked with Basic tab via shared self.unit_var)
        unit_row = tk.Frame(inp, bg=PANEL_BG)
        unit_row.grid(row=0, column=0, columnspan=7, pady=(0, 6))
        tk.Label(unit_row, text="Diameter units:", font=("Arial", 10),
                 bg=PANEL_BG).pack(side='left')
        for txt, val in [("Inches (in)", "in"), ("Millimeters (mm)", "mm")]:
            tk.Radiobutton(unit_row, text=txt, variable=self.unit_var, value=val,
                           bg=PANEL_BG, font=("Arial", 10),
                           command=self._update_unit_labels).pack(side='left', padx=8)

        sched_label_opts = dict(label_width=30, label_anchor='e', label_sticky='e')
        sched_input_opts = dict(
            entry_width=7,
            unit_width=5,
            unit_colspan=1,
            tip_col=1,
            tip_sticky='e',
            tip_padx=(0, 14),
            unit_padx=(0, 0),
        )

        # Starting and target diameters
        self.sched_d_start_var = tk.StringVar()
        self.sched_d_start_unit_lbl = self._add_input_row(
            inp, 1, "Starting Diameter  D_start :",
            self.sched_d_start_var, self.unit_var.get(),
            "Incoming rod/wire diameter before any passes",
            **sched_label_opts, **sched_input_opts)

        self.sched_d_target_var = tk.StringVar()
        self.sched_d_target_unit_lbl = self._add_input_row(
            inp, 2, "Target Diameter  D_target :",
            self.sched_d_target_var, self.unit_var.get(),
            "Final finished wire diameter",
            **sched_label_opts, **sched_input_opts)

        # Die angle (shared with Die Geometry tab if available, but editable here too)
        self.sched_angle_var = tk.StringVar(value="16")
        self.sched_angle_var.trace_add("write", self._sync_angle_from_schedule)
        self._add_input_row(inp, 3, "Die Included Angle  (full) :",
                            self.sched_angle_var, "degrees",
                            "Full die included angle – same value as Die Geometry tab",
                            **sched_label_opts, **sched_input_opts)
        self.sched_angle_var.set(self.alpha_var.get())

        # CoF
        self.sched_cof_var = tk.StringVar(value="0.10")
        self._add_input_row(inp, 4, "Coefficient of Friction  μ :",
                            self.sched_cof_var, "",
                            "Used to calculate Δ per pass",
                            **sched_label_opts, **sched_input_opts)

        # Strategy selector
        strat_frame = tk.Frame(inp, bg=PANEL_BG)
        strat_frame.grid(row=5, column=0, columnspan=7, sticky='w', pady=(8, 4))
        tk.Label(strat_frame, text="Strategy:", font=("Arial", 10, "bold"),
                 bg=PANEL_BG, width=34, anchor='e').grid(row=0, column=0, sticky='e', padx=(0, 4))
        self.sched_strategy = tk.StringVar(value="n_passes")
        strategies = [
            ("n_passes",  "Equal N passes  (specify N below)"),
            ("const_ra",  "Constant RA per pass  (specify RA% below)"),
            ("const_delta","Constant Δ per pass  (specify Δ below)"),
        ]
        for idx, (val, txt) in enumerate(strategies):
            tk.Radiobutton(strat_frame, text=txt, variable=self.sched_strategy,
                           value=val, bg=PANEL_BG, font=("Arial", 10)).grid(
                row=idx, column=1, sticky='w', padx=(16, 0), pady=1)

        # Strategy-specific input
        param_frame = tk.Frame(inp, bg=PANEL_BG)
        param_frame.grid(row=6, column=0, columnspan=7, sticky='w', pady=(6, 2))
        tk.Label(param_frame, text="Pass:", font=("Arial", 10),
                 bg=PANEL_BG, width=34, anchor='e').pack(side='left')
        self.sched_param_var = tk.StringVar(value="1")
        tk.Entry(param_frame, textvariable=self.sched_param_var,
                 font=("Arial", 11), width=10).pack(side='left', padx=4)
        tk.Label(param_frame,
                 text="(N = number of passes | RA% = percent per pass | Δ = target delta)",
                 font=("Arial", 9, "italic"), bg=PANEL_BG, fg="#555").pack(
            side='left', padx=6)

        tk.Button(inp, text="  Generate Pass Schedule  ",
                  font=("Arial", 11, "bold"),
                  bg=ACCENT, fg="white", relief='flat', padx=10, pady=5,
                  cursor="hand2", command=self._calc_schedule).grid(
            row=7, column=0, columnspan=7, pady=(10, 6))

        # ── Results table ────────────────────────────────────
        tbl_frame = tk.LabelFrame(
            tab, text="  Pass Schedule Results  ",
            font=("Arial", 10, "bold"), bg=PANEL_BG, fg=HEADER_BG,
            padx=6, pady=6)
        tbl_frame.pack(fill='both', expand=True, padx=12, pady=4)

        cols = ("pass", "d_in", "d_out", "ra_pct", "true_strain",
                "cum_strain", "length_ratio", "delta")
        col_hdr = {
            "pass":         "Pass",
            "d_in":         "D_in",
            "d_out":        "D_out",
            "ra_pct":       "RA %",
            "true_strain":  "True Strain",
            "cum_strain":   "Cum. Strain",
            "length_ratio": "Len. Ratio",
            "delta":        "Δ",
        }
        col_width = {
            "pass": 40, "d_in": 90, "d_out": 90, "ra_pct": 70,
            "true_strain": 90, "cum_strain": 90, "length_ratio": 80, "delta": 60,
        }

        self.sched_tree = ttk.Treeview(
            tbl_frame, columns=cols, show='headings', height=14)
        for c in cols:
            self.sched_tree.heading(c, text=col_hdr[c])
            self.sched_tree.column(c, width=col_width[c], anchor='center')

        vsb = ttk.Scrollbar(tbl_frame, orient='vertical',
                            command=self.sched_tree.yview)
        self.sched_tree.configure(yscrollcommand=vsb.set)
        self.sched_tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        # Summary row below table
        self._sched_summary = tk.Label(
            tab, text="", font=("Arial", 9), bg=BG, fg=NEUTRAL_COLOR,
            anchor='w', justify='left')
        self._sched_summary.pack(anchor='w', padx=14, pady=(2, 6))

    # ──────────────────────────────────────────────────────────
    #  Pass schedule calculation
    # ──────────────────────────────────────────────────────────

    def _calc_schedule(self):
        try:
            unit = self.unit_var.get()

            d_start = safe_float(self.sched_d_start_var.get(), "Starting Diameter")
            d_target = safe_float(self.sched_d_target_var.get(), "Target Diameter")
            if d_start <= 0 or d_target <= 0:
                raise ValueError("Diameters must be positive.")
            if d_target >= d_start:
                raise ValueError("Target diameter must be smaller than starting diameter.")

            alpha_full = safe_float(self.sched_angle_var.get(), "Die Included Angle")
            if not (0 < alpha_full < 90):
                raise ValueError("Die included angle must be between 0° and 90°.")
            alpha_rad = math.radians(alpha_full / 2.0)

            cof = safe_float(self.sched_cof_var.get(), "CoF")
            if not (0 < cof < 1):
                raise ValueError("CoF must be between 0 and 1.")

            strategy = self.sched_strategy.get()
            param    = safe_float(self.sched_param_var.get(), "Strategy value")

            # Total true strain from start to target
            eps_total = math.log((d_start / d_target) ** 2)

            # ── Determine per-pass RA based on strategy ──────
            if strategy == "n_passes":
                n = int(round(param))
                if n < 1:
                    raise ValueError("Number of passes must be ≥ 1.")
                eps_per_pass = eps_total / n
                ra_per_pass  = 1.0 - math.exp(-eps_per_pass)
                passes = [ra_per_pass] * n

            elif strategy == "const_ra":
                if not (0 < param < 100):
                    raise ValueError("RA% must be between 0 and 100.")
                ra_per_pass = param / 100.0
                eps_per_pass = math.log(1.0 / (1.0 - ra_per_pass))
                n = math.ceil(eps_total / eps_per_pass)
                # Last pass may be smaller to hit target exactly
                passes = [ra_per_pass] * (n - 1)
                # Calculate remaining RA for final pass
                d_after_n_minus1 = d_start * (1.0 - ra_per_pass) ** (0.5 * (n - 1))
                ra_last = ra_from_diameters(d_after_n_minus1, d_target)
                if ra_last > 0.001:
                    passes.append(ra_last)
                else:
                    passes = passes[:n - 1]  # already hit target

            elif strategy == "const_delta":
                target_delta = param
                if target_delta <= 0:
                    raise ValueError("Target Δ must be positive.")
                ra_per_pass = _ra_for_delta(target_delta, alpha_rad)
                eps_per_pass = math.log(1.0 / (1.0 - ra_per_pass))
                n = math.ceil(eps_total / eps_per_pass)
                passes = [ra_per_pass] * (n - 1)
                d_after_n_minus1 = d_start
                for ra_i in passes:
                    d_after_n_minus1 = d1_from_ra(d_after_n_minus1, ra_i)
                ra_last = ra_from_diameters(d_after_n_minus1, d_target)
                if ra_last > 0.001:
                    passes.append(ra_last)
            else:
                raise ValueError("Unknown strategy.")

            if len(passes) > 50:
                raise ValueError(
                    f"Schedule requires {len(passes)} passes – too many.\n"
                    "Increase RA per pass, target Δ, or reduce total reduction."
                )

            # ── Build table rows ─────────────────────────────
            for row in self.sched_tree.get_children():
                self.sched_tree.delete(row)

            d_cur      = d_start
            cum_strain = 0.0
            cum_L_ratio = 1.0

            for i, ra_i in enumerate(passes, start=1):
                d_out_i = d1_from_ra(d_cur, ra_i)
                eps_i   = true_strain_ra(ra_i)
                cum_strain  += eps_i
                cum_L_ratio *= length_ratio(ra_i)

                try:
                    D_i = delta(alpha_rad, ra_i)
                    delta_str = f"{D_i:.3f}"
                    tag = "warn" if D_i > 3 else ("caution" if D_i > 1.3 else "ok")
                except Exception:
                    delta_str = "—"
                    tag = "ok"

                self.sched_tree.insert(
                    "", "end",
                    values=(
                        i,
                        f"{d_cur:.5g}",
                        f"{d_out_i:.5g}",
                        f"{ra_i*100:.3f}",
                        f"{eps_i:.4f}",
                        f"{cum_strain:.4f}",
                        f"{cum_L_ratio:.3f}",
                        delta_str,
                    ),
                    tags=(tag,)
                )
                d_cur = d_out_i

            # Row colours
            self.sched_tree.tag_configure("ok",      background="#edfbee")
            self.sched_tree.tag_configure("caution",  background="#fff8e6")
            self.sched_tree.tag_configure("warn",     background="#fdecea")

            # Update column header to show units
            for col in ("d_in", "d_out"):
                self.sched_tree.heading(col, text=f"D  ({unit})")

            actual_target = d_cur
            summary = (
                f"{len(passes)} passes   |   "
                f"Start: {d_start:.5g} {unit}   →   "
                f"Finish: {actual_target:.5g} {unit}   "
                f"(target: {d_target:.5g} {unit})   |   "
                f"Total true strain: {cum_strain:.4f}   |   "
                f"Length ratio: {cum_L_ratio:.2f}×"
            )
            self._sched_summary.config(text=summary)
            self.status_var.set(summary)

        except ValueError as exc:
            messagebox.showerror("Input Error", str(exc))
            self.status_var.set(f"Error: {exc}")


# ─────────────────────────────────────────────────────────────
#  Module-level helper – find RA for a target Δ at given α
# ─────────────────────────────────────────────────────────────

def _ra_for_delta(target_delta, alpha_rad, tol=1e-9):
    """
    Bisection solve:  find RA ∈ (0, 1) such that delta(alpha_rad, RA) = target_delta.
    Δ is monotonically decreasing in RA, so bisection converges cleanly.
    """
    lo, hi = 1e-7, 0.9999
    if delta(alpha_rad, lo) < target_delta:
        raise ValueError(
            f"Cannot achieve Δ = {target_delta:.3f} at this die angle.\n"
            f"Maximum Δ with this angle approaches {delta(alpha_rad, lo):.2f}."
        )
    for _ in range(120):
        mid = (lo + hi) / 2.0
        if delta(alpha_rad, mid) > target_delta:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return (lo + hi) / 2.0


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    DrawBenchApp(root)
    root.mainloop()
