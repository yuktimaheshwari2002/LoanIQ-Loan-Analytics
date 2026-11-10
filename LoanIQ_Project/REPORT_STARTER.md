# LoanIQ – Intelligent Loan Analytics & Risk Intelligence

## Abstract
This individual project develops an interactive loan analytics platform using a synthetic dataset of loan applications. It demonstrates data generation, data cleaning, descriptive analytics, diagnostic analysis and dashboard-based communication of business insights. The dataset is synthetic and is not sourced from a real bank or real borrowers.

## 1. Introduction
Lenders need to understand application volumes, customer profiles, requested loan amounts, repayment outcomes and risk indicators. LoanIQ provides a consolidated view of these dimensions to support exploratory business analysis.

## 2. Business objectives
- Describe the synthetic loan application portfolio.
- Explore approval and default patterns across customer and loan attributes.
- Examine relationships among income, loan amount, credit score and debt burden.
- Demonstrate how interactive filters and a what-if interface can support exploratory analysis.

## 3. Dataset and domain
The dataset contains 10,000 generated customer/application records before a small number of deliberately introduced duplicate rows. Fields include age, employment type, city tier, monthly income, loan amount, tenure, credit score, existing EMI, debt-to-income ratio, loan purpose, interest rate, approval outcome and default outcome. The generation process uses a fixed random seed for reproducibility.

## 4. Synthetic data generation
Data is generated in `generate_data.py`. The script uses probability distributions and controlled relationships to create plausible variation. A small proportion of missing values and duplicate customer IDs is intentionally added to demonstrate preparation techniques. The default outcome is generated from a transparent synthetic probability mechanism; it is not a validated real-world credit-risk model.

## 5. Data cleaning and transformation
The application removes duplicate customer IDs, imputes missing numeric values using the median, imputes missing categorical values using the mode, parses application dates and caps the debt-to-income ratio at 2 for exploratory stability. Derived fields include approval status, default status, income band and credit band.

## 6. Descriptive and diagnostic analytics
The dashboard provides application counts, approval share, default share, average credit score, requested loan amount and average income. Visualizations include application trends, loan-purpose comparisons, credit-score distributions, income-versus-loan scatter plots, tenure distributions and city-tier comparisons. Grouped default rates are used to diagnose where observed outcomes differ across segments.

## 7. Dashboard framework
The Streamlit application contains seven modules: Executive Command Centre, Loan Portfolio, Credit Risk Intelligence, Customer Segments, Data Quality & EDA, What-if Simulator and Data Export. Global filters allow users to explore subsets of the synthetic records.

## 8. Key interpretation guidance
Observed associations are descriptive and do not establish causation. Segment differences can arise from the synthetic data-generation rules. The what-if simulator is illustrative and must not be used for actual credit decisions. Before submission, run the dashboard, capture screenshots of each module and insert the screenshots in this report.

## 9. Conclusion
LoanIQ demonstrates an end-to-end individual data analytics workflow: generating a business-oriented synthetic dataset, preparing the data, exploring patterns and presenting findings through an interactive dashboard. Future group-project extensions may include classification model comparison, clustering, association-rule mining or regression, as specified in the course brief.

## 10. Reproducibility
Run `pip install -r requirements.txt`, then `python generate_data.py`, followed by `streamlit run app.py`. The fixed seed in the generator supports repeatable dataset creation.
