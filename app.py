# app.py - Fintech tabs upgraded + TL;DR banners + World Bank/Findex search
import time, random, os
import streamlit as st
import pandas as pd
import numpy as np
import requests
from sklearn.ensemble import IsolationForest
import plotly.graph_objects as go

st.set_page_config(page_title="Cloud • Fintech • Security • Data Platforms", layout="wide")

# =========================
# Utilities (shared)
# =========================

def get_compliance_recommendations(model, data_sensitivity, compliance_reqs, industry):
    # ---- (your compliance logic unchanged) ----
    sensitivity_reqs = {
        "Public (marketing data)": {"encryption":"Standard TLS in transit","access_controls":"Basic IAM roles","data_residency":"Any region acceptable","audit_logging":"Basic access logs","backup_retention":"30 days"},
        "Internal (business metrics)": {"encryption":"TLS 1.3 + encryption at rest","access_controls":"Role-based access (RBAC)","data_residency":"Preferred region/country","audit_logging":"Detailed access + change logs","backup_retention":"90 days"},
        "Confidential (customer PII)": {"encryption":"AES-256 + field-level encryption for PII","access_controls":"Strict RBAC + MFA required","data_residency":"Must stay in specific region","audit_logging":"Full audit trail + real-time alerts","backup_retention":"7 years (legal requirement)"},
        "Restricted (financial/health records)": {"encryption":"FIPS 140-2 Level 3 + HSM key management","access_controls":"Zero-trust + privileged access mgmt","data_residency":"On-premises or certified cloud only","audit_logging":"Immutable audit logs + compliance reports","backup_retention":"10+ years (regulatory requirement)"},
    }
    compliance_details = {
        "GDPR": {"key_requirements":["Right to be forgotten","Data portability","Privacy by design","DPO appointment"],
                 "technical_controls":["Pseudonymization","Encryption","Access controls","Breach notification (72hrs)"],
                 "deployment_impact":{"🏠 On-premises":"✅ Full control over data location and processing","☁️ Public Cloud":"⚠️ Need EU-based cloud regions + data processing agreements","🌉 Hybrid Cloud":"⚠️ Ensure EU data stays in compliant locations"}},
        "HIPAA": {"key_requirements":["PHI protection","Business Associate Agreements","Risk assessments","Employee training"],
                  "technical_controls":["End-to-end encryption","Access controls","Audit logs","Secure transmission"],
                  "deployment_impact":{"🏠 On-premises":"✅ Maximum control, easier compliance audits","☁️ Public Cloud":"⚠️ Requires HIPAA-compliant cloud services + BAAs","🌉 Hybrid Cloud":"⚠️ PHI must stay in HIPAA-compliant environments"}},
        "SOX": {"key_requirements":["Financial data integrity","Change controls","Segregation of duties","Audit trails"],
                "technical_controls":["Immutable logs","Change approval workflows","Access reviews","Data integrity checks"],
                "deployment_impact":{"🏠 On-premises":"✅ Direct control over financial systems","☁️ Public Cloud":"✅ Can use SOC 2 Type II certified services","🌉 Hybrid Cloud":"⚠️ Ensure consistent controls across environments"}},
        "PCI-DSS": {"key_requirements":["Cardholder data protection","Network segmentation","Regular testing","Access monitoring"],
                    "technical_controls":["Network segmentation","WAF","Encryption","Vulnerability scanning"],
                    "deployment_impact":{"🏠 On-premises":"✅ Full control but expensive PCI compliance","☁️ Public Cloud":"✅ Use PCI-DSS certified cloud services","🌉 Hybrid Cloud":"⚠️ Payment processing should be in certified environment"}},
        "ISO 27001": {"key_requirements":["Information security management","Risk assessment","Security controls","Continuous improvement"],
                      "technical_controls":["Security policies","Access controls","Incident response","Security monitoring"],
                      "deployment_impact":{"🏠 On-premises":"✅ Full control over security implementation","☁️ Public Cloud":"✅ Leverage cloud provider's ISO 27001 certification","🌉 Hybrid Cloud":"⚠️ Need consistent security framework across both"}},
    }
    industry_considerations = {
        "Financial Services":{"key_risks":["Regulatory fines","Data breaches","System downtime"],"recommended_model":"🏠 On-premises or 🌉 Hybrid","rationale":"Core systems often must remain private for regulatory compliance"},
        "Healthcare":{"key_risks":["HIPAA violations","Patient safety","Data breaches"],"recommended_model":"🏠 On-premises or 🌉 Hybrid","rationale":"Patient data requires strict controls and audit trails"},
        "Government":{"key_risks":["Security breaches","Data sovereignty","Public trust"],"recommended_model":"🏠 On-premises","rationale":"Government data often requires air-gapped or classified environments"},
        "E-commerce/Retail":{"key_risks":["PCI compliance","Customer data","Seasonal scaling"],"recommended_model":"☁️ Public Cloud or 🌉 Hybrid","rationale":"Need to scale for traffic spikes while protecting payment data"},
        "Manufacturing":{"key_risks":["Operational downtime","IP theft","Supply chain"],"recommended_model":"🌉 Hybrid Cloud","rationale":"Factory floor stays local, analytics and planning in cloud"},
        "Technology/SaaS":{"key_risks":["Service availability","Customer data","Competitive advantage"],"recommended_model":"☁️ Public Cloud","rationale":"Need global scale, high availability, and rapid feature deployment"},
    }
    base_reqs = sensitivity_reqs[data_sensitivity]
    industry_info = industry_considerations[industry]
    rec = {"data_requirements":base_reqs,"industry_context":industry_info,"compliance_details":{},"deployment_recommendation":"","implementation_priority":[],"estimated_complexity":"","timeline_estimate":""}
    if compliance_reqs and "None" not in compliance_reqs:
        for c in compliance_reqs:
            if c in compliance_details: rec["compliance_details"][c] = compliance_details[c]
    if data_sensitivity == "Restricted (financial/health records)":
        rec["deployment_recommendation"] = "⚠️ HIGH RISK: Restricted data typically requires on-premises or certified private cloud" if model == "☁️ Public Cloud" else "✅ GOOD FIT: Recommended for restricted data"
    elif data_sensitivity == "Confidential (customer PII)":
        rec["deployment_recommendation"] = "⚠️ MODERATE RISK: Requires careful cloud provider selection and configuration" if any(comp in ["HIPAA","PCI-DSS"] for comp in compliance_reqs) else "✅ ACCEPTABLE: With proper encryption and access controls"
    else:
        rec["deployment_recommendation"] = "✅ SUITABLE: Standard cloud security practices sufficient"
    if data_sensitivity in ["Restricted (financial/health records)","Confidential (customer PII)"]:
        rec["implementation_priority"] = ["1. Data classification and mapping","2. Encryption key management","3. Identity and access management","4. Audit logging and monitoring","5. Backup and disaster recovery"]
        rec["estimated_complexity"] = "HIGH - Requires specialized security expertise"; rec["timeline_estimate"] = "6-12 months for full implementation"
    else:
        rec["implementation_priority"] = ["1. Basic access controls","2. Data encryption in transit/rest","3. Regular backups","4. Monitoring and alerting","5. Documentation and training"]
        rec["estimated_complexity"] = "MEDIUM - Standard security practices"; rec["timeline_estimate"] = "2-4 months for full implementation"
    return rec

def display_compliance_recommendations(model, data_sensitivity, compliance_reqs, industry):
    recs = get_compliance_recommendations(model, data_sensitivity, compliance_reqs, industry)
    st.markdown("### 🎯 Deployment Fit Assessment")
    if "HIGH RISK" in recs["deployment_recommendation"]: st.error(recs["deployment_recommendation"])
    elif "MODERATE RISK" in recs["deployment_recommendation"]: st.warning(recs["deployment_recommendation"])
    else: st.success(recs["deployment_recommendation"])
    st.markdown("### 🏢 Industry-Specific Considerations")
    industry_info = recs["industry_context"]; col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Recommended Model:** {industry_info['recommended_model']}"); st.write("**Key Risks:**"); [st.write(f"• {r}") for r in industry_info['key_risks']]
    with col2: st.write(f"**Rationale:** {industry_info['rationale']}")
    st.markdown("### 🔒 Security Requirements")
    data_reqs = recs["data_requirements"]; req_col1, req_col2 = st.columns(2)
    with req_col1: st.write(f"**Encryption:** {data_reqs['encryption']}"); st.write(f"**Access Controls:** {data_reqs['access_controls']}"); st.write(f"**Data Residency:** {data_reqs['data_residency']}")
    with req_col2: st.write(f"**Audit Logging:** {data_reqs['audit_logging']}"); st.write(f"**Backup Retention:** {data_reqs['backup_retention']}")
    if recs["compliance_details"]:
        st.markdown("### 📋 Compliance Requirements")
        for comp, det in recs["compliance_details"].items():
            with st.expander(f"{comp} Compliance Details"):
                st.write("**Key Requirements:**"); [st.write(f"• {x}") for x in det["key_requirements"]]
                st.write("**Technical Controls Needed:**"); [st.write(f"• {x}") for x in det["technical_controls"]]
                st.write("**Deployment Model Impact:**")
                for dm, impact in det["deployment_impact"].items():
                    (st.success if "✅" in impact else st.warning)(f"{dm}: {impact}")
    st.markdown("### 🚀 Implementation Roadmap")
    impl_col1, impl_col2 = st.columns(2)
    with impl_col1: st.write("**Priority Order:**"); [st.write(x) for x in recs["implementation_priority"]]
    with impl_col2: st.write("**Complexity Level:**"); st.write(f"**{recs['estimated_complexity']}**"); st.write("**Timeline Estimate:**"); st.write(f"**{recs['timeline_estimate']}**")
    st.markdown("### ⚠️ Risk Assessment Matrix")
    if data_sensitivity == "Restricted (financial/health records)": risk_level, risk_desc = "🔴 CRITICAL","Highest security measures required. Consider on-premises or specialized compliance cloud."
    elif data_sensitivity == "Confidential (customer PII)":
        if any(comp in ["HIPAA","PCI-DSS","SOX"] for comp in compliance_reqs): risk_level, risk_desc = "🟠 HIGH","Significant compliance requirements. Requires specialized cloud configuration."
        else: risk_level, risk_desc = "🟡 MEDIUM","Standard enterprise security practices sufficient."
    elif data_sensitivity == "Internal (business metrics)": risk_level, risk_desc = "🟡 MEDIUM","Business-standard security controls needed."
    else: risk_level, risk_desc = "🟢 LOW","Basic security measures sufficient."
    st.write("**Overall Risk Level:**"); st.write(f"**{risk_level}**"); st.caption(risk_desc)

# =========================
# Live data helpers (CoinGecko/Binance)
# =========================

SESSION_HEADERS = {"User-Agent": "streamlit-portfolio/1.0"}

@st.cache_data(ttl=30)
def cg_prices(ids=("bitcoin","ethereum","solana"), vs="usd"):
    r = requests.get("https://api.coingecko.com/api/v3/simple/price",
                     params={"ids": ",".join(ids), "vs_currencies": vs},
                     headers=SESSION_HEADERS, timeout=12)
    r.raise_for_status(); return r.json()

@st.cache_data(ttl=120)
def cg_history(token_id: str, days: int = 30, vs="usd"):
    r = requests.get(f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart",
                     params={"vs_currency": vs, "days": days},
                     headers=SESSION_HEADERS, timeout=12)
    r.raise_for_status(); data = r.json().get("prices", [])
    if not data: return pd.DataFrame(columns=["t","price"])
    df = pd.DataFrame(data, columns=["t_ms","price"]); df["t"] = pd.to_datetime(df["t_ms"], unit="ms")
    return df[["t","price"]]

@st.cache_data(ttl=180)
def cg_global():
    r = requests.get("https://api.coingecko.com/api/v3/global", headers=SESSION_HEADERS, timeout=12)
    r.raise_for_status(); return r.json().get("data", {})

@st.cache_data(ttl=180)
def cg_top_exchanges(per_page=10, page=1):
    r = requests.get("https://api.coingecko.com/api/v3/exchanges",
                     params={"per_page": per_page, "page": page},
                     headers=SESSION_HEADERS, timeout=12)
    r.raise_for_status(); return r.json()

@st.cache_data(ttl=90)
def binance_klines(symbol="BTCUSDT", interval="1h", limit=168):
    r = requests.get("https://api.binance.com/api/v3/klines",
                     params={"symbol": symbol, "interval": interval, "limit": limit},
                     headers=SESSION_HEADERS, timeout=12)
    r.raise_for_status()
    kl = r.json()
    df = pd.DataFrame(kl, columns=["t","o","h","l","c","v","ct","qv","n","tb","tqv","i"])
    df["t"] = pd.to_datetime(df["t"], unit="ms")
    for c in ["o","h","l","c","v"]: df[c] = df[c].astype(float)
    return df[["t","o","h","l","c","v"]]

BINANCE_MAP = {
    "bitcoin":"BTCUSDT","ethereum":"ETHUSDT","solana":"SOLUSDT","binancecoin":"BNBUSDT",
    "cardano":"ADAUSDT","ripple":"XRPUSDT","polkadot":"DOTUSDT","uniswap":"UNIUSDT",
    "aave":"AAVEUSDT","chainlink":"LINKUSDT",
}

# Risk metrics from history
def realized_metrics_from_history(df_prices: pd.DataFrame):
    if df_prices.empty or len(df_prices) < 5:
        return dict(change_pct=np.nan, vol=np.nan, sharpe=np.nan, mdd=np.nan, var95=np.nan)
    d = df_prices.set_index("t")["price"].resample("1D").last().dropna()
    if len(d) < 5: d = df_prices.set_index("t")["price"]
    rets = d.pct_change().dropna()
    if rets.empty: return dict(change_pct=np.nan, vol=np.nan, sharpe=np.nan, mdd=np.nan, var95=np.nan)
    change_pct = (d.iloc[-1]/d.iloc[-2]-1)*100 if len(d)>=2 else np.nan
    vol_ann = rets.std()*np.sqrt(252)
    sharpe = (rets.mean()/(rets.std()+1e-9))*np.sqrt(252)
    cum = (1+rets).cumprod(); peak = cum.cummax(); mdd = (cum/peak - 1).min()*100
    var95 = np.percentile(rets, 5)*100
    return dict(change_pct=change_pct, vol=vol_ann*100, sharpe=sharpe, mdd=mdd, var95=var95)

def corr_from_tokens(token_ids, days=30, vs="usd"):
    series, names = [], []
    for tid in token_ids:
        df = cg_history(tid, days, vs)
        if df.empty: continue
        s = df.set_index("t")["price"].resample("1D").last().pct_change().rename(tid)
        series.append(s); names.append(tid)
    if not series: return pd.DataFrame()
    df_all = pd.concat(series, axis=1).dropna()
    return df_all.corr()

# =========================
# World Bank / Findex helpers
# =========================

@st.cache_data(ttl=600)
def wb_search_indicators(query: str, per_page: int = 20000):
    """Search World Bank indicators by name (client-side filter)."""
    r = requests.get("https://api.worldbank.org/v2/indicator",
                     params={"format":"json","per_page":per_page}, timeout=20)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list) or len(data) < 2: return []
    indicators = data[1]  # list of dicts
    q = query.lower()
    hits = [i for i in indicators if q in (i.get("name","").lower())]
    # Return compact tuples (code, name)
    return [(i.get("id"), i.get("name")) for i in hits][:50]

@st.cache_data(ttl=600)
def wb_indicator_series(indicator_code: str, countries: list, date="2010:2024"):
    """Fetch time-series for given indicator and countries."""
    result = {}
    for c in countries:
        r = requests.get(f"https://api.worldbank.org/v2/country/{c}/indicator/{indicator_code}",
                         params={"format":"json","date":date,"per_page":1000}, timeout=20)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list) or len(data) < 2: 
            result[c] = pd.DataFrame(columns=["date","value"]); continue
        rows = data[1]
        df = pd.DataFrame([{"date":int(x["date"]), "value":x["value"]} for x in rows if x.get("date")])
        df = df.sort_values("date")
        result[c] = df
    return result

# =========================
# Synthetic/SOC helpers (for Cyber tab)
# =========================

def synth_auth_logs(n=800, seed=7):
    random.seed(seed); rows=[]
    for _ in range(n):
        fail_p = 0.12; geo = random.choice(["SG","US","DE","CN","GB","IN","BR","AU"])
        device_risk = random.choice([0,1,2]); hour = random.randint(0,23); is_vpn = random.choice([0,0,0,1])
        if random.random() < 0.05: device_risk, is_vpn, hour, fail_p = 2, 1, random.choice([2,3,4]), 0.7
        outcome = "fail" if random.random() < fail_p else "success"
        rows.append(dict(hour=hour, geo=geo, device_risk=device_risk, is_vpn=is_vpn, outcome=outcome))
    return pd.DataFrame(rows)

def detect_anomalies(df):
    enc_geo = {g:i for i,g in enumerate(sorted(df["geo"].unique()))}
    dfn = df.copy(); dfn["geo"] = dfn["geo"].map(enc_geo); dfn["outcome_num"] = (dfn["outcome"]=="fail").astype(int)
    X = dfn[["hour","geo","device_risk","is_vpn","outcome_num"]]
    model = IsolationForest(n_estimators=120, contamination=0.06, random_state=42)
    model.fit(X)
    df["anomaly"] = model.predict(X).astype(int).map({-1:1, 1:0})
    return df, model

def zero_trust_score(device:int, vpn:int, geo:int, fail:float, segmentation:int, rbac:int):
    score = 20 + device*18 + vpn*15 + geo*10 + (fail*100)*0.25 + (2-segmentation)*10 + (2-rbac)*8
    return max(0, min(100, score))

def platform_reco(workload:str, data_type:str, team_skill:str, budget:str):
    s = d = 0
    if workload in ["BI/Reporting","ELT/SQL analytics"]: s += 2
    if workload in ["Data Science/ML","Streaming/Batch ML","Lakehouse"]: d += 2
    if data_type in ["Structured","Semi-structured"]: s += 1
    if data_type in ["Unstructured","Streaming"]: d += 1
    if team_skill == "SQL-first": s += 2
    if team_skill in ["Python/Scala notebooks","ML engineering"]: d += 2
    if budget == "Tight (pay for what you use)": s += 1; d += 1
    reco = "Snowflake leaning" if s>d else ("Databricks leaning" if d>s else "Either fits — depends on governance & ecosystem")
    bullets = {
        "Snowflake": ["Elastic cloud DW (compute/storage separation), strong SQL UX","Snowpark for Python/Java/Scala; secure data sharing/collab","Cross-cloud, governance features; Iceberg/Unistore options"],
        "Databricks": ["Lakehouse (Delta) unifies BI + ML; great notebooks & MLflow","Streaming + batch on open formats (Delta/Parquet/Iceberg)","Unity Catalog for governance; Photon engine for fast SQL"],
    }
    return reco, s, d, bullets

# =========================
# UI Shell
# =========================

st.title("Cloud x Fintech x Security — Interactive Portfolio")
st.sidebar.caption(f"Deployed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

page = st.sidebar.radio(
    "Navigate",
    ["1) Cloud Architectures", "2) Fintech: Live Crypto", "3) Cybersecurity Lab", "4) Data Platforms", "About"]
)

def tldr(badge: str, text: str):
    st.markdown(f"""
<div style="border-left: 6px solid #4F46E5; padding: 0.6rem 0.8rem; background:#F8FAFC; border-radius:6px;">
  <strong>{badge}</strong> — {text}
</div>""", unsafe_allow_html=True)

# =========================
# 1) Cloud Architectures
# =========================

if page.startswith("1"):
    tldr("TL;DR (Model-based)", "Illustrates trade-offs across On-prem / Public / Hybrid and IaaS/PaaS/SaaS. Costs are toy-calculated (not billing data). Use: explain governance, scale & cost posture quickly.")

    st.markdown("""
    # 🏗️ Cloud Architectures: Choose Your Adventure
    """)
    st.info("💡 **Try this:** Adjust the sliders below and watch how costs change for different scenarios!")

    st.markdown("## 🎛️ Interactive Cost Calculator")
    col_left, col_right = st.columns([1, 1], gap="large")
    with col_left:
        model = st.radio("Pick a deployment model to see real-world examples:", ["🏠 On-premises","☁️ Public Cloud","🌉 Hybrid Cloud"], index=1)
        company_size = st.selectbox("Company size", ["Startup (1-50 employees)","SME (51-500 employees)","Enterprise (500+ employees)"], 1)
        industry = st.selectbox("Industry vertical", ["Financial Services","Healthcare","E-commerce/Retail","Manufacturing","Government","Technology/SaaS"], 0)
        st.markdown("### Workload Requirements")
        ingest_gb = st.slider("Daily data processing (GB)", 1, 500, 40, 5)
        users = st.slider("People using analytics dashboards", 5, 1000, 60, 5)
        st.markdown("### Security & Compliance Needs")
        data_sensitivity = st.selectbox("Data sensitivity level", ["Public (marketing data)","Internal (business metrics)","Confidential (customer PII)","Restricted (financial/health records)"], 2)
        compliance_reqs = st.multiselect("Compliance requirements", ["GDPR","HIPAA","SOX","PCI-DSS","ISO 27001","None"], default=["GDPR"])
        network_isolation = st.select_slider("Network security level", options=["Basic","Standard","High","Maximum"], value="Standard")
    with col_right:
        st.markdown("### 💰 Cost Breakdown")
        base_costs = {"🏠 On-premises":800,"☁️ Public Cloud":200,"🌉 Hybrid Cloud":400}
        base_cost = base_costs[model]; data_cost = ingest_gb * 2.5; user_cost = users * 1.2
        security_multiplier = {"Basic":1.0,"Standard":1.2,"High":1.5,"Maximum":2.0}[network_isolation]
        compliance_cost = len(compliance_reqs) * 150 if compliance_reqs != ["None"] else 0
        industry_multiplier = {"Financial Services":1.4,"Healthcare":1.3,"Government":1.5,"E-commerce/Retail":1.1,"Manufacturing":1.2,"Technology/SaaS":1.0}[industry]
        size_multiplier = {"Startup (1-50)":0.8,"SME (51-500)":1.0,"Enterprise (500+)":1.3}
        size_multiplier = {"Startup (1-50 employees)":0.8,"SME (51-500 employees)":1.0,"Enterprise (500+ employees)":1.3}[company_size]
        total_cost = (base_cost + data_cost + user_cost + compliance_cost) * security_multiplier * industry_multiplier * size_multiplier
        st.metric("💸 Estimated Monthly Cost", f"${total_cost:,.0f}")
        with st.expander("💡 See cost breakdown"):
            st.write(f"• **Base infrastructure**: ${base_cost:,}")
            st.write(f"• **Data processing**: ${data_cost:,.0f}")
            st.write(f"• **User access**: ${user_cost:,.0f}")
            st.write(f"• **Compliance**: ${compliance_cost:,}")
            st.write(f"• **Security level**: {security_multiplier}x")
            st.write(f"• **Industry factor**: {industry_multiplier}x")
            st.write(f"• **Company size**: {size_multiplier}x")
    st.markdown("---")
    display_compliance_recommendations(model, data_sensitivity, compliance_reqs, industry)
    st.markdown("---")
    st.markdown("## 🏗️ Cloud Service Models: IaaS vs PaaS vs SaaS")
    service_col1, service_col2 = st.columns([1, 2])
    with service_col1:
        selected_service = st.selectbox("Choose a service model to explore:", ["🚗 IaaS (Infrastructure as a Service)","🚌 PaaS (Platform as a Service)","🚕 SaaS (Software as a Service)"])
    with service_col2:
        if "IaaS" in selected_service: st.markdown("### 🚗 IaaS — Raw building blocks\n**Examples:** EC2, GCE, Azure VMs")
        elif "PaaS" in selected_service: st.markdown("### 🚌 PaaS — Focus on code, not infra\n**Examples:** App Engine, Cloud Run, Heroku, RDS")
        else: st.markdown("### 🚕 SaaS — Ready-to-use apps\n**Examples:** Salesforce, Google Workspace")
    st.markdown("### 👥 Who's Responsible for What?")
    responsibilities = ["Physical Data Centers","Network & Security Infrastructure","Virtual Machines & Storage","Operating System & Updates","Runtime & Development Tools","Application Code & Logic","User Data & Access Control","Business Processes & Training"]
    iaas_resp = ["🟢","🟢","🟢","🔴","🔴","🔴","🔴","🔴"]; paas_resp = ["🟢","🟢","🟢","🟢","🟢","🔴","🔴","🔴"]; saas_resp = ["🟢","🟢","🟢","🟢","🟢","🟢","🟡","🔴"]
    resp_df = pd.DataFrame({"Responsibility Layer":responsibilities,"IaaS":iaas_resp,"PaaS":paas_resp,"SaaS":saas_resp})
    st.dataframe(resp_df, use_container_width=True, hide_index=True)
    st.caption("🟢 = Cloud Provider  |  🟡 = Shared  |  🔴 = You (Customer)")

# =========================
# 2) Fintech: Live Crypto
# =========================

elif page.startswith("2"):
    st.markdown("# 🏦 Fintech & Digital Assets Dashboard")
    tldr("TL;DR (Live + Open Data)",
         "Crypto uses live CoinGecko/Binance. Payments shows live global crypto market proxies + World Bank/Findex indicators. Fraud tab supports your CSV or a clearly-marked synthetic demo.")

    fintech_tab1, fintech_tab2, fintech_tab3 = st.tabs([
        "💰 Crypto & Portfolio Analytics",
        "💳 Payments & Transaction Economics",
        "🔍 Risk & Fraud Detection"
    ])

    # ---------- Tab 1: Crypto & Portfolio ----------
    with fintech_tab1:
        tldr("TL;DR (Live)", "Prices & history from CoinGecko; candles/volumes from Binance. Illustrates portfolio construction, realized volatility, correlations.")
        portfolio_col1, portfolio_col2, portfolio_col3 = st.columns([3, 4, 3])
        with portfolio_col1:
            st.markdown("**Select Assets**")
            major_tokens = st.multiselect("Major:", ["bitcoin","ethereum","solana","binancecoin","cardano","ripple","polkadot"], default=["bitcoin","ethereum"], key="major")
            stable_tokens = st.multiselect("Stablecoins:", ["tether","usd-coin","dai","busd"], default=["usd-coin"], key="stable")
            defi_tokens = st.multiselect("DeFi:", ["uniswap","aave","chainlink"], default=[], key="defi")
            all_tokens = major_tokens + stable_tokens + defi_tokens
            if not all_tokens: all_tokens = ["bitcoin","ethereum"]
            st.markdown("**Allocations (must total 100%)**")
            allocations = {t: st.slider(t.replace("-"," ").title(), 0, 100, int(100/len(all_tokens)), key=f"alloc_{t}") for t in all_tokens}
            total_allocation = sum(allocations.values())
            if total_allocation != 100: st.warning(f"⚠️ Total allocation is {total_allocation}% (should be 100%)")
            period = st.selectbox("Analysis Period", ["7 days","30 days","90 days","1 year"], 1)
            days = {"7 days":7,"30 days":30,"90 days":90,"1 year":365}[period]
            portfolio_size = st.number_input("Portfolio Value (USD):", min_value=100, max_value=1_000_000, value=10_000, step=1000)

        with portfolio_col2:
            st.markdown("#### 📈 Live Portfolio Dashboard")
            try:
                prices = cg_prices(tuple(all_tokens), vs="usd")
                asset_values = {t: (portfolio_size * (allocations[t]/100.0)) for t in all_tokens if t in prices}
                st.metric("Portfolio Value", f"${sum(asset_values.values()):,.0f}")
                primary = all_tokens[0]; hist = cg_history(primary, days=days, vs="usd"); metrics = realized_metrics_from_history(hist)
                if not np.isnan(metrics["change_pct"]):
                    st.metric("24H Change", f"{metrics['change_pct']:+.2f}%", delta_color=("normal" if metrics['change_pct']>=0 else "inverse"))
                    st.metric("Realized Vol (ann.)", f"{metrics['vol']:.1f}%")
                if asset_values:
                    fig_pie = go.Figure(data=[go.Pie(labels=[k.title() for k in asset_values.keys()], values=list(asset_values.values()), hole=0.3)])
                    fig_pie.update_traces(textinfo='percent+label'); fig_pie.update_layout(title="Portfolio Allocation", height=300)
                    st.plotly_chart(fig_pie, use_container_width=True)
                sym = BINANCE_MAP.get(primary)
                if sym:
                    dfk = binance_klines(sym, "1h", min(168, max(24, days*24 if days<=14 else 168)))
                    fig_chart = go.Figure(data=[go.Candlestick(x=dfk['t'], open=dfk['o'], high=dfk['h'], low=dfk['l'], close=dfk['c'])])
                    fig_chart.update_layout(title=f"{primary.replace('-', ' ').title()} Candles", height=260, xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig_chart, use_container_width=True)
                elif not hist.empty:
                    st.info("No Binance symbol mapping for this token; showing CoinGecko line.")
                    st.line_chart(hist.set_index("t")["price"])
            except Exception as e:
                st.error(f"Price source unavailable: {e}")

        with portfolio_col3:
            st.markdown("#### 🔍 Risk Analytics (Realized)")
            try:
                if len(all_tokens) > 1:
                    corr = corr_from_tokens(all_tokens, days=days, vs="usd")
                    if not corr.empty:
                        fig_heatmap = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.index, colorscale='RdBu', zmid=0))
                        fig_heatmap.update_layout(height=300, title="Return Correlations")
                        st.plotly_chart(fig_heatmap, use_container_width=True)
                if not np.isnan(metrics["sharpe"]):
                    st.metric("Sharpe (rf≈0)", f"{metrics['sharpe']:.2f}")
                    st.metric("Max Drawdown", f"{metrics['mdd']:.1f}%")
                    st.metric("VaR 95% (1D)", f"{metrics['var95']:.2f}%")
                st.caption("Sources: CoinGecko (prices, history); Binance (candles). Metrics are realized from selected lookback — not investment advice.")
            except Exception as e:
                st.warning(f"Risk metrics unavailable: {e}")

    # ---------- Tab 2: Payments & Transaction Economics ----------
    with fintech_tab2:
        tldr("TL;DR (Live + Open Data)",
             "Top-down activity via CoinGecko (global volume/exchange volume). Macro adoption via World Bank/Findex indicators. Calculator is model-based (clearly labeled).")

        left, right = st.columns([3, 4], gap="large")
        with left:
            st.markdown("#### 🌐 Market-wide Activity (Crypto proxy)")
            try:
                g = cg_global()
                mcap_dominance = g.get("market_cap_percentage", {})
                total_vol = g.get("total_volume", {}).get("usd", None)
                active_assets = g.get("active_cryptocurrencies", None)
                if mcap_dominance:
                    labels = [k.upper() for k in mcap_dominance.keys()]
                    values = list(mcap_dominance.values())
                    fig_dom = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.35)])
                    fig_dom.update_traces(textinfo='percent+label'); fig_dom.update_layout(title="Market Cap Dominance (Top Coins)")
                    st.plotly_chart(fig_dom, use_container_width=True)
                m1, m2 = st.columns(2)
                if total_vol: m1.metric("24h Total Volume (USD)", f"${total_vol:,.0f}")
                if active_assets: m2.metric("Active Cryptocurrencies", f"{active_assets:,}")
                st.caption("Source: CoinGecko Global endpoint (near real-time).")
            except Exception as e:
                st.error(f"Global metrics unavailable: {e}")

            st.markdown("#### 🏦 Top Exchanges by 24h Volume")
            try:
                ex = cg_top_exchanges(per_page=10, page=1)
                names = [x["name"] for x in ex]; vols_btc = [x.get("trade_volume_24h_btc", 0) for x in ex]
                btc_price = cg_prices(("bitcoin",), "usd")["bitcoin"]["usd"]
                vols_usd = [v * btc_price for v in vols_btc]
                fig_ex = go.Figure(data=[go.Bar(x=names, y=vols_usd)])
                fig_ex.update_layout(title="Top Exchanges — 24h Volume (USD)", yaxis_title="USD", xaxis_tickangle=-20, height=320)
                st.plotly_chart(fig_ex, use_container_width=True)
                st.caption("Source: CoinGecko Exchanges.")
            except Exception as e:
                st.warning(f"Exchange volumes unavailable: {e}")

        with right:
            st.markdown("#### ⏱️ Hour-of-Day Volume Heatmap (Binance)")
            symbol = st.selectbox("Symbol for heatmap", ["BTCUSDT","ETHUSDT","SOLUSDT","ADAUSDT","XRPUSDT"], 0)
            lookback_days = st.slider("Lookback (days)", 2, 7, 5)
            try:
                dfk = binance_klines(symbol, "1h", limit=24*lookback_days)
                dfk["hour"] = dfk["t"].dt.hour; dfk["day"] = dfk["t"].dt.date
                pv = dfk.pivot_table(index="day", columns="hour", values="v", aggfunc="sum").fillna(0)
                avg_by_hour = pv.mean(axis=0).reindex(range(24)).fillna(0).values
                fig_hm = go.Figure(data=go.Heatmap(z=[avg_by_hour], x=list(range(24)), y=[str(symbol)], colorscale="Blues"))
                fig_hm.update_layout(title=f"Avg Hourly Volume (last {lookback_days} days)", height=220, xaxis_title="Hour of Day")
                st.plotly_chart(fig_hm, use_container_width=True)
                st.caption("Source: Binance candles (volume).")
            except Exception as e:
                st.warning(f"Heatmap unavailable: {e}")

            st.markdown("#### 🌍 World Bank / Global Findex — Adoption Indicators")
            st.caption("Search indicators (e.g., **digital payments**, **account ownership**, **mobile money**) and plot them for selected countries.")
            q = st.text_input("Search indicators by keyword", value="digital payments")
            if q.strip():
                try:
                    hits = wb_search_indicators(q.strip())
                    if hits:
                        nice = [f"{code} — {name}" for code, name in hits]
                        pick = st.selectbox("Pick an indicator", options=nice, index=0)
                        code = pick.split(" — ")[0]
                        countries = st.multiselect("Countries (ISO3)", ["SGP","USA","GBR","IND","IDN","MYS","VNM","AUS","CAN"], default=["SGP","USA","IND"])
                        series = wb_indicator_series(code, countries, date="2010:2024")
                        fig = go.Figure()
                        latest_vals = []
                        for c in countries:
                            df = series.get(c, pd.DataFrame())
                            if not df.empty:
                                fig.add_trace(go.Scatter(x=df["date"], y=df["value"], mode="lines+markers", name=c))
                                lv = df.dropna().tail(1)
                                if not lv.empty:
                                    latest_vals.append((c, int(lv.iloc[0]["date"]), lv.iloc[0]["value"]))
                        fig.update_layout(title=f"World Bank Indicator: {code}", xaxis_title="Year", yaxis_title="Value", height=300)
                        st.plotly_chart(fig, use_container_width=True)
                        if latest_vals:
                            cols = st.columns(min(4, len(latest_vals)))
                            for i, (c, yr, v) in enumerate(latest_vals):
                                with cols[i % len(cols)]:
                                    st.metric(f"{c} ({yr})", f"{v:,.2f}" if v is not None else "n/a")
                        st.caption("Source: World Bank Open Data API (latest available year per country).")
                    else:
                        st.info("No indicators matched your search. Try a broader keyword.")
                except Exception as e:
                    st.error(f"World Bank API unavailable: {e}")

            st.markdown("#### 🧮 Revenue Calculator (Model-based)")
            st.caption("This is a calculator, not live data.")
            business_model = st.selectbox("Revenue Model:", ["Transaction Fees","Subscription + Fees","Freemium Model"])
            monthly_users = st.slider("Monthly Active Users", 1_000, 10_000_000, 100_000, 10_000)
            avg_tx = st.slider("Avg Transaction Value ($)", 5, 1000, 75)
            tx_per_user = st.slider("Transactions per User/Month", 1, 50, 8)
            if business_model == "Transaction Fees":
                fee_rate = st.slider("Transaction Fee (%)", 0.5, 5.0, 2.9, 0.1)
                fixed_fee = st.slider("Fixed Fee per Tx ($)", 0.00, 1.00, 0.30, 0.05)
                txs = monthly_users * tx_per_user; vol = txs * avg_tx
                rev = (vol * fee_rate / 100.0) + (txs * fixed_fee)
                st.metric("Monthly Volume", f"${vol:,.0f}"); st.metric("Monthly Revenue", f"${rev:,.0f}"); st.metric("Annual Revenue", f"${rev*12:,.0f}")
            else:
                sub_fee = st.slider("Monthly Subscription ($)", 2, 100, 20)
                red_fee = st.slider("Reduced Tx Fee (%)", 0.0, 3.0, 1.9, 0.1)
                sub_rev = monthly_users * sub_fee
                tx_rev = monthly_users * tx_per_user * avg_tx * red_fee / 100.0
                total = sub_rev + tx_rev
                st.metric("Subscription Revenue", f"${sub_rev:,.0f}"); st.metric("Transaction Revenue", f"${tx_rev:,.0f}"); st.metric("Total Monthly Revenue", f"${total:,.0f}")

    # ---------- Tab 3: Risk & Fraud Detection ----------
    with fintech_tab3:
        tldr("TL;DR (BYO or Synthetic)", "Upload a labeled CSV (recommended) to compute real precision/recall/F1. If none, uses a synthetic dataset clearly marked as demo.")
        uploaded = st.file_uploader("Upload a CSV with transactions (columns like: amount, hour, merchant_category, card_present, is_fraud)", type=["csv"])
        use_synth = st.checkbox("Use synthetic demo data (if no CSV provided)", value=True)

        if uploaded is not None:
            try:
                df_transactions = pd.read_csv(uploaded)
                st.success(f"Loaded {len(df_transactions):,} rows from your file.")
                source_label = "User-provided dataset"
            except Exception as e:
                st.error(f"Could not read CSV: {e}"); df_transactions = None
        else:
            df_transactions = None

        if df_transactions is None and use_synth:
            n_transactions = st.slider("Synthetic rows", 1000, 10000, 3000, 500)
            np.random.seed(42)
            tx = []
            fraud_rate = st.slider("Simulated fraud rate (%)", 0.5, 10.0, 2.0, 0.1)
            for i in range(n_transactions):
                is_fraud = np.random.random() < (fraud_rate / 100.0)
                tx.append({'amount': np.random.lognormal(3, 1) if not is_fraud else np.random.lognormal(5, 1.3),
                           'hour': np.random.randint(0, 24),
                           'merchant_category': np.random.choice(['retail','gas','restaurant','online','grocery']),
                           'card_present': 1 if not is_fraud else 0,
                           'is_fraud': int(is_fraud)})
            df_transactions = pd.DataFrame(tx); source_label = "Synthetic demo dataset"

        if df_transactions is not None:
            st.caption(f"Data source: **{source_label}**")
            df = df_transactions.copy()
            if "merchant_category" in df.columns: df["mc_enc"] = df["merchant_category"].astype("category").cat.codes
            else: df["mc_enc"] = 0
            for col in ["amount","hour","card_present"]:
                if col not in df.columns: df[col] = 0
            labeled = "is_fraud" in df.columns
            if not labeled: df["is_fraud"] = 0
            feats = ["amount","hour","card_present","mc_enc"]
            model = IsolationForest(n_estimators=200, contamination=0.02, random_state=42)
            model.fit(df[feats])
            scores = model.decision_function(df[feats]); preds = model.predict(df[feats])
            df["anomaly"] = (preds == -1).astype(int); df["score"] = -scores
            c1, c2, c3 = st.columns(3)
            c1.metric("Transactions", f"{len(df):,}"); c2.metric("Anomalies flagged", f"{int(df['anomaly'].sum()):,}")
            if labeled:
                tp = int(((df["anomaly"]==1) & (df["is_fraud"]==1)).sum())
                fp = int(((df["anomaly"]==1) & (df["is_fraud"]==0)).sum())
                fn = int(((df["anomaly"]==0) & (df["is_fraud"]==1)).sum())
                precision = tp / max(tp+fp, 1); recall = tp / max(tp+fn, 1); f1 = 2*precision*recall / max(precision+recall, 1e-9)
                c3.metric("F1 (if labeled)", f"{f1:.2f}"); st.caption(f"Precision {precision:.2f} • Recall {recall:.2f} • TP {tp} • FP {fp} • FN {fn}")
            hist = go.Figure(); hist.add_trace(go.Histogram(x=df[df["anomaly"]==0]["amount"], name="Normal", opacity=0.75, nbinsx=40))
            hist.add_trace(go.Histogram(x=df[df["anomaly"]==1]["amount"], name="Anomaly", opacity=0.75, nbinsx=40))
            hist.update_layout(barmode="overlay", title="Amount Distribution by Anomaly", xaxis_title="Amount ($)")
            st.plotly_chart(hist, use_container_width=True)
            hourly = df.groupby(["hour","anomaly"], as_index=False).size().pivot(index="hour", columns="anomaly", values="size").fillna(0)
            st.bar_chart(hourly)
            st.markdown("#### 💵 Cost–Benefit (user assumptions)")
            avg_fraud_loss = st.slider("Avg Loss per Fraud ($)", 20, 1000, 150, 10)
            false_positive_cost = st.slider("Cost per False Positive ($)", 0, 50, 5, 1)
            anomalies = int(df["anomaly"].sum())
            if labeled:
                prevented_loss = tp * avg_fraud_loss; friction_cost = fp * false_positive_cost
            else:
                prevented_loss = int(anomalies * 0.5) * avg_fraud_loss; friction_cost = int(anomalies * 0.5) * false_positive_cost
            net = prevented_loss - friction_cost
            b1, b2, b3 = st.columns(3)
            b1.metric("Prevented Loss (est.)", f"${prevented_loss:,.0f}")
            b2.metric("Friction Cost (est.)", f"${friction_cost:,.0f}")
            b3.metric("Net Benefit", f"${net:,.0f}")

# =========================
# 3) Cybersecurity Lab
# =========================

elif page.startswith("3"):
    tldr("TL;DR (Simulator + ML)", "Zero-Trust scoring simulator (policy knobs) and SOC mini using IsolationForest on synthetic logs. Illustrates verification, least privilege, anomaly hunting.")
    st.subheader("Zero-Trust simulator + SOC mini anomaly detection")
    a, b = st.columns(2, gap="large")
    with a:
        st.markdown("### Zero-Trust policy")
        device = st.select_slider("Device posture", options=[0,1,2], value=1)
        vpn = st.selectbox("Suspected VPN/Proxy", [0,1], index=0)
        geo = st.selectbox("Unusual geo change", [0,1], index=0)
        fail = st.slider("Recent login fail %", 0.0, 1.0, 0.15, 0.05)
        seg = st.select_slider("Network segmentation depth", options=[0,1,2], value=1)
        role = st.select_slider("RBAC granularity", options=[0,1,2], value=1)
        z = zero_trust_score(device, vpn, geo, fail, seg, role)
        st.metric("Composite Risk Score", f"{z}/100")
        st.write("**Decision:**", "❌ Block" if z>=60 else ("⚠️ Step-up (MFA)" if z>=35 else "✅ Allow"))
        with st.expander("Zero-Trust TL;DR"): st.write("- Verify explicitly • Least privilege • Assume breach • Continuous evaluation")
    with b:
        st.markdown("### SOC mini — anomaly hunt (toy)")
        n = st.slider("Log size", 200, 5000, 800, 100)
        df = synth_auth_logs(n=n, seed=42); df, model = detect_anomalies(df)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Anomaly Count", int(df["anomaly"].sum()))
            agg = df.groupby(["geo","outcome"], as_index=False).size()
            st.dataframe(agg, use_container_width=True, height=240)
        with col2:
            hourly = df.groupby(["hour","outcome"], as_index=False).size()
            pivot = hourly.pivot(index="hour", columns="outcome", values="size").fillna(0)
            st.bar_chart(pivot)
        st.caption("Model: IsolationForest. Extend with IP reputation, device intel, and alerts to Slack/SIEM.")

# =========================
# 4) Data Platforms
# =========================

elif page.startswith("4"):
    tldr("TL;DR (Decision Aid)", "Interactive helper to frame Snowflake vs Databricks fit by workload/data/team/budget. Illustrates trade-off communication, not vendor benchmarks.")
    st.subheader("Snowflake vs Databricks — interactive fit helper")
    l, r = st.columns([2,3], gap="large")
    with l:
        workload = st.selectbox("Primary workload", ["BI/Reporting","ELT/SQL analytics","Data Science/ML","Streaming/Batch ML","Lakehouse"])
        data_type = st.selectbox("Dominant data type", ["Structured","Semi-structured","Unstructured","Streaming"])
        team_skill = st.selectbox("Team skill bias", ["SQL-first","Python/Scala notebooks","ML engineering"])
        budget = st.selectbox("Budget posture", ["Tight (pay for what you use)","Flexible"])
        reco, s, d, bullets = platform_reco(workload, data_type, team_skill, budget)
        st.metric("Recommendation", reco)
        st.progress(min(1.0, s/6.0), text=f"Snowflake fit score: {s}")
        st.progress(min(1.0, d/6.0), text=f"Databricks fit score: {d}")
    with r:
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Snowflake strengths**"); [st.write("•", btxt) for btxt in bullets["Snowflake"]]
        with c2:
            st.write("**Databricks strengths**"); [st.write("•", btxt) for btxt in bullets["Databricks"]]
        st.caption("Illustrative only. For production, confirm SKU/feature availability by region/date.")

# =========================
# About
# =========================

else:
    tldr("TL;DR", "This portfolio blends live crypto data, open macro indicators, a fraud BYO-data lab, and cloud/security explainers.")
    st.subheader("About & Cost control")
    st.markdown("""
    **Live sources used in Fintech:**
    - CoinGecko: prices, history, global stats, top exchanges (free/public)
    - Binance: OHLCV candles for supported symbols (public REST)
    - World Bank / Global Findex: macro adoption & financial inclusion indicators

    Fraud tab supports **your CSV** (labeled ground truth) or a clearly-marked synthetic demo.
    """)
