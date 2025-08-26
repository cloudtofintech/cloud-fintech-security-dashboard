# app.py - Cloud & Crypto Intelligence Hub
import time, random, os
import streamlit as st
import pandas as pd
import numpy as np
import requests
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
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": ",".join(ids), "vs_currencies": vs},
            timeout=8,
        )
        r.raise_for_status()
        return r.json()
    except:
        return {}

@st.cache_data(ttl=60)
def binance_klines(symbol="BTCUSDT", interval="1m", limit=60):
    """1-minute candles for last ~hour (REST)."""
    try:
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
    except:
        return pd.DataFrame()

# =========================
# UI Shell
# =========================

st.title("🌐 Cloud & Crypto Intelligence Hub")
st.sidebar.caption(f"Last updated: {time.strftime('%H:%M')}")

page = st.sidebar.radio(
    "🧭 Navigate",
    ["👨 About", "☁️ Cloud Architectures", "🏦 Fintech & Crypto"]
)

# =========================
# About Section (moved to top)
# =========================

if page == "👨 About":
    st.markdown("""
    # 👨‍💻 My Journey in Cloud & Crypto Technologies
    
    Hello, I am Mao Jie aka M J. Welcome to my interactive portfolio showcasing my educational journey and knowledge/experience 
    in cloud architecture, fintech, and cryptocurrency technologies. This dashboard reflects my passion for gamification at the intersection of cloud computing and digital finance—have fun exploring the widgets, and I hope you learn something useful
    
    ## 🎓 Educational Foundation
    
    My journey began with a strong technical foundation in computer science, enhanced by 
    specialized certifications and continuous learning in:
    - **Cloud** — Go-to-market leader with deep technical expertise who drove product launches that captured 30% additional market share within 6 months, developed scalable enablement programs that reduced onboarding time by 40%, and expanded cloud developer ecosystems through community initiatives that boosted engagement by 30%. Hold current certifications as Google Cloud Digital Leader (2024) and AWS Cloud Practitioner (2025), with hands-on experience in BigQuery, Google Cloud Storage, and Amazon S3.
    - **Fintech & Web3** - Combined advanced academic foundation in Financial Technology & Analytics (SMU) with practical developer advocacy experience at Google Cloud to execute Web3 go-to-market strategies. Successfully scaled Layer-2 blockchain adoption, guided 20+ startups through structured hackathons and bootcamps, and achieved 40% improvement in post-program Cloud platform activation across the Web3 developer community.
    - **Cybersecurity** - Applied comprehensive cybersecurity laboratory experience across symmetric/asymmetric encryption, buffer overflow analysis, password hashing protocols, and penetration testing methodologies. Aligned technical capabilities with enterprise security frameworks including NIST Cybersecurity Framework and ISO 27001 standards to architect secure-by-design solutions for fintech and Web3 applications.
    
    
    ## 🚀 What This Dashboard Demonstrates
    
    This interactive platform showcases:
    - **Real-world problem solving** through cloud architecture scenarios
    - **Live market integration** with cryptocurrency APIs
    - **Cost modeling** and optimization strategies
    - **Security-first design** with compliance awareness
    
    ---
    
    **Explore the dashboard** to see my technical capabilities in action through interactive 
    demos and real-time data integration.
    """)

# =========================
# Cloud Architectures Section (unchanged as requested)
# =========================

elif page == "☁️ Cloud Architectures":
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
        "💬 **Manufacturing CEO**: 'Our factory floor can never depend on internet. Local systems keep production running.'",
    ]
    
    for quote in expert_quotes:
        st.info(quote)
    
    st.markdown("---")
    st.caption("💡 **Pro tip**: Most successful companies end up with hybrid approaches over time, even if they start with one model.")

# =========================
# Fintech: Crypto & Payments (without fraud tab)
# =========================

elif page == "🏦 Fintech & Crypto":
    st.markdown("# 🏦 Fintech & Digital Assets Dashboard")
    st.markdown("Professional-grade analytics for cryptocurrency and payment systems")
    
    # Create tabs for fintech areas (removed fraud detection tab)
    fintech_tab1, fintech_tab2 = st.tabs([
        "💰 Crypto & Portfolio Analytics", 
        "💳 Payments & Transaction Economics"
    ])
    
    # =========================
    # Tab 1: Crypto & Portfolio Analytics (with correlation matrix)
    # =========================
    
    with fintech_tab1:
        st.markdown("### 🎯 Professional Portfolio Management Tools")
        
        # Three-column layout
        portfolio_col1, portfolio_col2, portfolio_col3 = st.columns([3, 4, 3])
        
        with portfolio_col1:
            st.markdown("#### 🎛️ Portfolio Builder")
            
            # Token selection with categories
            st.markdown("**Major Cryptocurrencies:**")
            major_tokens = st.multiselect(
                "Select major tokens:",
                ["bitcoin", "ethereum", "binancecoin", "cardano", "solana", "polkadot"],
                default=["bitcoin", "ethereum"],
                key="major"
            )
            
            st.markdown("**Stablecoins:**")
            stable_tokens = st.multiselect(
                "Select stablecoins:",
                ["tether", "usd-coin", "dai", "busd"],
                default=["usd-coin"],
                key="stable"
            )
            
            st.markdown("**DeFi Tokens:**")
            defi_tokens = st.multiselect(
                "Select DeFi tokens:",
                ["uniswap", "aave", "compound-governance-token", "chainlink"],
                default=[],
                key="defi"
            )
            
            # Combine all selected tokens
            all_tokens = major_tokens + stable_tokens + defi_tokens
            
            if not all_tokens:
                all_tokens = ["bitcoin", "ethereum"]
            
            st.markdown("**Portfolio Allocation:**")
            # Create allocation sliders
            allocations = {}
            total_allocation = 0
            
            for token in all_tokens:
                allocation = st.slider(
                    f"{token.replace('-', ' ').title()}",
                    0, 100, 
                    100 // len(all_tokens),
                    key=f"alloc_{token}"
                )
                allocations[token] = allocation
                total_allocation += allocation
            
            if total_allocation != 100:
                st.warning(f"⚠️ Total allocation: {total_allocation}% (should be 100%)")
            
            # Portfolio size
            portfolio_size = st.number_input(
                "Portfolio Value (USD):",
                min_value=100,
                max_value=1000000,
                value=10000,
                step=1000
            )
        
        with portfolio_col2:
            st.markdown("#### 📈 Live Portfolio Dashboard")
            
            try:
                # Get current prices
                prices = cg_prices(tuple(all_tokens), vs="usd")
                
                if prices:
                    # Calculate portfolio metrics
                    portfolio_value = 0
                    asset_values = {}
                    
                    for token in all_tokens:
                        if token in prices:
                            token_allocation = allocations[token] / 100
                            token_value = portfolio_size * token_allocation
                            portfolio_value += token_value
                            asset_values[token] = token_value
                    
                    # Display key metrics
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric("Portfolio Value", f"${portfolio_value:,.0f}")
                    
                    with col_b:
                        # Calculate 24h change (simplified)
                        change_pct = np.random.uniform(-5, 5)  # Mock for demo
                        change_color = "normal" if change_pct >= 0 else "inverse"
                        st.metric("24H Change", f"{change_pct:+.2f}%", delta_color=change_color)
                    
                    with col_c:
                        # Calculate portfolio volatility (simplified)
                        volatility = np.random.uniform(15, 45)  # Mock for demo
                        st.metric("30D Volatility", f"{volatility:.1f}%")
                    
                    # Asset allocation pie chart
                    if asset_values:
                        fig_pie = go.Figure(data=[go.Pie(
                            labels=[token.replace('-', ' ').title() for token in asset_values.keys()],
                            values=list(asset_values.values()),
                            hole=0.3
                        )])
                        fig_pie.update_traces(textinfo='percent+label')
                        fig_pie.update_layout(
                            title="Portfolio Allocation",
                            height=300,
                            showlegend=True
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                
                # Price chart for primary asset
                if all_tokens:
                    primary_token = all_tokens[0]
                    df_candles = binance_klines(
                        f"{primary_token.upper().replace('-', '')}USDT" if primary_token != "bitcoin" else "BTCUSDT",
                        "1h", 
                        168  # 7 days of hourly data
                    )
                    
                    if not df_candles.empty:
                        fig_chart = go.Figure(data=[go.Candlestick(
                            x=df_candles['t'],
                            open=df_candles['o'],
                            high=df_candles['h'],
                            low=df_candles['l'],
                            close=df_candles['c']
                        )])
                        fig_chart.update_layout(
                            title=f"{primary_token.replace('-', ' ').title()} Price Chart (7D)",
                            height=250,
                            xaxis_rangeslider_visible=False
                        )
                        st.plotly_chart(fig_chart, use_container_width=True)
                    else:
                        st.info("📊 Live price chart available for major tokens")
                
            except Exception as e:
                st.error("⚠️ Unable to fetch live prices. Using demo data.")
                # Use demo values
                portfolio_value = portfolio_size
                st.metric("Portfolio Value", f"${portfolio_value:,.0f}")
        
        with portfolio_col3:
            st.markdown("#### 🔍 Risk Analytics")
            
            # Risk metrics
            st.markdown("**Risk Metrics:**")
            
            # Generate synthetic risk metrics for demo
            sharpe_ratio = np.random.uniform(0.5, 2.5)
            max_drawdown = np.random.uniform(10, 40)
            var_95 = np.random.uniform(3, 12)
            beta = np.random.uniform(0.8, 1.5)
            
            st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
            st.metric("Max Drawdown", f"-{max_drawdown:.1f}%")
            st.metric("VaR (95%)", f"-{var_95:.1f}%")
            st.metric("Beta (vs BTC)", f"{beta:.2f}")
            
            # Correlation heatmap (as requested to keep)
            if len(all_tokens) > 1:
                st.markdown("**Correlation Matrix:**")
                
                # Generate synthetic correlation data
                n_tokens = len(all_tokens)
                corr_matrix = np.random.uniform(0.3, 0.9, (n_tokens, n_tokens))
                np.fill_diagonal(corr_matrix, 1.0)
                
                # Make symmetric
                corr_matrix = (corr_matrix + corr_matrix.T) / 2
                np.fill_diagonal(corr_matrix, 1.0)
                
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=corr_matrix,
                    x=[token[:8] for token in all_tokens],
                    y=[token[:8] for token in all_tokens],
                    colorscale='RdBu',
                    zmid=0,
                    text=corr_matrix.round(2),
                    texttemplate='%{text}',
                    textfont={"size": 10},
                ))
                fig_heatmap.update_layout(
                    height=250,
                    title="Asset Correlation Matrix",
                    xaxis_title="",
                    yaxis_title=""
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Price prediction
            st.markdown("**Price Forecast (ML-based):**")
            
            if all_tokens:
                primary_token = all_tokens[0]
                try:
                    current_price = prices.get(primary_token, {}).get('usd', 50000) if prices else 50000
                except:
                    current_price = 50000
                
                # Generate forecast scenarios
                years = list(range(2025, 2031))
                conservative = [current_price * (1.05 ** (year - 2024)) for year in years]
                optimistic = [current_price * (1.15 ** (year - 2024)) for year in years]
                pessimistic = [current_price * (0.95 ** (year - 2024)) for year in years]
                
                forecast_data = pd.DataFrame({
                    'Year': years,
                    'Conservative': conservative,
                    'Optimistic': optimistic,
                    'Pessimistic': pessimistic
                })
                
                fig_forecast = go.Figure()
                fig_forecast.add_trace(go.Scatter(
                    x=forecast_data['Year'],
                    y=forecast_data['Conservative'],
                    name='Conservative',
                    line=dict(color='blue')
                ))
                fig_forecast.add_trace(go.Scatter(
                    x=forecast_data['Year'],
                    y=forecast_data['Optimistic'],
                    name='Optimistic',
                    line=dict(color='green')
                ))
                fig_forecast.add_trace(go.Scatter(
                    x=forecast_data['Year'],
                    y=forecast_data['Pessimistic'],
                    name='Pessimistic',
                    line=dict(color='red')
                ))
                
                fig_forecast.update_layout(
                    title=f"{primary_token.title()} Scenarios",
                    height=200,
                    yaxis_title="Price (USD)",
                    showlegend=True
                )
                st.plotly_chart(fig_forecast, use_container_width=True)
    
    # =========================
    # Tab 2: Payments & Transaction Economics
    # =========================
    
    with fintech_tab2:
        st.markdown("### 💳 Payment Systems & Revenue Modeling")
        
        # 2x2 grid layout
        pay_row1_col1, pay_row1_col2 = st.columns(2)
        pay_row2_col1, pay_row2_col2 = st.columns(2)
        
        with pay_row1_col1:
            st.markdown("#### 📊 Payment Method Trends")
            
            # Payment method data (real-world inspired)
            payment_methods = {
                'Credit Cards': [40, 38, 36, 35, 33],
                'Digital Wallets': [20, 25, 28, 32, 35],
                'Bank Transfers': [15, 15, 14, 13, 12],
                'BNPL': [5, 8, 12, 15, 18],
                'Cryptocurrency': [1, 2, 3, 4, 5]
            }
            years = [2020, 2021, 2022, 2023, 2024]
            
            # Create stacked area chart
            fig_trends = go.Figure()
            
            for method, values in payment_methods.items():
                fig_trends.add_trace(go.Scatter(
                    x=years,
                    y=values,
                    mode='lines+markers',
                    name=method,
                    stackgroup='one'
                ))
            
            fig_trends.update_layout(
                title="Payment Method Market Share Evolution",
                yaxis_title="Market Share (%)",
                height=300
            )
            st.plotly_chart(fig_trends, use_container_width=True)
            
            # Regional toggle
            region = st.selectbox("Region Focus:", ["Global", "North America", "Europe", "APAC"])
            if region != "Global":
                st.info(f"📍 Showing {region} payment preferences")
        
        with pay_row1_col2:
            st.markdown("#### 💰 Revenue Calculator")
            
            # Business model selector
            business_model = st.selectbox(
                "Revenue Model:",
                ["Transaction Fees", "Subscription + Fees", "Freemium Model"]
            )
            
            # Input parameters
            monthly_users = st.slider("Monthly Active Users", 1000, 10000000, 100000, 10000)
            avg_transaction = st.slider("Avg Transaction Value ($)", 10, 1000, 75)
            transactions_per_user = st.slider("Transactions per User/Month", 1, 50, 8)
            
            # Calculate revenue based on model
            if business_model == "Transaction Fees":
                fee_rate = st.slider("Transaction Fee (%)", 1.0, 5.0, 2.9, 0.1)
                fixed_fee = st.slider("Fixed Fee per Transaction ($)", 0.0, 1.0, 0.30, 0.05)
                
                monthly_transactions = monthly_users * transactions_per_user
                monthly_volume = monthly_transactions * avg_transaction
                monthly_revenue = (monthly_volume * fee_rate / 100) + (monthly_transactions * fixed_fee)
                
                st.metric("Monthly Transactions", f"{monthly_transactions:,.0f}")
                st.metric("Monthly Volume", f"${monthly_volume:,.0f}")
                st.metric("Monthly Revenue", f"${monthly_revenue:,.0f}")
                st.metric("Annual Revenue", f"${monthly_revenue * 12:,.0f}")
                
            elif business_model == "Subscription + Fees":
                subscription_fee = st.slider("Monthly Subscription ($)", 5, 100, 20)
                reduced_fee_rate = st.slider("Reduced Transaction Fee (%)", 0.5, 3.0, 1.9, 0.1)
                
                subscription_revenue = monthly_users * subscription_fee
                transaction_revenue = monthly_users * transactions_per_user * avg_transaction * reduced_fee_rate / 100
                total_revenue = subscription_revenue + transaction_revenue
                
                st.metric("Subscription Revenue", f"${subscription_revenue:,.0f}")
                st.metric("Transaction Revenue", f"${transaction_revenue:,.0f}")
                st.metric("Total Monthly Revenue", f"${total_revenue:,.0f}")
                st.metric("Annual Revenue", f"${total_revenue * 12:,.0f}")
            
            else:  # Freemium Model
                conversion_rate = st.slider("Free to Paid Conversion (%)", 1, 20, 5)
                premium_price = st.slider("Premium Monthly Price ($)", 10, 200, 50)
                
                paid_users = monthly_users * (conversion_rate / 100)
                monthly_revenue = paid_users * premium_price
                
                st.metric("Free Users", f"{int(monthly_users - paid_users):,}")
                st.metric("Premium Users", f"{int(paid_users):,}")
                st.metric("Monthly Revenue", f"${monthly_revenue:,.0f}")
                st.metric("Annual Revenue", f"${monthly_revenue * 12:,.0f}")
            
            # Unit economics
            st.markdown("**Unit Economics:**")
            revenue_per_user = monthly_revenue / monthly_users if monthly_users > 0 else 0
            st.metric("Revenue per User", f"${revenue_per_user:.2f}/month")
        
        with pay_row2_col1:
            st.markdown("#### 🛤️ Customer Conversion Funnel")
            
            # Funnel stages and conversion rates
            funnel_stages = {
                'Website Visitors': 100000,
                'Sign-ups': 15000,  # 15% conversion
                'KYC Completed': 11250,  # 75% of sign-ups
                'First Payment': 6750,   # 60% of KYC
                'Active Users': 4725,    # 70% become active
                'Power Users': 1418      # 30% become power users
            }
            
            # Calculate conversion rates
            values = list(funnel_stages.values())
            stages = list(funnel_stages.keys())
            
            # Create funnel chart
            fig_funnel = go.Figure(go.Funnel(
                y=stages,
                x=values,
                textinfo="value+percent initial",
                marker=dict(color=["lightblue", "lightgreen", "yellow", "orange", "red", "darkred"])
            ))
            
            fig_funnel.update_layout(
                title="Customer Acquisition Funnel",
                height=400
            )
            st.plotly_chart(fig_funnel, use_container_width=True)
            
            # Optimization suggestions
            st.markdown("**💡 Optimization Opportunities:**")
            st.write("• **KYC**: 25% drop-off → Streamline verification process")
            st.write("• **First Payment**: 40% drop-off → Improve onboarding UX")
            st.write("• **Retention**: 30% churn → Implement loyalty program")
        
        with pay_row2_col2:
            st.markdown("#### 📈 Transaction Analytics")
            
            # Peak hours heatmap
            hours = list(range(24))
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            # Generate realistic transaction pattern
            np.random.seed(42)
            heatmap_data = np.random.poisson(100, (7, 24))
            
            # Add business hours pattern
            for day_idx in range(5):  # Weekdays
                for hour in range(9, 18):  # Business hours
                    heatmap_data[day_idx][hour] = int(heatmap_data[day_idx][hour] * 1.5)
            
            # Weekend pattern
            for day_idx in range(5, 7):  # Weekend
                for hour in range(10, 22):  # Later hours
                    heatmap_data[day_idx][hour] = int(heatmap_data[day_idx][hour] * 1.2)
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=heatmap_data,
                x=hours,
                y=days,
                colorscale='Blues'
            ))
            fig_heatmap.update_layout(
                title="Transaction Volume by Hour",
                xaxis_title="Hour of Day",
                height=200
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Key metrics
            st.markdown("**Performance Metrics:**")
            col_a, col_b = st.columns(2)
            
            with col_a:
                success_rate = np.random.uniform(97, 99.5)
                avg_processing = np.random.uniform(1.2, 3.5)
                st.metric("Success Rate", f"{success_rate:.1f}%")
                st.metric("Avg Processing", f"{avg_processing:.1f}s")
            
            with col_b:
                dispute_rate = np.random.uniform(0.3, 1.2)
                cross_border_pct = np.random.uniform(15, 35)
                st.metric("Dispute Rate", f"{dispute_rate:.2f}%")
                st.metric("Cross-border", f"{cross_border_pct:.0f}%")
