import sys
import os
import requests
import pandas as pd
from loguru import logger
# from test_dbt_ducklake.ducklake import setup_ducklake

# Adds the directory one level up to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))




WB_API = "https://api.worldbank.org/v2"

# ---------------------------------------------------------------------------
# World Bank Doing Business (source=1, discontinued 2021)
# Covers: startup registration burden, contract enforcement, insolvency
# ---------------------------------------------------------------------------
DOING_BUSINESS_INDICATORS = {
    # Overall
    "IC.BUS.EASE.XQ":              "ease_of_doing_business_rank",
    "IC.BUS.EASE.DFRN.XQ.DB1719": "ease_of_doing_business_score",
    # Starting a business
    "IC.REG.PROC.MA.NO":           "start_biz_procedures_men",
    "IC.REG.PROC.FE.NO":           "start_biz_procedures_women",
    "IC.REG.DURS.MA.DY":           "start_biz_time_days_men",
    "IC.REG.DURS.FE.DY":           "start_biz_time_days_women",
    "IC.REG.MIN.CAP":              "start_biz_min_capital_pct_income",
    "IC.REG.STRT.BUS.RK.DB19":    "start_biz_rank",
    # Enforcing contracts
    "ENF.CONT.DURS.DY":            "enforce_contract_time_days",
    "ENF.CONT.COEN.COST.ZS":       "enforce_contract_cost_pct_claim",
    "ENF.CONT.COEN.PROC.NO":       "enforce_contract_procedures",
    # Resolving insolvency
    "RESLV.ISV.DURS.YR":           "insolvency_time_years",
    "RESLV.ISV.COST.ZS":           "insolvency_cost_pct_estate",
    "RESLV.ISV.RCOV.RT":           "insolvency_recovery_rate_cents_per_dollar",
    "RESLV.ISV.RK.DB19":           "insolvency_rank",
}

# ---------------------------------------------------------------------------
# World Bank Enterprise Surveys (source=13)
# Covers: ownership structure, corruption, financing, licensing, workforce
# ---------------------------------------------------------------------------
ENTERPRISE_SURVEY_INDICATORS = {
    # Ownership
    "IC.FRM.FCHAR.CAR2":   "pct_private_domestic_ownership",
    "IC.FRM.FCHAR.CAR7":   "pct_firms_foreign_ownership_10pct",
    "IC.FRM.FCHAR.CAR8":   "pct_firms_govt_ownership_10pct",
    "IC.FRM.GEN.GEND1":    "pct_firms_female_ownership",
    "IC.FRM.GEN.GEND4":    "pct_firms_female_top_manager",
    "IC.FRM.GEN.GEND6":    "pct_firms_majority_female_ownership",
    # Legal / corruption
    "IC.FRM.BRIB.GRAFT2":  "bribery_depth_pct",
    "IC.FRM.BRIB.GRAFT3":  "bribery_incidence_pct",
    "IC.FRM.CORR.CORR11":  "pct_firms_corruption_major_constraint",
    "IC.FRM.CORR.CORR10":  "pct_firms_gifts_for_operating_license",
    "IC.FRM.CORR.CRIME9":  "pct_firms_courts_major_constraint",
    "IC.FRM.OBS.OBST4":    "pct_firms_corruption_biggest_obstacle",
    # Business implementation / licensing
    "IC.FRM.REG.BUS2":     "days_to_obtain_operating_license",
    "IC.FRM.REG.BUS3":     "days_to_obtain_construction_permit",
    "IC.FRM.REG.BUS1":     "days_to_obtain_import_license",
    "IC.FRM.OBS.OBST3":    "pct_firms_licensing_biggest_obstacle",
    # Financing
    "IC.FRM.FIN.FIN14":    "pct_firms_with_bank_loan",
    "IC.FRM.FIN.FIN16":    "pct_firms_access_finance_major_constraint",
    "IC.FRM.FIN.FIN12":    "pct_firms_using_banks_for_investment",
    # Workforce
    "IC.FRM.WRKF.WK1":     "pct_firms_offering_formal_training",
    "IC.FRM.WRKF.WK8":     "top_manager_experience_years",
}

# ---------------------------------------------------------------------------
# World Bank Worldwide Governance Indicators (source=3)
# Covers: regulatory quality, rule of law, corruption control
# ---------------------------------------------------------------------------
GOVERNANCE_INDICATORS = {
    "GOV_WGI_RQ.EST": "regulatory_quality_estimate",
    "GOV_WGI_RL.EST": "rule_of_law_estimate",
    "GOV_WGI_CC.EST": "control_of_corruption_estimate",
    "GOV_WGI_GE.EST": "govt_effectiveness_estimate",
    "GOV_WGI_PV.EST": "political_stability_estimate",
    "GOV_WGI_VA.EST": "voice_accountability_estimate",
    "GOV_WGI_RQ.SC":  "regulatory_quality_score",
    "GOV_WGI_RL.SC":  "rule_of_law_score",
    "GOV_WGI_CC.SC":  "control_of_corruption_score",
}


def _fetch_wb_indicator(indicator_id, source=None, mrv=1):
    """Fetch all country data for a single World Bank indicator."""
    params = {"format": "json", "per_page": 500, "mrv": mrv}
    if source:
        params["source"] = source
    url = f"{WB_API}/country/all/indicator/{indicator_id}"
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
            return []
        return payload[1]
    except Exception as exc:
        logger.error(f"Failed to fetch {indicator_id}: {exc}")
        return []


def _wb_records_to_df(records, value_col):
    """Normalise raw World Bank API records into a flat DataFrame."""
    rows = []
    for r in records:
        if r.get("value") is None:
            continue
        rows.append({
            "country_iso3": r.get("countryiso3code", ""),
            "country_name": r.get("country", {}).get("value", ""),
            "year": int(r.get("date", 0)),
            value_col: r.get("value"),
        })
    return pd.DataFrame(rows)


def _pivot_to_wide(indicator_map, fetch_kwargs):
    """
    Fetch each indicator, keep the most recent non-null value per country,
    then pivot into a single wide DataFrame indexed by country.
    """
    frames = []
    for indicator_id, col_name in indicator_map.items():
        records = _fetch_wb_indicator(indicator_id, **fetch_kwargs)
        df = _wb_records_to_df(records, col_name)
        if df.empty:
            logger.warning(f"  No data: {indicator_id} ({col_name})")
            continue
        df = (
            df.sort_values("year", ascending=False)
              .drop_duplicates(subset=["country_iso3"])
            [["country_iso3", "country_name", "year", col_name]]
        )
        frames.append(
            df.set_index(["country_iso3", "country_name"])
              .rename(columns={"year": f"year_{col_name}"})
        )
        logger.info(f"  {col_name}: {len(df)} countries")

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, axis=1).reset_index()


def ingest_wb_countries(con):
    """Country reference table: ISO codes, region, income level, coordinates."""
    logger.info("Fetching World Bank country metadata ...")
    resp = requests.get(
        f"{WB_API}/country",
        params={"format": "json", "per_page": 500},
        timeout=30,
    )
    resp.raise_for_status()
    raw = resp.json()[1]

    rows = []
    for c in raw:
        rows.append({
            "iso2_code":    c.get("iso2Code", ""),
            "iso3_code":    c.get("id", ""),
            "country_name": c.get("name", ""),
            "region":       c.get("region", {}).get("value", ""),
            "income_level": c.get("incomeLevel", {}).get("value", ""),
            "lending_type": c.get("lendingType", {}).get("value", ""),
            "capital_city": c.get("capitalCity", ""),
            "longitude":    float(c["longitude"]) if c.get("longitude") else None,
            "latitude":     float(c["latitude"])  if c.get("latitude")  else None,
        })

    df = pd.DataFrame(rows)
    con.execute("DROP TABLE IF EXISTS raw_wb_countries")
    con.execute("CREATE TABLE raw_wb_countries AS SELECT * FROM df")
    logger.info(f"  -> raw_wb_countries: {len(df)} rows")


def ingest_doing_business(con):
    """
    World Bank Doing Business (discontinued 2021).
    Startup registration burden, contract enforcement, insolvency resolution.
    One row per country, most recent value per indicator.
    """
    logger.info("Fetching Doing Business indicators ...")
    wide = _pivot_to_wide(DOING_BUSINESS_INDICATORS, {"source": 1, "mrv": 5})
    if wide.empty:
        logger.error("No Doing Business data retrieved.")
        return
    con.execute("DROP TABLE IF EXISTS raw_doing_business")
    con.execute("CREATE TABLE raw_doing_business AS SELECT * FROM wide")
    logger.info(f"  -> raw_doing_business: {len(wide)} rows, {len(wide.columns)} columns")


def ingest_enterprise_surveys(con):
    """
    World Bank Enterprise Surveys.
    Ownership structure, corruption burden, licensing, financing, workforce.
    One row per country, most recent survey value per indicator.
    """
    logger.info("Fetching Enterprise Survey indicators ...")
    wide = _pivot_to_wide(ENTERPRISE_SURVEY_INDICATORS, {"source": 13, "mrv": 10})
    if wide.empty:
        logger.error("No Enterprise Survey data retrieved.")
        return
    con.execute("DROP TABLE IF EXISTS raw_enterprise_surveys")
    con.execute("CREATE TABLE raw_enterprise_surveys AS SELECT * FROM wide")
    logger.info(f"  -> raw_enterprise_surveys: {len(wide)} rows, {len(wide.columns)} columns")


def ingest_governance_indicators(con):
    """
    World Bank Worldwide Governance Indicators (source=3).
    Regulatory quality, rule of law, corruption control — scored -2.5 to +2.5.
    One row per country, most recent year.
    """
    logger.info("Fetching Worldwide Governance Indicators ...")
    wide = _pivot_to_wide(GOVERNANCE_INDICATORS, {"source": 3, "mrv": 3})
    if wide.empty:
        logger.error("No Governance Indicator data retrieved.")
        return
    con.execute("DROP TABLE IF EXISTS raw_governance_indicators")
    con.execute("CREATE TABLE raw_governance_indicators AS SELECT * FROM wide")
    logger.info(f"  -> raw_governance_indicators: {len(wide)} rows, {len(wide.columns)} columns")


def ingest_from_api(path=None):
    """Fetch all sources and load into DuckLake."""
    from ducklake import setup_ducklake

    con = setup_ducklake()
    
    ingest_wb_countries(con)
    ingest_doing_business(con)
    ingest_enterprise_surveys(con)
    ingest_governance_indicators(con)

    tables = con.execute("SHOW TABLES").fetchall()
    logger.info("Ingestion complete. Tables in datalake:")
    for (t,) in tables:
        count = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        logger.info(f"  {t}: {count} rows")

    con.close()

    # # Generate TPC-H data in memory, then copy to Ducklake
    # conn.execute("USE memory;")
    # conn.execute("CALL dbgen(sf = 0.1);")  # ~60K lineitem records

    # conn.execute("USE ducklake_catalog;")
    # conn.execute("CREATE TABLE lineitem AS SELECT * FROM memory.lineitem;")

    # conn.close()

if __name__ == "__main__":
    ingest_from_api()
