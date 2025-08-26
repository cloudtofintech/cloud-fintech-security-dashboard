# app.py
import time, random, os
import streamlit as st
import pandas as pd
import numpy as np
import requests
from sklearn.ensemble import IsolationForest
import plotly.graph_objects as go

st.set_page_config(page_title="Cloud • Fintech • Security • Data Platforms", layout="wide")

# ======= Utilities =======

@st.cache_data(ttl=15)
def cg_prices(ids=("bitcoin","ethereum","solana"), vs="usd"):
    """Free CoinGecko spot prices (cached)."""
    r = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={"ids": ",".join(ids), "vs_currencies": vs},
        timeout=8,
    )
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=60)
def binance_klines(symbol="BTCUSDT", interval="1m", limit=60):
    """1-minute candles for last ~hour (REST)."""
    r = requests.get(
        "https://api.binance.com/api/v3/klines",
        params={"symbol": symbol, "interval": interval, "limit": limit},
        timeout=8,
    )
    r.raise_for_status()
    kl = r.json()
    df = pd.DataFrame(kl, columns=["t","o","h","l","c","v","ct","qv","n","tb","tqv","i"])
    df["t"] = pd.to_datetime(df["t"], unit="ms")
    for c in ["o","h","l","c","v"]:
        df[c] = df[c].astype(float)
    return df[["t","o","h","l","c","v"]]

def synth_auth_logs(n=800, seed=7):
    """Synthetic login events for SOC toy analytics."""
    random.seed(seed)
    rows = []
    for _ in range(n):
        fail_p = 0.12
        geo = random.choice(["SG","US","DE","CN","GB","IN","BR","AU"])
        device_risk = random.choice([0,1,2])  # 0=healthy ... 2=high
        mfa = random.choice([0,1])            # 1=on
        hour = random.randint(0,23)
        is_vpn = random.choice([0,0,0,1])
        # attacker-ish cluster
        if random.random() < 0.05:
            device_risk, mfa, is_vpn = 2, 0, 1
            hour = random.choice([2,3,4])
            fail_p = 0.7
        outcome = "fail" if random.random() < fail_p else "success"
        rows.append(dict(hour=hour, geo=geo, device_risk=device_risk,
                         mfa=mfa, is_vpn=is_vpn, outcome=outcome))
    return pd.DataFrame(rows)

def detect_anomalies(df):
    """IsolationForest on simple encoded features."""
    enc_geo = {g:i for i,g in enumerate(sorted(df["geo"].unique()))}
    dfn = df.copy()
    dfn["geo"] = dfn["geo"].map(enc_geo)
    dfn["outcome_num"] = (dfn["outcome"]=="fail").astype(int)
    X = dfn[["hour","geo","device_risk","mfa","is_vpn","outcome_num"]]
    model = IsolationForest(n_estimators=120, contamination=0.06, random_state=42)
    model.fit(X)
    df["anomaly"] = model.predict(X).astype(int).map({-1:1, 1:0})
    return df, model

def zero_trust_score(device:int, mfa:int, vpn:int, geo:int, fail:float, segmentation:int, rbac:int):
    """Toy composite risk score 0..100 (lower=safer)."""
    score = 20 + device*18 + vpn*15 + geo*10 + (fail*100)*0.25 + (2-segmentation)*10 + (2-rbac)*8
    if mfa == 1:
        score -= 15
    return max(0, min(100, score))

def arch_cost_estimate(ingest_gb: float, users: int, env: str):
    """Toy cost model for concept illustration."""
    base = dict(OnPrem=500, Private=200, Hybrid=300)
    key = "OnPrem" if env=="On-prem" else ("Private" if env=="Private Cloud" else "Hybrid")
    return round(base[key] + ingest_gb*2 + users*0.5, 2)

def shared_responsibility_matrix(model:str):
    """
    Return responsibility table (Customer/Shared/Provider) per layer for each model.
    """
    layers = [
        "Facilities/Physical", "Network", "Compute (IaaS)",
        "Platform (PaaS)", "Apps (SaaS/Custom)", "Data", "Identity & Access"
    ]
    # 0 = Customer, 1 = Provider, 0.5 = Shared
    if model == "On-prem":
        vals = [0,0,0,0,0,0,0]
    elif model == "Private Cloud":
        vals = [1,1,0.5,0.5,0,0,0.5]
    else:  # Hybrid
        vals = [0.5,0.5,0.5,0.5,0,0,0.5]
    who = ["Customer" if v==0 else ("Provider" if v==1 else "Shared") for v in vals]
    return pd.DataFrame({"Layer": layers, "Responsibility": who, "Code": vals})

def iaas_paas_saas_cards():
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### IaaS\nVMs, storage, networks.\n\n**Examples:** EC2, GCE, Azure VMs")
    with c2:
        st.markdown("### PaaS\nManaged runtimes & DBs.\n\n**Examples:** Cloud Run, App Engine, Heroku, RDS/Cloud SQL")
    with c3:
        st.markdown("### SaaS\nComplete apps.\n\n**Examples:** Salesforce, Google Workspace, Snowflake (as delivered service)")

def platform_reco(workload:str, data_type:str, team_skill:str, budget:str):
    """Simple Snowflake vs Databricks fit helper."""
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
        "Snowflake": [
            "Elastic cloud DW (compute/storage separation), strong SQL UX",
            "Snowpark for Python/Java/Scala; secure data sharing/collab",
            "Cross-cloud, governance features; Iceberg/Unistore options"
        ],
        "Databricks": [
            "Lakehouse (Delta) unifies BI + ML; great notebooks & MLflow",
            "Streaming + batch on open formats (Delta/Parquet/Iceberg)",
            "Unity Catalog for governance; Photon engine for fast SQL"
        ],
    }
    return reco, s, d, bullets

# ======= UI Shell =======

st.title("Cloud x Fintech x Security — Interactive Portfolio")
st.sidebar.caption(f"Deployed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

page = st.sidebar.radio(
    "Navigate",
    ["1) Cloud Architectures", "2) Fintech: Live Crypto", "3) Cybersecurity Lab", "4) Data Platforms", "About"]
)

# ======= 1) Cloud Architectures (richer + WHY verticals) =======

if page.startswith("1"):
    st.subheader("On-prem • Private • Hybrid — plus IaaS / PaaS / SaaS and WHY")

    # --- Controls
    top_l, top_r = st.columns([2,3], gap="large")
    with top_l:
        model = st.radio("Deployment model", ["On-prem","Private Cloud","Hybrid"], index=2, horizontal=True)
        ingest_gb = st.slider("Daily data ingestion (GB)", 1, 200, 40)
        users = st.slider("Concurrent analytics users", 5, 500, 60, 5)
        mfa = st.selectbox("MFA enforced?", [1,0], index=0, format_func=lambda x: "Yes" if x==1 else "No")
        seg = st.select_slider("Network segmentation depth", options=[0,1,2], value=1)
        rbac = st.select_slider("RBAC granularity", options=[0,1,2], value=1)
        st.metric("Est. monthly infra cost (toy)", f"${arch_cost_estimate(ingest_gb, users, model):,}")

    with top_r:
        st.markdown("**Narrative:** Use the knobs to discuss _scale_, _governance_, and _placement_.")
        if model=="On-prem":
            st.write("• All layers managed in-house. ✅ Residency & control • ❌ Elasticity & CapEx burden.")
        elif model=="Private Cloud":
            st.write("• Provider manages lower stack; you focus on data/apps. ✅ Elastic & managed • ❌ Some lock-in risk.")
        else:
            st.write("• Place sensitive workloads privately; burst analytics to cloud. ✅ Best of both • ❌ Governance discipline needed.")

    st.markdown("---")

    # --- IaaS/PaaS/SaaS quick cards
    iaas_paas_saas_cards()

    st.markdown("---")

    # --- WHY vertical (When it shines / Watchouts / Use cases)
    st.markdown("#### WHY this model?")
    col1, col2, col3 = st.columns(3, gap="large")

    def why_block(title, shines, watch, cases):
        st.markdown(f"**{title}**")
        st.write("**When it shines**")
        for s in shines: st.write("•", s)
        st.write("**Watchouts**")
        for w in watch: st.write("•", w)
        st.write("**Typical use cases**")
        for c in cases: st.write("•", c)

    with col1:
        why_block(
            "On-prem",
            shines=[
                "Strict data residency / classified workloads",
                "Ultra-low latency to plant/branch systems",
                "Full control over network & hardware"
            ],
            watch=[
                "CapEx heavy; slower to scale",
                "Hardware lifecycle & patching overhead",
                "Harder to adopt managed analytics quickly"
            ],
            cases=[
                "Banks with mainframes/hosted cores",
                "Manufacturing OT networks",
                "Gov/defence secure enclaves"
            ]
        )

    with col2:
        why_block(
            "Private Cloud",
            shines=[
                "Elastic scale for analytics/AI",
                "Managed services reduce ops toil",
                "Global distribution & DR options"
            ],
            watch=[
                "Vendor lock-in risk & egress costs",
                "Shared responsibility still applies (Identity/Data)",
                "Requires guardrails (IAM, SCP, budgets)"
            ],
            cases=[
                "Digital product with spiky demand",
                "Data warehouse modernization",
                "ML experimentation platforms"
            ]
        )

    with col3:
        why_block(
            "Hybrid",
            shines=[
                "Sensitive data/processes remain private",
                "Burst to cloud for compute-intensive jobs",
                "Gradual migration without big-bang"
            ],
            watch=[
                "Network & identity federation complexity",
                "Data gravity / duplication if unmanaged",
                "Requires strong governance & catalogs"
            ],
            cases=[
                "Regulated enterprises modernizing DW",
                "Edge/branch analytics + cloud training",
                "M&A / multi-cloud coexistence"
            ]
        )

    st.markdown("---")

    # --- Responsibility heatmap
    st.markdown("#### Shared Responsibility by Model")
    df_resp = shared_responsibility_matrix(model)
    color_map = {"Customer":"#ef4444", "Shared":"#f59e0b", "Provider":"#10b981"}  # red/orange/green

    st.dataframe(
        df_resp[["Layer","Responsibility"]]
        .style.apply(
            lambda s: [f"color: white; background-color: {color_map.get(v,'#333')}; font-weight: 600"
                       if s.name=="Responsibility" else "" for v in s], axis=0),
        use_container_width=True, height=280
    )
    st.caption("Red = Customer • Orange = Shared • Green = Provider. Identity & Data remain largely your responsibility in all models.")

    st.markdown("---")

    # --- IaaS→PaaS→SaaS Sankey (illustrative)
    st.markdown("#### Workload flow across IaaS / PaaS / SaaS")
    nodes = ["Users", "Edge/WAF", "IaaS", "PaaS", "SaaS", "Data Lake/Warehouse", "BI/Apps"]
    idx = {n:i for i,n in enumerate(nodes)}

    # Weights adapt to chosen model
    if model=="On-prem":
        w_edge_iaas = 8; w_iaas_paas = 3; w_paas_saas = 1; w_iaas_data = 6; w_data_bi = 7
    elif model=="Private Cloud":
        w_edge_iaas = 5; w_iaas_paas = 6; w_paas_saas = 4; w_iaas_data = 5; w_data_bi = 7
    else:  # Hybrid
        w_edge_iaas = 6; w_iaas_paas = 6; w_paas_saas = 3; w_iaas_data = 7; w_data_bi = 8

    links = dict(
        source=[idx["Users"], idx["Edge/WAF"], idx["IaaS"], idx["PaaS"], idx["IaaS"], idx["Data Lake/Warehouse"]],
        target=[idx["Edge/WAF"], idx["IaaS"], idx["PaaS"], idx["SaaS"], idx["Data Lake/Warehouse"], idx["BI/Apps"]],
        value =[9,              w_edge_iaas,   w_iaas_paas,   w_paas_saas,   w_iaas_data,                 w_data_bi]
    )
    fig = go.Figure(data=[go.Sankey(
        node=dict(label=nodes, pad=20, thickness=18),
        link=dict(source=links["source"], target=links["target"], value=links["value"])
    )])
    fig.update_layout(height=420, margin=dict(l=20,r=20,t=10,b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Sankey emphasizes where traffic and responsibility sit for each model (weights are illustrative).")

# ======= 2) Fintech: Live Crypto =======

elif page.startswith("2"):
    st.subheader("Real-time(ish) crypto — free/public APIs + caching")
    left, right = st.columns([2,3], gap="large")
    with left:
        tokens = st.multiselect("Tokens", ["bitcoin","ethereum","solana","binancecoin","cardano","ripple"],
                                ["bitcoin","ethereum","solana"])
        if not tokens: tokens = ["bitcoin"]
        vs = st.selectbox("Quote currency", ["usd","sgd","eur"], index=0)
        try:
            prices = cg_prices(tuple(tokens), vs=vs)
            for t in tokens:
                st.metric(t.upper(), f"{prices[t][vs]:,} {vs.upper()}")
        except Exception as e:
            st.error(f"Price source unavailable: {e}")
        st.caption("Source: CoinGecko (free). Consider WebSockets later for tick updates.")
    with right:
        st.markdown("**BTC 1-minute close (last 60 mins)**")
        try:
            dfk = binance_klines("BTCUSDT", "1m", 60)
            st.line_chart(dfk.set_index("t")["c"])
        except Exception as e:
            st.warning(f"Candle source unavailable: {e}")

# ======= 3) Cybersecurity Lab =======

elif page.startswith("3"):
    st.subheader("Zero-Trust simulator + SOC mini anomaly detection")
    a, b = st.columns(2, gap="large")
    with a:
        st.markdown("### Zero-Trust policy")
        device = st.select_slider("Device posture", options=[0,1,2], value=1)
        mfa = st.selectbox("MFA", [1,0], index=0)
        vpn = st.selectbox("Suspected VPN/Proxy", [0,1], index=0)
        geo = st.selectbox("Unusual geo change", [0,1], index=0)
        fail = st.slider("Recent login fail %", 0.0, 1.0, 0.15, 0.05)
        seg = st.select_slider("Network segmentation depth", options=[0,1,2], value=1)
        role = st.select_slider("RBAC granularity", options=[0,1,2], value=1)
        z = zero_trust_score(device, mfa, vpn, geo, fail, seg, role)
        st.metric("Composite Risk Score", f"{z}/100")
        st.write("**Decision:**", "❌ Block" if z>=60 else ("⚠️ Step-up (MFA)" if z>=35 else "✅ Allow"))
        with st.expander("Zero-Trust TL;DR"):
            st.write("- Verify explicitly • Least privilege • Assume breach • Continuous evaluation")
    with b:
        st.markdown("### SOC mini — anomaly hunt (toy)")
        n = st.slider("Log size", 200, 5000, 800, 100)
        df = synth_auth_logs(n=n, seed=42)
        df, model = detect_anomalies(df)
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

# ======= 4) Data Platforms =======

elif page.startswith("4"):
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
            st.write("**Snowflake strengths**")
            for btxt in bullets["Snowflake"]:
                st.write("•", btxt)
        with c2:
            st.write("**Databricks strengths**")
            for btxt in bullets["Databricks"]:
                st.write("•", btxt)
        st.caption("Illustrative only. For production, confirm SKU/feature availability by region/date.")

# ======= About =======

else:
    st.subheader("About & Cost control")
    st.markdown("""
- **Hosting:** Streamlit Community Cloud (free) for MVP.
- **Data:** CoinGecko & Binance REST (free/public).
- **Compute:** Lightweight; synthetic logs; no DB.
- **Caching:** `@st.cache_data` minimizes external calls.
- **Security:** No secrets required. If you add paid APIs, store keys in Streamlit **Secrets**.
""")
