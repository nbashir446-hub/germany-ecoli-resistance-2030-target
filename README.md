# 🧫 Third-Generation Cephalosporin-Resistant *E. coli*: Analysis and RAG Assistant

Analysis of antimicrobial resistance (AMR) trends, burden metrics and 2030 EU targets across 8 European countries, 2015-2024.

## 🎯 Executive Summary

- **Is Germany on track?** Yes, on the latest official ECDC data. Germany's incidence fell by 14.9% from its 2019 baseline (12.0 to 10.2 per 100,000 in 2023). This is below its 2030 target of 10.6 (a required 12% reduction), with a small margin of 0.4.
- **EU comparison:**
  - At or below target: Germany, Italy and the Netherlands.
  - Above target: Sweden and Poland.
  - Moving the wrong way: Spain (+29.5% against its 2019 baseline).
  - No confirmed 2030 target in the data: Austria and Denmark.
- **Note:** targets are judged in 2030, so these reductions have to be sustained.

## 📊 Data Sources

- 🌐 **ECDC Surveillance Atlas of Infectious Diseases (EARS-Net):** % resistant isolates and resistant isolate counts per country and year.
- 👥 **Eurostat-style Population Data:** Annual population metrics used for calculating population-normalized incidence rates.
- 📋 **ECDC country data:** official 2019 baselines, latest incidence and 2030 targets (EU Council Recommendation 2023/C 220/01).

## ⚙️ Methodology

1. **Data integration:** loaded and merged four datasets with `pandas` on country and year.
2. **Calculated incidence:** resistant isolates ÷ population × 100,000.
3. **Linear regression:** one `scikit-learn` model per country for % resistant and for calculated incidence over time (slope and R²).
4. **Target check:** latest official ECDC incidence compared with each country's 2030 target.
5. **Dashboard:** Built comprehensive analytical dashboards in Power BI and Tableau Public.

## 🔑 Key Insights

- **Metric Divergence:** The two measures can disagree,in Italy the % resistant fell (30.1% in 2015 to 27.7% in 2024) while calculated incidence rose (2.8 to 14.9 per 100,000). Both need to be looked at.
- **Calculated vs official incidence.** Calculated incidence uses reported isolates only, so it depends on how many isolates a country reports. It is used for direction and trend. Targets are checked against the official ECDC figure.

## ⚠️ Limitations

- **Sample Size & Linearity:** Only 10 yearly points per country, so the linear trends describe direction and are not forecasts. Germany's fit is weak (R² = 0.28).
- **Train/Test Splitting:** No train/test split in this project.
- **Reporting coverage changed over time:** German isolate counts rose from 930 (2015) to 2,816 (2017), and Italy's from 2,087 (2017) to 4,664 (2018). Part of the rise in calculated incidence may reflect this.

## 🤖 Technical Extensions & RAG Chatbot (LlamaIndex, Groq, Gradio)

- **Interactive Assistant:** An assistant that answers only from the project results and the ECDC report (notebook/02_amr_chatbot.ipynb, source files in chatbot/). It refuses questions outside the data and shows the evidence it used.
- **Run it:** pip install -r requirements.txt, set the environment variable GROQ_API_KEY, then python app.py. In Colab, use notebook/02_amr_chatbot.ipynb and add the key as a Colab secret named GROQ_API_KEY.
- **Security:** add your own Groq key as a Colab secret named `GROQ_API_KEY`. Never commit a key to the repository.

## 📁 Repository Structure

```
├── notebooks/
│   ├── 01_amr_analysis.ipynb      # merge, calculated incidence, regression, charts, target check
│   └── 02_amr_chatbot.ipynb       # chatbot
├── Data/                          # four input CSVs and two result CSVs
├── Chatbot/
│   ├── results_sources.md         # text the chatbot searches
│   └── test_questions.csv         # test questions with expected answers
├── app.py                         # run the chatbot outside Colab
├── requirements.txt
├── Dashboard/                     # Power BI file, Tableau PDF export
├── report/
│   └── AMR_Project_Report.docx    # written report
└── README.md
```

## 🛠️ Built With

Python, pandas, scikit-learn, matplotlib, LlamaIndex, Groq, Gradio, Google Colab, Power BI and Tableau Public.
