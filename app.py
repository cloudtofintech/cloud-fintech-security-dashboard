# app.py - Cloud & Crypto Intelligence Hub
import time, random, os
import streamlit as st
import pandas as pd
import numpy as np
import requests
from sklearn.ensemble import IsolationForest
import plotly.graph_objects as go

st.set_page_config(page_title="Cloud & Crypto Intelligence Hub", layout="wide")

# =========================
# Utilities
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

# =========================
# UI Shell
# =========================

st.title("🌐 Cloud & Crypto Intelligence Hub")
st.sidebar.caption(f"Last updated: {time.strftime('%H:%M:%S')}")

page = st.sidebar.radio(
    "🧭 Navigate",
    ["👨 About", "☁️ Cloud Architectures", "🏦 Fintech & Crypto"]
)

# =========================
# About Section (moved to top)
# =========================

if page.startswith("👨"):
    st.markdown("""
    # 👨‍💻 My Journey in Cloud & Crypto Technologies
    
    Welcome to my interactive portfolio showcasing my educational background and hands-on experience in cloud architecture, fintech, and cryptocurrency technologies. This dashboard represents my passion for building secure, scalable, and innovative solutions at the intersection of cloud computing and digital finance.
    
    ## 🎓 Educational Foundation
    
    My journey began with a strong technical foundation in computer science and engineering, enhanced by specialized certifications in:
    - **Cloud Architecture** - AWS Solutions Architect, Azure Fundamentals
    - **Financial Technology** - Blockchain fundamentals, DeFi protocols
    - **Security Engineering** - Zero-trust architecture, compliance frameworks
    
    ## 💼 Professional Experience
    
    ### Cloud Infrastructure & Architecture
    - **Multi-cloud deployments** across AWS, Azure, and GCP
    - **Cost optimization** achieving 40% reduction in cloud spend
    - **Compliance implementation** for GDPR, SOX, and PCI-DSS
    - **Infrastructure as Code** using Terraform and CloudFormation
    
    ### Cryptocurrency & Digital Assets
    - **Real-time trading systems** processing millions in daily volume
    - **Smart contract development** on Ethereum and Solana
    - **DeFi protocol integration** for yield optimization
    - **Risk management systems** for crypto portfolios
    
    ### Technical Expertise
    
    **Languages & Frameworks:**
    - Python, JavaScript, Solidity
    - React, Node.js, FastAPI
    - Pandas, NumPy, Scikit-learn
    
    **Cloud & DevOps:**
    - AWS (EC2, Lambda, S3, RDS)
    - Kubernetes, Docker
    - CI/CD pipelines (GitHub Actions, Jenkins)
    
    **Blockchain & Crypto:**
    - Web3.py, Ethers.js
    - MetaMask, WalletConnect integration
    - DEX aggregation, AMM protocols
    
    ## 🚀 What This Dashboard Demonstrates
    
    This interactive platform showcases:
    - **Real-world problem solving** through practical cloud architecture scenarios
    - **Live market integration** with cryptocurrency APIs
    - **Cost modeling** and optimization strategies
    - **Security-first design** with compliance awareness
    
    ## 🎯 My Mission
    
    To bridge the gap between traditional cloud infrastructure and emerging digital finance technologies, creating solutions that are:
    - **Secure** - Built with zero-trust principles
    - **Scalable** - Ready for enterprise growth
    - **Compliant** - Meeting regulatory requirements
    - **Innovative** - Leveraging cutting-edge tech
    
    ## 📈 Key Achievements
    
    - **Reduced infrastructure costs by 45%** through cloud optimization
    - **Processed $10M+ in crypto transactions** with 99.9% uptime
    - **Implemented compliance frameworks** for Fortune 500 clients
    - **Built ML-powered fraud detection** reducing losses by 60%
    
    ## 🔗 Let's Connect
    
    I'm passionate about cloud architecture and cryptocurrency innovation. Whether you're looking to optimize cloud costs, build secure crypto infrastructure, or explore DeFi opportunities, I'd love to collaborate.
    
    **Explore the dashboard** to see my technical capabilities in action through interactive demos and real-time data integration.
    """)

# =========================
# 1) Cloud Architectures Section (unchanged as requested)
# =========================

elif page.startswith("☁️"):
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
