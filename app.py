"""
BusinessIQ Engine — Lógica de análisis estratégico sin APIs externas.
Todos los scores, textos e insights se generan a partir de los datos del usuario.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# ─── CONSTANTES SECTORIALES ──────────────────────────────────────────────────

# (rivalidad_base, barreras_entrada, concentracion_proveedores, poder_cliente, disrupcion_digital)
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

# (crecimiento_mercado_5y, volatilidad, margen_tipico, digitalizacion_sector)
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

# Indicadores macro por provincia española
MACRO_PROVINCIAS: Dict[str, Dict] = {
    "Madrid":    {"pib": 3.2, "paro": 9.8,  "inversion": 22, "confianza": 58},
    "Barcelona": {"pib": 3.0, "paro": 10.1, "inversion": 20, "confianza": 56},
    "Valencia":  {"pib": 2.6, "paro": 12.4, "inversion": 14, "confianza": 51},
    "Sevilla":   {"pib": 2.3, "paro": 16.8, "inversion": 11, "confianza": 48},
    "Zaragoza":  {"pib": 2.5, "paro": 11.2, "inversion": 12, "confianza": 52},
    "Málaga":    {"pib": 3.1, "paro": 14.1, "inversion": 15, "confianza": 53},
    "Bilbao":    {"pib": 2.8, "paro": 9.4,  "inversion": 16, "confianza": 55},
    "Alicante":  {"pib": 2.4, "paro": 13.5, "inversion": 12, "confianza": 50},
    "Córdoba":   {"pib": 2.0, "paro": 18.2, "inversion": 9,  "confianza": 45},
    "Valladolid":{"pib": 2.3, "paro": 11.8, "inversion": 10, "confianza": 50},
    "Vigo":      {"pib": 2.4, "paro": 12.6, "inversion": 11, "confianza": 49},
    "A Coruña":  {"pib": 2.3, "paro": 12.9, "inversion": 10, "confianza": 49},
    "Granada":   {"pib": 2.1, "paro": 17.0, "inversion": 8,  "confianza": 46},
    "Vitoria":   {"pib": 2.9, "paro": 8.9,  "inversion": 17, "confianza": 56},
    "Elche":     {"pib": 2.2, "paro": 13.8, "inversion": 9,  "confianza": 48},
    "Santander": {"pib": 2.2, "paro": 12.5, "inversion": 10, "confianza": 49},
    "Oviedo":    {"pib": 2.1, "paro": 13.2, "inversion": 9,  "confianza": 48},
    "Pamplona":  {"pib": 2.7, "paro": 9.1,  "inversion": 14, "confianza": 54},
    "Logroño":   {"pib": 2.4, "paro": 10.8, "inversion": 11, "confianza": 51},
    "Badajoz":   {"pib": 1.8, "paro": 22.1, "inversion": 7,  "confianza": 43},
    "Salamanca": {"pib": 1.9, "paro": 14.9, "inversion": 8,  "confianza": 46},
    "Huelva":    {"pib": 2.0, "paro": 19.8, "inversion": 8,  "confianza": 44},
    "Lleida":    {"pib": 2.3, "paro": 11.4, "inversion": 10, "confianza": 50},
    "Tarragona": {"pib": 2.4, "paro": 11.8, "inversion": 11, "confianza": 51},
    "Girona":    {"pib": 2.5, "paro": 10.9, "inversion": 12, "confianza": 52},
    "Toledo":    {"pib": 2.2, "paro": 13.6, "inversion": 9,  "confianza": 48},
    "Palma":     {"pib": 2.9, "paro": 11.8, "inversion": 16, "confianza": 53},
    "Las Palmas":{"pib": 2.5, "paro": 15.2, "inversion": 12, "confianza": 50},
    "Gijón":     {"pib": 2.0, "paro": 14.1, "inversion": 8,  "confianza": 47},
    "Murcia":    {"pib": 2.3, "paro": 14.8, "inversion": 10, "confianza": 49},
}

MACRO_PAISES: Dict[str, Dict] = {
    "España":    {"pib": 2.5, "paro": 11.4, "ipc": 2.8, "euribor": 2.65},
    "México":    {"pib": 1.8, "paro": 2.8,  "ipc": 4.2, "euribor": 11.0},
    "Argentina": {"pib": 2.1, "paro": 6.2,  "ipc": 55.0,"euribor": 40.0},
    "Colombia":  {"pib": 2.3, "paro": 9.8,  "ipc": 6.5, "euribor": 11.5},
    "Chile":     {"pib": 2.0, "paro": 8.5,  "ipc": 4.5, "euribor": 6.5},
    "Perú":      {"pib": 2.5, "paro": 6.8,  "ipc": 3.8, "euribor": 6.75},
    "EE.UU.":   {"pib": 2.2, "paro": 3.9,  "ipc": 3.2, "euribor": 5.25},
    "Otro":      {"pib": 2.5, "paro": 8.0,  "ipc": 4.0, "euribor": 5.0},
}

TECH_SCORE = {"Muy bajo": 1, "Bajo": 3, "Medio": 5, "Alto": 7, "Avanzado": 9}
MERCADO_SCORE = {"Local / Comarcal": 2, "Regional / Autonómico": 4, "Nacional": 6, "Europeo": 8, "Global": 10}

# ─── DATACLASS RESULTADO ─────────────────────────────────────────────────────

@dataclass
class AnalysisResult:
    # Scores globales
    score_global: float = 0
    competitividad: float = 0
    potencial_ia: float = 0
    rentabilidad_esperada_pct: float = 0

    # KPIs financieros
    beneficio_bruto: float = 0
    margen_operativo: float = 0
    revenue_empleado: float = 0
    coste_empleado: float = 0

    # Executive summary
    executive_summary: str = ""
    alertas: List[str] = field(default_factory=list)
    oportunidades_rapidas: List[str] = field(default_factory=list)

    # Dimensiones
    dimensiones: List[Dict] = field(default_factory=list)

    # Porter
    porter: List[Dict] = field(default_factory=list)
    porter_conclusion: str = ""
    porter_score_global: float = 0

    # PESTEL
    pestel: List[Dict] = field(default_factory=list)

    # BCG
    bcg: Dict = field(default_factory=dict)

    # DAFO
    dafo: Dict = field(default_factory=dict)
    dafo_estrategias: Dict = field(default_factory=dict)

    # Macro
    macro: Dict = field(default_factory=dict)

    # ROI IA
    roi_ia: Dict = field(default_factory=dict)


# ─── MOTOR PRINCIPAL ─────────────────────────────────────────────────────────

def analizar(d: dict) -> AnalysisResult:
    r = AnalysisResult()

    # Extraer y normalizar inputs
    fac   = float(d.get("facturacion", 0) or 0)
    cos   = float(d.get("costes", 0) or 0)
    emp   = max(int(d.get("empleados", 1) or 1), 1)
    años  = int(d.get("años", 1) or 1)
    comp  = int(d.get("competidores", 5) or 5)
    cli   = int(d.get("clientes", 0) or 0)
    crec  = float(d.get("crecimiento", 0) or 0)
    margen_bruto = float(d.get("margen", 0) or 0)
    tech  = TECH_SCORE.get(d.get("nivel_tech", "Medio"), 5)
    merc  = MERCADO_SCORE.get(d.get("mercado", "Nacional"), 6)
    sector = d.get("sector", "Otro")
    provincia = d.get("provincia", "Madrid")
    pais  = d.get("pais", "España")
    empresa = d.get("empresa", "la empresa")
    procesos = d.get("procesos", [])

    # Datos sectoriales
    porter_base = SECTOR_PORTER.get(sector, SECTOR_PORTER["Otro"])
    meta = SECTOR_META.get(sector, SECTOR_META["Otro"])
    crec_sector, volatilidad, margen_tipico, dig_sector = meta

    # ── FINANCIEROS BÁSICOS ──────────────────────────────────────────────────
    r.beneficio_bruto   = fac - cos
    r.margen_operativo  = (r.beneficio_bruto / fac * 100) if fac > 0 else 0
    r.revenue_empleado  = fac / emp
    r.coste_empleado    = cos / emp

    # ── SCORES ───────────────────────────────────────────────────────────────
    # Salud financiera (0-10)
    fin_score = _clamp(
        (r.margen_operativo / margen_tipico) * 4          # vs benchmark sector
        + (1 if r.beneficio_bruto > 0 else 0) * 2        # rentable
        + _norm(crec, -20, 40) * 3                        # crecimiento
        + (1 if margen_bruto > 20 else 0)                 # margen bruto OK
    , 0, 10)

    # Posición competitiva (0-10)
    competidores_penalty = _clamp(comp / 3, 0, 4)
    comp_score = _clamp(
        (años / 10) * 2                                   # veteranía
        + _norm(cli / max(emp, 1), 0, 20) * 2             # clientes por empleado
        + merc / 2                                        # alcance de mercado
        + (10 - competidores_penalty) / 2                 # menos competidores = mejor
    , 0, 10)

    # Madurez digital (0-10)
    dig_score = _clamp(tech * 0.8 + _norm(dig_sector, 3, 9) * 2, 0, 10)

    # Capital humano (0-10)
    p_dir = float(d.get("p_dir", 10) or 10)
    p_mm  = float(d.get("p_mm",  20) or 20)
    p_tec = float(d.get("p_tec", 30) or 30)
    edades_jovenes = float(d.get("e1825", 10) or 10) + float(d.get("e2635", 30) or 30)
    rrhh_score = _clamp(
        (p_dir + p_mm) / 20          # liderazgo
        + p_tec / 15                  # talento técnico
        + _norm(edades_jovenes, 10, 70) * 2  # rejuvenecimiento
        + _norm(emp, 1, 200) * 1.5   # tamaño equipo
    , 0, 10)

    # Potencial crecimiento (0-10)
    crec_score = _clamp(
        _norm(crec, -10, 40) * 4
        + _norm(crec_sector, 2, 15) * 3
        + _norm(merc, 2, 10) * 2
        + (1 if fac > 0 and cos < fac else 0)
    , 0, 10)

    r.dimensiones = [
        {"nombre": "Posición Competitiva",  "score": round(comp_score,  1)},
        {"nombre": "Capacidad Financiera",  "score": round(fin_score,   1)},
        {"nombre": "Capital Humano",        "score": round(rrhh_score,  1)},
        {"nombre": "Madurez Digital",       "score": round(dig_score,   1)},
        {"nombre": "Crecimiento Potencial", "score": round(crec_score,  1)},
    ]

    r.score_global      = round((comp_score + fin_score + rrhh_score + dig_score + crec_score) / 5 * 10, 1)
    r.competitividad    = round(comp_score * 10, 1)
    r.potencial_ia      = round((10 - dig_score) * 6 + crec_score * 2 + fin_score, 1)
    r.potencial_ia      = _clamp(r.potencial_ia, 20, 95)
    r.rentabilidad_esperada_pct = round(r.margen_operativo * (1 + crec / 100), 2)

    # ── PORTER ───────────────────────────────────────────────────────────────
    riv, bar, prov, cli_pow, sust = porter_base
    # Ajustar por número de competidores
    riv_ajust = _clamp(riv * 0.7 + (comp / 10) * 3, 1, 10)
    # Ajustar poder cliente por número de clientes
    cli_ajust = _clamp(cli_pow * 0.8 + (1 if cli < 20 else 0) * 2, 1, 10)
    # Ajustar sustitutos por nivel tech sector
    sust_ajust = _clamp(sust * 0.7 + dig_sector * 0.3, 1, 10)

    r.porter = [
        _porter_fuerza("Rivalidad entre competidores",    riv_ajust, sector, comp, "rivalidad"),
        _porter_fuerza("Amenaza de nuevos entrantes",      bar,       sector, comp, "entrantes"),
        _porter_fuerza("Poder negociador de proveedores",  prov,      sector, comp, "proveedores"),
        _porter_fuerza("Poder negociador de clientes",     cli_ajust, sector, cli,  "clientes"),
        _porter_fuerza("Amenaza de productos sustitutos",  sust_ajust,sector, comp, "sustitutos"),
    ]
    r.porter_score_global = round(sum(f["score"] for f in r.porter) / 5, 1)
    r.porter_conclusion   = _porter_conclusion(r.porter_score_global, sector, empresa)

    # ── PESTEL ────────────────────────────────────────────────────────────────
    macro_pais = MACRO_PAISES.get(pais, MACRO_PAISES["España"])
    r.pestel = _build_pestel(sector, pais, provincia, macro_pais, tech, dig_sector)

    # ── BCG ───────────────────────────────────────────────────────────────────
    cuota = _cuota_relativa(comp, años, merc, fin_score)
    crec_mkt = _norm(crec_sector, 0, 20) * 100
    r.bcg = _build_bcg(cuota, crec_mkt, sector, empresa, crec)

    # ── DAFO ─────────────────────────────────────────────────────────────────
    r.dafo = _build_dafo(d, r, sector, fin_score, dig_score, comp_score, rrhh_score)
    r.dafo_estrategias = _build_estrategias_dafo(r.dafo, sector, empresa)

    # ── MACRO ─────────────────────────────────────────────────────────────────
    r.macro = _build_macro(provincia, pais, sector, macro_pais)

    # ── ROI IA ────────────────────────────────────────────────────────────────
    r.roi_ia = _build_roi_ia(d, r, fac, cos, emp, tech, procesos, sector)

    # ── ALERTAS & QUICK WINS ──────────────────────────────────────────────────
    r.alertas = _alertas(d, r, fin_score, dig_score, comp_score, crec, comp, fac, cos)
    r.oportunidades_rapidas = _quick_wins(d, r, tech, procesos, sector)

    # ── EXECUTIVE SUMMARY ────────────────────────────────────────────────────
    r.executive_summary = _executive_summary(d, r, empresa, sector, provincia, pais, fac, cos, crec)

    return r


# ─── FUNCIONES AUXILIARES ────────────────────────────────────────────────────

def _clamp(v, lo, hi):
    return max(lo, min(hi, v))

def _norm(v, lo, hi):
    """Normaliza v entre lo y hi → [0, 1]"""
    if hi == lo:
        return 0.5
    return _clamp((v - lo) / (hi - lo), 0, 1)

def _nivel(score):
    if score >= 7.5: return "Alto"
    if score >= 4.5: return "Medio"
    return "Bajo"

def _nivel_color(nivel):
    return {"Alto": "#ef4444", "Medio": "#f59e0b", "Bajo": "#10b981"}[nivel]


# ── PORTER ───────────────────────────────────────────────────────────────────

_PORTER_TEXTOS = {
    "rivalidad": {
        "Alto":  ("Intensa competencia entre actores consolidados con presión constante en precios y captación de clientes.",
                  "Diferenciar por valor y calidad; invertir en fidelización y marca."),
        "Medio": ("Competencia moderada con espacio para diferenciación sin guerra de precios extrema.",
                  "Consolidar posición en nicho y mejorar propuesta de valor."),
        "Bajo":  ("Mercado con pocos rivales directos y espacio para crecer con relativa comodidad.",
                  "Aprovechar la ventana de baja competencia para expandir cuota de mercado."),
    },
    "entrantes": {
        "Alto":  ("Barreras de entrada bajas permiten que nuevos jugadores entren con facilidad.",
                  "Construir barreras: marca, relaciones, economías de escala o patentes."),
        "Medio": ("Inversión inicial y curva de aprendizaje disuaden a muchos entrantes.",
                  "Mantener liderazgo técnico o relacional para frenar entrada de competidores."),
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
                  "Mejorar experiencia cliente y valor añadido para reducir sensibilidad al precio."),
        "Bajo":  ("Clientes con pocas alternativas o alta dependencia del producto/servicio.",
                  "Mantener calidad y servicio; aprovechar posición para ampliar cartera."),
    },
    "sustitutos": {
        "Alto":  ("Alternativas digitales o tecnológicas amenazan con desplazar el modelo actual.",
                  "Innovar activamente e incorporar IA y automatización antes que los sustitutos."),
        "Medio": ("Sustitutos presentes pero con limitaciones; cliente valora la propuesta actual.",
                  "Evolucionar la oferta incorporando las ventajas de los sustitutos."),
        "Bajo":  ("Pocos sustitutos reales; el producto o servicio difícilmente reemplazable.",
                  "Comunicar mejor la propuesta única y ampliar barreras de sustitución."),
    },
}

def _porter_fuerza(nombre, score, sector, extra, tipo):
    score = round(_clamp(score, 1, 10), 1)
    nivel = _nivel(score)
    desc, rec = _PORTER_TEXTOS[tipo][nivel]
    return {"nombre": nombre, "nivel": nivel, "score": score,
            "descripcion": desc, "recomendacion": rec}

def _porter_conclusion(score_global, sector, empresa):
    if score_global >= 7:
        return (f"El entorno competitivo de {empresa} es muy exigente (score {score_global}/10). "
                f"El sector {sector} combina alta rivalidad y presión desde múltiples frentes. "
                f"La estrategia debe priorizar diferenciación clara y fidelización de clientes como palancas de rentabilidad.")
    elif score_global >= 5:
        return (f"{empresa} opera en un entorno de intensidad competitiva moderada (score {score_global}/10) "
                f"en el sector {sector}. Existen nichos defendibles y espacio para crecer con la estrategia adecuada.")
    else:
        return (f"El sector {sector} presenta condiciones competitivas favorables (score {score_global}/10). "
                f"{empresa} tiene una oportunidad privilegiada para consolidar posición y crecer sin presión extrema.")


# ── PESTEL ───────────────────────────────────────────────────────────────────

def _build_pestel(sector, pais, provincia, macro, tech, dig_sector):
    ipc = macro["ipc"]
    pib = macro["pib"]
    tipo_ref = macro.get("euribor", 3.0)

    politico_imp   = "Positivo" if pais in ["España", "EE.UU."] else "Neutro"
    economico_imp  = "Positivo" if pib >= 2.5 and ipc < 4 else "Negativo" if pib < 1 else "Neutro"
    tecnologico_imp= "Positivo"
    legal_imp      = "Neutro" if pais == "España" else "Neutro"
    ecologico_imp  = "Neutro"
    social_imp     = "Positivo" if dig_sector >= 6 else "Neutro"

    return [
        {
            "dimension": "Político",
            "impacto": politico_imp,
            "score": 6 if politico_imp == "Positivo" else 5,
            "descripcion": f"En {pais}, el marco político ofrece estabilidad institucional con fondos de digitalización disponibles para PYMEs del sector {sector}.",
            "factor_clave": "Fondos Next Generation EU / apoyo público a digitalización",
            "tendencia": "Estable con leve mejora",
        },
        {
            "dimension": "Económico",
            "impacto": economico_imp,
            "score": 7 if economico_imp == "Positivo" else 4,
            "descripcion": f"PIB creciendo al {pib}% con inflación del {ipc}%. Tipo de referencia en {tipo_ref}%, con tendencia bajista que favorece la inversión.",
            "factor_clave": f"Inflación {ipc}% · Tipos {tipo_ref}% · PIB +{pib}%",
            "tendencia": "Mejora gradual prevista",
        },
        {
            "dimension": "Social",
            "impacto": social_imp,
            "score": 6,
            "descripcion": f"Cambios en hábitos de consumo y trabajo híbrido impulsan demanda digital en {sector}. Creciente exigencia de transparencia y sostenibilidad.",
            "factor_clave": "Digitalización del consumidor y nuevas expectativas laborales",
            "tendencia": "Aceleración del cambio",
        },
        {
            "dimension": "Tecnológico",
            "impacto": "Positivo",
            "score": 8,
            "descripcion": f"La IA generativa y la automatización están democratizándose para PYMEs. El sector {sector} tiene un nivel de digitalización estimado de {dig_sector}/10.",
            "factor_clave": "IA accesible, cloud, automatización low-code",
            "tendencia": "Aceleración rápida",
        },
        {
            "dimension": "Ecológico",
            "impacto": "Neutro",
            "score": 5,
            "descripcion": f"Regulación ESG en aumento con reporting de sostenibilidad próximo a ser obligatorio. Impacto varía según actividad en {sector}.",
            "factor_clave": "Directiva CSRD europea · reporting sostenibilidad",
            "tendencia": "Presión regulatoria creciente",
        },
        {
            "dimension": "Legal",
            "impacto": "Neutro",
            "score": 5,
            "descripcion": f"AI Act europeo establece obligaciones para sistemas IA. RGPD vigente con sanciones reforzadas. Normativa sectorial específica de {sector}.",
            "factor_clave": "AI Act · RGPD · normativa sectorial",
            "tendencia": "Regulación creciente",
        },
    ]


# ── BCG ───────────────────────────────────────────────────────────────────────

def _cuota_relativa(comp, años, merc, fin_score):
    """Estima cuota relativa 0-100 a partir de proxies."""
    base = 100 / max(comp + 1, 1)          # si hay 4 competidores → ~20% mercado potencial
    madurez = min(años / 20, 1) * 20        # hasta 20 puntos por veteranía
    finanzas = fin_score * 2                # hasta 20 puntos por salud financiera
    return _clamp(base + madurez + finanzas, 5, 90)

def _build_bcg(cuota, crec_mkt, sector, empresa, crec_empresa):
    umbral_cuota = 45
    umbral_crec  = 55
    if cuota >= umbral_cuota and crec_mkt >= umbral_crec:
        pos = "Estrella"
        desc = (f"{empresa} combina alta cuota relativa con mercado en crecimiento. "
                f"Posición privilegiada que requiere inversión sostenida para mantenerse.")
        estrategia = "Invertir para mantener liderazgo. Defender posición frente a nuevos entrantes."
    elif cuota >= umbral_cuota and crec_mkt < umbral_crec:
        pos = "Vaca Lechera"
        desc = (f"{empresa} tiene buena posición en un mercado maduro. "
                f"Genera caja estable que puede reinvertirse en nuevas líneas.")
        estrategia = "Maximizar rentabilidad y usar el cash flow para diversificar o modernizar."
    elif cuota < umbral_cuota and crec_mkt >= umbral_crec:
        pos = "Interrogante"
        desc = (f"{empresa} opera en un mercado creciente pero aún no ha consolidado su cuota. "
                f"La decisión de invertir agresivamente o no es crítica.")
        estrategia = "Definir si se invierte para ganar cuota (→ Estrella) o se abandona el segmento."
    else:
        pos = "Perro"
        desc = (f"{empresa} compite en un mercado de bajo crecimiento con cuota limitada. "
                f"Se recomienda revisar la propuesta de valor o pivotar.")
        estrategia = "Reducir costes, buscar nicho específico o evaluar pivote estratégico."

    return {
        "posicion": pos,
        "descripcion": desc,
        "crecimiento_mercado": round(crec_mkt, 1),
        "cuota_relativa": round(cuota, 1),
        "estrategia": estrategia,
    }


# ── DAFO ─────────────────────────────────────────────────────────────────────

def _build_dafo(d, r, sector, fin, dig, comp, rrhh):
    emp   = int(d.get("empleados", 10) or 10)
    años  = int(d.get("años", 1) or 1)
    merc  = MERCADO_SCORE.get(d.get("mercado","Nacional"), 6)
    crec  = float(d.get("crecimiento", 0) or 0)
    tech  = TECH_SCORE.get(d.get("nivel_tech","Medio"), 5)
    empresa = d.get("empresa","la empresa")
    procesos = d.get("procesos", [])

    fortalezas, debilidades, oportunidades, amenazas = [], [], [], []

    # FORTALEZAS
    if años >= 5:
        fortalezas.append(f"Experiencia contrastada de {años} años en el mercado con cartera de clientes consolidada")
    if fin >= 6:
        fortalezas.append("Salud financiera sólida con márgenes por encima de la media del sector")
    if rrhh >= 6:
        fortalezas.append("Equipo humano con buena estructura de perfiles y distribución generacional equilibrada")
    if comp >= 6:
        fortalezas.append("Posición competitiva defendida con relaciones establecidas con clientes clave")
    if merc >= 6:
        fortalezas.append(f"Presencia en mercado {d.get('mercado','nacional')} con capacidad de expansión")
    if not fortalezas:
        fortalezas.append("Flexibilidad operativa propia de una empresa ágil")
        fortalezas.append("Conocimiento directo del mercado local y relaciones personales con clientes")

    # DEBILIDADES
    if dig < 5:
        debilidades.append(f"Madurez digital por debajo del benchmark del sector {sector} — procesos manuales pendientes de automatizar")
    if fin < 5:
        debilidades.append("Márgenes operativos por debajo de la media sectorial con riesgo de presión de costes")
    if años < 3:
        debilidades.append("Empresa joven con track record limitado y marca todavía en construcción")
    if emp < 10:
        debilidades.append("Tamaño reducido del equipo limita capacidad de ejecución simultánea de proyectos")
    if len(procesos) == 0:
        debilidades.append("Procesos internos no documentados, dificultando la escalabilidad")
    if not debilidades:
        debilidades.append("Posible dependencia de personas clave sin planes de sucesión claros")
        debilidades.append("Limitada inversión en marca y marketing digital")

    # OPORTUNIDADES
    oportunidades.append("Acceso a financiación pública (Next Generation EU, Kit Digital) para digitalización")
    oportunidades.append(f"IA y automatización asequibles para PYMEs del sector {sector} con ROI demostrable en 12 meses")
    if crec > 5:
        oportunidades.append(f"Crecimiento propio del {crec:.0f}% abre puerta a inversión y contratación de talento")
    if merc < 8:
        oportunidades.append("Expansión geográfica a mercados europeos como palanca de crecimiento")
    oportunidades.append("Demanda creciente de clientes por proveedores digitales y sostenibles")

    # AMENAZAS
    amenazas.append("Competidores con mayor madurez digital que pueden ofrecer precios más competitivos")
    amenazas.append("Escasez de talento tecnológico en el mercado laboral con costes salariales al alza")
    amenazas.append("Incertidumbre macroeconómica y posible contracción del consumo")
    amenazas.append(f"Nuevos entrantes digitales que pueden disruptar el modelo tradicional en {sector}")

    return {
        "fortalezas":    fortalezas[:4],
        "debilidades":   debilidades[:4],
        "oportunidades": oportunidades[:4],
        "amenazas":      amenazas[:4],
    }

def _build_estrategias_dafo(dafo, sector, empresa):
    f = dafo["fortalezas"][0] if dafo["fortalezas"] else "sus fortalezas"
    o = dafo["oportunidades"][0] if dafo["oportunidades"] else "las oportunidades del mercado"
    d = dafo["debilidades"][0] if dafo["debilidades"] else "sus debilidades"
    a = dafo["amenazas"][0] if dafo["amenazas"] else "las amenazas del entorno"
    return {
        "FO": f"Aprovechar {f.lower()} para capitalizar {o.lower()}. Estrategia ofensiva de crecimiento.",
        "FA": f"Usar {f.lower()} como escudo frente a {a.lower()}. Mantener posición y reforzar diferenciación.",
        "DO": f"Subsanar {d.lower()} invirtiendo en {o.lower()}. Estrategia de reorientación con fondos disponibles.",
        "DA": f"Reducir exposición a {a.lower()} minimizando el impacto de {d.lower()}. Plan defensivo y de contención de riesgos.",
    }


# ── MACRO ─────────────────────────────────────────────────────────────────────

def _build_macro(provincia, pais, sector, macro_pais):
    prov_data = MACRO_PROVINCIAS.get(provincia, {"pib": macro_pais["pib"], "paro": macro_pais["paro"], "inversion": 12, "confianza": 50})
    pib   = prov_data["pib"]
    paro  = prov_data["paro"]
    inv   = prov_data["inversion"]
    conf  = prov_data["confianza"]
    ipc   = macro_pais["ipc"]
    eurib = macro_pais.get("euribor", 3.0)
    meta  = SECTOR_META.get(sector, SECTOR_META["Otro"])
    crec_sect = meta[0]

    tendencia_paro  = "↓" if paro < 12 else "→"
    tendencia_pib   = "↑" if pib > 2 else "→"
    tendencia_eurib = "↓" if eurib > 3 else "→"

    perspectiva = (
        f"Para los próximos 12 meses, {provincia} muestra indicadores {('favorables' if pib > 2.5 else 'moderados')} "
        f"con PIB regional creciendo al {pib}% y paro {'en descenso' if paro < 12 else 'elevado pero estable'}. "
        f"El sector {sector} presenta una tasa de crecimiento estimada del {crec_sect}% anual, "
        f"{'por encima' if crec_sect > 5 else 'en línea con'} la media de la economía."
    )

    oportunidades = [
        f"Fondos públicos disponibles para digitalización de PYMEs en {pais}",
        f"Crecimiento de demanda en {sector} estimado en +{crec_sect}% anual",
        f"Reducción de tipos de interés favorece financiación de inversiones",
    ]
    if inv > 14:
        oportunidades.append(f"{provincia} entre las regiones con mayor atracción de inversión extranjera")

    riesgos = [
        f"Inflación del {ipc}% presiona costes operativos, especialmente energía y personal",
        "Incertidumbre geopolítica global con impacto en cadenas de suministro",
        "Posible desaceleración del consumo si los tipos no bajan lo esperado",
    ]
    if paro > 15:
        riesgos.append(f"Alta tasa de paro en {provincia} ({paro}%) puede afectar demanda local")

    return {
        "indicadores": [
            {"nombre": "PIB Regional",      "valor": f"+{pib}%",   "tendencia": tendencia_pib,   "positivo": pib > 2},
            {"nombre": "Desempleo",         "valor": f"{paro}%",   "tendencia": tendencia_paro,  "positivo": paro < 12},
            {"nombre": "IPC",               "valor": f"{ipc}%",    "tendencia": "→",             "positivo": ipc < 3},
            {"nombre": "Tipo referencia",   "valor": f"{eurib}%",  "tendencia": tendencia_eurib, "positivo": eurib < 4},
            {"nombre": "Confianza Emp.",    "valor": str(conf),    "tendencia": "↑",             "positivo": conf > 50},
            {"nombre": "Inv. Digital",      "valor": f"+{inv}%",   "tendencia": "↑",             "positivo": True},
        ],
        "contexto_regional": (
            f"{provincia} {'es una de las regiones más dinámicas' if pib > 2.8 else 'mantiene una economía estable'} "
            f"de {pais}, con una tasa de paro del {paro}% y un índice de confianza empresarial de {conf}/100. "
            f"La inversión en infraestructura digital creció un {inv}% interanual, "
            f"posicionando la región {'favorablemente' if inv > 14 else 'de forma moderada'} para la transformación digital."
        ),
        "perspectiva_12m": perspectiva,
        "oportunidades": oportunidades[:4],
        "riesgos": riesgos[:4],
    }


# ── ROI IA ───────────────────────────────────────────────────────────────────

_HERRAMIENTAS_IA: Dict[str, List[Dict]] = {
    "Tecnología / Software":    [
        {"nombre": "GitHub Copilot",      "categoria": "Código",          "coste_mes": "19€/dev",     "uso": "Autocompletar código y refactoring asistido"},
        {"nombre": "Linear AI",           "categoria": "Gestión proyectos","coste_mes": "18€/usuario", "uso": "Priorización automática de tickets e incidencias"},
        {"nombre": "Intercom AI",         "categoria": "Soporte cliente",  "coste_mes": "39€/mes",     "uso": "Chatbot para soporte técnico 24/7"},
    ],
    "Industria / Manufactura": [
        {"nombre": "Microsoft Copilot",   "categoria": "Productividad",    "coste_mes": "30€/usuario", "uso": "Automatización de informes de producción y calidad"},
        {"nombre": "Power BI + IA",       "categoria": "Analítica",        "coste_mes": "10€/usuario", "uso": "Dashboards predictivos de producción y mantenimiento"},
        {"nombre": "Make + IA",           "categoria": "Automatización",   "coste_mes": "29€/mes",     "uso": "Flujos automáticos entre ERP, almacén y logística"},
    ],
    "Retail / Comercio": [
        {"nombre": "Tidio AI",            "categoria": "Atención cliente", "coste_mes": "29€/mes",     "uso": "Chatbot para resolución de dudas y seguimiento pedidos"},
        {"nombre": "Klaviyo AI",          "categoria": "Email marketing",  "coste_mes": "45€/mes",     "uso": "Segmentación automática y personalización de campañas"},
        {"nombre": "Inventory Planner",   "categoria": "Stock",            "coste_mes": "99€/mes",     "uso": "Predicción de demanda y optimización de inventario"},
    ],
    "Servicios Profesionales": [
        {"nombre": "Microsoft Copilot",   "categoria": "Productividad",    "coste_mes": "30€/usuario", "uso": "Redacción de propuestas, informes y resúmenes de reuniones"},
        {"nombre": "HubSpot AI",          "categoria": "CRM",              "coste_mes": "45€/mes",     "uso": "Scoring de leads y automatización de seguimiento comercial"},
        {"nombre": "Notion AI",           "categoria": "Conocimiento",     "coste_mes": "10€/usuario", "uso": "Base de conocimiento inteligente y documentación automática"},
    ],
    "Salud / Farma": [
        {"nombre": "Abridge AI",          "categoria": "Clínico",          "coste_mes": "Consultar",   "uso": "Resumen automático de consultas médicas"},
        {"nombre": "Microsoft Copilot",   "categoria": "Administración",   "coste_mes": "30€/usuario", "uso": "Gestión de informes clínicos y documentación"},
        {"nombre": "Power Automate + IA", "categoria": "Flujos",           "coste_mes": "15€/usuario", "uso": "Automatización de citas, recordatorios y facturación"},
    ],
}
_HERRAMIENTAS_DEFAULT = [
    {"nombre": "Microsoft Copilot",  "categoria": "Productividad",  "coste_mes": "30€/usuario", "uso": "Automatización de tareas administrativas y redacción"},
    {"nombre": "Make + IA",          "categoria": "Automatización", "coste_mes": "29€/mes",     "uso": "Automatización de flujos de trabajo entre aplicaciones"},
    {"nombre": "Power BI + IA",      "categoria": "Analítica",      "coste_mes": "10€/usuario", "uso": "Dashboards inteligentes y análisis predictivo"},
]

def _build_roi_ia(d, r, fac, cos, emp, tech, procesos, sector):
    # Inversión estimada según tamaño empresa
    if fac < 300_000:
        inv = 5_000
    elif fac < 1_000_000:
        inv = 15_000
    elif fac < 5_000_000:
        inv = 35_000
    else:
        inv = 80_000

    # Potencial ahorro basado en costes y nivel tech actual
    gap_digital = (10 - tech) / 10            # 0 = ya digitalizado, 1 = sin digitalizar
    ahorro = round(cos * 0.06 * (0.5 + gap_digital), 0)  # 3-12% costes

    # Ingresos extra basado en crecimiento potencial
    ingresos_extra = round(fac * 0.03 * (1 + r.crec_potencial_proxy()), 0)

    beneficio_neto_ia = ahorro + ingresos_extra - inv
    roi_pct = round((beneficio_neto_ia / inv) * 100, 0) if inv > 0 else 0
    payback = round(inv / max((ahorro + ingresos_extra) / 12, 1), 1)

    # Procesos con mayor potencial
    procesos_ia = _procesos_ia_ranking(procesos, sector, tech)

    # Herramientas
    herramientas = _HERRAMIENTAS_IA.get(sector, _HERRAMIENTAS_DEFAULT)

    # Fases
    fases = [
        {
            "mes": "Q1 (Meses 1-3)",
            "titulo": "Diagnóstico y Quick Wins",
            "descripcion": "Auditoría de procesos automatizables. Implantación de herramientas IA básicas: asistente de productividad, automatización de email y clasificación documental.",
            "impacto": f"Ahorro estimado {round(ahorro*0.15/1000,1)}k€ en tareas administrativas",
            "herramientas": [herramientas[0]["nombre"] if herramientas else "Microsoft Copilot", "Make"],
        },
        {
            "mes": "Q2 (Meses 4-6)",
            "titulo": "Automatización de Procesos Core",
            "descripcion": "Integración IA en CRM y facturación. Automatización de flujos repetitivos. Formación del equipo en herramientas seleccionadas.",
            "impacto": f"Reducción 20-25% del tiempo en procesos operativos · ~{round(ahorro*0.35/1000,1)}k€ acumulado",
            "herramientas": [herramientas[1]["nombre"] if len(herramientas) > 1 else "Make", "Power Automate"],
        },
        {
            "mes": "Q3 (Meses 7-9)",
            "titulo": "Análisis Predictivo",
            "descripcion": "Dashboards de inteligencia de negocio. Modelos predictivos de demanda y retención de clientes. Segmentación automática.",
            "impacto": f"Mejora 8-12% en conversión · {round(ingresos_extra*0.4/1000,1)}k€ ingresos adicionales estimados",
            "herramientas": ["Power BI AI", "Google Analytics AI"],
        },
        {
            "mes": "Q4 (Meses 10-12)",
            "titulo": "IA Estratégica y Optimización",
            "descripcion": "IA generativa para contenidos y propuestas comerciales. Pricing dinámico. Revisión de ROI y planificación del año 2.",
            "impacto": f"Incremento 5-8% ingresos · ROI acumulado año 1: {roi_pct:.0f}%",
            "herramientas": [herramientas[2]["nombre"] if len(herramientas) > 2 else "ChatGPT Ent.", "Perplexity Pro"],
        },
    ]

    conclusion = (
        f"La incorporación de IA en {d.get('empresa','la empresa')} tiene un ROI estimado del {roi_pct:.0f}% en 12 meses, "
        f"con un payback aproximado de {payback:.0f} meses. "
        f"La inversión recomendada de {inv:,.0f}€ genera un ahorro operativo de {ahorro:,.0f}€ anuales "
        f"y {ingresos_extra:,.0f}€ de ingresos adicionales. "
        f"{'La clave es comenzar por los quick wins del Q1 para demostrar valor rápido al equipo.' if tech < 6 else 'Con la base digital existente, el salto a IA avanzada puede ser más rápido.'}"
    ).replace(",", ".")

    return {
        "inversion_estimada": int(inv),
        "ahorro_anual": int(ahorro),
        "ingresos_extra": int(ingresos_extra),
        "roi_porcentaje": int(roi_pct),
        "payback_meses": round(payback, 1),
        "fases": fases,
        "procesos_ia": procesos_ia,
        "herramientas_recomendadas": herramientas,
        "conclusion": conclusion,
    }

def _procesos_ia_ranking(procesos, sector, tech):
    """Asigna tipo de IA y potencial de ahorro a los procesos declarados."""
    ia_map = {
        "facturación": ("OCR + automatización", "30-40%", "Baja", "Alto"),
        "contabilidad": ("RPA + IA financiera", "25-35%", "Media", "Alto"),
        "atención al cliente": ("Chatbot + NLP", "40-60%", "Baja", "Alto"),
        "soporte": ("Chatbot + base conocimiento", "35-50%", "Baja", "Alto"),
        "marketing": ("IA generativa + segmentación", "20-30%", "Baja", "Medio"),
        "rrhh": ("IA selección + onboarding", "25-35%", "Media", "Medio"),
        "logística": ("Optimización de rutas IA", "15-25%", "Alta", "Alto"),
        "producción": ("Mantenimiento predictivo IA", "20-30%", "Alta", "Alto"),
        "ventas": ("CRM IA + scoring leads", "20-30%", "Media", "Alto"),
        "gestión": ("Asistente IA + reporting auto", "25-35%", "Baja", "Medio"),
        "reportes": ("Generación automática informes", "40-60%", "Baja", "Medio"),
        "compras": ("IA negociación + predicción", "10-20%", "Media", "Medio"),
        "desarrollo": ("Copilot de código", "30-50%", "Baja", "Alto"),
        "calidad": ("Visión artificial + control", "20-35%", "Alta", "Alto"),
    }
    result = []
    for proc in (procesos[:5] if procesos else ["Gestión administrativa", "Atención al cliente", "Reporting"]):
        matched = None
        for k, v in ia_map.items():
            if k in proc.lower():
                matched = v
                break
        if not matched:
            matched = ("Automatización RPA + IA", "15-25%", "Media", "Medio")
        result.append({
            "proceso": proc,
            "tipo_ia": matched[0],
            "ahorro_potencial": matched[1],
            "dificultad": matched[2],
            "impacto": matched[3],
        })
    return result


# ── ALERTAS & QUICK WINS ──────────────────────────────────────────────────────

def _alertas(d, r, fin, dig, comp, crec, n_comp, fac, cos, *args):
    alerts = []
    if cos > fac * 0.85:
        alerts.append(f"⚠️ Estructura de costes muy elevada ({round(cos/max(fac,1)*100,0):.0f}% de la facturación) — revisar eficiencia operativa con urgencia")
    if dig < 4:
        alerts.append(f"⚠️ Madurez digital muy baja — el sector avanza hacia la digitalización y el gap con competidores crece")
    if n_comp > 10:
        alerts.append(f"⚠️ Alta fragmentación del mercado con {n_comp} competidores — diferenciación es crítica para no competir solo por precio")
    if crec < 0:
        alerts.append("⚠️ Crecimiento negativo — revisar causas estructurales vs coyunturales con plan de acción a 90 días")
    if fin < 4:
        alerts.append("⚠️ Salud financiera débil — priorizar la mejora de márgenes antes de acometer nuevas inversiones")
    if not alerts:
        alerts.append("✅ No se detectan alertas críticas — empresa en posición estable para acometer inversiones estratégicas")
    return alerts[:3]

def _quick_wins(d, r, tech, procesos, sector):
    wins = []
    if tech < 6:
        wins.append("🚀 Implementar Microsoft Copilot o similar: ahorro inmediato de 1-2h/empleado/día en tareas administrativas")
    if procesos:
        wins.append(f"🚀 Automatizar '{procesos[0]}' con RPA: proceso identificado como de alto potencial de ahorro")
    wins.append("🚀 Solicitar Kit Digital (hasta 12.000€ subvencionados para digitalización de PYMEs en España)")
    wins.append(f"🚀 Revisar estructura de costes con IA: identificar el 10-15% de gastos optimizables en {sector}")
    return wins[:3]


# ── EXECUTIVE SUMMARY ─────────────────────────────────────────────────────────

def _executive_summary(d, r, empresa, sector, provincia, pais, fac, cos, crec):
    score = r.score_global
    margen = r.margen_operativo
    bcg_pos = r.bcg.get("posicion","Interrogante")
    porter_score = r.porter_score_global

    estado_financiero = "con márgenes sólidos" if margen > 15 else "con presión en márgenes que requiere atención" if margen > 0 else "con pérdidas operativas que deben corregirse"
    estado_competitivo = "en un entorno muy competitivo" if porter_score >= 7 else "en un mercado con intensidad competitiva moderada" if porter_score >= 5 else "en un entorno competitivo favorable"

    return (
        f"{empresa} es una empresa del sector {sector} ubicada en {provincia} ({pais}), "
        f"con {d.get('empleados',0)} empleados y una facturación de {fac:,.0f}€, {estado_financiero}. "
        f"Opera {estado_competitivo} (score Porter {porter_score}/10) y ocupa la posición '{bcg_pos}' "
        f"en la Matriz BCG, con un potencial de IA del {round(r.potencial_ia,0):.0f}/100. "
        f"El score global de la empresa es {score}/100, "
        f"{'con claras oportunidades de mejora en digitalización y eficiencia operativa' if score < 65 else 'con una base sólida para acometer una estrategia de crecimiento y transformación digital'}."
    ).replace(",", ".")


# ── HELPER PARA ROI ───────────────────────────────────────────────────────────

def _crec_potencial_proxy_method(self):
    for dim in self.dimensiones:
        if dim["nombre"] == "Crecimiento Potencial":
            return dim["score"] / 10
    return 0.5

AnalysisResult.crec_potencial_proxy = _crec_potencial_proxy_method

# ═══════════════════════════════════════════════════════════════
# APP STREAMLIT
# ═══════════════════════════════════════════════════════════════

import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="BusinessIQ Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── ESTILOS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif !important; }
.kpi-card {
    background: #161d2e; border: 1px solid #1e2d45;
    border-radius: 14px; padding: 18px 16px; text-align: center; margin-bottom: 8px;
}
.kpi-val { font-size: 26px; font-weight: 800; }
.kpi-lbl { font-size: 11px; color: #64748b; margin-top: 4px; }
.sec-hdr {
    background: linear-gradient(135deg,#161d2e,#0d1526);
    border-left: 4px solid #00d4ff; border-radius: 0 10px 10px 0;
    padding: 10px 18px; margin: 20px 0 12px;
    font-weight: 700; font-size: 15px; color: #e2e8f0;
}
.tag  { display:inline-block; background:#00d4ff22; color:#00d4ff; border:1px solid #00d4ff44; border-radius:20px; padding:2px 10px; font-size:11px; font-weight:600; margin:2px; }
.tg   { background:#10b98122; color:#10b981; border-color:#10b98144; }
.tr   { background:#ef444422; color:#ef4444; border-color:#ef444444; }
.tw   { background:#f59e0b22; color:#f59e0b; border-color:#f59e0b44; }
.tp   { background:#7c3aed22; color:#7c3aed; border-color:#7c3aed44; }
.alert  { background:#ef444415; border:1px solid #ef444444; border-radius:10px; padding:12px 16px; margin-bottom:8px; font-size:13px; color:#fca5a5; }
.ok     { background:#10b98115; border:1px solid #10b98144; border-radius:10px; padding:12px 16px; margin-bottom:8px; font-size:13px; color:#6ee7b7; }
.dafo-item { border-left:3px solid; border-radius:0 8px 8px 0; padding:8px 12px; margin-bottom:6px; font-size:12px; color:#e2e8f0; }
</style>
""", unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────────────────────

def kpi(val, lbl, color="#00d4ff"):
    st.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:{color}">{val}</div><div class="kpi-lbl">{lbl}</div></div>', unsafe_allow_html=True)

def sec(titulo):
    st.markdown(f'<div class="sec-hdr">{titulo}</div>', unsafe_allow_html=True)

def bar(label, score, max_val=10, color="#00d4ff"):
    pct = int(min(max(float(score) / float(max_val), 0), 1) * 100)
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px">
      <span style="color:#94a3b8">{label}</span>
      <span style="color:{color};font-size:12px">{float(score):.1f}/{max_val}</span>
    </div>
    <div style="height:6px;background:#111827;border-radius:3px;margin-bottom:10px;overflow:hidden">
      <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,{color}88,{color});border-radius:3px"></div>
    </div>""", unsafe_allow_html=True)

def nivel_color(n):
    return {"Alto": "#ef4444", "Medio": "#f59e0b", "Bajo": "#10b981"}.get(n, "#64748b")

def impacto_color(i):
    return {"Positivo": "#10b981", "Negativo": "#ef4444", "Neutro": "#64748b"}.get(i, "#64748b")

def fmt_eur(v):
    return f"{int(v):,}€".replace(",", ".")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ BusinessIQ")
    st.caption("Análisis estratégico · Sin coste · Sin APIs")
    st.markdown("---")

    st.markdown("### 🏢 Empresa")
    empresa        = st.text_input("Nombre", placeholder="Ej. Acme Solutions S.L.")
    sector         = st.selectbox("Sector", SECTORES)
    subsector      = st.text_input("Sub-sector", placeholder="Ej. SaaS B2B")
    pais           = st.selectbox("País", PAISES)
    provincia      = (st.selectbox("Provincia", PROVINCIAS)
                      if pais == "España"
                      else st.text_input("Región / Estado"))
    modelo_negocio = st.selectbox("Modelo de negocio",
        ["B2B — Empresas", "B2C — Consumidor final", "B2B2C — Mixto",
         "Marketplace / Plataforma", "SaaS / Suscripción"])
    mercado = st.selectbox("Alcance de mercado",
        ["Local / Comarcal", "Regional / Autonómico", "Nacional", "Europeo", "Global"])
    años   = st.number_input("Años de actividad", 0, 200, 5)
    desc   = st.text_area("Descripción breve", placeholder="Qué hace, producto/servicio...", height=75)

    st.markdown("---")
    st.markdown("### 👥 Equipo")
    empleados    = st.number_input("Nº empleados/as", 1, 100000, 20)
    clientes     = st.number_input("Nº clientes activos", 0, 1000000, 50)
    competidores = st.number_input("Nº competidores directos", 0, 500, 5)
    nivel_tech   = st.select_slider("Nivel tecnológico",
        options=["Muy bajo","Bajo","Medio","Alto","Avanzado"], value="Medio")

    with st.expander("📊 Distribución por edad (%)"):
        c1, c2 = st.columns(2)
        e1825 = c1.number_input("18-25", 0, 100, 10, key="e1")
        e2635 = c2.number_input("26-35", 0, 100, 30, key="e2")
        e3645 = c1.number_input("36-45", 0, 100, 30, key="e3")
        e4655 = c2.number_input("46-55", 0, 100, 20, key="e4")
        e55p  = c1.number_input("55+",   0, 100, 10, key="e5")

    with st.expander("👔 Perfiles profesionales (%)"):
        p_dir = st.number_input("Directivos",    0, 100, 10, key="p1")
        p_mm  = st.number_input("Mando medio",   0, 100, 20, key="p2")
        p_tec = st.number_input("Técnicos",      0, 100, 30, key="p3")
        p_adm = st.number_input("Admin/Soporte", 0, 100, 20, key="p4")
        p_op  = st.number_input("Operativos",    0, 100, 20, key="p5")

    st.markdown("---")
    st.markdown("### ⚙️ Procesos clave")
    sugs = SUGERENCIAS_SECTOR.get(sector, ["Gestión administrativa", "Contabilidad", "Atención al cliente"])
    procs_sel   = st.multiselect("Sugerencias del sector", sugs)
    proc_libre  = st.text_input("Proceso adicional")
    if "extra" not in st.session_state:
        st.session_state.extra = []
    if proc_libre and st.button("➕ Añadir"):
        if proc_libre not in st.session_state.extra:
            st.session_state.extra.append(proc_libre)
    if st.session_state.extra:
        st.caption(", ".join(st.session_state.extra))
        if st.button("🗑️ Limpiar"):
            st.session_state.extra = []
    procesos = procs_sel + st.session_state.extra

    st.markdown("---")
    st.markdown("### 💰 Datos financieros")
    facturacion  = st.number_input("Facturación anual (€)",      0, 10_000_000_000, 1_000_000, step=10_000)
    costes       = st.number_input("Costes totales anuales (€)",  0, 10_000_000_000, 700_000,   step=10_000)
    margen_bruto = st.number_input("Margen bruto (%)",            0.0, 100.0, 30.0)
    crecimiento  = st.number_input("Crecimiento YoY (%)",         -100.0, 500.0, 8.0)

    st.markdown("---")
    analizar_btn = st.button("⚡ GENERAR ANÁLISIS", use_container_width=True, type="primary")

# ── PÁGINA PRINCIPAL ──────────────────────────────────────────────────────────
st.markdown("# ⚡ BusinessIQ Analyzer")
st.markdown("**Análisis estratégico empresarial** · Porter · PESTEL · BCG · DAFO · Macro · ROI IA · **100% gratuito**")
st.markdown("---")

if not analizar_btn:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**🔍 Análisis Estratégico**\n- ⚔️ 5 Fuerzas de Porter\n- 🌍 PESTEL completo\n- 📦 Matriz BCG\n- 🔍 DAFO + Estrategias cruzadas")
    with c2:
        st.markdown("**📈 Contexto de Mercado**\n- Indicadores macro regionales\n- Previsión sectorial 12 meses\n- Score competitivo\n- Alertas estratégicas")
    with c3:
        st.markdown("**🤖 ROI Inteligencia Artificial**\n- Inversión y ahorro estimados\n- Plan Q1–Q4\n- Procesos con mayor potencial\n- Herramientas recomendadas")
    st.info("👈 Rellena el formulario lateral y pulsa **⚡ GENERAR ANÁLISIS** — sin APIs, sin registro, sin coste.")
    st.stop()

if not empresa:
    st.error("⚠️ El nombre de la empresa es obligatorio.")
    st.stop()

# ── EJECUTAR ANÁLISIS ─────────────────────────────────────────────────────────
datos = dict(
    empresa=empresa, sector=sector, subsector=subsector,
    pais=pais, provincia=provincia, modelo=modelo_negocio,
    mercado=mercado, años=años, descripcion=desc,
    empleados=empleados, clientes=clientes, competidores=competidores,
    nivel_tech=nivel_tech, facturacion=facturacion, costes=costes,
    margen=margen_bruto, crecimiento=crecimiento,
    e1825=e1825, e2635=e2635, e3645=e3645, e4655=e4655, e55p=e55p,
    p_dir=p_dir, p_mm=p_mm, p_tec=p_tec, p_adm=p_adm, p_op=p_op,
    procesos=procesos,
)

with st.spinner("⚡ Calculando análisis estratégico..."):
    r = analizar(datos)

# ── TABS ──────────────────────────────────────────────────────────────────────
t1, t2, t3, t4, t5, t6, t7 = st.tabs([
    "📊 Resumen", "⚔️ Porter", "🌍 PESTEL",
    "📦 BCG", "🔍 DAFO", "📈 Macro", "🤖 ROI IA"
])

# ── TAB 1: RESUMEN ────────────────────────────────────────────────────────────
with t1:
    sec("📊 Executive Summary")
    st.info(r.executive_summary)

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi(f"{r.score_global}/100",    "Score Global",           "#00d4ff")
    with c2: kpi(f"{r.competitividad}/100",  "Competitividad",         "#10b981")
    with c3: kpi(f"{r.potencial_ia:.0f}/100","Potencial IA",           "#7c3aed")
    with c4: kpi(f"{r.rentabilidad_esperada_pct:.1f}%","Rentabilidad Esperada","#f59e0b")

    st.markdown("")
    sec("🎯 Dimensiones Estratégicas")
    c_left, c_right = st.columns(2)
    for i, dim in enumerate(r.dimensiones):
        s = dim["score"]
        col = "#10b981" if s >= 7 else "#00d4ff" if s >= 5 else "#f59e0b"
        with (c_left if i % 2 == 0 else c_right):
            bar(dim["nombre"], s, color=col)

    sec("💰 Métricas Financieras")
    c1, c2, c3, c4 = st.columns(4)
    ben_col = "#10b981" if r.beneficio_bruto >= 0 else "#ef4444"
    with c1: kpi(fmt_eur(r.beneficio_bruto),     "Beneficio Bruto",    ben_col)
    with c2: kpi(f"{r.margen_operativo:.1f}%",   "Margen Operativo",   "#00d4ff")
    with c3: kpi(fmt_eur(r.revenue_empleado),    "Revenue/Empleado",   "#7c3aed")
    with c4: kpi(fmt_eur(r.coste_empleado),      "Coste/Empleado",     "#f59e0b")

    c_left, c_right = st.columns(2)
    with c_left:
        sec("⚠️ Alertas Estratégicas")
        for a in r.alertas:
            st.markdown(f'<div class="alert">{a}</div>', unsafe_allow_html=True)
    with c_right:
        sec("✅ Quick Wins")
        for o in r.oportunidades_rapidas:
            st.markdown(f'<div class="ok">{o}</div>', unsafe_allow_html=True)

# ── TAB 2: PORTER ─────────────────────────────────────────────────────────────
with t2:
    sec("⚔️ Las 5 Fuerzas de Porter")
    st.markdown(f"**Score global de intensidad competitiva:** `{r.porter_score_global:.1f}/10`")
    for f in r.porter:
        nc = nivel_color(f["nivel"])
        with st.expander(f"**{f['nombre']}** — {f['nivel']} · {f['score']:.1f}/10"):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**Análisis:** {f['descripcion']}")
                st.markdown(f"**→ Recomendación:** *{f['recomendacion']}*")
            with c2:
                bar("Intensidad", f["score"], color=nc)
    st.markdown("---")
    st.markdown(f"**Conclusión Porter:** {r.porter_conclusion}")

# ── TAB 3: PESTEL ─────────────────────────────────────────────────────────────
with t3:
    sec("🌍 Análisis PESTEL")
    items = r.pestel
    for i in range(0, len(items), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(items):
                item = items[i + j]
                ic = impacto_color(item["impacto"])
                with col:
                    with st.expander(f"**{item['dimension']}** — {item['impacto']}"):
                        st.markdown(f"**Descripción:** {item['descripcion']}")
                        st.markdown(f"**Factor clave:** `{item['factor_clave']}`")
                        st.markdown(f"**Tendencia:** {item['tendencia']}")
                        bar("Impacto positivo", item["score"], color=ic)

# ── TAB 4: BCG ────────────────────────────────────────────────────────────────
with t4:
    bcg = r.bcg
    sec("📦 Matriz BCG")
    pos = bcg["posicion"]
    emoji_map  = {"Estrella": "⭐", "Vaca Lechera": "🐄", "Interrogante": "❓", "Perro": "🐕"}
    color_map  = {"Estrella": "#f59e0b", "Vaca Lechera": "#10b981", "Interrogante": "#00d4ff", "Perro": "#ef4444"}
    em = emoji_map.get(pos, "❓"); col = color_map.get(pos, "#00d4ff")

    c1, c2 = st.columns([1, 2])
    with c1:
        kpi(f"{em} {pos}", "Posición BCG", col)
        st.markdown("")
        bar("Crecimiento de mercado", bcg["crecimiento_mercado"], 100, "#00d4ff")
        bar("Cuota relativa estimada", bcg["cuota_relativa"], 100, col)
    with c2:
        st.markdown(f"**Descripción:** {bcg['descripcion']}")
        st.markdown(f"**Estrategia recomendada:** {bcg['estrategia']}")
        st.markdown("""
        <div style="background:#111827;border-radius:12px;padding:14px;margin-top:12px">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;max-width:280px">
            <div style="background:#f59e0b22;border:1px solid #f59e0b44;border-radius:6px;padding:10px;text-align:center;font-size:12px">⭐ Estrella<br><small style="color:#64748b">Alta cuota · Alto crec.</small></div>
            <div style="background:#ef444422;border:1px solid #ef444444;border-radius:6px;padding:10px;text-align:center;font-size:12px">❓ Interrogante<br><small style="color:#64748b">Baja cuota · Alto crec.</small></div>
            <div style="background:#10b98122;border:1px solid #10b98144;border-radius:6px;padding:10px;text-align:center;font-size:12px">🐄 Vaca Lechera<br><small style="color:#64748b">Alta cuota · Bajo crec.</small></div>
            <div style="background:#ef444411;border:1px solid #ef444433;border-radius:6px;padding:10px;text-align:center;font-size:12px">🐕 Perro<br><small style="color:#64748b">Baja cuota · Bajo crec.</small></div>
        </div></div>""", unsafe_allow_html=True)

# ── TAB 5: DAFO ───────────────────────────────────────────────────────────────
with t5:
    dafo = r.dafo
    sec("🔍 Análisis DAFO")
    items_cfg = [
        ("fortalezas",    "💪 FORTALEZAS",    "#10b981"),
        ("debilidades",   "⚠️ DEBILIDADES",   "#ef4444"),
        ("oportunidades", "🚀 OPORTUNIDADES", "#00d4ff"),
        ("amenazas",      "🔥 AMENAZAS",      "#f59e0b"),
    ]
    ca, cb = st.columns(2)
    cols4 = [ca, cb, ca, cb]
    for (key, title, color), col in zip(items_cfg, cols4):
        with col:
            st.markdown(f"<div style='color:{color};font-weight:700;font-size:13px;margin:14px 0 8px'>{title}</div>", unsafe_allow_html=True)
            for item in dafo.get(key, []):
                st.markdown(f"<div class='dafo-item' style='background:{color}12;border-color:{color}'>▸ {item}</div>", unsafe_allow_html=True)

    est = r.dafo_estrategias
    if est:
        st.markdown("")
        sec("🧭 Estrategias Cruzadas DAFO")
        ca, cb = st.columns(2)
        with ca:
            st.markdown(f"**FO — Explotar (Fortalezas + Oportunidades):**\n\n{est.get('FO','')}")
            st.markdown(f"\n**DO — Reorientar (Debilidades + Oportunidades):**\n\n{est.get('DO','')}")
        with cb:
            st.markdown(f"**FA — Defender (Fortalezas + Amenazas):**\n\n{est.get('FA','')}")
            st.markdown(f"\n**DA — Sobrevivir (Debilidades + Amenazas):**\n\n{est.get('DA','')}")

# ── TAB 6: MACRO ──────────────────────────────────────────────────────────────
with t6:
    macro = r.macro
    sec(f"📈 Previsión Macroeconómica — {provincia}, {pais}")

    inds = macro.get("indicadores", [])
    if inds:
        cols = st.columns(len(inds))
        for col, ind in zip(cols, inds):
            col_ind = "#10b981" if ind["positivo"] else "#f59e0b"
            with col:
                kpi(f"{ind['tendencia']} {ind['valor']}", ind["nombre"], col_ind)

    st.markdown("")
    ca, cb = st.columns(2)
    with ca:
        sec("🏙️ Contexto Regional")
        st.markdown(macro.get("contexto_regional",""))
        st.markdown("")
        sec("📅 Perspectiva 12 meses")
        st.markdown(macro.get("perspectiva_12m",""))
    with cb:
        sec("✅ Oportunidades del Entorno")
        for o in macro.get("oportunidades", []):
            st.markdown(f'<div class="ok">✓ {o}</div>', unsafe_allow_html=True)
        sec("⚠️ Riesgos Macro")
        for risk in macro.get("riesgos", []):
            st.markdown(f'<div class="alert">! {risk}</div>', unsafe_allow_html=True)

# ── TAB 7: ROI IA ─────────────────────────────────────────────────────────────
with t7:
    roi = r.roi_ia
    sec("🤖 ROI de Incorporar Inteligencia Artificial — 12 meses")

    inv  = roi["inversion_estimada"]
    aho  = roi["ahorro_anual"]
    ing  = roi["ingresos_extra"]
    rpct = roi["roi_porcentaje"]
    pay  = roi["payback_meses"]

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi(fmt_eur(inv),          "Inversión estimada",  "#f59e0b")
    with c2: kpi(fmt_eur(aho),          "Ahorro anual",        "#10b981")
    with c3: kpi(f"+{fmt_eur(ing)}",    "Ingresos extra",      "#10b981")
    with c4: kpi(f"{rpct:.0f}%", "ROI año 1", "#00d4ff" if rpct >= 0 else "#ef4444")

    st.markdown(f"⏱️ **Payback estimado:** `{pay} meses`")

    sec("📅 Plan de Implementación Trimestral")
    for fase in roi.get("fases", []):
        with st.expander(f"**{fase['mes']}** — {fase['titulo']}"):
            ca, cb = st.columns([3, 1])
            with ca:
                st.markdown(f"**Descripción:** {fase['descripcion']}")
                st.markdown(f"**💰 Impacto:** {fase['impacto']}")
            with cb:
                herr = fase.get("herramientas", [])
                if herr:
                    st.markdown("**Herramientas:**")
                    for h in herr:
                        st.markdown(f"<span class='tag'>{h}</span>", unsafe_allow_html=True)

    sec("⚙️ Procesos con Mayor Potencial IA")
    procs_ia = roi.get("procesos_ia", [])
    if procs_ia:
        hdr = st.columns([3, 2, 1, 1, 1])
        for col, lbl in zip(hdr, ["Proceso", "Tipo IA", "Ahorro", "Dificultad", "Impacto"]):
            col.markdown(f"<span style='font-size:11px;color:#64748b;font-weight:600'>{lbl}</span>", unsafe_allow_html=True)
        dc = {"Baja": "#10b981", "Media": "#f59e0b", "Alta": "#ef4444"}
        ic2= {"Alto": "#10b981", "Medio": "#00d4ff", "Bajo": "#64748b"}
        for p in procs_ia:
            row = st.columns([3, 2, 1, 1, 1])
            row[0].markdown(f"<span style='font-size:13px'>{p['proceso']}</span>", unsafe_allow_html=True)
            row[1].markdown(f"<span style='font-size:12px;color:#94a3b8'>{p['tipo_ia']}</span>", unsafe_allow_html=True)
            row[2].markdown(f"<span class='tag tg'>{p['ahorro_potencial']}</span>", unsafe_allow_html=True)
            dif = p.get("dificultad","Media")
            row[3].markdown(f"<span style='color:{dc.get(dif,'#64748b')};font-size:12px'>{dif}</span>", unsafe_allow_html=True)
            imp = p.get("impacto","Medio")
            row[4].markdown(f"<span style='color:{ic2.get(imp,'#64748b')};font-size:12px'>{imp}</span>", unsafe_allow_html=True)

    sec("🛠️ Herramientas IA Recomendadas")
    herrs = roi.get("herramientas_recomendadas", [])
    if herrs:
        h_cols = st.columns(len(herrs))
        for col, h in zip(h_cols, herrs):
            with col:
                st.markdown(f"""<div class='kpi-card' style='text-align:left'>
                  <div style='font-weight:700;font-size:14px;color:#e2e8f0'>{h['nombre']}</div>
                  <div style='margin:4px 0'>
                    <span class='tag tp'>{h['categoria']}</span>
                    <span class='tag'>{h['coste_mes']}</span>
                  </div>
                  <div style='font-size:12px;color:#94a3b8;margin-top:6px'>{h['uso']}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("")
    sec("✅ Conclusión y Recomendación Final")
    st.success(roi["conclusion"])

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;color:#64748b;font-size:11px'>"
    f"BusinessIQ Analyzer · {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
    f"Análisis para <b style='color:#00d4ff'>{empresa}</b> · "
    f"<span style='color:#10b981'>100% gratuito · Sin APIs · Sin coste</span>"
    f"</div>",
    unsafe_allow_html=True,
)
