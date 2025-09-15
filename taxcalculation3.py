#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd

st.set_page_config(page_title="Indian Tax Calculator FY 2024-25", layout="wide")
st.title("🇮🇳 Indian Income Tax Calculator (Old vs New Regime)")
st.caption("Salary, House Property, Business, Capital Gains & Deductions with Slab-wise Computation")

# -------------------------
# Instructions
# -------------------------
st.header("ℹ️ Instructions")
st.info("""
- Resident: Taxed on global income.
- RNOR: Taxed only on Indian income.
- Non-Resident: Taxed only on Indian income.

- Rebate under Section 87A: Old ≤5L → ₹12,500, New ≤7L → ₹25,000
- Health & Education Cess: 4% on total tax
- Standard Deduction: Old ₹50,000, New ₹75,000
""")

# -------------------------
# Residential Status
# -------------------------
status = st.radio("Select Residential Status:", ["Resident", "Resident but Not Ordinarily Resident (RNOR)", "Non-Resident"])

# -------------------------
# Age Group
# -------------------------
age_group = st.radio("Select Age Group:", ["<60","60-80",">80"])

# -------------------------
# Salary Inputs
# -------------------------
st.header("💼 Salary Income")
basic = st.number_input("Basic Salary (Annual) ₹", 0, step=1000)
da = st.number_input("Dearness Allowance (DA) ₹", 0, step=1000)
hra = st.number_input("House Rent Allowance (HRA) ₹", 0, step=1000)
rent_paid = st.number_input("Actual Rent Paid (Annual) ₹", 0, step=1000)
metro = st.checkbox("Metro City (HRA exemption 50% of Basic+DA, else 40%)")
allowances = st.number_input("Other Allowances ₹", 0, step=1000)
perquisites = st.number_input("Perquisites ₹", 0, step=1000)
bonus = st.number_input("Bonus ₹", 0, step=1000)

# HRA Exemption
hra_exempt = 0
if hra > 0 and rent_paid > 0:
    hra_exempt = min(hra, (0.5 if metro else 0.4)*(basic+da), rent_paid - 0.1*(basic+da))

salary_gross = basic + da + hra + allowances + perquisites + bonus
salary_taxable_old = max(0, salary_gross - hra_exempt - 50000)  # Std Deduction Old
salary_taxable_new = max(0, salary_gross - hra_exempt - 75000)  # Std Deduction New
st.write(f"Total Gross Salary: ₹{salary_gross:,}")
st.write(f"HRA Exemption: ₹{hra_exempt:,}")

# -------------------------
# House Property Inputs
# -------------------------
st.header("🏠 House Property Income")
n_props = st.number_input("Number of Properties", 1, 3, 1)
house_list = []
for i in range(int(n_props)):
    with st.expander(f"Property #{i+1}"):
        ptype = st.selectbox("Type", ["Self-occupied", "Let-out"], key=f"ptype{i}")
        rent = st.number_input("Monthly Rent (₹)", 0, step=500, key=f"rent{i}") if ptype=="Let-out" else 0
        muni = st.number_input("Municipal Taxes (Annual ₹)", 0, step=500, key=f"muni{i}")
        loan = st.number_input("Home Loan Interest (Annual ₹)", 0, step=1000, key=f"loan{i}")
        house_list.append({"type": ptype, "rent": rent, "municipal": muni, "loan": loan})

house_df, total_house_income = [], 0
for idx, h in enumerate(house_list):
    if h["type"]=="Self-occupied":
        income = -min(200000, h["loan"])
        nav, deduction30 = 0, 0
    else:
        nav = h["rent"]*12 - h["municipal"]
        deduction30 = 0.3*nav
        income = nav - deduction30 - h["loan"]
    total_house_income += income
    house_df.append({"Property": f"Property {idx+1}", "Type": h["type"], "NAV": nav, "30% Deduction": deduction30, "Loan Interest": h["loan"], "Income": income})

house_df = pd.DataFrame(house_df)
st.dataframe(house_df)
st.write(f"Total House Property Income: ₹{total_house_income:,}")

# -------------------------
# Business/Profession Inputs
# -------------------------
st.header("🏢 Business/Professional Income")
turnover = st.number_input("Gross Receipts / Turnover ₹", 0, step=1000)
expenses = st.number_input("Business Expenses ₹", 0, step=1000)
dep = st.number_input("Depreciation ₹", 0, step=1000)
net_business_income = max(0, turnover - expenses - dep)
st.write(f"Net Business Income: ₹{net_business_income:,}")

# -------------------------
# Capital Gains Inputs
# -------------------------
st.header("📈 Capital Gains")
stcg_111a = st.number_input("STCG on Equity (u/s 111A, 15%) ₹", 0, step=1000)
stcg_other = st.number_input("Other STCG (taxed at slab) ₹", 0, step=1000)
ltcg_112a = st.number_input("LTCG on Equity (u/s 112A, 10% > ₹1L) ₹", 0, step=1000)
ltcg_other = st.number_input("Other LTCG (u/s 112, 20% with indexation) ₹", 0, step=1000)
ltcg_taxable = max(0, ltcg_112a - 100000)

# -------------------------
# Other Income & Deductions
# -------------------------
st.header("💰 Other Income & Deductions")
other_income = st.number_input("Other Income (FD, Dividends, Gifts) ₹", 0, step=1000)
ded_80c = st.number_input("80C Investments ₹ (Max ₹1.5L)", 0, step=1000)
ded_80d = st.number_input("80D Medical Insurance ₹ (Max ₹25k/₹50k)", 0, step=1000)
ded_80tta = st.number_input("80TTA Savings Interest ₹ (Max ₹10k)", 0, step=1000)

total_deductions = min(150000, ded_80c) + ded_80d + min(10000, ded_80tta)
st.write(f"Total Deductions: ₹{total_deductions:,}")

# -------------------------
# Taxable Income
# -------------------------
gross_income_old = salary_taxable_old + total_house_income + net_business_income + stcg_other + other_income
gross_income_new = salary_taxable_new + total_house_income + net_business_income + stcg_other + other_income

# -------------------------
# Tax Functions
# -------------------------
def tax_old_regime(income, age="<60"):
    tax = 0
    if age=="<60": slabs=[(250000,0.0),(250000,0.05),(500000,0.2),(float('inf'),0.3)]
    elif age=="60-80": slabs=[(300000,0.0),(200000,0.05),(500000,0.2),(float('inf'),0.3)]
    else: slabs=[(500000,0.0),(500000,0.2),(float('inf'),0.3)]
    prev=0
    for slab,rate in slabs:
        taxable=min(max(income-prev,0),slab)
        tax+=taxable*rate
        prev+=slab
    return tax

def tax_new_regime(income):
    tax=0
    slabs=[(300000,0.0),(400000,0.05),(300000,0.10),(300000,0.15),(300000,0.20),(float('inf'),0.30)]
    prev=0
    for slab,rate in slabs:
        taxable=min(max(income-prev,0),slab)
        tax+=taxable*rate
        prev+=slab
    return tax

# -------------------------
# Compute Tax
# -------------------------
tax_old = tax_old_regime(gross_income_old, age_group) + 0.15*stcg_111a + 0.10*ltcg_taxable + 0.20*ltcg_other
if gross_income_old <= 500000: tax_old = max(0, tax_old-12500)
tax_old_total = tax_old*1.04  # 4% cess

tax_new = tax_new_regime(gross_income_new) + 0.15*stcg_111a + 0.10*ltcg_taxable + 0.20*ltcg_other
if gross_income_new <= 700000: tax_new = max(0, tax_new-25000)
tax_new_total = tax_new*1.04

# -------------------------
# Display Tax
# -------------------------
st.subheader("💵 Tax Computation (incl. 4% Cess)")
st.write(f"Old Regime Tax: ₹{tax_old_total:,.0f}")
st.write(f"New Regime Tax: ₹{tax_new_total:,.0f}")

# Compare Regimes
if tax_old_total < tax_new_total:
    st.success(f"✅ Old Regime is better. You save ₹{tax_new_total - tax_old_total:,.0f}")
else:
    st.success(f"✅ New Regime is better. You save ₹{tax_old_total - tax_new_total:,.0f}")

