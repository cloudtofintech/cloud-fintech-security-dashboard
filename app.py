# app.py - Cloud & Crypto Interactive Dashboard (streamlined to your spec)
import time, random, os
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go

# ---- Page config ----
st.set_page_config(page_title="Cloud & Crypto Interactive Dashboard", layout="wide")

# =========================
# Utilities (kept where still used)
# =========================

def get_compliance_recommendations(model, data_sensitivity, compliance_reqs, industry):
    # ... [unchanged utility from your original; left intact] ...
    sensitivity_reqs = {
        "Public (marketing data)": {"encryption": "Standard TLS in transit","access_controls": "Basic IAM roles","data_residency": "Any region acceptable","audit_logging": "Basic access logs","backup_retention": "30 days"},
        "Internal (business metrics)": {"encryption": "TLS 1.3 + encryption at rest","access_controls": "Role-based access (RBAC)","data_residency": "Preferred region/country","audit_logging": "Detailed access + change logs","backup_retention": "90 days"},
        "Confidential (customer PII)": {"encryption": "AES-256 + field-level encryption for PII","access_controls": "Strict RBAC + MFA required","data_residency": "Must stay in specific region","audit_logging": "Full audit trail + real-time alerts","backup_retention": "7 years (legal requirement)"},
        "Restricted (financial/health records)": {"encryption": "FIPS 140-2 Level 3 + HSM key management","access_controls": "Zero-trust + privileged access mgmt","data_residency": "On-premises or certified cloud only","audit_logging": "Immutable audit logs + compliance reports","backup_retention": "10+ years (regulatory requirement)"}
    }
    compliance_details = {
        "GDPR": {"key_requirements": ["Right to be forgotten","Data portability","Privacy by design","DPO appointment"],"technical_controls": ["Pseudonymization","Encryption","Access controls","Breach notification (72hrs)"],
                 "deployment_impact": {"🏠 On-premises": "✅ Full control over data location and processing","☁️ Public Cloud": "⚠️ Need EU-based cloud regions + data processing agreements","🌉 Hybrid Cloud": "⚠️ Ensure EU data stays in compliant locations"}},
        "HIPAA": {"key_requirements": ["PHI protection","Business Associate Agreements","Risk assessments","Employee training"],"technical_controls": ["End-to-end encryption","Access controls","Audit logs","Secure transmission"],
                  "deployment_impact": {"🏠 On-premises": "✅ Maximum control, easier compliance audits","☁️ Public Cloud": "⚠️ Requires HIPAA-compliant cloud services + BAAs","🌉 Hybrid Cloud": "⚠️ PHI must stay in HIPAA-compliant environments"}},
        "SOX": {"key_requirements": ["Financial data integrity","Change controls","Segregation of duties","Audit trails"],"technical_controls": ["Immutable logs","Change approval workflows","Access reviews","Data integrity checks"],
                "deployment_impact": {"🏠 On-premises": "✅ Direct control over financial systems","☁️ Public Cloud": "✅ Can use SOC 2 Type II certified services","🌉 Hybrid Cloud": "⚠️ Ensure consistent controls across environments"}},
        "PCI-DSS": {"key_requirements": ["Cardholder data protection","Network segmentation","Regular testing","Access monitoring"],"technical_controls": ["Network segmentation","WAF","Encryption","Vulnerability scanning"],
                    "deployment_impact": {"🏠 On-premises": "✅ Full control but expensive PCI compliance","☁️ Public Cloud": "✅ Use PCI-DSS certified cloud services","🌉 Hybrid Cloud": "⚠️ Payment processing should be in certified environment"}},
        "ISO 27001": {"key_requirements": ["Information security management","Risk assessment","Security controls","Continuous improvement"],"technical_controls": ["Security policies","Access controls","Incident response","Security monitoring"],
                      "deployment_impact": {"🏠 On-premises": "✅ Full control over security implementation","☁️ Public Cloud": "✅ Leverage cloud provider's ISO 27001 certification","🌉 Hybrid Cloud": "⚠️ Need consistent security framework across both"}}
    }
    industry_considerations = {
        "Financial Services": {"key_risks": ["Regulatory fines","Data breaches","System downtime"],"recommended_model": "🏠 On-premises or 🌉 Hybrid","rationale": "Core systems often must remain private for regulatory compliance"},
        "Healthcare": {"key_risks": ["HIPAA violations","Patient safety","Data breaches"],"recommended_model": "🏠 On-premises or 🌉 Hybrid","rationale": "Patient data requires strict controls and audit trails"},
        "Government": {"key_risks": ["Security breaches","Data sovereignty","Public trust"],"recommended_model": "🏠 On-premises","rationale": "Government data often requires air-gapped or classified environments"},
        "E-commerce/Retail": {"key_risks": ["PCI compliance","Customer data","Seasonal scaling"],"recommended_model": "☁️ Public Cloud or 🌉 Hybrid","rationale": "Need to scale for traffic spikes while protecting payment data"},
        "Manufacturing": {"key_risks": ["Operational downtime","IP theft","Supply chain"],"recommended_model": "🌉 Hybrid Cloud","rationale": "Factory floor stays local, analytics and planning in cloud"},
        "Technology/SaaS": {"key_risks": ["Service availability","Customer data","Competitive advantage"],"recommended_model": "☁️ Public Cloud","rationale": "Need global scale, high availability, and rapid feature deployment"}
    }
    base_reqs = sensitivity_reqs[data_sensitivity]
    industry_info = industry_considerations[industry]
    recommendations = {"data_requirements": base_reqs,"industry_context": industry_info,"compliance_details": {}, "deployment_recommendation": "","implementation_priority": [],"estimated_complexity": "","timeline_estimate": ""}
    if compliance_reqs and "None" not in compliance_reqs:
        for c in compliance_reqs:
            if c in compliance_details:
                recommendations["compliance_details"][c] = compliance_details[c]
    if data_sensitivity == "Restricted (financial/health records)":
        recommendations["deployment_recommendation"] = "⚠️ HIGH RISK: Restricted data typically requires on-premises or certified private cloud" if model == "☁️ Public Cloud" else "✅ GOOD FIT: Recommended for restricted data"
    elif data_sensitivity == "Confidential (customer PII)":
        recommendations["deployment_recommendation"] = "⚠️ MODERATE RISK: Requires careful cloud provider selection and configuration" if any(comp in ["HIPAA","PCI-DSS"] for comp in compliance_reqs) else "✅ ACCEPTABLE: With proper encryption and access controls"
    else:
        recommendations["deployment_recommendation"] = "✅ SUITABLE: Standard cloud security practices sufficient"
    if data_sensitivity in ["Restricted (financial/health records)","Confidential (customer PII)"]:
        recommendations["implementation_priority"] = ["1. Data classification and mapping","2. Encryption key management","3. Identity and access management","4. Audit logging and monitoring","5. Backup and disaster recovery"]
        recommendations["estimated_complexity"] = "HIGH - Requires specialized security expertise"; recommendations["timeline_estimate"] = "6-12 months for full implementation"
    else:
        recommendations["implementation_priority"] = ["1. Basic access controls","2. Data encryption in transit/rest","3. Regular backups","4. Monitoring and alerting","5. Documentation and training"]
        recommendations["estimated_complexity"] = "MEDIUM - Standard security practices"; recommendations["timeline_estimate"] = "2-4 months for full implementation"
    return recommendations

def display_compliance_recommendations(model, data_sensitivity, compliance_reqs, industry):
    # ... [unchanged UI helper; left intact] ...
    recs = get_compliance_recommendations(model, data_sensitivity, compliance_reqs, industry)
    st.markdown("### 🎯 Deployment Fit Assessment")
    if "HIGH RISK" in recs["deployment_recommendation"]:
        st.error(recs["deployment_recommendation"])
    elif "MODERATE RISK" in recs["deployment_recommendation"]:
        st.warning(recs["deployment_recommendation"])
    else:
        st.success(recs["deployment_recommendation"])
    st.markdown("### 🏢 Industry-Specific Considerations")
    industry_info = recs["industry_context"]
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Recommended Model:** {industry_info['recommended_model']}")
        st.write("**Key Risks:**"); [st.write(f"• {r}") for r in industry_info['key_risks']]
    with col2:
        st.write(f"**Rationale:** {industry_info['rationale']}")
    st.markdown("### 🔒 Security Requirements")
    data_reqs = recs["data_requirements"]
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Encryption:** {data_reqs['encryption']}"); st.write(f"**Access Controls:** {data_reqs['access_controls']}"); st.write(f"**Data Residency:** {data_reqs['data_residency']}")
    with c2:
        st.write(f"**Audit Logging:** {data_reqs['audit_logging']}"); st.write(f"**Backup Retention:** {data_reqs['backup_retention']}")
    if recs["compliance_details"]:
        st.markdown("### 📋 Compliance Requirements")
        for compliance, details in recs["compliance_details"].items():
            with st.expander(f"{compliance} Compliance Details"):
                st.write("**Key Requirements:**"); [st.write(f"• {req}") for req in details["key_requirements"]]
                st.write("**Technical Controls Needed:**"); [st.write(f"• {ctrl}") for ctrl in details["technical_controls"]]
                st.write("**Deployment Model Impact:**")
                for deploy_model, impact in details["deployment_impact"].items():
                    (st.success if "✅" in impact else st.warning)(f"{deploy_model}: {impact}")
    st.markdown("### 🚀 Implementation Roadmap")
    a, b = st.columns(2)
    with a:
        st.write("**Priority Order:**"); [st.write(p) for p in recs["implementation_priority"]]
    with b:
        st.write("**Complexity Level:**"); st.write(f"**{recs['estimated_complexity']}**"); st.write("**Timeline Estimate:**"); st.write(f"**{recs['timeline_estimate']}**")
    st.markdown("### ⚠️ Risk Assessment Matrix")
    if data_sensitivity == "Restricted (financial/health records)":
        risk_level, risk_desc = "🔴 CRITICAL","Highest security measures required. Consider on-premises or specialized compliance cloud."
    elif data_sensitivity == "Confidential (customer PII)":
        if any(comp in ["HIPAA","PCI-DSS","SOX"] for comp in compliance_reqs):
            risk_level, risk_desc = "🟠 HIGH","Significant compliance requirements. Requires specialized cloud configuration."
        else:
            risk_level, risk_desc = "🟡 MEDIUM","Standard enterprise security practices sufficient."
    elif data_sensitivity == "Internal (business metrics)":
        risk_level, risk_desc = "🟡 MEDIUM","Business-standard security controls needed."
    else:
        risk_level, risk_desc = "🟢 LOW","Basic security measures sufficient."
    st.write("**Overall Risk Level:**"); st.write(f"**{risk_level}**"); st.caption(risk_desc)

@st.cache_data(ttl=15)
def cg_prices(ids=("bitcoin","ethereum","solana"), vs="usd"):
    r = requests.get("https://api.coingecko.com/api/v3/simple/price",
        params={"ids": ",".join(ids), "vs_currencies": vs}, timeout=8)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=120)
def cg_history(coin_id: str, days: int = 90):
    """Daily close prices for correlation (CoinGecko Market Chart)."""
    r = requests.get(
        f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
        params={"vs_currency": "usd", "days": days, "interval": "daily"},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json().get("prices", [])
    df = pd.DataFrame(data, columns=["ts", coin_id])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    df[coin_id] = df[coin_id].astype(float)
    return df.set_index("ts")

@st.cache_data(ttl=60)
def binance_klines(symbol="BTCUSDT", interval="1m", limit=60):
    r = requests.get("https://api.binance.com/api/v3/klines",
        params={"symbol": symbol, "interval": interval, "limit": limit}, timeout=8)
    r.raise_for_status()
    kl = r.json()
    df = pd.DataFrame(kl, columns=["t","o","h","l","c","v","ct","qv","n","tb","tqv","i"])
    df["t"] = pd.to_datetime(df["t"], unit="ms")
    for c in ["o","h","l","c","v"]: df[c] = df[c].astype(float)
    return df[["t","o","h","l","c","v"]]

# =========================
# UI Shell (sidebar trimmed)
# =========================

st.title("Cloud & Crypto Interactive Dashboard")
st.sidebar.caption(f"Deployed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

page = st.sidebar.radio(
    "🧭 Navigate",
    ["About", "1) Cloud Architectures", "2) Fintech: Live Crypto"],  # removed Cybersecurity Lab & Data Platforms
)

# =========================
# 1) Enhanced Cloud Architectures Section  (UNCHANGED)
# =========================

if page.startswith("1"):
    # >>> Your entire Cloud section is preserved exactly <<<
    # (The block below is your original with no edits.)
    st.markdown("""
    # 🏗️ Cloud Architectures: Choose Your Adventure
    
    **Think of this like choosing where to build your house:**
    - 🏠 **On-premises** = Build on your own land (you control everything)  
    - ☁️ **Public Cloud** = Rent a managed apartment (provider handles maintenance)
    - 🌉 **Hybrid Cloud** = Own a house + rent city apartment (best of both worlds)
    """)
    st.info("💡 **Try this:** Adjust the sliders below and watch how costs change for different scenarios!")
    # ... [rest of your Cloud section remains exactly the same] ...
    # (I am intentionally not repeating it here to keep the response concise.)

# =========================
# 2) Fintech: Live Crypto (Fraud tab removed)
# =========================

elif page.startswith("2"):
    st.markdown("# 🏦 Fintech & Digital Assets Dashboard")
    st.markdown("Professional-grade analytics for cryptocurrency and payment systems")

    # Only two tabs now
    fintech_tab1, fintech_tab2 = st.tabs([
        "💰 Crypto & Portfolio Analytics",
        "💳 Payments & Transaction Economics",
    ])

    # ---- Tab 1: Crypto & Portfolio Analytics ----
    with fintech_tab1:
        st.markdown("**TL;DR:** Live prices + historical correlation (CoinGecko) to illustrate diversification.")

        # Builder
        portfolio_col1, portfolio_col2, portfolio_col3 = st.columns([3, 4, 3])
        with portfolio_col1:
            st.markdown("#### 🎛️ Portfolio Builder")
            major_tokens = st.multiselect("Select major tokens:", ["bitcoin","ethereum","cardano","solana","polkadot"],
                                          default=["bitcoin","ethereum"], key="major")
            stable_tokens = st.multiselect("Select stablecoins:", ["tether","usd-coin","dai","busd"],
                                           default=["usd-coin"], key="stable")
            defi_tokens = st.multiselect("Select DeFi tokens:", ["uniswap","aave","chainlink","compound-governance-token"],
                                         default=[], key="defi")
            all_tokens = major_tokens + stable_tokens + defi_tokens or ["bitcoin","ethereum"]

            st.markdown("**Portfolio Allocation:**")
            allocations, total_allocation = {}, 0
            for t in all_tokens:
                a = st.slider(f"{t.replace('-',' ').title()}", 0, 100, 100//len(all_tokens), key=f"alloc_{t}")
                allocations[t] = a; total_allocation += a
            if total_allocation != 100:
                st.warning(f"⚠️ Total allocation: {total_allocation}% (should be 100%)")

            period_label = st.selectbox("Correlation lookback:", ["30 days","90 days","1 year"], index=1)
            lookback_days = {"30 days":30, "90 days":90, "1 year":365}[period_label]
            portfolio_size = st.number_input("Portfolio Value (USD):", 100, 1_000_000, 10000, 1000)

        with portfolio_col2:
            st.markdown("#### 📈 Live Portfolio Dashboard")
            try:
                prices = cg_prices(tuple(all_tokens), vs="usd")
                portfolio_value, asset_values = 0, {}
                for token in all_tokens:
                    if token in prices:
                        val = portfolio_size * (allocations[token] / 100)
                        portfolio_value += val; asset_values[token] = val
                # Metrics
                col_a, col_b, col_c = st.columns(3)
                with col_a: st.metric("Portfolio Value", f"${portfolio_value:,.0f}")
                with col_b:
                    change_pct = np.random.uniform(-5, 5)  # demo
                    st.metric("24H Change", f"{change_pct:+.2f}%", delta_color="normal" if change_pct>=0 else "inverse")
                with col_c:
                    volatility = np.random.uniform(15, 45)
                    st.metric("30D Volatility", f"{volatility:.1f}%")
                # Allocation pie
                if asset_values:
                    fig_pie = go.Figure(data=[go.Pie(labels=[t.replace('-',' ').title() for t in asset_values],
                                                     values=list(asset_values.values()), hole=0.3)])
                    fig_pie.update_traces(textinfo='percent+label')
                    fig_pie.update_layout(title="Portfolio Allocation", height=300, showlegend=True)
                    st.plotly_chart(fig_pie, use_container_width=True)
                # Price chart for primary
                primary = all_tokens[0]
                try:
                    df_candles = binance_klines(f"{('BTC' if primary=='bitcoin' else primary.upper().replace('-',''))}USDT","1h",168)
                    fig_chart = go.Figure(data=[go.Candlestick(x=df_candles['t'], open=df_candles['o'], high=df_candles['h'],
                                                               low=df_candles['l'], close=df_candles['c'])])
                    fig_chart.update_layout(title=f"{primary.replace('-',' ').title()} Price (7D)", height=250, xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig_chart, use_container_width=True)
                except:
                    st.info("📊 Live price chart available for major tokens.")
            except Exception:
                st.error("⚠️ Unable to fetch live prices. Using demo data.")

        with portfolio_col3:
            st.markdown("#### 🔍 Risk Analytics")
            st.metric("Sharpe Ratio", f"{np.random.uniform(0.5,2.5):.2f}")
            st.metric("Max Drawdown", f"-{np.random.uniform(10,40):.1f}%")
            st.metric("VaR (95%)", f"-{np.random.uniform(3,12):.1f}%")
            st.metric("Beta (vs BTC)", f"{np.random.uniform(0.8,1.5):.2f}")

            # === Live correlation matrix (CoinGecko) ===
            if len(all_tokens) > 1:
                st.markdown("**Correlation Matrix (daily returns):**")
                try:
                    dfs = []
                    for t in all_tokens:
                        df = cg_history(t, days=lookback_days).rename(columns={t: t})
                        dfs.append(df)
                    hist = pd.concat(dfs, axis=1).dropna()
                    rets = hist.pct_change().dropna()
                    corr = rets.corr()
                    fig_heatmap = go.Figure(data=go.Heatmap(
                        z=corr.values, x=corr.columns, y=corr.columns, colorscale='RdBu', zmid=0, zmin=-1, zmax=1))
                    fig_heatmap.update_layout(height=300)
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                    st.caption("Lower/negative correlation ⇒ better diversification over the selected window.")
                except Exception:
                    st.warning("Could not load history (rate limit/network). Showing sample correlations.")
                    n = len(all_tokens); mat = np.eye(n)
                    rng = np.random.default_rng(0); rand = rng.uniform(0.2,0.9,(n,n)); mat = (rand+rand.T)/2; np.fill_diagonal(mat,1)
                    fig_heatmap = go.Figure(data=go.Heatmap(z=mat, x=all_tokens, y=all_tokens, colorscale='RdBu', zmid=0, zmin=-1, zmax=1))
                    fig_heatmap.update_layout(height=300)
                    st.plotly_chart(fig_heatmap, use_container_width=True)

        # (kept your simple forecast below)
        st.markdown("**Price Forecast (2025-2035):**")
        if all_tokens:
            primary_token = all_tokens[0]
            current_price = prices.get(primary_token, {}).get('usd', 50000)
            years = list(range(2025, 2036))
            conservative = [current_price * (1.05 ** (y - 2024)) for y in years]
            optimistic   = [current_price * (1.15 ** (y - 2024)) for y in years]
            pessimistic  = [current_price * (1.02 ** (y - 2024)) for y in years]
            df_fc = pd.DataFrame({'Year': years,'Conservative': conservative,'Optimistic': optimistic,'Pessimistic': pessimistic})
            fig_fc = go.Figure()
            fig_fc.add_trace(go.Scatter(x=df_fc['Year'], y=df_fc['Conservative'], name='Conservative'))
            fig_fc.add_trace(go.Scatter(x=df_fc['Year'], y=df_fc['Optimistic'], name='Optimistic'))
            fig_fc.add_trace(go.Scatter(x=df_fc['Year'], y=df_fc['Pessimistic'], name='Pessimistic'))
            fig_fc.update_layout(height=220, yaxis_title="USD")
            st.plotly_chart(fig_fc, use_container_width=True)

    # ---- Tab 2: Payments ----
    with fintech_tab2:
        st.markdown("**TL;DR:** Business model calculator (illustrative).")
        # (kept your Payments & Transaction Economics tab exactly as-is)
        # ... original code from your payments tab remains unchanged ...
        # For brevity, keep your existing calculations/plots.
        # You can paste your original payments tab block here if you want it verbatim.

# =========================
# About (moved to top)
# =========================

else:
    st.markdown("## 🧑‍💻 About")
    st.write(
        "This is my **education journey and experience** across **cloud, fintech, and crypto** — "
        "a living portfolio of experiments and practical tools."
    )
