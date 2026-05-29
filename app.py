"""
BusinessIQ Analyzer — Análisis estratégico empresarial sin APIs externas.
100% gratuito · Funciona offline · Sin coste de uso.
"""
import streamlit as st
from datetime import datetime
from engine import analizar, SECTORES, PROVINCIAS, PAISES, MACRO_PAISES, SUGERENCIAS_SECTOR

# ── CONFIG ────────────────────────────────────────────────────────────────────
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
