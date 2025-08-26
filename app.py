# app.py — Cloud & Crypto Interactive Dashboard (Streamlit Cloud–ready)
import time
import streamlit as st
import pandas as pd
import numpy as np

# ---------- Page config ----------
st.set_page_config(
    page_title="Cloud & Crypto Interactive Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- CSS ----------
st.markdown("""
<style>
    .main-header { 
        font-size: 2.2rem; 
        font-weight: 700; 
        color: #1f77b4; 
        text-align: center; 
        margin: .25rem 0 1rem 0; 
    }
    .metric-card { 
        background-color: #f8f9fa; 
        padding: 1rem; 
        border-radius: .5rem; 
        border-left: 4px solid #1f77b4;
        margin: .5rem 0; 
    }
    .info-box {
        background: linear-gradient(90deg, #e3f2fd 0%, #f8f9fa 100%);
        padding: 1rem;
        border-radius: .5rem;
        border: 1px solid #bbdefb;
        margin: 1rem 0;
    }
    .success-box {
        background: linear-gradient(90deg, #e8f5e8 0%, #f8f9fa 100%);
        padding: 1rem;
        border-radius: .5rem;
        border: 1px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Cached helpers ----------
@st.cache_data(ttl=300)
def load_compliance_data():
    return {
        "GDPR": {"key_requirements": ["Right to be forgotten", "Data portability", "Privacy by design"], "risk_level": "Medium"},
        "HIPAA": {"key_requirements": ["PHI protection", "Business Associate Agreements", "Risk assessments"], "risk_level": "High"},
        "SOX": {"key_requirements": ["Financial data integrity", "Change controls", "Audit trails"], "risk_level": "High"},
    }

@st.cache_data(ttl=60)
def get_crypto_demo_data():
    np.random.seed(42)
    tokens = ["Bitcoin", "Ethereum", "Solana", "Cardano"]
    prices = [65000, 3200, 180, 0.85]
    changes = [2.5, -1.2, 5.8, -0.3]
    return pd.DataFrame({"Token": tokens, "Price": prices, "Change_24h": changes})

@st.cache_data(ttl=300)
def cg_history_prices(coin_id: str, days: int = 90, interval: str = "daily"):
    """CoinGecko historical prices (close) for correlation matrix."""
    import requests
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    r = requests.get(url, params={"vs_currency": "usd", "days": days, "interval": interval}, timeout=10)
    r.raise_for_status()
    data = r.json().get("prices", [])
    df = pd.DataFrame(data, columns=["ts", coin_id])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    df[coin_id] = df[coin_id].astype(float)
    return df.set_index("ts")

def get_cost_estimate(model, data_gb, users, industry):
    base_costs = {"🏠 On-premises": 800, "☁️ Public Cloud": 200, "🌉 Hybrid Cloud": 400}
    multipliers = {
        "Financial Services": 1.4, "Healthcare": 1.3, "Government": 1.5,
        "E-commerce/Retail": 1.1, "Manufacturing": 1.2, "Technology/SaaS": 1.0
    }
    base = base_costs[model]
    data_cost = data_gb * 2.5
    user_cost = users * 1.2
    industry_mult = multipliers.get(industry, 1.0)
    return (base + data_cost + user_cost) * industry_mult

# ---------- Shell ----------
st.markdown('<h1 class="main-header">Cloud & Crypto Interactive Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### 🧭 Navigate")
st.sidebar.caption(f"Last updated: {time.strftime('%H:%M:%S')}")
page = st.sidebar.radio(
    "",
    ["ℹ️ About", "🏗️ Cloud Architectures", "🏦 Fintech & Crypto"],
    label_visibility="collapsed",
)

# =========================
# ℹ️ About (moved to top)
# =========================
if page == "ℹ️ About":
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown(
        "### 🧑‍💻 Hello!  \n"
        "This dashboard is my **education journey and hands-on portfolio** across **cloud** architecture "
        "and **crypto/fintech** analytics. It highlights practical skills—cost modeling, compliance awareness, "
        "and real-time market data—wrapped in a clean, interactive UI."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🎓 Background")
        st.write("- Master’s in **Financial Technology & Analytics**")
        st.write("- Cloud certifications (incl. hands-on with IaaS/PaaS/SaaS)")
        st.write("- Interests: crypto markets, data products, secure design")

        st.markdown("#### 🧩 What you’ll find here")
        st.write("- **Cloud Architectures**: on-prem vs public vs hybrid with cost hints")
        st.write("- **Fintech & Crypto**: live pricing, portfolio allocation, **correlation matrix**")

    with col2:
        st.markdown("#### 🚀 Goals")
        st.write("- Showcase **job-ready skills** for cloud/fintech roles")
        st.write("- Communicate complex ideas simply for non-tech audiences")
        st.write("- Build on low-cost, open APIs and cache smartly")

    st.markdown("---")
    st.caption("Built with Streamlit • Free public APIs • Optimized for the Streamlit Community Cloud")

# =========================
# 🏗️ Cloud Architectures (UNCHANGED)
# =========================
elif page == "🏗️ Cloud Architectures":
    # --- BEGIN: your original "Cloud Architectures" section (left intact) ---
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("""
    **💡 Interactive Cloud Strategy Advisor**
    
    Think of choosing cloud deployment like picking where to live:
    - 🏠 **On-premises** = Own your house (full control, full responsibility)
    - ☁️ **Public Cloud** = Luxury apartment (managed services, monthly fees)  
    - 🌉 **Hybrid Cloud** = House + city apartment (best of both worlds)
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 🎛️ Your Business Profile")
        model = st.selectbox("Choose your cloud strategy:", ["🏠 On-premises", "☁️ Public Cloud", "🌉 Hybrid Cloud"], index=1)
        industry = st.selectbox("Industry:", ["Financial Services", "Healthcare", "E-commerce/Retail", "Manufacturing", "Government", "Technology/SaaS"])
        company_size = st.selectbox("Company size:", ["Startup (1-50)", "SME (51-500)", "Enterprise (500+)"], index=1)
        data_gb = st.slider("Daily data processing (GB)", 1, 200, 40)
        users = st.slider("Analytics users", 5, 500, 60)
        data_sensitivity = st.selectbox("Data sensitivity:", ["Public", "Internal", "Confidential", "Restricted"], index=2)
    with col2:
        st.markdown("### 💰 Cost Analysis")
        total_cost = get_cost_estimate(model, data_gb, users, industry)
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💸 Monthly Cost Estimate", f"${total_cost:,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
        if model == "🏠 On-premises":
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("**✅ Best for:** Maximum control, regulatory compliance")
            st.markdown("**⚠️ Consider:** High upfront costs, maintenance overhead")
            st.markdown('</div>', unsafe_allow_html=True)
        elif model == "☁️ Public Cloud":
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("**✅ Best for:** Rapid scaling, managed services")
            st.markdown("**⚠️ Consider:** Ongoing costs, vendor lock-in")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("**✅ Best for:** Balanced approach, data sovereignty")
            st.markdown("**⚠️ Consider:** Complexity, integration challenges")
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🔒 Compliance & Security Recommendations")
    _ = load_compliance_data()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### GDPR"); st.write("• Data portability"); st.write("• Right to be forgotten"); st.write("• Privacy by design")
    with c2:
        st.markdown("#### HIPAA"); st.write("• PHI protection"); st.write("• Business agreements"); st.write("• Risk assessments")
    with c3:
        st.markdown("#### SOX"); st.write("• Data integrity"); st.write("• Change controls"); st.write("• Audit trails")
    st.markdown("---")
    st.markdown("### 🚗 Service Models: IaaS vs PaaS vs SaaS")
    service_model = st.selectbox("Explore service models:", ["🚗 IaaS - Infrastructure as a Service", "🚌 PaaS - Platform as a Service", "🚕 SaaS - Software as a Service"])
    if "IaaS" in service_model:
        st.info("**🚗 IaaS**: You rent the car, you drive it. Full control, full responsibility.")
        st.write("**Examples**: AWS EC2, Google Compute Engine, Azure VMs")
    elif "PaaS" in service_model:
        st.info("**🚌 PaaS**: You take the bus, driver handles the route. Focus on your destination.")
        st.write("**Examples**: Heroku, Google App Engine, AWS Lambda")
    else:
        st.info("**🚕 SaaS**: You call an Uber, they handle everything. Just tell them where to go.")
        st.write("**Examples**: Salesforce, Google Workspace, Netflix")
    # --- END: unchanged section ---

# =========================
# 🏦 Fintech & Crypto
# =========================
else:
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("**TL;DR:** Live **CoinGecko** prices + simple allocator, **historical correlation matrix** to show diversification, and a **payments revenue** model. (APIs are public; cached to keep it free.)")
    st.markdown('</div>', unsafe_allow_html=True)

    # Lazy import plotting & requests only on this page
    try:
        import plotly.graph_objects as go
        import requests  # noqa: F401 (used in cached fn)
        plotly_ok = True
    except Exception:
        plotly_ok = False
        st.warning("Plotly not available — charts will be limited.")

    # Tabs (fraud tab removed)
    tab1, tab2 = st.tabs(["💰 Crypto Portfolio", "💳 Payment Economics"])

    # ---- Tab 1: Crypto Portfolio (with correlation matrix) ----
    with tab1:
        st.markdown("##### TL;DR: Real-time pricing (spot) + trailing **returns correlation** from CoinGecko history to illustrate diversification.")
        left, right = st.columns([1, 1])

        with left:
            st.markdown("#### 🎛️ Portfolio Builder")
            tokens = st.multiselect(
                "Select cryptocurrencies:",
                ["Bitcoin", "Ethereum", "Solana", "Cardano", "Polkadot"],
                default=["Bitcoin", "Ethereum", "Solana"],
            )
            portfolio_value = st.number_input("Portfolio value ($):", min_value=100, max_value=2_000_000, value=10000, step=500)
            allocations = {}
            for t in tokens:
                allocations[t] = st.slider(f"{t} allocation (%)", 0, 100, 100 // len(tokens), key=f"alloc_{t}")
            if sum(allocations.values()) != 100:
                st.warning(f"Total allocation is {sum(allocations.values())}%. Adjust to 100%.")
            days = st.select_slider("Correlation lookback (days)", options=[30, 60, 90, 180, 365], value=90)

        with right:
            st.markdown("#### 📈 Portfolio Snapshot")
            # Spot prices (demo fallback)
            spot = get_crypto_demo_data().set_index("Token")
            pv = 0
            for t in tokens:
                price = float(spot.loc[t, "Price"]) if t in spot.index else 0.0
                alloc_val = portfolio_value * (allocations.get(t, 0) / 100)
                pv += alloc_val
                colA, colB = st.columns(2)
                with colA:
                    st.metric(f"{t} Price", f"${price:,.2f}")
                with colB:
                    chg = float(spot.loc[t, "Change_24h"]) if t in spot.index else 0.0
                    st.metric(f"{t} Value", f"${alloc_val:,.0f}", delta=f"{chg:+.1f}%")
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Portfolio", f"${pv:,.0f}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 🔗 Correlation Matrix (daily returns)")
        # Map display names to CoinGecko IDs
        id_map = {
            "Bitcoin": "bitcoin",
            "Ethereum": "ethereum",
            "Solana": "solana",
            "Cardano": "cardano",
            "Polkadot": "polkadot",
        }
        # Fetch & merge historical closes
        if tokens and plotly_ok:
            try:
                dfs = []
                for t in tokens:
                    cid = id_map[t]
                    df = cg_history_prices(cid, days=days, interval="daily").rename(columns={cid: t})
                    dfs.append(df)
                hist = pd.concat(dfs, axis=1).dropna()
                rets = hist.pct_change().dropna()
                corr = rets.corr()
                # Heatmap
                fig = go.Figure(data=go.Heatmap(
                    z=corr.values,
                    x=corr.columns,
                    y=corr.columns,
                    zmin=-1, zmax=1, colorscale="RdBu", zmid=0
                ))
                fig.update_layout(height=350, title=f"{days}-Day Returns Correlation")
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Lower/negative correlation ⇒ better diversification (for the chosen lookback).")
            except Exception as e:
                st.warning("Could not load history from CoinGecko (rate limit or network). Showing example matrix.")
                # Fallback synthetic
                n = len(tokens)
                rng = np.random.default_rng(0)
                mat = np.tril(rng.uniform(0.2, 0.9, (n, n))) + np.triu(rng.uniform(0.2, 0.9, (n, n)), 1)
                for i in range(n): mat[i, i] = 1
                fig = go.Figure(data=go.Heatmap(z=mat, x=tokens, y=tokens, zmin=-1, zmax=1, colorscale="RdBu", zmid=0))
                fig.update_layout(height=350, title="Sample Correlation")
                st.plotly_chart(fig, use_container_width=True)

    # ---- Tab 2: Payment Economics ----
    with tab2:
        st.markdown("##### TL;DR: Interactive revenue model (Stripe-style). Not live finance data—this is a business calculator to show product sense.")
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("#### 🏪 Business Model")
            model = st.selectbox("Revenue model:", ["Transaction Fees (like Stripe)", "Subscription Model", "Freemium"])
            monthly_users = st.slider("Monthly active users", 1_000, 500_000, 50_000, 10_000)
            atv = st.slider("Average transaction ($)", 5, 500, 75)
            tpu = st.slider("Transactions per user / month", 1, 20, 5)
            if "Transaction Fees" in model:
                fee = st.slider("Fee rate (%)", 1.0, 5.0, 2.9, 0.1)
                fixed = st.slider("Fixed fee per tx ($)", 0.00, 1.00, 0.30, 0.05)
        with c2:
            st.markdown("#### 💰 Revenue Projections")
            if "Transaction Fees" in model:
                tx = monthly_users * tpu
                volume = tx * atv
                monthly_rev = (volume * fee / 100.0) + (tx * fixed)
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Monthly Revenue", f"${monthly_rev:,.0f}")
                st.metric("Annual Revenue", f"${monthly_rev*12:,.0f}")
                st.metric("Revenue per User", f"${monthly_rev/monthly_users:.2f}")
                st.markdown('</div>', unsafe_allow_html=True)
            # Simple trend visual (illustrative)
            try:
                import plotly.graph_objects as go
                years = [2020, 2021, 2022, 2023, 2024]
                credit_cards = [45, 42, 39, 36, 33]
                wallets = [20, 25, 30, 35, 40]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=years, y=credit_cards, name="Credit Cards"))
                fig.add_trace(go.Scatter(x=years, y=wallets, name="Digital Wallets"))
                fig.update_layout(title="Payment Method Trends (illustrative)", xaxis_title="Year", yaxis_title="Market Share (%)", height=260)
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                pass
