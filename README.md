# IFRC Community Trust Index — Data Pipeline

A Bronze/Silver/Gold Lakehouse data pipeline built for the IFRC Community Trust Index (CTI) consultancy brief.

## Architecture
- **Bronze**: Raw KoboToolbox survey ingestion (4,389 responses across 8 countries)
- **Silver**: Cleaned, standardised dimension and fact tables (52,668 trust score records)
- **Gold**: Analytics-ready mart tables powering real-time trust monitoring

## Stack
Python · PostgreSQL · dbt · Streamlit · Plotly · Star Schema · Medallion Architecture

## Files
- `generate_cti_data.py` — Data pipeline generating all Bronze/Silver/Gold datasets
- `cti_dashboard.py` — Streamlit dashboard for real-time trust monitoring
- `cti_data/` — Generated datasets across all pipeline layers

## Countries Covered
Kenya · Nigeria · Philippines · Colombia · Ukraine · Bangladesh · Ethiopia · Mexico

## Built by
Henrietta Atsenokhai | Data Engineer
henrietta-atsenokhai-fe22ba.webflow.io/data-engineer-portfolio/portfolio
