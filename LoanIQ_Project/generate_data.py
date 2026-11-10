import numpy as np
import pandas as pd

def generate_loan_data(n=10000, seed=42):
    rng = np.random.default_rng(seed)
    age = rng.integers(21, 66, n)
    employment = rng.choice(["Salaried", "Self-employed", "Business", "Contract"], n, p=[.52,.20,.18,.10])
    city_tier = rng.choice(["Tier 1", "Tier 2", "Tier 3"], n, p=[.35,.40,.25])
    income = np.where(employment=="Salaried", rng.normal(72000, 28000, n),
             np.where(employment=="Self-employed", rng.normal(85000, 42000, n),
             np.where(employment=="Business", rng.normal(115000, 60000, n), rng.normal(48000,18000,n))))
    income = np.clip(income, 15000, 500000).round(0)
    loan_amount = np.clip(rng.lognormal(np.log(650000), .65, n), 50000, 5000000).round(0)
    tenure = rng.choice([12, 24, 36, 48, 60, 72, 84], n, p=[.05,.08,.15,.18,.25,.17,.12])
    credit_score = np.clip(rng.normal(690, 75, n), 300, 900).round().astype(int)
    existing_emi = np.clip(income*rng.uniform(.02,.35,n), 0, income*.6)
    debt_to_income = (existing_emi + loan_amount/(tenure*1.0)) / income
    purpose = rng.choice(["Home", "Personal", "Education", "Vehicle", "Business", "Medical"], n,
                         p=[.20,.28,.12,.17,.13,.10])
    interest_rate = np.clip(15.5 - credit_score*.009 + rng.normal(0,1.2,n), 7.5, 22).round(2)
    # Transparent synthetic risk mechanism; not a real lender scorecard.
    logit = (-2.0 + (650-credit_score)*.012 + debt_to_income*2.0
             + (employment=="Contract")*.35 + (employment=="Self-employed")*.15
             + (loan_amount/income > 18)*.65 + rng.normal(0,.45,n))
    probability = 1/(1+np.exp(-logit))
    defaulted = rng.binomial(1, np.clip(probability,.02,.85), n)
    approval_prob = 1/(1+np.exp(-(-1.5 + (credit_score-650)*.018 - debt_to_income*2.4
                                  + (income>60000)*.25)))
    approved = rng.binomial(1, approval_prob, n)
    application_date = pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 1400, n), unit="D")
    df = pd.DataFrame({
        "customer_id":[f"CUST{i:06d}" for i in range(1,n+1)],
        "application_date":application_date,
        "age":age, "employment_type":employment, "city_tier":city_tier,
        "monthly_income_inr":income, "loan_amount_inr":loan_amount,
        "loan_tenure_months":tenure, "credit_score":credit_score,
        "existing_emi_inr":existing_emi.round(0),
        "debt_to_income_ratio":debt_to_income.round(3),
        "loan_purpose":purpose, "interest_rate_pct":interest_rate,
        "approved":approved, "defaulted":defaulted
    })
    # Add a small amount of realistic data-quality issues for cleaning exercise.
    for col in ["monthly_income_inr", "credit_score", "employment_type"]:
        idx = rng.choice(n, size=max(1,int(.012*n)), replace=False)
        df.loc[idx,col] = np.nan
    dup = df.sample(frac=.003, random_state=seed)
    df = pd.concat([df,dup], ignore_index=True)
    return df

if __name__ == "__main__":
    generate_loan_data().to_csv("data/loan_applications_raw.csv", index=False)
