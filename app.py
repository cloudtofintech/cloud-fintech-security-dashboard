# app.py - Complete Enhanced Version with Compliance Recommendations
import time, random, os
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page config at the very beginning
st.set_page_config(page_title="Cloud & Crypto Dashboard", layout="wide")

# =========================
# Utilities (kept utilities that are still in use)
# =========================

def get_compliance_recommendations(model, data_sensitivity, compliance_reqs, industry):
    """Generate specific recommendations based on compliance and data sensitivity"""
    
    # Base recommendations by data sensitivity
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
    
    # Compliance-specific requirements
    compliance_details = {
        "GDPR": {
            "key_requirements": ["Right to be forgotten", "Data portability", "Privacy by design", "DPO appointment"],
            "technical_controls": ["Pseudonymization", "Encryption", "Access controls", "Breach notification (72hrs)"],
            "deployment_impact": {
                "🏠 On-premises": "✅ Full control over data location and processing",
                "☁️ Public Cloud": "⚠️ Need EU-based cloud regions + data processing agreements",
                "🌉 Hybrid Cloud": "⚠️ Ensure EU data stays in compliant locations"
            }
        },
        "HIPAA": {
            "key_requirements": ["PHI protection", "Business Associate Agreements", "Risk assessments", "Employee training"],
            "technical_controls": ["End-to-end encryption", "Access controls", "Audit logs", "Secure transmission"],
            "deployment_impact": {
                "🏠 On-premises": "✅ Maximum control, easier compliance audits",
                "☁️ Public Cloud": "⚠️ Requires HIPAA-compliant cloud services + BAAs",
                "🌉 Hybrid Cloud": "⚠️ PHI must stay in HIPAA-compliant environments"
            }
        },
        "SOX": {
            "key_requirements": ["Financial data integrity", "Change controls", "Segregation of duties", "Audit trails"],
            "technical_controls": ["Immutable logs", "Change approval workflows", "Access reviews", "Data integrity checks"],
            "deployment_impact": {
                "🏠 On-premises": "✅ Direct control over financial systems",
                "☁️ Public Cloud": "✅ Can use SOC 2 Type II certified services",
                "🌉 Hybrid Cloud": "⚠️ Ensure consistent controls across environments"
            }
        },
        "PCI-DSS": {
            "key_requirements": ["Cardholder data protection", "Network segmentation", "Regular testing", "Access monitoring"],
            "technical_controls": ["Network segmentation", "WAF", "Encryption", "Vulnerability scanning"],
            "deployment_impact": {
                "🏠 On-premises": "✅ Full control but expensive PCI compliance",
                "☁️ Public Cloud": "✅ Use PCI-DSS certified cloud services",
                "🌉 Hybrid Cloud": "⚠️ Payment processing should be in certified environment"
            }
        },
        "ISO 27001": {
            "key_requirements": ["Information security management", "Risk assessment", "Security controls", "Continuous improvement"],
            "technical_controls": ["Security policies", "Access controls", "Incident response", "Security monitoring"],
            "deployment_impact": {
                "🏠 On-premises": "✅ Full control over security implementation",
                "☁️ Public Cloud": "✅ Leverage cloud provider's ISO 27001 certification",
                "🌉 Hybrid Cloud": "⚠️ Need consistent security framework across both"
            }
        }
    }
    
    # Industry-specific considerations
    industry_considerations = {
        "Financial Services": {
            "key_risks": ["Regulatory fines", "Data breaches", "System downtime"],
            "recommended_model": "🏠 On-premises or 🌉 Hybrid",
            "rationale": "Core systems often must remain private for regulatory compliance"
        },
        "Healthcare": {
            "key_risks": ["HIPAA violations", "Patient safety", "Data breaches"],
            "recommended_model": "🏠 On-premises or 🌉 Hybrid",
            "rationale": "Patient data requires strict controls and audit trails"
        },
        "Government": {
            "key_risks": ["Security breaches", "Data sovereignty", "Public trust"],
            "recommended_model": "🏠 On-premises",
            "rationale": "Government data often requires air-gapped or classified environments"
        },
        "E-commerce/Retail": {
            "key_risks": ["PCI compliance", "Customer data", "Seasonal scaling"],
            "recommended_model": "☁️ Public Cloud or 🌉 Hybrid",
            "rationale": "Need to scale for traffic spikes while protecting payment data"
        },
        "Manufacturing": {
            "key_risks": ["Operational downtime", "IP theft", "Supply chain"],
            "recommended_model": "🌉 Hybrid Cloud",
            "rationale": "Factory floor stays local, analytics and planning in cloud"
        },
        "Technology/SaaS": {
            "key_risks": ["Service availability", "Customer data", "Competitive advantage"],
            "recommended_model": "☁️ Public Cloud",
            "rationale": "Need global scale, high availability, and rapid feature deployment"
        }
    }
    
    # Generate recommendations
    base_reqs = sensitivity_reqs[data_sensitivity]
    industry_info = industry_considerations[industry]
    
    recommendations = {
        "data_requirements": base_reqs,
        "industry_context": industry_info,
        "compliance_details": {},
        "deployment_recommendation": "",
        "implementation_priority": [],
        "estimated_complexity": "",
        "timeline_estimate": ""
    }
    
    # Add compliance-specific details
    if compliance_reqs and "None" not in compliance_reqs:
        for compliance in compliance_reqs:
            if compliance in compliance_details:
                recommendations["compliance_details"][compliance] = compliance_details[compliance]
    
    # Generate deployment recommendation based on sensitivity + compliance
    if data_sensitivity == "Restricted (financial/health records)":
        if model == "☁️ Public Cloud":
            recommendations["deployment_recommendation"] = "⚠️ HIGH RISK: Restricted data typically requires on-premises or certified private cloud"
        else:
            recommendations["deployment_recommendation"] = "✅ GOOD FIT: Recommended for restricted data"
    elif data_sensitivity == "Confidential (customer PII)":
        if any(comp in ["HIPAA", "PCI-DSS"] for comp in compliance_reqs):
            recommendations["deployment_recommendation"] = "⚠️ MODERATE RISK: Requires careful cloud provider selection and configuration"
        else:
            recommendations["deployment_recommendation"] = "✅ ACCEPTABLE: With proper encryption and access controls"
    else:
        recommendations["deployment_recommendation"] = "✅ SUITABLE: Standard cloud security practices sufficient"
    
    # Implementation priority based on sensitivity and compliance
    if data_sensitivity in ["Restricted (financial/health records)", "Confidential (customer PII)"]:
        recommendations["implementation_priority"] = [
            "1. Data classification and mapping",
            "2. Encryption key management",
            "3. Identity and access management",
            "4. Audit logging and monitoring",
            "5. Backup and disaster recovery"
        ]
        recommendations["estimated_complexity"] = "HIGH - Requires specialized security expertise"
        recommendations["timeline_estimate"] = "6-12 months for full implementation"
    else:
        recommendations["implementation_priority"] = [
            "1. Basic access controls",
            "2. Data encryption in transit/rest",
            "3. Regular backups",
            "4. Monitoring and alerting",
            "5. Documentation and training"
        ]
        recommendations["estimated_complexity"] = "MEDIUM - Standard security practices"
        recommendations["timeline_estimate"] = "2-4 months for full implementation"
    
    return recommendations

def display_compliance_recommendations(model, data_sensitivity, compliance_reqs, industry):
    """Display detailed compliance and security recommendations"""
    
    recs = get_compliance_recommendations(model, data_sensitivity, compliance_reqs, industry)
    
    # Deployment fit assessment
    st.markdown("### 🎯 Deployment Fit Assessment")
    if "HIGH RISK" in recs["deployment_recommendation"]:
        st.error(recs["deployment_recommendation"])
    elif "MODERATE RISK" in recs["deployment_recommendation"]:
        st.warning(recs["deployment_recommendation"])
    else:
        st.success(recs["deployment_recommendation"])
    
    # Industry context
    st.markdown("### 🏢 Industry-Specific Considerations")
    industry_info = recs["industry_context"]
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Recommended Model:** {industry_info['recommended_model']}")
        st.write(f"**Key Risks:**")
        for risk in industry_info['key_risks']:
            st.write(f"• {risk}")
    
    with col2:
        st.write(f"**Rationale:** {industry_info['rationale']}")
    
    # Data requirements
    st.markdown("### 🔒 Security Requirements")
    data_reqs = recs["data_requirements"]
    
    req_col1, req_col2 = st.columns(2)
    with req_col1:
        st.write(f"**Encryption:** {data_reqs['encryption']}")
        st.write(f"**Access Controls:** {data_reqs['access_controls']}")
        st.write(f"**Data Residency:** {data_reqs['data_residency']}")
    
    with req_col2:
        st.write(f"**Audit Logging:** {data_reqs['audit_logging']}")
        st.write(f"**Backup Retention:** {data_reqs['backup_retention']}")
    
    # Compliance details
    if recs["compliance_details"]:
        st.markdown("### 📋 Compliance Requirements")
        
        for compliance, details in recs["compliance_details"].items():
            with st.expander(f"{compliance} Compliance Details"):
                st.write("**Key Requirements:**")
                for req in details["key_requirements"]:
                    st.write(f"• {req}")
                
                st.write("**Technical Controls Needed:**")
                for control in details["technical_controls"]:
                    st.write(f"• {control}")
                
                st.write("**Deployment Model Impact:**")
                for deploy_model, impact in details["deployment_impact"].items():
                    if "✅" in impact:
                        st.success(f"{deploy_model}: {impact}")
                    else:
                        st.warning(f"{deploy_model}: {impact}")
    
    # Implementation guidance
    st.markdown("### 🚀 Implementation Roadmap")
    
    impl_col1, impl_col2 = st.columns(2)
    
    with impl_col1:
        st.write("**Priority Order:**")
        for priority in recs["implementation_priority"]:
            st.write(priority)
    
    with impl_col2:
        st.write("**Complexity Level:**")
        st.write(f"**{recs['estimated_complexity']}**")
        st.write("")  # Add space
        st.write("**Timeline Estimate:**")
        st.write(f"**{recs['timeline_estimate']}**")
    
    # Risk assessment
    st.markdown("### ⚠️ Risk Assessment Matrix")
    
    # Simple risk assessment based on data sensitivity
    if data_sensitivity == "Restricted (financial/health records)":
        risk_level = "🔴 CRITICAL"
        risk_desc = "Highest security measures required. Consider on-premises or specialized compliance cloud."
    elif data_sensitivity == "Confidential (customer PII)":
        if any(comp in ["HIPAA", "PCI-DSS", "SOX"] for comp in compliance_reqs):
            risk_level = "🟠 HIGH"
            risk_desc = "Significant compliance requirements. Requires specialized cloud configuration."
        else:
            risk_level = "🟡 MEDIUM"
            risk_desc = "Standard enterprise security practices sufficient."
    elif data_sensitivity == "Internal (business metrics)":
        risk_level = "🟡 MEDIUM"
        risk_desc = "Business-standard security controls needed."
    else:
        risk_level = "🟢 LOW"
        risk_desc = "Basic security measures sufficient."
    
    st.write("**Overall Risk Level:**")
    st.write(f"**{risk_level}**")
    st.caption(risk_desc)

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

# =========================
# UI Shell
# =========================

st.title("Cloud & Crypto Dashboard")
st.sidebar.caption(f"Deployed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

page = st.sidebar.radio(
    "Navigate",
    ["About", "1) Cloud Architectures", "2) Fintech: Live Crypto"]
)

# =========================
# New "About" Section
# =========================

if page == "About":
    st.markdown("""
    # About Me 👋
    
    This dashboard is a reflection of my educational journey and experience in the dynamic worlds of cloud computing, fintech, and crypto. It demonstrates my skills in creating interactive data applications and showcasing complex concepts in an intuitive way. 
    """)
    st.info("I love exploring how cloud technology empowers financial and crypto innovations! ☁️💰")
    
# =========================
# 1) Enhanced Cloud Architectures Section
# =========================

if page.startswith("1"):
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
        # Deployment model with better descriptions
        st.markdown("### Choose Your Cloud Strategy")
        model = st.radio(
            "Pick a deployment model to see real-world examples:",
            ["🏠 On-premises", "☁️ Public Cloud", "🌉 Hybrid Cloud"], 
            index=1,
            help="Each model has different trade-offs in cost, control, and complexity"
        )
        
        # Scenario selectors to make it more relatable
        st.markdown("### Your Business Scenario")
        company_size = st.selectbox(
            "Company size",
            ["Startup (1-50 employees)", "SME (51-500 employees)", "Enterprise (500+ employees)"],
            index=1
        )
        
        industry = st.selectbox(
            "Industry vertical",
            ["Financial Services", "Healthcare", "E-commerce/Retail", "Manufacturing", "Government", "Technology/SaaS"],
            index=0
        )
        
        # Interactive sliders with business context
        st.markdown("### Workload Requirements")
        ingest_gb = st.slider(
            "Daily data processing (GB)", 
            1, 500, 40, 5,
            help="Think: customer transactions, IoT sensors, log files, etc."
        )
        
        users = st.slider(
            "People using analytics dashboards", 
            5, 1000, 60, 5,
            help="Business analysts, data scientists, executives viewing reports"
        )
        
        # Security requirements (simplified, no MFA)
        st.markdown("### Security & Compliance Needs")
        data_sensitivity = st.selectbox(
            "Data sensitivity level",
            ["Public (marketing data)", "Internal (business metrics)", "Confidential (customer PII)", "Restricted (financial/health records)"],
            index=2
        )
        
        compliance_reqs = st.multiselect(
            "Compliance requirements",
            ["GDPR", "HIPAA", "SOX", "PCI-DSS", "ISO 27001", "None"],
            default=["GDPR"]
        )
        
        network_isolation = st.select_slider(
            "Network security level", 
            options=["Basic", "Standard", "High", "Maximum"], 
            value="Standard",
            help="How isolated should your systems be from the internet?"
        )

    with col_right:
        # Dynamic cost calculation with explanations
        st.markdown("### 💰 Cost Breakdown")
        
        # Base costs by model
        base_costs = {
            "🏠 On-premises": 800,
            "☁️ Public Cloud": 200, 
            "🌉 Hybrid Cloud": 400
        }
        
        base_cost = base_costs[model]
        data_cost = ingest_gb * 2.5
        user_cost = users * 1.2
        
        # Security premium based on selections
        security_multiplier = {
            "Basic": 1.0, "Standard": 1.2, "High": 1.5, "Maximum": 2.0
        }[network_isolation]
        
        compliance_cost = len(compliance_reqs) * 150 if compliance_reqs != ["None"] else 0
        
        # Industry and size adjustments
        industry_multiplier = {
            "Financial Services": 1.4,
            "Healthcare": 1.3,
            "Government": 1.5,
            "E-commerce/Retail": 1.1,
            "Manufacturing": 1.2,
            "Technology/SaaS": 1.0
        }[industry]
        
        size_multiplier = {
            "Startup (1-50 employees)": 0.8,
            "SME (51-500 employees)": 1.0,
            "Enterprise (500+ employees)": 1.3
        }[company_size]
        
        total_cost = (base_cost + data_cost + user_cost + compliance_cost) * security_multiplier * industry_multiplier * size_multiplier
        
        # Display cost breakdown
        st.metric("💸 Estimated Monthly Cost", f"${total_cost:,.0f}")
        
        with st.expander("💡 See cost breakdown"):
            st.write(f"• **Base infrastructure**: ${base_cost:,}")
            st.write(f"• **Data processing**: ${data_cost:,.0f}")
            st.write(f"• **User access**: ${user_cost:,.0f}")
            st.write(f"• **Compliance**: ${compliance_cost:,}")
            st.write(f"• **Security level**: {security_multiplier}x multiplier")
            st.write(f"• **Industry factor**: {industry_multiplier}x")
            st.write(f"• **Company size**: {size_multiplier}x")

    # Enhanced recommendations section
    st.markdown("---")
    display_compliance_recommendations(model, data_sensitivity, compliance_reqs, industry)
    
    # Quick model benefits (keep this for overview)
    with st.expander("📋 Quick Model Overview"):
        if model == "🏠 On-premises":
            st.success("✅ **Benefits:** Complete control, data never leaves your building")
            st.warning("⚠️ **Challenges:** High upfront costs, you handle all maintenance")
        elif model == "☁️ Public Cloud":
            st.success("✅ **Benefits:** Pay-as-you-go, automatic updates, global scale")
            st.warning("⚠️ **Challenges:** Ongoing costs, less control, internet dependency")
        else:  # Hybrid
            st.success("✅ **Benefits:** Keep sensitive data private, burst to cloud when needed")
            st.warning("⚠️ **Challenges:** More complex to manage, need expertise in both")
    
    st.markdown("---")
    
    # IaaS/PaaS/SaaS Section
    st.markdown("## 🏗️ Cloud Service Models: IaaS vs PaaS vs SaaS")
    st.markdown("**Think of it like transportation options:**")
    st.markdown("- 🚗 **IaaS** = Rent a car (you drive, maintain, fuel it)")
    st.markdown("- 🚌 **PaaS** = Take a bus (just get on, driver handles the rest)")  
    st.markdown("- 🚕 **SaaS** = Call an Uber (complete door-to-door service)")
    
    # Interactive service model selector
    service_col1, service_col2 = st.columns([1, 2])
    
    with service_col1:
        selected_service = st.selectbox(
            "Choose a service model to explore:",
            ["🚗 IaaS (Infrastructure as a Service)", "🚌 PaaS (Platform as a Service)", "🚕 SaaS (Software as a Service)"],
            help="Each model gives you different levels of control vs convenience"
        )
    
    with service_col2:
        if "IaaS" in selected_service:
            st.markdown("""
            ### 🚗 IaaS - You Get the Raw Building Blocks
            **What you get:** Virtual machines, storage, networks
            **You manage:** Operating systems, applications, data, security patches
            **Examples:** AWS EC2, Google Compute Engine, Azure VMs
            **Best for:** Custom applications, full control needed
            """)
        elif "PaaS" in selected_service:
            st.markdown("""
            ### 🚌 PaaS - You Focus on Your App, Not Infrastructure  
            **What you get:** Runtime environment, databases, development tools
            **You manage:** Your application code and data
            **Examples:** Heroku, Google App Engine, AWS Lambda
            **Best for:** Developers who want to code, not manage servers
            """)
        else:  # SaaS
            st.markdown("""
            ### 🚕 SaaS - Complete Ready-to-Use Applications
            **What you get:** Fully functional software accessible via web browser
            **You manage:** User accounts, data input, business processes
            **Examples:** Salesforce, Google Workspace, Zoom, Netflix
            **Best for:** Business users who need tools, not technology
            """)
    
    # Detailed responsibility matrix
    st.markdown("### 👥 Who's Responsible for What?")
    
    # Create responsibility visualization
    responsibilities = [
        "Physical Data Centers",
        "Network & Security Infrastructure", 
        "Virtual Machines & Storage",
        "Operating System & Updates",
        "Runtime & Development Tools",
        "Application Code & Logic",
        "User Data & Access Control",
        "Business Processes & Training"
    ]
    
    # Color coding: Red = Customer, Yellow = Shared, Green = Provider
    iaas_resp = ["🟢", "🟢", "🟢", "🔴", "🔴", "🔴", "🔴", "🔴"]
    paas_resp = ["🟢", "🟢", "🟢", "🟢", "🟢", "🔴", "🔴", "🔴"] 
    saas_resp = ["🟢", "🟢", "🟢", "🟢", "🟢", "🟢", "🟡", "🔴"]
    
    resp_df = pd.DataFrame({
        "Responsibility Layer": responsibilities,
        "IaaS": iaas_resp,
        "PaaS": paas_resp, 
        "SaaS": saas_resp
    })
    
    st.dataframe(resp_df, use_container_width=True, hide_index=True)
    st.caption("🟢 = Cloud Provider  |  🟡 = Shared  |  🔴 = You (Customer)")
    
    # Decision matrix
    st.markdown("### 🤔 Quick Decision Matrix: Which Model Should You Choose?")
    
    decision_col1, decision_col2 = st.columns(2)
    
    with decision_col1:
        user_priority = st.radio(
            "What's most important to you?",
            ["Maximum control and customization", "Speed to market", "Lowest operational overhead", "Cost predictability"]
        )
        
        team_expertise = st.radio(
            "What's your team's technical expertise?",
            ["We have infrastructure experts", "We're mainly developers", "We're business users", "Mixed technical skills"]
        )
    
    with decision_col2:
        # Simple recommendation logic
        if user_priority == "Maximum control and customization":
            if team_expertise == "We have infrastructure experts":
                rec = "🚗 **IaaS** - You have the skills to manage everything"
            else:
                rec = "🚌 **PaaS** - Get control without infrastructure complexity"
        elif user_priority == "Speed to market":
            if team_expertise == "We're business users":
                rec = "🚕 **SaaS** - Get started immediately with ready solutions"
            else:
                rec = "🚌 **PaaS** - Deploy fast without infrastructure setup"
        elif user_priority == "Lowest operational overhead":
            rec = "🚕 **SaaS** - Let someone else handle all the operations"
        else:  # Cost predictability
            rec = "🚗 **IaaS** - Most predictable long-term costs at scale"
        
        st.success(f"### 🎯 Recommendation: {rec}")
    
    # Common evolution path
    st.info("""
    **💡 Common Evolution Path:**
    Most companies start with SaaS → Add PaaS for custom apps → Use IaaS for specialized needs
    
    **Example:** Start with Google Workspace (SaaS) → Build custom app on Heroku (PaaS) → Add ML workloads on AWS EC2 (IaaS)
    """)
    
    st.markdown("---")
    
    # Decision Framework
    st.markdown("## 🤔 Decision Framework: Which Service Model Should You Choose?")
    
    # Interactive decision tree
    st.markdown("### Quick Decision Helper")
    
    q1 = st.radio(
        "**1. What's your primary concern?**",
        ["Maximum security/control", "Lowest initial cost", "Fastest time to market", "Flexibility/future-proofing"]
    )
    
    q2 = st.radio(
        "**2. How predictable is your workload?**",
        ["Very predictable (same every day)", "Some spikes (seasonal/events)", "Completely unpredictable", "Mix of both"]
    )
    
    q3 = st.radio(
        "**3. What's your IT team like?**",
        ["We have lots of infrastructure experts", "We're mostly developers", "Small team, need managed services", "Mixed skills"]
    )
    
    # Simple recommendation logic for deployment models
    if q1 == "Maximum security/control":
        recommendation = "🏠 **On-Premises** - You value control over convenience"
    elif q1 == "Fastest time to market":
        recommendation = "☁️ **Public Cloud** - Get started in minutes, not months"
    elif q1 == "Flexibility/future-proofing":
        recommendation = "🌉 **Hybrid Cloud** - Best of both worlds, harder to manage"
    else:  # Lowest initial cost
        if q2 == "Very predictable (same every day)":
            recommendation = "🏠 **On-Premises** - Predictable workload = predictable costs"
        else:
            recommendation = "☁️ **Public Cloud** - Pay only for what you use"
    
    st.success(f"### 🎯 Recommendation: {recommendation}")
    
    # Reality check section
    st.markdown("---")
    st.markdown("## 🎯 Reality Check: What Industry Experts Actually Say")
    
    expert_quotes = [
        "💬 **Netflix CTO**: 'We went all-in on AWS because we needed global scale fast. On-premises couldn't handle our growth.'",
        "💬 **Bank of America**: 'We use hybrid - core banking stays private for regulation, but mobile apps use cloud for scale.'",
        "💬 **Spotify**: 'We started in cloud, but moved some workloads on-premises to control costs at scale.'",
        "💬 **Manufactur"

# =========================
# 2) Fintech: Live Crypto Section
# =========================

if page.startswith("2"):
    st.markdown("# 📈 Fintech: Live Crypto Portfolio")
    st.write("This section connects to live cryptocurrency APIs to display real-time price and market data.")
    
    # User selects cryptos
    crypto_list = st.multiselect(
        "Select Cryptocurrencies",
        ["bitcoin", "ethereum", "solana", "cardano", "ripple", "dogecoin", "shiba-inu"],
        default=["bitcoin", "ethereum", "solana"]
    )
    
    # Get live prices
    if crypto_list:
        try:
            prices = cg_prices(ids=crypto_list)
            st.markdown("### 📊 Live Market Data")
            price_cols = st.columns(len(crypto_list))
            
            for i, crypto_id in enumerate(crypto_list):
                with price_cols[i]:
                    symbol = crypto_id.split('-')[0].upper()
                    price = prices.get(crypto_id, {}).get("usd", "N/A")
                    st.metric(label=f"{symbol.upper()} Price", value=f"${price:,.2f}" if isinstance(price, (int, float)) else price)
            
            # Candlestick chart
            st.markdown("### 📉 Live Candlestick Chart (BTCUSDT)")
            with st.spinner("Fetching live market data..."):
                try:
                    df = binance_klines(symbol="BTCUSDT")
                    fig_klines = go.Figure(
                        data=[go.Candlestick(
                            x=df["t"],
                            open=df["o"],
                            high=df["h"],
                            low=df["l"],
                            close=df["c"]
                        )]
                    )
                    fig_klines.update_layout(
                        xaxis_rangeslider_visible=False,
                        title="BTC/USDT 1-Hour Chart (1-Minute Intervals)",
                        height=500
                    )
                    st.plotly_chart(fig_klines, use_container_width=True)
                except requests.exceptions.RequestException as e:
                    st.error(f"Error fetching Binance data: {e}")
                    st.info("The Binance API might be unavailable. Please try again in a few minutes.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching CoinGecko data: {e}")
            st.info("The CoinGecko API might be unavailable. Please try again in a few minutes.")
    
        # --- Add Correlation Matrix Section ---
        st.markdown("---")
        st.markdown("### 🤝 Cryptocurrency Price Correlation Matrix")
        
        @st.cache_data(ttl=3600)
        def get_historical_prices(ids, days="30"):
            """Fetches 30-day historical data for multiple cryptocurrencies."""
            price_data = pd.DataFrame()
            for crypto_id in ids:
                try:
                    r = requests.get(f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart",
                                     params={"vs_currency": "usd", "days": days},
                                     timeout=10)
                    r.raise_for_status()
                    data = r.json().get("prices", [])
                    df_temp = pd.DataFrame(data, columns=["timestamp", crypto_id])
                    df_temp["timestamp"] = pd.to_datetime(df_temp["timestamp"], unit="ms")
                    if price_data.empty:
                        price_data = df_temp
                    else:
                        price_data = pd.merge(price_data, df_temp, on="timestamp", how="outer")
                except requests.exceptions.RequestException as e:
                    st.warning(f"Could not fetch historical data for {crypto_id}. Skipping.")
            return price_data.set_index("timestamp").dropna()
        
        if len(crypto_list) >= 2:
            with st.spinner("Calculating correlation matrix..."):
                historical_df = get_historical_prices(crypto_list)
                if not historical_df.empty:
                    correlation_matrix = historical_df.corr()
                    
                    fig = go.Figure(data=go.Heatmap(
                        z=correlation_matrix.values,
                        x=correlation_matrix.columns,
                        y=correlation_matrix.index,
                        colorscale='Viridis',
                        zmin=-1,
                        zmax=1,
                        text=correlation_matrix.round(2).values,
                        hoverinfo='text'
                    ))
                    
                    fig.update_layout(
                        title='Price Correlation (Last 30 Days)',
                        xaxis_title="Cryptocurrency",
                        yaxis_title="Cryptocurrency",
                        xaxis_showgrid=False,
                        yaxis_showgrid=False,
                        xaxis_side='bottom',
                        height=500,
                        width=600
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("A value close to **+1** means prices move together, **-1** means they move in opposite directions, and **0** means no correlation.")
                else:
                    st.warning("Not enough data to create a correlation matrix. Please select at least two cryptocurrencies and ensure API is accessible.")
        else:
            st.info("Select at least two cryptocurrencies to view the correlation matrix.")
    else:
        st.info("Please select at least one cryptocurrency to view market data.") 
