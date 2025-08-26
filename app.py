# app.py — Cloud & Crypto Dashboard (Streamlit)
import time
import random
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go

# ---------------------------------------------------------
# Page config
# ---------------------------------------------------------
st.set_page_config(
    page_title="Cloud & Crypto Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Helpers & cached APIs
# ---------------------------------------------------------
@st.cache_data(ttl=15)
def cg_prices(ids=("bitcoin", "ethereum", "solana"), vs="usd"):
    """CoinGecko spot prices (cached)."""
    r = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={"ids": ",".join(ids), "vs_currencies": vs},
        timeout=8,
    )
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=60)
def binance_klines(symbol="BTCUSDT", interval="1h", limit=168):
    """Candles for Binance symbols."""
    r = requests.get(
        "https://api.binance.com/api/v3/klines",
        params={"symbol": symbol, "interval": interval, "limit": int(limit)},
        timeout=8,
    )
    r.raise_for_status()
    kl = r.json()
    df = pd.DataFrame(
        kl,
        columns=["t","o","h","l","c","v","ct","qv","n","tb","tqv","i"],
    )
    df["t"] = pd.to_datetime(df["t"], unit="ms")
    for c in ["o","h","l","c","v"]:
        df[c] = df[c].astype(float)
    return df[["t","o","h","l","c","v"]]

# Map Coingecko IDs → Binance USDT symbols (major assets only)
BINANCE_SYMBOLS = {
    "bitcoin": "BTCUSDT",
    "ethereum": "ETHUSDT",
    "cardano": "ADAUSDT",
    "solana": "SOLUSDT",
    "polkadot": "DOTUSDT",
    "binancecoin": "BNBUSDT",
    "chainlink": "LINKUSDT",
    "uniswap": "UNIUSDT",
    "aave": "AAVEUSDT",
    "compound-governance-token": "COMPUSDT",
    # Stablecoins intentionally excluded from correlation:
    "usd-coin": "USDCUSDT",
    "dai": "DAIUSDT",
    "tether": None,
    "busd": None,
}

def compute_corr_for_tokens(token_ids, interval="1d", limit=90):
    """
    Build a correlation matrix from recent close-to-close returns
    for supported tokens (excludes stables by default).
    """
    # Exclude stables (low signal / odd pairs) and unknowns
    stables = {"usd-coin", "dai", "tether", "busd"}
    token_ids = [t for t in token_ids if t not in stables and BINANCE_SYMBOLS.get(t)]
    token_ids = token_ids[:8]  # keep it light

    series = {}
    for tid in token_ids:
        try:
            sym = BINANCE_SYMBOLS[tid]
            df = binance_klines(sym, interval=interval, limit=limit)
            s = df.set_index("t")["c"].pct_change().dropna()
            if len(s) > 5:
                series[tid] = s
        except Exception:
            continue

    if len(series) < 2:
        return None  # not enough for a matrix

    # Align on intersection of timestamps
    df_ret = pd.concat(series, axis=1).dropna()
    corr = df_ret.corr()
    return corr

# ---------------------------------------------------------
# Compliance utilities (kept as-is for Cloud page)
# ---------------------------------------------------------
def get_compliance_recommendations(model, data_sensitivity, compliance_reqs, industry):
    sensitivity_reqs = {
        "Public (marketing data)": {
            "encryption": "Standard TLS in transit",
            "access_controls": "Basic IAM roles",
            "data_residency": "Any region acceptable",
            "audit_logging": "Basic access logs",
            "backup_retention": "30 days"
        },
        "Internal (business metrics)": {
            "encryption": "TLS 1.3 + encryption at rest",
            "access_controls": "Role-based access (RBAC)",
            "data_residency": "Preferred region/country",
            "audit_logging": "Detailed access + change logs",
            "backup_retention": "90 days"
        },
        "Confidential (customer PII)": {
            "encryption": "AES-256 + field-level encryption for PII",
            "access_controls": "Strict RBAC + MFA required",
            "data_residency": "Must stay in specific region",
            "audit_logging": "Full audit trail + real-time alerts",
            "backup_retention": "7 years (legal requirement)"
        },
        "Restricted (financial/health records)": {
            "encryption": "FIPS 140-2 Level 3 + HSM key management",
            "access_controls": "Zero-trust + privileged access mgmt",
            "data_residency": "On-premises or certified cloud only",
            "audit_logging": "Immutable audit logs + compliance reports",
            "backup_retention": "10+ years (regulatory requirement)"
        }
    }

    compliance_details = {
        "GDPR": {
            "key_requirements": ["Right to be forgotten", "Data portability", "Privacy by design", "DPO appointment"],
            "technical_controls": ["Pseudonymization", "Encryption", "Access controls", "Breach notification (72hrs)"],
            "deployment_impact": {
                "🏠 On-premises": "✅ Full control over data location and processing",
                "☁️ Public Cloud": "⚠️ Need EU-based regions + data processing agreements",
                "🌉 Hybrid Cloud": "⚠️ Ensure EU data stays in compliant locations"
            }
        },
        "HIPAA": {
            "key_requirements": ["PHI protection", "Business Associate Agreements", "Risk assessments", "Employee training"],
            "technical_controls": ["End-to-end encryption", "Access controls", "Audit logs", "Secure transmission"],
            "deployment_impact": {
                "🏠 On-premises": "✅ Maximum control, easier compliance audits",
                "☁️ Public Cloud": "⚠️ Requires HIPAA-compliant services + BAAs",
                "🌉 Hybrid Cloud": "⚠️ PHI must stay in HIPAA-compliant environments"
            }
        },
        "SOX": {
            "key_requirements": ["Financial data integrity", "Change controls", "Segregation of duties", "Audit trails"],
            "technical_controls": ["Immutable logs", "Change approval workflows", "Access reviews", "Data integrity checks"],
            "deployment_impact": {
                "🏠 On-premises": "✅ Direct control over financial systems",
                "☁️ Public Cloud": "✅ Use SOC 2 Type II certified services",
                "🌉 Hybrid Cloud": "⚠️ Ensure consistent controls across environments"
            }
        },
        "PCI-DSS": {
            "key_requirements": ["Cardholder data protection", "Network segmentation", "Regular testing", "Access monitoring"],
            "technical_controls": ["Network segmentation", "WAF", "Encryption", "Vulnerability scanning"],
            "deployment_impact": {
                "🏠 On-premises": "✅ Full control but expensive PCI compliance",
                "☁️ Public Cloud": "✅ Use PCI-DSS certified cloud services",
                "🌉 Hybrid Cloud": "⚠️ Payments should be in certified env"
            }
        },
        "ISO 27001": {
            "key_requirements": ["ISMS", "Risk assessment", "Security controls", "Continuous improvement"],
            "technical_controls": ["Security policies", "Access controls", "Incident response", "Security monitoring"],
            "deployment_impact": {
                "🏠 On-premises": "✅ Full control over implementation",
                "☁️ Public Cloud": "✅ Leverage provider's ISO 27001 cert",
                "🌉 Hybrid Cloud": "⚠️ Keep controls consistent across both"
            }
        }
    }

    industry_considerations = {
        "Financial Services": {
            "key_risks": ["Regulatory fines", "Data breaches", "System downtime"],
            "recommended_model": "🏠 On-premises or 🌉 Hybrid",
            "rationale": "Core systems often must remain private for regulation"
        },
        "Healthcare": {
            "key_risks": ["HIPAA violations", "Patient safety", "Data breaches"],
            "recommended_model": "🏠 On-premises or 🌉 Hybrid",
            "rationale": "Patient data requires strict controls and audit trails"
        },
        "Government": {
            "key_risks": ["Security breaches", "Data sovereignty", "Public trust"],
            "recommended_model": "🏠 On-premises",
            "rationale": "Often needs air-gapped / classified environments"
        },
        "E-commerce/Retail": {
            "key_risks": ["PCI compliance", "Customer data", "Seasonal scaling"],
            "recommended_model": "☁️ Public Cloud or 🌉 Hybrid",
            "rationale": "Scale for traffic spikes while protecting payment data"
        },
        "Manufacturing": {
            "key_risks": ["Operational downtime", "IP theft", "Supply chain"],
            "recommended_model": "🌉 Hybrid Cloud",
            "rationale": "Factory stays local; analytics in cloud"
        },
        "Technology/SaaS": {
            "key_risks": ["Availability", "Customer data", "Competitive edge"],
            "recommended_model": "☁️ Public Cloud",
            "rationale": "Global scale & rapid delivery"
        }
    }

    base_reqs = sensitivity_reqs[data_sensitivity]
    industry_info = industry_considerations[industry]

    recs = {
        "data_requirements": base_reqs,
        "industry_context": industry_info,
        "compliance_details": {},
        "deployment_recommendation": "",
        "implementation_priority": [],
        "estimated_complexity": "",
        "timeline_estimate": ""
    }

    if compliance_reqs and "None" not in compliance_reqs:
        for c in compliance_reqs:
            if c in compliance_details:
                recs["compliance_details"][c] = compliance_details[c]

    if data_sensitivity == "Restricted (financial/health records)":
        recs["deployment_recommendation"] = (
            "⚠️ HIGH RISK: Restricted data typically requires on-premises or certified private cloud"
            if model == "☁️ Public Cloud" else "✅ GOOD FIT: Recommended for restricted data"
        )
    elif data_sensitivity == "Confidential (customer PII)":
        if any(comp in ["HIPAA", "PCI-DSS"] for comp in compliance_reqs):
            recs["deployment_recommendation"] = "⚠️ MODERATE RISK: Needs careful provider selection/config"
        else:
            recs["deployment_recommendation"] = "✅ ACCEPTABLE: With strong encryption & access controls"
    else:
        recs["deployment_recommendation"] = "✅ SUITABLE: Standard cloud security practices sufficient"

    if data_sensitivity in ["Restricted (financial/health records)", "Confidential (customer PII)"]:
        recs["implementation_priority"] = [
            "1. Data classification & mapping",
            "2. Encryption & key management (HSM/KMS)",
            "3. Identity & access management (RBAC/MFA)",
            "4. Audit logging & monitoring",
            "5. Backup & disaster recovery",
        ]
        recs["estimated_complexity"] = "HIGH - Needs specialized security expertise"
        recs["timeline_estimate"] = "6-12 months for full implementation"
    else:
        recs["implementation_priority"] = [
            "1. Basic access controls",
            "2. Encrypt in transit & at rest",
            "3. Regular backups",
            "4. Monitoring & alerting",
            "5. Documentation & training",
        ]
        recs["estimated_complexity"] = "MEDIUM - Standard controls"
        recs["timeline_estimate"] = "2-4 months for full implementation"

    return recs

def display_compliance_recommendations(model, data_sensitivity, compliance_reqs, industry):
    recs = get_compliance_recommendations(model, data_sensitivity, compliance_reqs, industry)

    st.markdown("### 🎯 Deployment Fit Assessment")
    txt = recs["deployment_recommendation"]
    if "HIGH RISK" in txt:
        st.error(txt)
    elif "MODERATE RISK" in txt:
        st.warning(txt)
    else:
        st.success(txt)

    st.markdown("### 🏢 Industry-Specific Considerations")
    info = recs["industry_context"]
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Recommended Model:** {info['recommended_model']}")
        st.write("**Key Risks:**")
        for r in info["key_risks"]:
            st.write("•", r)
    with c2:
        st.write("**Rationale:**", info["rationale"])

    st.markdown("### 🔒 Security Requirements")
    req = recs["data_requirements"]
    a, b = st.columns(2)
    with a:
        st.write("**Encryption:**", req["encryption"])
        st.write("**Access Controls:**", req["access_controls"])
        st.write("**Data Residency:**", req["data_residency"])
    with b:
        st.write("**Audit Logging:**", req["audit_logging"])
        st.write("**Backup Retention:**", req["backup_retention"])

    if recs["compliance_details"]:
        st.markdown("### 📋 Compliance Requirements")
        for name, details in recs["compliance_details"].items():
            with st.expander(f"{name} Compliance Details"):
                st.write("**Key Requirements:**")
                for k in details["key_requirements"]:
                    st.write("•", k)
                st.write("**Technical Controls:**")
                for c in details["technical_controls"]:
                    st.write("•", c)
                st.write("**Deployment Model Impact:**")
                for m, impact in details["deployment_impact"].items():
                    (st.success if "✅" in impact else st.warning)(f"{m}: {impact}")

    st.markdown("### 🚀 Implementation Roadmap")
    x, y = st.columns(2)
    with x:
        st.write("**Priority Order:**")
        for step in recs["implementation_priority"]:
            st.write(step)
    with y:
        st.write("**Complexity:** **", recs["estimated_complexity"], "**")
        st.write("**Timeline:** **", recs["timeline_estimate"], "**")

    st.markdown("### ⚠️ Overall Risk")
    if data_sensitivity == "Restricted (financial/health records)":
        st.write("**🔴 CRITICAL**")
        st.caption("Highest safeguards required; prefer on-prem or dedicated compliance cloud.")
    elif data_sensitivity == "Confidential (customer PII)":
        lvl = "🟠 HIGH" if any(c in ["HIPAA", "PCI-DSS", "SOX"] for c in compliance_reqs) else "🟡 MEDIUM"
        st.write(f"**{lvl}**")
        st.caption("Strong enterprise controls required.")
    elif data_sensitivity == "Internal (business metrics)":
        st.write("**🟡 MEDIUM**")
        st.caption("Standard business controls.")
    else:
        st.write("**🟢 LOW**")
        st.caption("Basic best practices suffice.")

# ---------------------------------------------------------
# Sidebar (matches screenshot; About first)
# ---------------------------------------------------------
st.sidebar.markdown("### 🧭 Navigate")
st.sidebar.caption(f"Last updated: {time.strftime('%H:%M:%S')}")
page = st.sidebar.radio(
    "",
    ["ℹ️ About", "🏗️ Cloud Architectures", "🏦 Fintech & Crypto"],
    label_visibility="collapsed",
    index=0,
)

# ---------------------------------------------------------
# ℹ️ About (on top)
# ---------------------------------------------------------
if page == "ℹ️ About":
    st.markdown("## Cloud & Crypto Dashboard")
    st.caption("**TL;DR:** Overview page. Static description + links. Shows what this app is and how to use it.")

    st.markdown(
        """
### 👨‍🎓 My learning journey
Hi! This is a compact, interactive portfolio that documents my **education journey** and hands-on
experience across **cloud architecture** and **crypto/fintech analytics**.  
You’ll find:
- a decision aide for **cloud** trade-offs (cost, security, compliance), and  
- a **crypto** workspace with live pricing and diversification tools.

Use the sidebar to jump between sections. Enjoy exploring! 🚀
        """
    )

# ---------------------------------------------------------
# 🏗️ Cloud Architectures (unchanged logic; small TL;DR)
# ---------------------------------------------------------
elif page == "🏗️ Cloud Architectures":
    # Tiny TL;DR (does not change layout/logic)
    st.caption(
        "**TL;DR:** Interactive advisor. Placeholder cost model + rules-based "
        "compliance guidance to illustrate trade-offs by industry/size."
    )

    st.markdown("""
    # 🏗️ Cloud Architectures: Choose Your Adventure
    
    **Think of this like choosing where to build your house:**
    - 🏠 **On-premises** = Build on your own land (you control everything)  
    - ☁️ **Public Cloud** = Rent a managed apartment (provider handles maintenance)
    - 🌉 **Hybrid Cloud** = Own a house + rent city apartment (best of both worlds)
    """)

    st.info("💡 **Try this:** Adjust the sliders below and watch how costs change for different scenarios!")

    # Interactive Controls Section
    st.markdown("## 🎛️ Interactive Cost Calculator")
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("### Choose Your Cloud Strategy")
        model = st.radio(
            "Pick a deployment model to see real-world examples:",
            ["🏠 On-premises", "☁️ Public Cloud", "🌉 Hybrid Cloud"],
            index=1,
            help="Each model has different trade-offs in cost, control, and complexity",
        )

        st.markdown("### Your Business Scenario")
        company_size = st.selectbox(
            "Company size",
            ["Startup (1-50 employees)", "SME (51-500 employees)", "Enterprise (500+ employees)"],
            index=1,
        )

        industry = st.selectbox(
            "Industry vertical",
            ["Financial Services", "Healthcare", "E-commerce/Retail", "Manufacturing", "Government", "Technology/SaaS"],
            index=0,
        )

        st.markdown("### Workload Requirements")
        ingest_gb = st.slider(
            "Daily data processing (GB)",
            1, 500, 40, 5,
            help="Think: customer transactions, IoT sensors, log files, etc.",
        )

        users = st.slider(
            "People using analytics dashboards",
            5, 1000, 60, 5,
            help="Business analysts, data scientists, executives viewing reports",
        )

        st.markdown("### Security & Compliance Needs")
        data_sensitivity = st.selectbox(
            "Data sensitivity level",
            ["Public (marketing data)", "Internal (business metrics)", "Confidential (customer PII)", "Restricted (financial/health records)"],
            index=2,
        )

        compliance_reqs = st.multiselect(
            "Compliance requirements",
            ["GDPR", "HIPAA", "SOX", "PCI-DSS", "ISO 27001", "None"],
            default=["GDPR"],
        )

        network_isolation = st.select_slider(
            "Network security level",
            options=["Basic", "Standard", "High", "Maximum"],
            value="Standard",
            help="How isolated should your systems be from the internet?",
        )

    with col_right:
        st.markdown("### 💰 Cost Breakdown")
        base_costs = {"🏠 On-premises": 800, "☁️ Public Cloud": 200, "🌉 Hybrid Cloud": 400}
        base_cost = base_costs[model]
        data_cost = ingest_gb * 2.5
        user_cost = users * 1.2

        security_multiplier = {"Basic": 1.0, "Standard": 1.2, "High": 1.5, "Maximum": 2.0}[network_isolation]
        compliance_cost = len(compliance_reqs) * 150 if compliance_reqs != ["None"] else 0
        industry_multiplier = {
            "Financial Services": 1.4,
            "Healthcare": 1.3,
            "Government": 1.5,
            "E-commerce/Retail": 1.1,
            "Manufacturing": 1.2,
            "Technology/SaaS": 1.0,
        }[industry]
        size_multiplier = {
            "Startup (1-50 employees)": 0.8,
            "SME (51-500 employees)": 1.0,
            "Enterprise (500+ employees)": 1.3,
        }[company_size]

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

    with st.expander("📋 Quick Model Overview"):
        if model == "🏠 On-premises":
            st.success("✅ **Benefits:** Complete control; data never leaves your building")
            st.warning("⚠️ **Challenges:** High upfront costs; you handle maintenance")
        elif model == "☁️ Public Cloud":
            st.success("✅ **Benefits:** Pay-as-you-go, automatic updates, global scale")
            st.warning("⚠️ **Challenges:** Ongoing costs; less control; internet dependency")
        else:
            st.success("✅ **Benefits:** Keep sensitive data private; burst to cloud when needed")
            st.warning("⚠️ **Challenges:** More complex to manage; expertise needed in both")

    st.markdown("---")
    st.markdown("## 🏗️ Cloud Service Models: IaaS vs PaaS vs SaaS")
    st.markdown("**Transport analogy:** 🚗 IaaS • 🚌 PaaS • 🚕 SaaS")
    service_col1, service_col2 = st.columns([1, 2])
    with service_col1:
        selected_service = st.selectbox(
            "Choose a service model to explore:",
            ["🚗 IaaS (Infrastructure as a Service)", "🚌 PaaS (Platform as a Service)", "🚕 SaaS (Software as a Service)"],
        )
    with service_col2:
        if "IaaS" in selected_service:
            st.markdown("""### 🚗 IaaS
**You manage:** OS, patches, apps, data  
**You get:** VMs, storage, networks  
**Examples:** AWS EC2, GCE, Azure VMs""")
        elif "PaaS" in selected_service:
            st.markdown("""### 🚌 PaaS
**You manage:** Your code & data  
**You get:** Runtime, DBs, dev tools  
**Examples:** Heroku, App Engine, AWS Lambda""")
        else:
            st.markdown("""### 🚕 SaaS
**You manage:** Accounts & usage  
**You get:** Ready apps in browser  
**Examples:** Salesforce, Google Workspace, Zoom""")

    st.markdown("### 👥 Who's Responsible for What?")
    responsibilities = [
        "Physical Data Centers","Network & Security Infrastructure","Virtual Machines & Storage",
        "Operating System & Updates","Runtime & Development Tools","Application Code & Logic",
        "User Data & Access Control","Business Processes & Training"
    ]
    iaas_resp = ["🟢","🟢","🟢","🔴","🔴","🔴","🔴","🔴"]
    paas_resp = ["🟢","🟢","🟢","🟢","🟢","🔴","🔴","🔴"]
    saas_resp = ["🟢","🟢","🟢","🟢","🟢","🟢","🟡","🔴"]
    resp_df = pd.DataFrame({"Responsibility Layer": responsibilities, "IaaS": iaas_resp, "PaaS": paas_resp, "SaaS": saas_resp})
    st.dataframe(resp_df, use_container_width=True, hide_index=True)
    st.caption("🟢 Provider • 🟡 Shared • 🔴 You")

# ---------------------------------------------------------
# 🏦 Fintech & Crypto
# ---------------------------------------------------------
else:  # "🏦 Fintech & Crypto"
    st.markdown("# 🏦 Fintech & Crypto")
    st.caption("**TL;DR:** Live spot prices via CoinGecko; live candles via Binance for selected primary asset. "
               "Correlation matrix uses recent Binance daily closes (best effort). Revenue tab is a simulator (placeholders).")

    tab1, tab2 = st.tabs(["💰 Crypto Portfolio", "💳 Payment Economics"])

    # --------------------- Tab 1: Crypto Portfolio ---------------------
    with tab1:
        st.caption("**TL;DR:** Real-time prices + live chart (primary asset). Correlation is computed from recent daily returns; "
                   "if an exchange pair isn’t available, we fall back to a demo heatmap.")

        col1, col2, col3 = st.columns([3, 4, 3])

        with col1:
            st.markdown("#### 🎛️ Portfolio Builder")

            major_tokens = st.multiselect(
                "Major cryptocurrencies:",
                ["bitcoin", "ethereum", "binancecoin", "cardano", "solana", "polkadot", "chainlink"],
                default=["bitcoin", "ethereum"],
                key="major",
            )
            stable_tokens = st.multiselect(
                "Stablecoins:",
                ["tether", "usd-coin", "dai"],
                default=["usd-coin"],
                key="stable",
            )
            defi_tokens = st.multiselect(
                "DeFi tokens:",
                ["uniswap", "aave", "compound-governance-token"],
                default=[],
                key="defi",
            )

            all_tokens = major_tokens + stable_tokens + defi_tokens
            if not all_tokens:
                all_tokens = ["bitcoin", "ethereum"]

            st.markdown("**Allocation (must sum to 100%)**")
            allocations, total_alloc = {}, 0
            for tid in all_tokens:
                pretty = tid.replace("-", " ").title()
                default_val = max(0, 100 // len(all_tokens))
                val = st.slider(pretty, 0, 100, default_val, key=f"alloc_{tid}")
                allocations[tid] = val
                total_alloc += val
            if total_alloc != 100:
                st.warning(f"⚠️ Total allocation: {total_alloc}% (should be 100%)")

            period = st.selectbox("Analysis period", ["7D", "30D", "90D", "1Y"], index=1)
            portfolio_size = st.number_input("Portfolio value (USD)", 100, 1_000_000, 10_000, step=1000)

        with col2:
            st.markdown("#### 📈 Live Portfolio Dashboard")
            try:
                prices = cg_prices(tuple(all_tokens), vs="usd")
            except Exception:
                prices = {}

            # Key metrics
            pvalue = 0
            asset_values = {}
            for t in all_tokens:
                px = prices.get(t, {}).get("usd")
                alloc = allocations.get(t, 0) / 100
                val = portfolio_size * alloc
                asset_values[t] = val
                pvalue += val

            a, b, c = st.columns(3)
            a.metric("Portfolio Value", f"${pvalue:,.0f}")
            # demo 24h change & vol (since CG simple endpoint lacks it)
            b.metric("24H Change", f"{np.random.uniform(-5,5):+.2f}%")
            c.metric("30D Volatility", f"{np.random.uniform(15,45):.1f}%")

            # Allocation pie
            if asset_values:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=[t.replace("-", " ").title() for t in asset_values.keys()],
                    values=list(asset_values.values()),
                    hole=0.35,
                )])
                fig_pie.update_traces(textinfo="percent+label")
                fig_pie.update_layout(title="Portfolio Allocation", height=320)
                st.plotly_chart(fig_pie, use_container_width=True)

            # Live candlestick for primary asset (if supported)
            primary = all_tokens[0]
            sym = BINANCE_SYMBOLS.get(primary)
            if sym:
                try:
                    df = binance_klines(sym, interval="1h", limit=168)  # ~7D
                    fig = go.Figure(data=[go.Candlestick(
                        x=df["t"], open=df["o"], high=df["h"], low=df["l"], close=df["c"]
                    )])
                    fig.update_layout(title=f"{primary.replace('-', ' ').title()} Price (7D, 1h)", xaxis_rangeslider_visible=False, height=260)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    st.info("Live chart temporarily unavailable for this asset.")

        with col3:
            st.markdown("#### 🔍 Risk Analytics")
            st.metric("Sharpe (demo)", f"{np.random.uniform(0.6,2.2):.2f}")
            st.metric("Max Drawdown (demo)", f"-{np.random.uniform(10,40):.1f}%")
            st.metric("VaR 95% (demo)", f"-{np.random.uniform(3,12):.1f}%")
            st.metric("Beta vs BTC (demo)", f"{np.random.uniform(0.8,1.5):.2f}")

            # --- Correlation matrix ---
            st.markdown("**Correlation Matrix (daily returns)**")
            corr = None
            try:
                corr = compute_corr_for_tokens(all_tokens, interval="1d", limit=90)
            except Exception:
                corr = None

            if corr is not None:
                labels = [t.replace("-", " ").title() for t in corr.columns]
                fig_heat = go.Figure(
                    data=go.Heatmap(
                        z=corr.values,
                        x=labels,
                        y=labels,
                        colorscale="RdBu",
                        zmin=-1, zmax=1,
                    )
                )
                fig_heat.update_layout(height=300)
                st.plotly_chart(fig_heat, use_container_width=True)
                st.caption("Computed from recent Binance daily closes. Higher = move together; lower = diversify.")
            else:
                # fallback placeholder
                n = len(all_tokens)
                if n >= 2:
                    rng = np.random.default_rng(42)
                    M = rng.uniform(0.2, 0.9, (n, n))
                    M = (M + M.T) / 2
                    np.fill_diagonal(M, 1.0)
                    labels = [t.replace("-", " ").title() for t in all_tokens]
                    fig_heat = go.Figure(data=go.Heatmap(z=M, x=labels, y=labels, colorscale="RdBu", zmin=-1, zmax=1))
                    fig_heat.update_layout(height=300)
                    st.plotly_chart(fig_heat, use_container_width=True)
                    st.caption("Demo matrix (fallback). Some pairs may not be available on Binance or rate-limited.")

        st.markdown("**Simple 2025-2035 Scenario Forecast (demo)**")
        try:
            current = cg_prices((primary,), vs="usd").get(primary, {}).get("usd", 20_000)
        except Exception:
            current = 20_000
        years = list(range(2025, 2036))
        conservative = [current * (1.05 ** (y - 2024)) for y in years]
        optimistic = [current * (1.15 ** (y - 2024)) for y in years]
        pessimistic = [current * (1.02 ** (y - 2024)) for y in years]
        fig_fx = go.Figure()
        fig_fx.add_trace(go.Scatter(x=years, y=conservative, name="Conservative"))
        fig_fx.add_trace(go.Scatter(x=years, y=optimistic, name="Optimistic"))
        fig_fx.add_trace(go.Scatter(x=years, y=pessimistic, name="Pessimistic"))
        fig_fx.update_layout(height=230, yaxis_title="USD")
        st.plotly_chart(fig_fx, use_container_width=True)

    # --------------------- Tab 2: Payment Economics ---------------------
    with tab2:
        st.caption("**TL;DR:** Simulator (placeholder). Model revenue streams and unit economics; no live payments data.")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 📊 Payment Method Trends (demo)")
            payment_methods = {
                'Credit Cards': [40, 38, 36, 35, 33],
                'Digital Wallets': [20, 25, 28, 32, 35],
                'Bank Transfers': [15, 15, 14, 13, 12],
                'BNPL': [5, 8, 12, 15, 18],
                'Cryptocurrency': [1, 2, 3, 4, 5]
            }
            years = [2020, 2021, 2022, 2023, 2024]
            fig_trends = go.Figure()
            for method, vals in payment_methods.items():
                fig_trends.add_trace(go.Scatter(x=years, y=vals, mode="lines+markers", name=method, stackgroup="one"))
            fig_trends.update_layout(title="Payment Method Market Share Evolution", yaxis_title="Market Share (%)", height=300)
            st.plotly_chart(fig_trends, use_container_width=True)

        with c2:
            st.markdown("#### 💰 Revenue Calculator (demo)")
            model = st.selectbox("Revenue Model", ["Transaction Fees", "Subscription + Fees", "Freemium"])
            monthly_users = st.slider("Monthly Active Users", 1_000, 10_000_000, 100_000, 10_000)
            avg_tx = st.slider("Avg Transaction ($)", 10, 1_000, 75)
            tx_per_user = st.slider("Transactions per User / Month", 1, 50, 8)

            if model == "Transaction Fees":
                fee_rate = st.slider("Fee (%)", 1.0, 5.0, 2.9, 0.1)
                fixed_fee = st.slider("Fixed per Tx ($)", 0.0, 1.0, 0.30, 0.05)
                mtx = monthly_users * tx_per_user
                vol = mtx * avg_tx
                rev = vol * fee_rate / 100 + mtx * fixed_fee
                st.metric("Monthly Volume", f"${vol:,.0f}")
                st.metric("Monthly Revenue", f"${rev:,.0f}")
                st.metric("Annual Revenue", f"${rev*12:,.0f}")
                rpu = rev / monthly_users
            else:
                sub_fee = st.slider("Subscription ($/mo)", 5, 100, 20)
                reduced = st.slider("Reduced Tx Fee (%)", 0.5, 3.0, 1.9, 0.1)
                sub_rev = monthly_users * sub_fee
                tx_rev = monthly_users * tx_per_user * avg_tx * reduced / 100
                total = sub_rev + tx_rev
                st.metric("Subscription Revenue", f"${sub_rev:,.0f}")
                st.metric("Transaction Revenue", f"${tx_rev:,.0f}")
                st.metric("Total Monthly Revenue", f"${total:,.0f}")
                rpu = total / monthly_users

            st.metric("Revenue per User", f"${rpu:.2f}/mo")
