import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from generate_data import generate_loan_data

st.set_page_config(page_title="LoanIQ | Risk Intelligence", page_icon="🏦", layout="wide")
st.markdown("""
<style>
  .stApp {background:#f4f7fb;}
  [data-testid="stSidebar"] {background:#0d1b35;}
  [data-testid="stSidebar"] * {color:#e8eef9;}
  .hero {background:linear-gradient(110deg,#102544,#164b63);padding:22px 26px;border-radius:14px;color:white;margin-bottom:16px;}
  .hero h1 {font-size:30px;margin:0;color:white;}
  .hero p {color:#c9d9e8;margin:5px 0 0 0;}
  .metric {background:white;border:1px solid #dce5ef;border-radius:12px;padding:15px 17px;min-height:105px;}
  .metric .label {font-size:13px;color:#61738a;}
  .metric .value {font-size:27px;font-weight:750;color:#132c4c;margin-top:5px;}
  .metric .hint {font-size:11px;color:#8292a5;margin-top:2px;}
  .section {font-size:20px;font-weight:700;color:#17314f;margin:12px 0 8px;}
  .note {background:#fff8e8;border-left:4px solid #d99b2b;padding:10px 14px;border-radius:6px;color:#6b5527;font-size:13px;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    p=Path("data/loan_applications_raw.csv")
    if p.exists():
        raw=pd.read_csv(p, parse_dates=["application_date"])
    else:
        raw=generate_loan_data()
    raw=raw.drop_duplicates(subset=["customer_id"]).copy()
    for c in ["monthly_income_inr","credit_score","employment_type"]:
        if c in raw and raw[c].isna().any():
            if c=="employment_type": raw[c]=raw[c].fillna(raw[c].mode().iloc[0])
            else: raw[c]=raw[c].fillna(raw[c].median())
    raw["application_date"]=pd.to_datetime(raw["application_date"], errors="coerce")
    raw["debt_to_income_ratio"]=raw["debt_to_income_ratio"].clip(0,2)
    raw["approval_status"]=raw["approved"].map({1:"Approved",0:"Rejected"})
    raw["default_status"]=raw["defaulted"].map({1:"Default",0:"Repaid"})
    raw["income_band"]=pd.cut(raw["monthly_income_inr"],[0,30000,60000,100000,200000,1000000],
        labels=["Under 30k","30k–60k","60k–100k","100k–200k","200k+"])
    raw["credit_band"]=pd.cut(raw["credit_score"],[0,579,669,739,799,900],
        labels=["Poor","Fair","Good","Very Good","Excellent"])
    return raw

df=load_data()
st.sidebar.markdown("## 🏦 LoanIQ")
st.sidebar.caption("INTELLIGENT LOAN ANALYTICS")
page=st.sidebar.radio("NAVIGATION",[
    "01  Executive Command Centre","02  Loan Portfolio","03  Credit Risk Intelligence",
    "04  Customer Segments","05  Data Quality & EDA","06  What-if Simulator","07  Data Export"
])
st.sidebar.markdown("---")
st.sidebar.caption("SYNTHETIC DEMONSTRATION DATA • NOT REAL BORROWERS")
st.markdown('<div class="hero"><h1>LoanIQ — Loan Intelligence Platform</h1><p>Understand the loan portfolio, identify risk patterns and make data-informed lending decisions.</p></div>',unsafe_allow_html=True)
st.markdown('<div class="note">Synthetic demonstration dataset. These records are generated for academic analysis and do not represent actual customers, loan decisions or a real financial institution.</div>',unsafe_allow_html=True)

with st.expander("Global filters", expanded=False):
    c1,c2,c3,c4=st.columns(4)
    purpose=c1.multiselect("Loan purpose",sorted(df.loan_purpose.unique()),default=sorted(df.loan_purpose.unique()))
    emp=c2.multiselect("Employment",sorted(df.employment_type.unique()),default=sorted(df.employment_type.unique()))
    tier=c3.multiselect("City tier",sorted(df.city_tier.unique()),default=sorted(df.city_tier.unique()))
    status=c4.multiselect("Approval status",["Approved","Rejected"],default=["Approved","Rejected"])
    min_score,max_score=st.slider("Credit score range",300,900,(300,900))
# Apply filters explicitly
f=df[df["loan_purpose"].isin(purpose)&df["employment_type"].isin(emp)&df["city_tier"].isin(tier)&
     df["approval_status"].isin(status)&df["credit_score"].between(min_score,max_score)]

def money(x): return f"₹{x/10000000:.2f} Cr" if x>=1e7 else f"₹{x/100000:.1f} L"
def metric(col,label,value,hint="Calculated from filtered records"):
    col.markdown(f'<div class="metric"><div class="label">{label}</div><div class="value">{value}</div><div class="hint">{hint}</div></div>',unsafe_allow_html=True)
def heading(t): st.markdown(f'<div class="section">{t}</div>',unsafe_allow_html=True)

if page.startswith("01"):
    st.subheader("Where is the loan opportunity, and where is the risk?")
    a,b,c,d=st.columns(4)
    metric(a,"Applications in view",f"{len(f):,}")
    metric(b,"Approval rate",f"{f.approved.mean()*100:.1f}%" if len(f) else "—")
    metric(c,"Default rate",f"{f.defaulted.mean()*100:.1f}%" if len(f) else "—")
    metric(d,"Average credit score",f"{f.credit_score.mean():.0f}" if len(f) else "—")
    e,g,h,i=st.columns(4)
    metric(e,"Loan book requested",money(f.loan_amount_inr.sum()) if len(f) else "₹0")
    metric(g,"Average loan size",f"₹{f.loan_amount_inr.mean():,.0f}" if len(f) else "—")
    metric(h,"Average monthly income",f"₹{f.monthly_income_inr.mean():,.0f}" if len(f) else "—")
    metric(i,"High-risk share",f"{(f.debt_to_income_ratio>.45).mean()*100:.1f}%" if len(f) else "—")
    heading("Portfolio overview")
    x,y=st.columns(2)
    by_month=f.set_index("application_date").resample("MS").size().reset_index(name="applications")
    x.plotly_chart(px.line(by_month,x="application_date",y="applications",title="Applications over time",markers=True),use_container_width=True)
    y.plotly_chart(px.histogram(f,x="loan_purpose",color="approval_status",barmode="group",title="Applications by loan purpose"),use_container_width=True)
    x,y=st.columns(2)
    x.plotly_chart(px.histogram(f,x="credit_score",color="default_status",nbins=25,title="Credit score distribution by repayment outcome"),use_container_width=True)
    y.plotly_chart(px.scatter(f,x="monthly_income_inr",y="loan_amount_inr",color="approval_status",size="loan_tenure_months",hover_data=["customer_id"],title="Income vs requested loan amount"),use_container_width=True)
    heading("Automated observations")
    if len(f):
        worst=f.groupby("employment_type").defaulted.mean().sort_values(ascending=False)
        purpose_risk=f.groupby("loan_purpose").defaulted.mean().sort_values(ascending=False)
        q1,q2,q3=st.columns(3)
        q1.info(f"Highest observed default share: **{worst.index[0]}** ({worst.iloc[0]*100:.1f}%).")
        q2.info(f"Highest purpose-level default share: **{purpose_risk.index[0]}** ({purpose_risk.iloc[0]*100:.1f}%).")
        q3.info(f"{(f.debt_to_income_ratio>.45).sum():,} filtered records have a debt-to-income ratio above 0.45.")
elif page.startswith("02"):
    st.subheader("Loan Portfolio Analytics")
    a,b=st.columns(2)
    a.plotly_chart(px.sunburst(f,path=["loan_purpose","approval_status"],values="loan_amount_inr",title="Loan amount mix by purpose and approval"),use_container_width=True)
    b.plotly_chart(px.box(f,x="employment_type",y="loan_amount_inr",color="employment_type",title="Loan amount by employment type"),use_container_width=True)
    c,d=st.columns(2)
    c.plotly_chart(px.bar(f.groupby("city_tier",as_index=False).agg(applications=("customer_id","count"),amount=("loan_amount_inr","sum")),x="city_tier",y="amount",title="Requested amount by city tier"),use_container_width=True)
    d.plotly_chart(px.histogram(f,x="loan_tenure_months",color="approval_status",barmode="group",title="Tenure distribution"),use_container_width=True)
    st.dataframe(f[["customer_id","application_date","loan_purpose","employment_type","loan_amount_inr","loan_tenure_months","approval_status"]].head(100),use_container_width=True)
elif page.startswith("03"):
    st.subheader("Credit Risk Intelligence")
    f=f.copy()
    f["risk_band"]=np.select([ (f.credit_score<580)|(f.debt_to_income_ratio>.65),
                              (f.credit_score<670)|(f.debt_to_income_ratio>.45)],
                             ["High","Medium"],default="Low")
    a,b=st.columns(2)
    a.plotly_chart(px.histogram(f,x="credit_band",color="default_status",barmode="group",title="Credit quality vs default outcome"),use_container_width=True)
    b.plotly_chart(px.bar(f.groupby("risk_band",as_index=False).agg(default_rate=("defaulted","mean"),count=("customer_id","count")),x="risk_band",y="default_rate",color="risk_band",title="Observed default rate by simple risk band"),use_container_width=True)
    st.caption("Risk bands here are transparent analytical segments, not a regulated credit score or lending recommendation.")
    st.plotly_chart(px.scatter(f,x="debt_to_income_ratio",y="credit_score",color="default_status",hover_data=["customer_id","loan_amount_inr"],title="Debt burden vs credit score"),use_container_width=True)
    st.dataframe(f.groupby("credit_band",observed=True).agg(applications=("customer_id","count"),default_rate=("defaulted","mean"),avg_loan=("loan_amount_inr","mean")).reset_index(),use_container_width=True)
elif page.startswith("04"):
    st.subheader("Customer Segmentation")
    seg=f.copy()
    seg["segment"]=np.select([(seg.monthly_income_inr<40000)&(seg.credit_score<650),
       (seg.monthly_income_inr>=100000)&(seg.credit_score>=700),
       (seg.age<30)],["Emerging / constrained","Established / stronger profile","Young applicants"],default="Mass market")
    summary=seg.groupby("segment",as_index=False).agg(customers=("customer_id","count"),avg_income=("monthly_income_inr","mean"),avg_loan=("loan_amount_inr","mean"),default_rate=("defaulted","mean"),approval_rate=("approved","mean"))
    st.plotly_chart(px.bar(summary,x="segment",y="customers",color="segment",title="Customer segment size"),use_container_width=True)
    st.dataframe(summary,use_container_width=True)
    st.plotly_chart(px.scatter(seg,x="monthly_income_inr",y="credit_score",color="segment",size="loan_amount_inr",hover_data=["customer_id"],title="Customer profile map"),use_container_width=True)
elif page.startswith("05"):
    st.subheader("Data Quality, Preparation & Exploratory Analysis")
    raw=pd.read_csv("data/loan_applications_raw.csv") if Path("data/loan_applications_raw.csv").exists() else generate_loan_data()
    q1,q2,q3=st.columns(3)
    metric(q1,"Raw rows",f"{len(raw):,}")
    metric(q2,"Duplicate customer IDs",f"{raw.customer_id.duplicated().sum():,}")
    metric(q3,"Missing cells",f"{raw.isna().sum().sum():,}")
    st.write("Missing values by column")
    miss=raw.isna().sum().reset_index(); miss.columns=["column","missing_values"]
    st.plotly_chart(px.bar(miss[miss.missing_values>0],x="column",y="missing_values",title="Missing values before cleaning"),use_container_width=True)
    st.write("Cleaning approach: remove duplicate customer IDs; impute numeric missing values with the median; impute categorical missing values with the mode; parse dates; cap extreme debt-to-income ratios at 2 for exploratory stability.")
    st.dataframe(pd.DataFrame({"Column":df.columns,"Data type":[str(x) for x in df.dtypes],"Missing after cleaning":df.isna().sum().values}),use_container_width=True)
    corr=df.select_dtypes(include=np.number).corr(numeric_only=True)
    st.plotly_chart(px.imshow(corr,text_auto=".2f",aspect="auto",color_continuous_scale="RdBu_r",title="Correlation matrix (numeric features)"),use_container_width=True)
    st.plotly_chart(px.box(df,x="loan_purpose",y="loan_amount_inr",title="Loan amount spread by purpose"),use_container_width=True)
elif page.startswith("06"):
    st.subheader("What-if Loan Simulator")
    st.caption("Explore how applicant attributes change a transparent illustrative risk indicator. This is not a loan decision engine.")
    c1,c2=st.columns(2)
    income=c1.number_input("Monthly income (₹)",min_value=10000,max_value=1000000,value=75000,step=5000)
    amount=c2.number_input("Loan amount (₹)",min_value=10000,max_value=10000000,value=800000,step=50000)
    score=c1.slider("Credit score",300,900,700)
    emi=c2.number_input("Existing monthly EMI (₹)",min_value=0,max_value=500000,value=10000,step=1000)
    tenure=c1.select_slider("Tenure (months)",options=[12,24,36,48,60,72,84],value=60)
    dti=(emi+amount/tenure)/income
    risk_logit=-2+(650-score)*.012+dti*2+(amount/income>18)*.65
    risk=1/(1+np.exp(-risk_logit))
    a,b,c=st.columns(3)
    metric(a,"Debt-to-income indicator",f"{dti:.2f}")
    metric(b,"Illustrative risk indicator",f"{risk*100:.1f}%")
    metric(c,"Profile band","Elevated" if risk>.5 else "Moderate" if risk>.25 else "Lower")
    st.progress(float(np.clip(risk,0,1)))
    st.warning("Do not use this simulator for real credit decisions. The synthetic formula is designed only to demonstrate analytics.")
elif page.startswith("07"):
    st.subheader("Data Export")
    st.write(f"Current filtered dataset: **{len(f):,} records**")
    st.download_button("Download filtered CSV",f.to_csv(index=False).encode("utf-8"),"loaniq_filtered_data.csv","text/csv")
    st.download_button("Download cleaned full dataset",df.to_csv(index=False).encode("utf-8"),"loaniq_cleaned_data.csv","text/csv")
    st.dataframe(f.head(50),use_container_width=True)
st.markdown("---")
st.caption("LoanIQ Academic Project • Synthetic data • Exploratory and educational use only")
