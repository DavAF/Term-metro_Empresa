"""
BusinessIQ Analyzer — Análisis estratégico 100% gratuito, sin APIs, sin coste.
Todo el análisis se calcula en Python puro a partir de los datos del usuario.
"""
from __future__ import annotations
import math
import streamlit as st
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════

SECTORES = [
    "Tecnología / Software", "Industria / Manufactura", "Servicios Profesionales",
    "Retail / Comercio", "Salud / Farma", "Construcción / Inmobiliaria",
    "Hostelería / Turismo", "Educación", "Finanzas / Seguros",
    "Logística / Transporte", "Agricultura / Agrotech",
    "Media / Entretenimiento", "Energía / Utilities", "Otro",
]

PROVINCIAS = [
    "Madrid", "Barcelona", "Valencia", "Sevilla", "Zaragoza", "Málaga",
    "Murcia", "Palma", "Las Palmas", "Bilbao", "Alicante", "Córdoba",
    "Valladolid", "Vigo", "Gijón", "A Coruña", "Granada", "Vitoria",
    "Elche", "Santander", "Oviedo", "Pamplona", "Logroño", "Badajoz",
    "Salamanca", "Huelva", "Lleida", "Tarragona", "Girona", "Toledo",
]

PAISES = ["España", "México", "Argentina", "Colombia", "Chile", "Perú", "EE.UU.", "Otro"]

SUGERENCIAS_SECTOR = {
    "Tecnología / Software":       ["Desarrollo de software", "Soporte técnico", "Ventas B2B", "Gestión de proyectos", "Testing QA", "DevOps"],
    "Industria / Manufactura":     ["Control de producción", "Gestión de inventario", "Mantenimiento preventivo", "Control de calidad", "Logística interna"],
    "Servicios Profesionales":     ["Gestión de clientes", "Facturación", "Propuestas comerciales", "Formación interna", "Reporting"],
    "Retail / Comercio":           ["Gestión de stock", "Atención al cliente", "Marketing digital", "Logística", "Contabilidad"],
    "Salud / Farma":               ["Gestión de pacientes", "Facturación sanitaria", "Inventario farmacéutico", "Historial clínico"],
    "Hostelería / Turismo":        ["Reservas", "Atención al cliente", "Gestión de personal", "Revenue management", "Marketing redes sociales"],
    "Construcción / Inmobiliaria": ["Gestión de obras", "Presupuestos", "Compras materiales", "Coordinación subcontratas"],
    "Finanzas / Seguros":          ["Análisis de riesgos", "Gestión cartera clientes", "Reporting regulatorio", "Siniestros"],
    "Educación":                   ["Gestión académica", "Atención al alumno", "Contenidos digitales", "Administración"],
    "Logística / Transporte":      ["Gestión de rutas", "Seguimiento de envíos", "Almacén", "Facturación", "Atención cliente"],
    "Agricultura / Agrotech":      ["Gestión de parcelas", "Control de riego", "Trazabilidad", "Logística", "Facturación"],
    "Media / Entretenimiento":     ["Producción de contenidos", "Distribución", "Monetización", "Atención suscriptores"],
    "Energía / Utilities":         ["Gestión de contratos", "Facturación", "Mantenimiento infraestructura", "Atención cliente"],
    "Otro":                        ["Gestión administrativa", "Contabilidad", "Atención al cliente", "Marketing", "RRHH"],
}

# ── Tablas sectoriales ────────────────────────────────────────────────────────
# (rivalidad, barreras_entrada, poder_proveedor, poder_cliente, disrupcion_digital)
SECTOR_PORTER: Dict[str, Tuple] = {
    "Tecnología / Software":       (8, 4, 4, 7, 9),
    "Industria / Manufactura":     (7, 7, 6, 5, 5),
    "Servicios Profesionales":     (6, 4, 3, 7, 6),
    "Retail / Comercio":           (8, 4, 5, 8, 8),
    "Salud / Farma":               (5, 8, 7, 4, 6),
    "Construcción / Inmobiliaria": (7, 6, 6, 6, 4),
    "Hostelería / Turismo":        (8, 4, 4, 8, 7),
    "Educación":                   (5, 5, 3, 5, 7),
    "Finanzas / Seguros":          (7, 8, 5, 6, 8),
    "Logística / Transporte":      (7, 6, 6, 6, 6),
    "Agricultura / Agrotech":      (5, 6, 6, 5, 5),
    "Media / Entretenimiento":     (8, 3, 3, 7, 9),
    "Energía / Utilities":         (4, 9, 7, 3, 6),
    "Otro":                        (6, 5, 5, 6, 5),
}

# (crecimiento_mercado_%, volatilidad, margen_tipico_%, digitalizacion_0_10)
SECTOR_META: Dict[str, Tuple] = {
    "Tecnología / Software":       (15, 6, 65, 9),
    "Industria / Manufactura":     (4,  4, 28, 5),
    "Servicios Profesionales":     (6,  3, 40, 6),
    "Retail / Comercio":           (5,  5, 30, 7),
    "Salud / Farma":               (8,  3, 45, 6),
    "Construcción / Inmobiliaria": (5,  6, 20, 4),
    "Hostelería / Turismo":        (7,  7, 25, 7),
    "Educación":                   (6,  3, 35, 7),
    "Finanzas / Seguros":          (6,  5, 40, 8),
    "Logística / Transporte":      (5,  4, 18, 6),
    "Agricultura / Agrotech":      (4,  5, 22, 5),
    "Media / Entretenimiento":     (8,  7, 35, 9),
    "Energía / Utilities":         (6,  4, 20, 5),
    "Otro":                        (5,  5, 30, 5),
}

MACRO_PROVINCIAS: Dict[str, Dict] = {
    "Madrid":     {"pib": 3.2, "paro": 9.8,  "inversion": 22, "confianza": 58},
    "Barcelona":  {"pib": 3.0, "paro": 10.1, "inversion": 20, "confianza": 56},
    "Valencia":   {"pib": 2.6, "paro": 12.4, "inversion": 14, "confianza": 51},
    "Sevilla":    {"pib": 2.3, "paro": 16.8, "inversion": 11, "confianza": 48},
    "Zaragoza":   {"pib": 2.5, "paro": 11.2, "inversion": 12, "confianza": 52},
    "Málaga":     {"pib": 3.1, "paro": 14.1, "inversion": 15, "confianza": 53},
    "Bilbao":     {"pib": 2.8, "paro": 9.4,  "inversion": 16, "confianza": 55},
    "Alicante":   {"pib": 2.4, "paro": 13.5, "inversion": 12, "confianza": 50},
    "Córdoba":    {"pib": 2.0, "paro": 18.2, "inversion": 9,  "confianza": 45},
    "Valladolid": {"pib": 2.3, "paro": 11.8, "inversion": 10, "confianza": 50},
    "Vigo":       {"pib": 2.4, "paro": 12.6, "inversion": 11, "confianza": 49},
    "A Coruña":   {"pib": 2.3, "paro": 12.9, "inversion": 10, "confianza": 49},
    "Granada":    {"pib": 2.1, "paro": 17.0, "inversion": 8,  "confianza": 46},
    "Vitoria":    {"pib": 2.9, "paro": 8.9,  "inversion": 17, "confianza": 56},
    "Elche":      {"pib": 2.2, "paro": 13.8, "inversion": 9,  "confianza": 48},
    "Santander":  {"pib": 2.2, "paro": 12.5, "inversion": 10, "confianza": 49},
    "Oviedo":     {"pib": 2.1, "paro": 13.2, "inversion": 9,  "confianza": 48},
    "Pamplona":   {"pib": 2.7, "paro": 9.1,  "inversion": 14, "confianza": 54},
    "Logroño":    {"pib": 2.4, "paro": 10.8, "inversion": 11, "confianza": 51},
    "Badajoz":    {"pib": 1.8, "paro": 22.1, "inversion": 7,  "confianza": 43},
    "Salamanca":  {"pib": 1.9, "paro": 14.9, "inversion": 8,  "confianza": 46},
    "Huelva":     {"pib": 2.0, "paro": 19.8, "inversion": 8,  "confianza": 44},
    "Lleida":     {"pib": 2.3, "paro": 11.4, "inversion": 10, "confianza": 50},
    "Tarragona":  {"pib": 2.4, "paro": 11.8, "inversion": 11, "confianza": 51},
    "Girona":     {"pib": 2.5, "paro": 10.9, "inversion": 12, "confianza": 52},
    "Toledo":     {"pib": 2.2, "paro": 13.6, "inversion": 9,  "confianza": 48},
    "Palma":      {"pib": 2.9, "paro": 11.8, "inversion": 16, "confianza": 53},
    "Las Palmas": {"pib": 2.5, "paro": 15.2, "inversion": 12, "confianza": 50},
    "Gijón":      {"pib": 2.0, "paro": 14.1, "inversion": 8,  "confianza": 47},
    "Murcia":     {"pib": 2.3, "paro": 14.8, "inversion": 10, "confianza": 49},
}

MACRO_PAISES: Dict[str, Dict] = {
    "España":    {"pib": 2.5, "paro": 11.4, "ipc": 2.8,  "tipo": 2.65},
    "México":    {"pib": 1.8, "paro": 2.8,  "ipc": 4.2,  "tipo": 11.0},
    "Argentina": {"pib": 2.1, "paro": 6.2,  "ipc": 55.0, "tipo": 40.0},
    "Colombia":  {"pib": 2.3, "paro": 9.8,  "ipc": 6.5,  "tipo": 11.5},
    "Chile":     {"pib": 2.0, "paro": 8.5,  "ipc": 4.5,  "tipo": 6.5},
    "Perú":      {"pib": 2.5, "paro": 6.8,  "ipc": 3.8,  "tipo": 6.75},
    "EE.UU.":    {"pib": 2.2, "paro": 3.9,  "ipc": 3.2,  "tipo": 5.25},
    "Otro":      {"pib": 2.5, "paro": 8.0,  "ipc": 4.0,  "tipo": 5.0},
}

TECH_SCORE   = {"Muy bajo": 1, "Bajo": 3, "Medio": 5, "Alto": 7, "Avanzado": 9}
MERCADO_SCORE= {"Local / Comarcal": 2, "Regional / Autonómico": 4, "Nacional": 6, "Europeo": 8, "Global": 10}

HERRAMIENTAS_IA: Dict[str, List[Dict]] = {
    "Tecnología / Software":    [
        {"nombre": "GitHub Copilot",    "categoria": "Código",           "coste_mes": "19€/dev",     "uso": "Autocompletar código y refactoring asistido"},
        {"nombre": "Linear AI",         "categoria": "Gestión proyectos","coste_mes": "18€/usuario", "uso": "Priorización automática de tickets e incidencias"},
        {"nombre": "Intercom AI",       "categoria": "Soporte cliente",  "coste_mes": "39€/mes",     "uso": "Chatbot para soporte técnico 24/7"},
    ],
    "Industria / Manufactura":  [
        {"nombre": "Microsoft Copilot", "categoria": "Productividad",    "coste_mes": "30€/usuario", "uso": "Informes de producción y calidad automatizados"},
        {"nombre": "Power BI + IA",     "categoria": "Analítica",        "coste_mes": "10€/usuario", "uso": "Dashboards predictivos de producción y mantenimiento"},
        {"nombre": "Make + IA",         "categoria": "Automatización",   "coste_mes": "29€/mes",     "uso": "Flujos automáticos entre ERP, almacén y logística"},
    ],
    "Retail / Comercio":        [
        {"nombre": "Tidio AI",          "categoria": "Atención cliente", "coste_mes": "29€/mes",     "uso": "Chatbot para dudas y seguimiento de pedidos"},
        {"nombre": "Klaviyo AI",        "categoria": "Email marketing",  "coste_mes": "45€/mes",     "uso": "Segmentación automática y personalización de campañas"},
        {"nombre": "Inventory Planner", "categoria": "Stock",            "coste_mes": "99€/mes",     "uso": "Predicción de demanda y optimización de inventario"},
    ],
    "Servicios Profesionales":  [
        {"nombre": "Microsoft Copilot", "categoria": "Productividad",    "coste_mes": "30€/usuario", "uso": "Redacción de propuestas, informes y resúmenes de reuniones"},
        {"nombre": "HubSpot AI",        "categoria": "CRM",              "coste_mes": "45€/mes",     "uso": "Scoring de leads y automatización de seguimiento comercial"},
        {"nombre": "Notion AI",         "categoria": "Conocimiento",     "coste_mes": "10€/usuario", "uso": "Base de conocimiento inteligente y documentación automática"},
    ],
    "Salud / Farma":            [
        {"nombre": "Microsoft Copilot", "categoria": "Administración",   "coste_mes": "30€/usuario", "uso": "Gestión de informes clínicos y documentación"},
        {"nombre": "Power Automate IA", "categoria": "Flujos",           "coste_mes": "15€/usuario", "uso": "Automatización de citas, recordatorios y facturación"},
        {"nombre": "Nuance DAX",        "categoria": "Clínico",          "coste_mes": "Consultar",   "uso": "Documentación clínica automática por voz"},
    ],
}
HERRAMIENTAS_DEFAULT = [
    {"nombre": "Microsoft Copilot", "categoria": "Productividad",  "coste_mes": "30€/usuario", "uso": "Automatización de tareas administrativas y redacción"},
    {"nombre": "Make + IA",         "categoria": "Automatización", "coste_mes": "29€/mes",     "uso": "Automatización de flujos de trabajo entre aplicaciones"},
    {"nombre": "Power BI + IA",     "categoria": "Analítica",      "coste_mes": "10€/usuario", "uso": "Dashboards inteligentes y análisis predictivo"},
]

# ══════════════════════════════════════════════════════════════════════════════
# ENGINE — LÓGICA DE ANÁLISIS
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class R:
    score_global: float = 0
    competitividad: float = 0
    potencial_ia: float = 0
    rentabilidad_esperada_pct: float = 0
    beneficio_bruto: float = 0
    margen_operativo: float = 0
    revenue_empleado: float = 0
    coste_empleado: float = 0
    executive_summary: str = ""
    alertas: List[str] = field(default_factory=list)
    oportunidades_rapidas: List[str] = field(default_factory=list)
    dimensiones: List[Dict] = field(default_factory=list)
    porter: List[Dict] = field(default_factory=list)
    porter_conclusion: str = ""
    porter_score_global: float = 0
    pestel: List[Dict] = field(default_factory=list)
    bcg: Dict = field(default_factory=dict)
    dafo: Dict = field(default_factory=dict)
    dafo_estrategias: Dict = field(default_factory=dict)
    macro: Dict = field(default_factory=dict)
    roi_ia: Dict = field(default_factory=dict)
    _crec_pot: float = 0.5

    def crec_potencial_proxy(self):
        return self._crec_pot


def _cl(v, lo, hi):
    return max(lo, min(hi, v))

def _nm(v, lo, hi):
    return _cl((v - lo) / (hi - lo), 0, 1) if hi != lo else 0.5

def _nivel(s):
    return "Alto" if s >= 7.5 else "Medio" if s >= 4.5 else "Bajo"

def _nc(n):
    return {"Alto": "#ef4444", "Medio": "#f59e0b", "Bajo": "#10b981"}.get(n, "#64748b")

def _ic(i):
    return {"Positivo": "#10b981", "Negativo": "#ef4444", "Neutro": "#64748b"}.get(i, "#64748b")


_PORTER_TXT = {
    "rivalidad": {
        "Alto":  ("Intensa competencia entre actores consolidados con presión en precios y captación de clientes.",
                  "Diferenciar por valor y calidad; invertir en fidelización y marca."),
        "Medio": ("Competencia moderada con espacio para diferenciación sin guerra de precios extrema.",
                  "Consolidar posición en nicho y mejorar propuesta de valor."),
        "Bajo":  ("Mercado con pocos rivales directos y espacio para crecer con relativa comodidad.",
                  "Aprovechar la ventana de baja competencia para expandir cuota de mercado."),
    },
    "entrantes": {
        "Alto":  ("Barreras de entrada bajas; nuevos jugadores pueden entrar con facilidad.",
                  "Construir barreras: marca, relaciones, economías de escala o patentes."),
        "Medio": ("Inversión inicial y curva de aprendizaje disuaden a muchos entrantes.",
                  "Mantener liderazgo técnico o relacional para frenar la entrada de competidores."),
        "Bajo":  ("Altas barreras regulatorias, de capital o know-how protegen al sector.",
                  "Mantener y reforzar las barreras existentes como ventaja competitiva."),
    },
    "proveedores": {
        "Alto":  ("Proveedores concentrados con capacidad de imponer precios y condiciones.",
                  "Diversificar proveedores y desarrollar alternativas para reducir dependencia."),
        "Medio": ("Poder de proveedores equilibrado; hay opciones alternativas disponibles.",
                  "Negociar contratos marco a largo plazo para asegurar condiciones estables."),
        "Bajo":  ("Proveedores fragmentados con escaso poder de negociación.",
                  "Aprovechar para negociar mejores precios y condiciones contractuales."),
    },
    "clientes": {
        "Alto":  ("Clientes con muchas alternativas y alta sensibilidad al precio.",
                  "Aumentar switching costs: contratos, integraciones, programas de fidelidad."),
        "Medio": ("Poder de negociación de clientes moderado; cierta dependencia mutua.",
                  "Mejorar experiencia y valor añadido para reducir sensibilidad al precio."),
        "Bajo":  ("Clientes con pocas alternativas o alta dependencia del producto/servicio.",
                  "Mantener calidad y servicio; aprovechar posición para ampliar cartera."),
    },
    "sustitutos": {
        "Alto":  ("Alternativas digitales o tecnológicas amenazan con desplazar el modelo actual.",
                  "Innovar activamente e incorporar IA antes de que lleguen los sustitutos."),
        "Medio": ("Sustitutos presentes pero con limitaciones; cliente valora la propuesta actual.",
                  "Evolucionar la oferta incorporando las ventajas de los sustitutos."),
        "Bajo":  ("Pocos sustitutos reales; el producto o servicio difícilmente reemplazable.",
                  "Comunicar mejor la propuesta única y ampliar barreras de sustitución."),
    },
}

def _porter_f(nombre, score, tipo):
    score = round(_cl(score, 1, 10), 1)
    nv = _nivel(score)
    desc, rec = _PORTER_TXT[tipo][nv]
    return {"nombre": nombre, "nivel": nv, "score": score, "descripcion": desc, "recomendacion": rec}


def analizar(d: dict) -> R:
    r = R()

    fac   = float(d.get("facturacion", 0) or 0)
    cos   = float(d.get("costes", 0) or 0)
    emp   = max(int(d.get("empleados", 1) or 1), 1)
    años  = int(d.get("años", 1) or 1)
    comp  = int(d.get("competidores", 5) or 5)
    cli   = int(d.get("clientes", 0) or 0)
    crec  = float(d.get("crecimiento", 0) or 0)
    margen_b = float(d.get("margen", 0) or 0)
    tech  = TECH_SCORE.get(d.get("nivel_tech", "Medio"), 5)
    merc  = MERCADO_SCORE.get(d.get("mercado", "Nacional"), 6)
    sector   = d.get("sector", "Otro")
    provincia= d.get("provincia", "Madrid")
    pais     = d.get("pais", "España")
    empresa  = d.get("empresa", "la empresa")
    procesos = d.get("procesos", [])

    pb   = SECTOR_PORTER.get(sector, SECTOR_PORTER["Otro"])
    meta = SECTOR_META.get(sector, SECTOR_META["Otro"])
    crec_sector, _, margen_tipico, dig_sector = meta

    # Financieros
    r.beneficio_bruto  = fac - cos
    r.margen_operativo = (r.beneficio_bruto / fac * 100) if fac > 0 else 0
    r.revenue_empleado = fac / emp
    r.coste_empleado   = cos / emp

    # Scores dimensiones
    fin   = _cl((r.margen_operativo / max(margen_tipico, 1)) * 4 + (2 if r.beneficio_bruto > 0 else 0) + _nm(crec, -20, 40) * 3 + (1 if margen_b > 20 else 0), 0, 10)
    comp_ = _cl((años / 10) * 2 + _nm(cli / emp, 0, 20) * 2 + merc / 2 + (10 - _cl(comp / 3, 0, 4)) / 2, 0, 10)
    dig   = _cl(tech * 0.8 + _nm(dig_sector, 3, 9) * 2, 0, 10)
    rrhh  = _cl((float(d.get("p_dir",10) or 10) + float(d.get("p_mm",20) or 20)) / 20 + float(d.get("p_tec",30) or 30) / 15 + _nm(float(d.get("e1825",10) or 10) + float(d.get("e2635",30) or 30), 10, 70) * 2 + _nm(emp, 1, 200) * 1.5, 0, 10)
    crec_ = _cl(_nm(crec, -10, 40) * 4 + _nm(crec_sector, 2, 15) * 3 + _nm(merc, 2, 10) * 2 + (1 if fac > cos else 0), 0, 10)

    r._crec_pot = crec_ / 10
    r.dimensiones = [
        {"nombre": "Posición Competitiva",  "score": round(comp_, 1)},
        {"nombre": "Capacidad Financiera",  "score": round(fin,   1)},
        {"nombre": "Capital Humano",        "score": round(rrhh,  1)},
        {"nombre": "Madurez Digital",       "score": round(dig,   1)},
        {"nombre": "Crecimiento Potencial", "score": round(crec_, 1)},
    ]
    r.score_global    = round((comp_ + fin + rrhh + dig + crec_) / 5 * 10, 1)
    r.competitividad  = round(comp_ * 10, 1)
    r.potencial_ia    = round(_cl((10 - dig) * 6 + crec_ * 2 + fin, 20, 95), 1)
    r.rentabilidad_esperada_pct = round(r.margen_operativo * (1 + crec / 100), 2)

    # Porter
    riv_a  = _cl(pb[0] * 0.7 + (comp / 10) * 3, 1, 10)
    cli_a  = _cl(pb[3] * 0.8 + (2 if cli < 20 else 0), 1, 10)
    sust_a = _cl(pb[4] * 0.7 + dig_sector * 0.3, 1, 10)
    r.porter = [
        _porter_f("Rivalidad entre competidores",     riv_a,  "rivalidad"),
        _porter_f("Amenaza de nuevos entrantes",       pb[1],  "entrantes"),
        _porter_f("Poder negociador de proveedores",   pb[2],  "proveedores"),
        _porter_f("Poder negociador de clientes",      cli_a,  "clientes"),
        _porter_f("Amenaza de productos sustitutos",   sust_a, "sustitutos"),
    ]
    r.porter_score_global = round(sum(f["score"] for f in r.porter) / 5, 1)
    psg = r.porter_score_global
    if psg >= 7:
        r.porter_conclusion = f"Entorno muy exigente (score {psg}/10). Alta presión competitiva en {sector}. Priorizar diferenciación y fidelización como ejes de rentabilidad."
    elif psg >= 5:
        r.porter_conclusion = f"Intensidad competitiva moderada (score {psg}/10) en {sector}. Existen nichos defendibles con la estrategia adecuada."
    else:
        r.porter_conclusion = f"Condiciones competitivas favorables (score {psg}/10). {empresa} tiene una oportunidad para consolidar posición y crecer."

    # PESTEL
    mp = MACRO_PAISES.get(pais, MACRO_PAISES["España"])
    r.pestel = [
        {"dimension": "Político",    "impacto": "Positivo" if pais in ["España","EE.UU."] else "Neutro",
         "score": 6, "descripcion": f"Marco político estable en {pais} con fondos de digitalización disponibles para PYMEs del sector {sector}.",
         "factor_clave": "Fondos Next Generation EU / apoyo público digitalización", "tendencia": "Estable"},
        {"dimension": "Económico",   "impacto": "Positivo" if mp["pib"] >= 2.5 and mp["ipc"] < 4 else "Neutro",
         "score": 7 if mp["pib"] >= 2.5 else 5,
         "descripcion": f"PIB creciendo al {mp['pib']}% con inflación del {mp['ipc']}%. Tipo de referencia en {mp['tipo']}%, con tendencia bajista.",
         "factor_clave": f"PIB +{mp['pib']}% · IPC {mp['ipc']}% · Tipo {mp['tipo']}%", "tendencia": "Mejora gradual"},
        {"dimension": "Social",      "impacto": "Positivo", "score": 6,
         "descripcion": f"Cambio en hábitos de consumo y trabajo híbrido impulsan la demanda digital en {sector}. Mayor exigencia de transparencia.",
         "factor_clave": "Digitalización del consumidor y nuevas expectativas laborales", "tendencia": "Aceleración"},
        {"dimension": "Tecnológico", "impacto": "Positivo", "score": 8,
         "descripcion": f"IA generativa y automatización accesibles para PYMEs. Nivel de digitalización del sector {sector}: {dig_sector}/10.",
         "factor_clave": "IA accesible, cloud, automatización low-code/no-code", "tendencia": "Aceleración rápida"},
        {"dimension": "Ecológico",   "impacto": "Neutro",   "score": 5,
         "descripcion": "Regulación ESG en aumento con reporting de sostenibilidad próximo a ser obligatorio para empresas medianas.",
         "factor_clave": "Directiva CSRD europea · reporting sostenibilidad", "tendencia": "Presión creciente"},
        {"dimension": "Legal",       "impacto": "Neutro",   "score": 5,
         "descripcion": f"AI Act europeo con obligaciones para sistemas IA. RGPD vigente con sanciones reforzadas. Normativa sectorial de {sector}.",
         "factor_clave": "AI Act · RGPD · normativa sectorial específica", "tendencia": "Regulación creciente"},
    ]

    # BCG
    cuota  = _cl(100 / max(comp + 1, 1) + min(años / 20, 1) * 20 + fin * 2, 5, 90)
    crec_m = _nm(crec_sector, 0, 20) * 100
    pos_map = [
        (cuota >= 45 and crec_m >= 55, "Estrella",     "Combina alta cuota relativa con mercado creciente. Posición privilegiada que requiere inversión sostenida.",
         "Invertir para mantener liderazgo. Defender posición frente a nuevos entrantes."),
        (cuota >= 45,                  "Vaca Lechera",  "Buena posición en mercado maduro. Genera caja estable que puede reinvertirse en nuevas líneas.",
         "Maximizar rentabilidad y usar el cash flow para diversificar o modernizar."),
        (crec_m >= 55,                 "Interrogante",  "Mercado creciente pero cuota aún no consolidada. La decisión de invertir agresivamente es crítica.",
         "Definir si se invierte para ganar cuota (→ Estrella) o se reorienta la estrategia."),
    ]
    pos, desc_bcg, est_bcg = "Perro", "Mercado de bajo crecimiento con cuota limitada. Revisar propuesta de valor o pivotar.", "Reducir costes, buscar nicho específico o evaluar pivote estratégico."
    for cond, p, d_, e_ in pos_map:
        if cond:
            pos, desc_bcg, est_bcg = p, f"{empresa} {d_}", e_
            break
    r.bcg = {"posicion": pos, "descripcion": desc_bcg, "crecimiento_mercado": round(crec_m, 1), "cuota_relativa": round(cuota, 1), "estrategia": est_bcg}

    # DAFO
    F, D, O, A = [], [], [], []
    if años >= 5:   F.append(f"Experiencia de {años} años con cartera de clientes consolidada")
    if fin >= 6:    F.append("Salud financiera sólida con márgenes por encima de la media sectorial")
    if rrhh >= 6:   F.append("Equipo humano con buena estructura de perfiles y distribución generacional")
    if comp_ >= 6:  F.append("Posición competitiva defendida con relaciones establecidas")
    if merc >= 6:   F.append(f"Presencia en mercado {d.get('mercado','nacional')} con capacidad de expansión")
    if not F:       F += ["Flexibilidad operativa propia de empresa ágil", "Conocimiento directo del mercado local"]
    if dig < 5:     D.append(f"Madurez digital por debajo del benchmark del sector — procesos manuales pendientes")
    if fin < 5:     D.append("Márgenes operativos por debajo de la media con riesgo de presión de costes")
    if años < 3:    D.append("Empresa joven con track record limitado y marca en construcción")
    if emp < 10:    D.append("Tamaño reducido limita capacidad de ejecución simultánea de proyectos")
    if not D:       D += ["Posible dependencia de personas clave sin planes de sucesión", "Limitada inversión en marca y marketing digital"]
    O += ["Acceso a financiación pública (Next Generation EU, Kit Digital) para digitalización",
          f"IA y automatización asequibles para PYMEs del sector {sector} con ROI en 12 meses",
          "Demanda creciente de clientes por proveedores digitales y sostenibles"]
    if crec > 5:    O.append(f"Crecimiento propio del {crec:.0f}% abre puerta a inversión y captación de talento")
    if merc < 8:    O.append("Expansión geográfica a mercados europeos como palanca de crecimiento")
    A += ["Competidores con mayor madurez digital que ofrecen precios más competitivos",
          "Escasez de talento tecnológico con costes salariales al alza",
          "Incertidumbre macroeconómica y posible contracción del consumo",
          f"Nuevos entrantes digitales que pueden disruptar el modelo tradicional en {sector}"]
    r.dafo = {"fortalezas": F[:4], "debilidades": D[:4], "oportunidades": O[:4], "amenazas": A[:4]}
    fstr = F[0].lower() if F else "sus fortalezas"
    ostr = O[0].lower() if O else "las oportunidades del mercado"
    dstr = D[0].lower() if D else "sus debilidades"
    astr = A[0].lower() if A else "las amenazas del entorno"
    r.dafo_estrategias = {
        "FO": f"Aprovechar {fstr} para capitalizar {ostr}. Estrategia ofensiva de crecimiento.",
        "FA": f"Usar {fstr} como escudo frente a {astr}. Mantener posición y reforzar diferenciación.",
        "DO": f"Subsanar {dstr} invirtiendo en {ostr}. Estrategia de reorientación con fondos disponibles.",
        "DA": f"Reducir exposición a {astr} minimizando el impacto de {dstr}. Plan defensivo de contención.",
    }

    # MACRO
    prov_d = MACRO_PROVINCIAS.get(provincia, {"pib": mp["pib"], "paro": mp["paro"], "inversion": 12, "confianza": 50})
    r.macro = {
        "indicadores": [
            {"nombre": "PIB Regional",    "valor": f"+{prov_d['pib']}%",  "tendencia": "↑" if prov_d["pib"] > 2 else "→",  "positivo": prov_d["pib"] > 2},
            {"nombre": "Desempleo",       "valor": f"{prov_d['paro']}%",  "tendencia": "↓" if prov_d["paro"] < 12 else "→", "positivo": prov_d["paro"] < 12},
            {"nombre": "IPC",             "valor": f"{mp['ipc']}%",       "tendencia": "→",                                 "positivo": mp["ipc"] < 3},
            {"nombre": "Tipo referencia", "valor": f"{mp['tipo']}%",      "tendencia": "↓" if mp["tipo"] > 3 else "→",      "positivo": mp["tipo"] < 4},
            {"nombre": "Confianza Emp.",  "valor": str(prov_d["confianza"]), "tendencia": "↑",                             "positivo": prov_d["confianza"] > 50},
            {"nombre": "Inv. Digital",   "valor": f"+{prov_d['inversion']}%", "tendencia": "↑",                           "positivo": True},
        ],
        "contexto_regional": (
            f"{provincia} {'es una de las regiones más dinámicas' if prov_d['pib'] > 2.8 else 'mantiene una economía estable'} "
            f"de {pais}, con paro del {prov_d['paro']}% e índice de confianza empresarial de {prov_d['confianza']}/100. "
            f"La inversión digital creció un {prov_d['inversion']}% interanual."
        ),
        "perspectiva_12m": (
            f"Para los próximos 12 meses, {provincia} muestra indicadores "
            f"{'favorables' if prov_d['pib'] > 2.5 else 'moderados'} con PIB creciendo al {prov_d['pib']}%. "
            f"El sector {sector} presenta crecimiento estimado del {crec_sector}% anual."
        ),
        "oportunidades": [
            f"Fondos públicos disponibles para digitalización de PYMEs en {pais}",
            f"Crecimiento de demanda en {sector} estimado en +{crec_sector}% anual",
            "Reducción de tipos de interés favorece la financiación de inversiones",
            f"{provincia} con índice de inversión digital al alza (+{prov_d['inversion']}%)",
        ][:3],
        "riesgos": [
            f"Inflación del {mp['ipc']}% presiona costes operativos",
            "Incertidumbre geopolítica con impacto en cadenas de suministro",
            "Posible desaceleración del consumo si tipos no bajan lo esperado",
        ],
    }

    # ROI IA
    inv = 5000 if fac < 300_000 else 15000 if fac < 1_000_000 else 35000 if fac < 5_000_000 else 80000
    gap = (10 - tech) / 10
    ahorro = round(cos * 0.06 * (0.5 + gap))
    ingresos_extra = round(fac * 0.03 * (1 + r._crec_pot))
    beneficio_ia = ahorro + ingresos_extra - inv
    roi_pct = round((beneficio_ia / inv) * 100) if inv > 0 else 0
    payback = round(inv / max((ahorro + ingresos_extra) / 12, 1), 1)

    ia_map = {
        "facturación": ("OCR + automatización", "30-40%", "Baja", "Alto"),
        "contabilidad": ("RPA + IA financiera", "25-35%", "Media", "Alto"),
        "atención": ("Chatbot + NLP", "40-60%", "Baja", "Alto"),
        "soporte": ("Chatbot + base conocimiento", "35-50%", "Baja", "Alto"),
        "marketing": ("IA generativa + segmentación", "20-30%", "Baja", "Medio"),
        "rrhh": ("IA selección + onboarding", "25-35%", "Media", "Medio"),
        "logística": ("Optimización de rutas IA", "15-25%", "Alta", "Alto"),
        "producción": ("Mantenimiento predictivo", "20-30%", "Alta", "Alto"),
        "ventas": ("CRM IA + scoring leads", "20-30%", "Media", "Alto"),
        "gestión": ("Asistente IA + reporting auto", "25-35%", "Baja", "Medio"),
        "reportes": ("Generación automática informes", "40-60%", "Baja", "Medio"),
        "compras": ("IA negociación + predicción", "10-20%", "Media", "Medio"),
        "desarrollo": ("Copilot de código", "30-50%", "Baja", "Alto"),
        "calidad": ("Visión artificial + control", "20-35%", "Alta", "Alto"),
    }
    procs_ia = []
    for proc in (procesos[:5] if procesos else ["Gestión administrativa", "Atención al cliente", "Reporting"]):
        m = next((v for k, v in ia_map.items() if k in proc.lower()), ("Automatización RPA + IA", "15-25%", "Media", "Medio"))
        procs_ia.append({"proceso": proc, "tipo_ia": m[0], "ahorro_potencial": m[1], "dificultad": m[2], "impacto": m[3]})

    herrs = HERRAMIENTAS_IA.get(sector, HERRAMIENTAS_DEFAULT)
    r.roi_ia = {
        "inversion_estimada": int(inv), "ahorro_anual": int(ahorro),
        "ingresos_extra": int(ingresos_extra), "roi_porcentaje": int(roi_pct), "payback_meses": payback,
        "fases": [
            {"mes": "Q1 (Meses 1-3)", "titulo": "Diagnóstico y Quick Wins",
             "descripcion": "Auditoría de procesos automatizables. Implantación IA básica: asistente de productividad, automatización de email, clasificación documental.",
             "impacto": f"Ahorro estimado {round(ahorro*0.15/1000,1)}k€ en tareas administrativas",
             "herramientas": [herrs[0]["nombre"] if herrs else "Microsoft Copilot", "Make"]},
            {"mes": "Q2 (Meses 4-6)", "titulo": "Automatización Core",
             "descripcion": "Integración IA en CRM y facturación. Automatización de flujos repetitivos. Formación del equipo.",
             "impacto": f"Reducción 20-25% tiempo en procesos operativos · {round(ahorro*0.35/1000,1)}k€ acumulado",
             "herramientas": [herrs[1]["nombre"] if len(herrs) > 1 else "Make", "Power Automate"]},
            {"mes": "Q3 (Meses 7-9)", "titulo": "Análisis Predictivo",
             "descripcion": "Dashboards de inteligencia de negocio. Modelos predictivos de demanda y retención de clientes.",
             "impacto": f"Mejora 8-12% en conversión · {round(ingresos_extra*0.4/1000,1)}k€ ingresos adicionales",
             "herramientas": ["Power BI AI", "Google Analytics AI"]},
            {"mes": "Q4 (Meses 10-12)", "titulo": "IA Estratégica",
             "descripcion": "IA generativa para contenidos y propuestas. Pricing dinámico. Revisión ROI y planificación año 2.",
             "impacto": f"Incremento 5-8% ingresos · ROI acumulado año 1: {roi_pct:.0f}%",
             "herramientas": [herrs[2]["nombre"] if len(herrs) > 2 else "ChatGPT Ent.", "Perplexity Pro"]},
        ],
        "procesos_ia": procs_ia,
        "herramientas_recomendadas": herrs,
        "conclusion": (
            f"La incorporación de IA en {empresa} tiene un ROI estimado del {roi_pct:.0f}% en 12 meses, "
            f"con payback de {payback:.0f} meses. Inversión recomendada: {inv:,.0f}€ para generar "
            f"{ahorro:,.0f}€ de ahorro y {ingresos_extra:,.0f}€ de ingresos adicionales."
        ).replace(",", "."),
    }

    # Alertas
    r.alertas = []
    if cos > fac * 0.85 and fac > 0:
        r.alertas.append(f"Estructura de costes muy elevada ({round(cos/fac*100):.0f}% de la facturación) — revisar eficiencia con urgencia")
    if dig < 4:
        r.alertas.append(f"Madurez digital muy baja — el gap con competidores crece en el sector {sector}")
    if comp > 10:
        r.alertas.append(f"Alta fragmentación del mercado con {comp} competidores — diferenciación crítica para no competir solo por precio")
    if crec < 0:
        r.alertas.append("Crecimiento negativo — revisar causas estructurales vs coyunturales con plan de acción a 90 días")
    if not r.alertas:
        r.alertas.append("No se detectan alertas críticas — empresa en posición estable para acometer inversiones estratégicas")

    # Quick wins
    r.oportunidades_rapidas = []
    if tech < 6:
        r.oportunidades_rapidas.append("Implementar Microsoft Copilot: ahorro inmediato de 1-2h/empleado/día en tareas administrativas")
    if procesos:
        r.oportunidades_rapidas.append(f"Automatizar '{procesos[0]}' con RPA: proceso con alto potencial de ahorro identificado")
    r.oportunidades_rapidas.append("Solicitar Kit Digital (hasta 12.000€ subvencionados para digitalización de PYMEs en España)")

    # Summary
    bcg_pos = r.bcg.get("posicion", "Interrogante")
    estado_fin = "con márgenes sólidos" if r.margen_operativo > 15 else "con presión en márgenes" if r.margen_operativo > 0 else "con pérdidas operativas"
    estado_comp = "en entorno muy competitivo" if psg >= 7 else "en mercado de intensidad moderada" if psg >= 5 else "en entorno competitivo favorable"
    r.executive_summary = (
        f"{empresa} es una empresa del sector {sector} en {provincia} ({pais}), "
        f"con {emp} empleados y {fac:,.0f}€ de facturación, {estado_fin}. "
        f"Opera {estado_comp} (Porter {psg}/10) y ocupa la posición '{bcg_pos}' en la Matriz BCG, "
        f"con potencial de IA de {round(r.potencial_ia)}/100. "
        f"Score global: {r.score_global}/100 — "
        f"{'con oportunidades claras de mejora en digitalización' if r.score_global < 65 else 'con base sólida para crecer y transformarse digitalmente'}."
    ).replace(",", ".")

    return r


# ══════════════════════════════════════════════════════════════════════════════
# STREAMLIT APP
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="BusinessIQ Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
html,body,[class*="css"]{font-family:'Space Grotesk',sans-serif!important}
.kpi-card{background:#161d2e;border:1px solid #1e2d45;border-radius:14px;padding:18px 16px;text-align:center;margin-bottom:8px}
.kpi-val{font-size:26px;font-weight:800}
.kpi-lbl{font-size:11px;color:#64748b;margin-top:4px}
.sec-hdr{background:linear-gradient(135deg,#161d2e,#0d1526);border-left:4px solid #00d4ff;border-radius:0 10px 10px 0;padding:10px 18px;margin:20px 0 12px;font-weight:700;font-size:15px;color:#e2e8f0}
.tag{display:inline-block;background:#00d4ff22;color:#00d4ff;border:1px solid #00d4ff44;border-radius:20px;padding:2px 10px;font-size:11px;font-weight:600;margin:2px}
.tg{background:#10b98122;color:#10b981;border-color:#10b98144}
.tp{background:#7c3aed22;color:#7c3aed;border-color:#7c3aed44}
.alert{background:#ef444415;border:1px solid #ef444444;border-radius:10px;padding:12px 16px;margin-bottom:8px;font-size:13px;color:#fca5a5}
.ok{background:#10b98115;border:1px solid #10b98144;border-radius:10px;padding:12px 16px;margin-bottom:8px;font-size:13px;color:#6ee7b7}
.di{border-left:3px solid;border-radius:0 8px 8px 0;padding:8px 12px;margin-bottom:6px;font-size:12px;color:#e2e8f0}
</style>
""", unsafe_allow_html=True)

def kpi(val, lbl, color="#00d4ff"):
    st.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:{color}">{val}</div><div class="kpi-lbl">{lbl}</div></div>', unsafe_allow_html=True)

def sec(t):
    st.markdown(f'<div class="sec-hdr">{t}</div>', unsafe_allow_html=True)

def bar(label, score, max_val=10, color="#00d4ff"):
    pct = int(min(max(float(score)/float(max_val),0),1)*100)
    st.markdown(f"""<div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px">
      <span style="color:#94a3b8">{label}</span><span style="color:{color};font-size:12px">{float(score):.1f}/{max_val}</span></div>
    <div style="height:6px;background:#111827;border-radius:3px;margin-bottom:10px;overflow:hidden">
      <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,{color}88,{color});border-radius:3px"></div></div>""",
    unsafe_allow_html=True)

def fmt(v):
    return f"{int(v):,}€".replace(",",".")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ BusinessIQ")
    st.caption("Sin APIs · Sin coste · 100% gratuito")
    st.markdown("---")

    st.markdown("### 🏢 Empresa")
    empresa        = st.text_input("Nombre", placeholder="Ej. Acme Solutions S.L.")
    sector         = st.selectbox("Sector", SECTORES)
    subsector      = st.text_input("Sub-sector", placeholder="Ej. SaaS B2B")
    pais           = st.selectbox("País", PAISES)
    provincia      = st.selectbox("Provincia", PROVINCIAS) if pais == "España" else st.text_input("Región / Estado")
    modelo         = st.selectbox("Modelo negocio", ["B2B — Empresas","B2C — Consumidor","B2B2C — Mixto","Marketplace","SaaS / Suscripción"])
    mercado        = st.selectbox("Alcance", ["Local / Comarcal","Regional / Autonómico","Nacional","Europeo","Global"])
    años           = st.number_input("Años de actividad", 0, 200, 5)
    desc           = st.text_area("Descripción breve", placeholder="Qué hace, producto/servicio...", height=70)

    st.markdown("---")
    st.markdown("### 👥 Equipo")
    empleados    = st.number_input("Nº empleados/as", 1, 100000, 20)
    clientes     = st.number_input("Nº clientes activos", 0, 1000000, 50)
    competidores = st.number_input("Nº competidores directos", 0, 500, 5)
    nivel_tech   = st.select_slider("Nivel tecnológico", options=["Muy bajo","Bajo","Medio","Alto","Avanzado"], value="Medio")

    with st.expander("📊 Distribución por edad (%)"):
        c1,c2 = st.columns(2)
        e1=c1.number_input("18-25",0,100,10,key="e1"); e2=c2.number_input("26-35",0,100,30,key="e2")
        e3=c1.number_input("36-45",0,100,30,key="e3"); e4=c2.number_input("46-55",0,100,20,key="e4")
        e5=c1.number_input("55+",  0,100,10,key="e5")

    with st.expander("👔 Perfiles profesionales (%)"):
        p1=st.number_input("Directivos",   0,100,10,key="p1"); p2=st.number_input("Mando medio",  0,100,20,key="p2")
        p3=st.number_input("Técnicos",     0,100,30,key="p3"); p4=st.number_input("Admin/Soporte",0,100,20,key="p4")
        p5=st.number_input("Operativos",   0,100,20,key="p5")

    st.markdown("---")
    st.markdown("### ⚙️ Procesos clave")
    sugs        = SUGERENCIAS_SECTOR.get(sector, SUGERENCIAS_SECTOR["Otro"])
    procs_sel   = st.multiselect("Sugerencias del sector", sugs)
    proc_libre  = st.text_input("Proceso adicional")
    if "extra" not in st.session_state: st.session_state.extra = []
    if proc_libre and st.button("➕ Añadir"):
        if proc_libre not in st.session_state.extra: st.session_state.extra.append(proc_libre)
    if st.session_state.extra:
        st.caption(", ".join(st.session_state.extra))
        if st.button("🗑️ Limpiar"): st.session_state.extra = []
    procesos = procs_sel + st.session_state.extra

    st.markdown("---")
    st.markdown("### 💰 Datos financieros")
    facturacion  = st.number_input("Facturación anual (€)",      0, 10_000_000_000, 1_000_000, step=10_000)
    costes       = st.number_input("Costes totales anuales (€)",  0, 10_000_000_000,   700_000, step=10_000)
    margen_bruto = st.number_input("Margen bruto (%)", 0.0, 100.0, 30.0)
    crecimiento  = st.number_input("Crecimiento YoY (%)", -100.0, 500.0, 8.0)

    st.markdown("---")
    run = st.button("⚡ GENERAR ANÁLISIS", use_container_width=True, type="primary")

# ── MAIN ──────────────────────────────────────────────────────────────────────
st.markdown("# ⚡ BusinessIQ Analyzer")
st.markdown("**Análisis estratégico empresarial** · Porter · PESTEL · BCG · DAFO · Macro · ROI IA · **100% gratuito · Sin APIs**")
st.markdown("---")

if not run:
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown("**🔍 Análisis Estratégico**\n- ⚔️ 5 Fuerzas de Porter\n- 🌍 PESTEL completo\n- 📦 Matriz BCG\n- 🔍 DAFO + Estrategias cruzadas")
    with c2: st.markdown("**📈 Contexto de Mercado**\n- Indicadores macro regionales\n- Previsión sectorial 12 meses\n- Score competitivo\n- Alertas estratégicas")
    with c3: st.markdown("**🤖 ROI Inteligencia Artificial**\n- Inversión y ahorro estimados\n- Plan Q1–Q4 detallado\n- Procesos con mayor potencial\n- Herramientas recomendadas")
    st.info("👈 Rellena el formulario lateral y pulsa **⚡ GENERAR ANÁLISIS** — sin registro, sin API Key, sin coste.")
    st.stop()

if not empresa:
    st.error("⚠️ El nombre de la empresa es obligatorio.")
    st.stop()

datos = dict(
    empresa=empresa, sector=sector, subsector=subsector, pais=pais, provincia=provincia,
    modelo=modelo, mercado=mercado, años=años, descripcion=desc,
    empleados=empleados, clientes=clientes, competidores=competidores, nivel_tech=nivel_tech,
    facturacion=facturacion, costes=costes, margen=margen_bruto, crecimiento=crecimiento,
    e1825=e1, e2635=e2, e3645=e3, e4655=e4, e55p=e5,
    p_dir=p1, p_mm=p2, p_tec=p3, p_adm=p4, p_op=p5, procesos=procesos,
)

with st.spinner("⚡ Calculando análisis estratégico..."):
    r = analizar(datos)

# ── TABS ──────────────────────────────────────────────────────────────────────
t1,t2,t3,t4,t5,t6,t7 = st.tabs(["📊 Resumen","⚔️ Porter","🌍 PESTEL","📦 BCG","🔍 DAFO","📈 Macro","🤖 ROI IA"])

with t1:
    sec("📊 Executive Summary"); st.info(r.executive_summary)
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi(f"{r.score_global}/100",    "Score Global",        "#00d4ff")
    with c2: kpi(f"{r.competitividad}/100",  "Competitividad",      "#10b981")
    with c3: kpi(f"{r.potencial_ia:.0f}/100","Potencial IA",        "#7c3aed")
    with c4: kpi(f"{r.rentabilidad_esperada_pct:.1f}%","Rentabilidad Esp.","#f59e0b")
    st.markdown("")
    sec("🎯 Dimensiones Estratégicas")
    cl,cr = st.columns(2)
    for i,dim in enumerate(r.dimensiones):
        s=dim["score"]; c="#10b981" if s>=7 else "#00d4ff" if s>=5 else "#f59e0b"
        with (cl if i%2==0 else cr): bar(dim["nombre"],s,color=c)
    sec("💰 Métricas Financieras")
    c1,c2,c3,c4 = st.columns(4)
    bc="#10b981" if r.beneficio_bruto>=0 else "#ef4444"
    with c1: kpi(fmt(r.beneficio_bruto),"Beneficio Bruto",bc)
    with c2: kpi(f"{r.margen_operativo:.1f}%","Margen Operativo","#00d4ff")
    with c3: kpi(fmt(r.revenue_empleado),"Revenue/Empleado","#7c3aed")
    with c4: kpi(fmt(r.coste_empleado),"Coste/Empleado","#f59e0b")
    cl,cr = st.columns(2)
    with cl:
        sec("⚠️ Alertas Estratégicas")
        for a in r.alertas: st.markdown(f'<div class="alert">{a}</div>',unsafe_allow_html=True)
    with cr:
        sec("✅ Quick Wins")
        for o in r.oportunidades_rapidas: st.markdown(f'<div class="ok">💡 {o}</div>',unsafe_allow_html=True)

with t2:
    sec("⚔️ Las 5 Fuerzas de Porter")
    st.markdown(f"**Score global:** `{r.porter_score_global:.1f}/10`")
    nc_map={"Alto":"#ef4444","Medio":"#f59e0b","Bajo":"#10b981"}
    for f in r.porter:
        with st.expander(f"**{f['nombre']}** — {f['nivel']} · {f['score']:.1f}/10"):
            cl,cr=st.columns([3,1])
            with cl: st.markdown(f"**Análisis:** {f['descripcion']}\n\n**→** *{f['recomendacion']}*")
            with cr: bar("Intensidad",f["score"],color=nc_map.get(f["nivel"],"#64748b"))
    st.markdown("---"); st.markdown(f"**Conclusión:** {r.porter_conclusion}")

with t3:
    sec("🌍 Análisis PESTEL")
    ic_map={"Positivo":"#10b981","Negativo":"#ef4444","Neutro":"#64748b"}
    items=r.pestel
    for i in range(0,len(items),2):
        cols=st.columns(2)
        for j,col in enumerate(cols):
            if i+j<len(items):
                it=items[i+j]; c=ic_map.get(it["impacto"],"#64748b")
                with col:
                    with st.expander(f"**{it['dimension']}** — {it['impacto']}"):
                        st.markdown(f"**Descripción:** {it['descripcion']}\n\n**Factor clave:** `{it['factor_clave']}`\n\n**Tendencia:** {it['tendencia']}")
                        bar("Impacto positivo",it["score"],color=c)

with t4:
    bcg=r.bcg; sec("📦 Matriz BCG")
    pos=bcg["posicion"]
    em_map={"Estrella":"⭐","Vaca Lechera":"🐄","Interrogante":"❓","Perro":"🐕"}
    co_map={"Estrella":"#f59e0b","Vaca Lechera":"#10b981","Interrogante":"#00d4ff","Perro":"#ef4444"}
    em=em_map.get(pos,"❓"); co=co_map.get(pos,"#00d4ff")
    cl,cr=st.columns([1,2])
    with cl:
        kpi(f"{em} {pos}","Posición BCG",co); st.markdown("")
        bar("Crecimiento de mercado",bcg["crecimiento_mercado"],100,"#00d4ff")
        bar("Cuota relativa estimada",bcg["cuota_relativa"],100,co)
    with cr:
        st.markdown(f"**Descripción:** {bcg['descripcion']}\n\n**Estrategia:** {bcg['estrategia']}")
        st.markdown("""<div style="background:#111827;border-radius:12px;padding:14px;margin-top:10px">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;max-width:280px">
          <div style="background:#f59e0b22;border:1px solid #f59e0b44;border-radius:6px;padding:10px;text-align:center;font-size:12px">⭐ Estrella<br><small style="color:#64748b">Alta cuota · Alto crec.</small></div>
          <div style="background:#ef444422;border:1px solid #ef444444;border-radius:6px;padding:10px;text-align:center;font-size:12px">❓ Interrogante<br><small style="color:#64748b">Baja cuota · Alto crec.</small></div>
          <div style="background:#10b98122;border:1px solid #10b98144;border-radius:6px;padding:10px;text-align:center;font-size:12px">🐄 Vaca Lechera<br><small style="color:#64748b">Alta cuota · Bajo crec.</small></div>
          <div style="background:#ef444411;border:1px solid #ef444433;border-radius:6px;padding:10px;text-align:center;font-size:12px">🐕 Perro<br><small style="color:#64748b">Baja cuota · Bajo crec.</small></div>
        </div></div>""",unsafe_allow_html=True)

with t5:
    sec("🔍 Análisis DAFO"); dafo=r.dafo
    cfg=[("fortalezas","💪 FORTALEZAS","#10b981"),("debilidades","⚠️ DEBILIDADES","#ef4444"),
         ("oportunidades","🚀 OPORTUNIDADES","#00d4ff"),("amenazas","🔥 AMENAZAS","#f59e0b")]
    ca,cb=st.columns(2); cols4=[ca,cb,ca,cb]
    for (key,title,color),col in zip(cfg,cols4):
        with col:
            st.markdown(f"<div style='color:{color};font-weight:700;font-size:13px;margin:14px 0 8px'>{title}</div>",unsafe_allow_html=True)
            for item in dafo.get(key,[]):
                st.markdown(f"<div class='di' style='background:{color}12;border-color:{color}'>▸ {item}</div>",unsafe_allow_html=True)
    est=r.dafo_estrategias
    if est:
        st.markdown(""); sec("🧭 Estrategias Cruzadas DAFO")
        ca,cb=st.columns(2)
        with ca:
            st.markdown(f"**FO — Explotar:** {est.get('FO','')}\n\n**DO — Reorientar:** {est.get('DO','')}")
        with cb:
            st.markdown(f"**FA — Defender:** {est.get('FA','')}\n\n**DA — Sobrevivir:** {est.get('DA','')}")

with t6:
    macro=r.macro; sec(f"📈 Previsión Macroeconómica — {provincia}, {pais}")
    inds=macro.get("indicadores",[])
    if inds:
        cols=st.columns(len(inds))
        for col,ind in zip(cols,inds):
            with col: kpi(f"{ind['tendencia']} {ind['valor']}",ind["nombre"],"#10b981" if ind["positivo"] else "#f59e0b")
    st.markdown(""); ca,cb=st.columns(2)
    with ca:
        sec("🏙️ Contexto Regional"); st.markdown(macro.get("contexto_regional",""))
        st.markdown(""); sec("📅 Perspectiva 12 meses"); st.markdown(macro.get("perspectiva_12m",""))
    with cb:
        sec("✅ Oportunidades")
        for o in macro.get("oportunidades",[]): st.markdown(f'<div class="ok">✓ {o}</div>',unsafe_allow_html=True)
        sec("⚠️ Riesgos Macro")
        for rk in macro.get("riesgos",[]): st.markdown(f'<div class="alert">! {rk}</div>',unsafe_allow_html=True)

with t7:
    roi=r.roi_ia; sec("🤖 ROI de Inteligencia Artificial — 12 meses")
    c1,c2,c3,c4=st.columns(4)
    with c1: kpi(fmt(roi["inversion_estimada"]),"Inversión estimada","#f59e0b")
    with c2: kpi(fmt(roi["ahorro_anual"]),"Ahorro anual","#10b981")
    with c3: kpi(f"+{fmt(roi['ingresos_extra'])}","Ingresos extra","#10b981")
    with c4: kpi(f"{roi['roi_porcentaje']:.0f}%","ROI año 1","#00d4ff" if roi["roi_porcentaje"]>=0 else "#ef4444")
    st.markdown(f"⏱️ **Payback estimado:** `{roi['payback_meses']} meses`")
    sec("📅 Plan Trimestral")
    for fase in roi.get("fases",[]):
        with st.expander(f"**{fase['mes']}** — {fase['titulo']}"):
            ca,cb=st.columns([3,1])
            with ca: st.markdown(f"**Descripción:** {fase['descripcion']}\n\n**💰 Impacto:** {fase['impacto']}")
            with cb:
                herr=fase.get("herramientas",[])
                if herr: st.markdown("**Herramientas:**"); [st.markdown(f"<span class='tag'>{h}</span>",unsafe_allow_html=True) for h in herr]
    sec("⚙️ Procesos con Mayor Potencial IA")
    pi=roi.get("procesos_ia",[])
    if pi:
        hdr=st.columns([3,2,1,1,1])
        for col,lbl in zip(hdr,["Proceso","Tipo IA","Ahorro","Dificultad","Impacto"]):
            col.markdown(f"<span style='font-size:11px;color:#64748b;font-weight:600'>{lbl}</span>",unsafe_allow_html=True)
        dc={"Baja":"#10b981","Media":"#f59e0b","Alta":"#ef4444"}
        ic2={"Alto":"#10b981","Medio":"#00d4ff","Bajo":"#64748b"}
        for p in pi:
            row=st.columns([3,2,1,1,1])
            row[0].markdown(f"<span style='font-size:13px'>{p['proceso']}</span>",unsafe_allow_html=True)
            row[1].markdown(f"<span style='font-size:12px;color:#94a3b8'>{p['tipo_ia']}</span>",unsafe_allow_html=True)
            row[2].markdown(f"<span class='tag tg'>{p['ahorro_potencial']}</span>",unsafe_allow_html=True)
            row[3].markdown(f"<span style='color:{dc.get(p.get('dificultad','Media'),'#64748b')};font-size:12px'>{p.get('dificultad','Media')}</span>",unsafe_allow_html=True)
            row[4].markdown(f"<span style='color:{ic2.get(p.get('impacto','Medio'),'#64748b')};font-size:12px'>{p.get('impacto','Medio')}</span>",unsafe_allow_html=True)
    sec("🛠️ Herramientas IA Recomendadas")
    herrs=roi.get("herramientas_recomendadas",[])
    if herrs:
        hc=st.columns(len(herrs))
        for col,h in zip(hc,herrs):
            with col: st.markdown(f"<div class='kpi-card' style='text-align:left'><div style='font-weight:700;font-size:14px;color:#e2e8f0'>{h['nombre']}</div><div style='margin:4px 0'><span class='tag tp'>{h['categoria']}</span> <span class='tag'>{h['coste_mes']}</span></div><div style='font-size:12px;color:#94a3b8;margin-top:6px'>{h['uso']}</div></div>",unsafe_allow_html=True)
    st.markdown(""); sec("✅ Conclusión Final"); st.success(roi["conclusion"])

st.markdown("---")
st.markdown(f"<div style='text-align:center;color:#64748b;font-size:11px'>BusinessIQ Analyzer · {datetime.now().strftime('%d/%m/%Y %H:%M')} · Análisis para <b style='color:#00d4ff'>{empresa}</b> · <span style='color:#10b981'>100% gratuito · Sin APIs · Sin coste</span></div>",unsafe_allow_html=True)
