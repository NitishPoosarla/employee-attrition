-- 09-management-attrition — people analytics in SQL.
-- Loads: data/processed/hr_clean.csv -> `hr` (Attrition, attrition, OverTime,
--        JobSatisfaction, YearsAtCompany, MonthlyIncome, Department, JobRole).

-- Headline: overtime flag (the sharpest management lever)
SELECT OverTime, COUNT(*) AS employees, ROUND(AVG(attrition) * 100, 1) AS attrition_pct
FROM hr GROUP BY OverTime;

-- Money is not the lever: average income by overtime status
SELECT OverTime, ROUND(AVG(MonthlyIncome), 0) AS avg_income
FROM hr GROUP BY OverTime;

-- Onboarding owns the risk: tenure bands
SELECT CASE WHEN YearsAtCompany <= 2 THEN '0-2y'
            WHEN YearsAtCompany <= 5 THEN '3-5y'
            WHEN YearsAtCompany <= 10 THEN '6-10y'
            ELSE '10y+' END AS tenure_band,
       COUNT(*) AS employees, ROUND(AVG(attrition) * 100, 1) AS attrition_pct
FROM hr GROUP BY tenure_band ORDER BY tenure_band;

-- Concentration by role & department
SELECT Department, JobRole, COUNT(*) AS employees,
       ROUND(AVG(attrition) * 100, 1) AS attrition_pct
FROM hr GROUP BY Department, JobRole ORDER BY attrition_pct DESC;

-- Ethics guardrail reminder: aggregate-level only in this file — no individual rows returned.
