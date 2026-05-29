# ⚡ BusinessIQ Analyzer

**Análisis estratégico empresarial completo — 100% gratuito, sin APIs, sin coste.**

Todo el análisis se calcula en Python puro a partir de los datos que introduce el usuario.
No requiere API Key, no consume créditos, funciona offline.

---

## Qué genera

| Módulo | Contenido |
|--------|-----------|
| 📊 Resumen | Score global, KPIs financieros, alertas, quick wins |
| ⚔️ Porter | 5 Fuerzas con scores, descripciones y recomendaciones |
| 🌍 PESTEL | 6 dimensiones con impacto, factor clave y tendencia |
| 📦 BCG | Posición (Estrella/Vaca/Interrogante/Perro) + estrategia |
| 🔍 DAFO | Fortalezas, Debilidades, Oportunidades, Amenazas + estrategias cruzadas FO/FA/DO/DA |
| 📈 Macro | Indicadores económicos regionales + previsión 12 meses |
| 🤖 ROI IA | Inversión, ahorro, ingresos extra, plan Q1–Q4, herramientas recomendadas |

---

## 🚀 Despliegue en Streamlit Cloud (gratis)

1. Sube este repositorio a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Selecciona el repo y `app.py` como entry point
4. Pulsa **Deploy** — listo en 2 minutos

---

## 💻 Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📁 Estructura

```
businessiq/
├── app.py              # Interfaz Streamlit
├── engine.py           # Motor de análisis (lógica Python pura)
├── requirements.txt    # Solo: streamlit>=1.35.0
├── .streamlit/
│   └── config.toml     # Tema oscuro
└── README.md
```

---

## 🔧 Cómo funciona el motor

`engine.py` contiene:
- **Tablas sectoriales** con parámetros de Porter y metadatos de mercado para 14 sectores
- **Indicadores macro** para 30 provincias españolas y 8 países
- **Fórmulas de scoring** para las 5 dimensiones estratégicas
- **Lógica BCG** basada en cuota relativa estimada y crecimiento de mercado
- **Generación de DAFO** contextual según los datos de la empresa
- **Cálculo de ROI IA** escalado a la facturación y nivel tecnológico

*Sin dependencias externas. Sin llamadas a internet. Resultados instantáneos.*
