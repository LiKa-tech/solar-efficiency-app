import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import base64

st.set_page_config(page_title="Solar Plant Efficiency Analyzer", page_icon="⚡")

st.title("🔆 Solar Plant Efficiency Analyzer")

# Input Panel Info
with st.sidebar:
    st.header("Solar Panel Info")
    model = st.text_input("Solar Panel Model")
    efficiency = st.number_input("Panel Efficiency (%)", min_value=0.0, max_value=100.0, value=18.0)
    num_panels = st.number_input("Number of Panels", min_value=1, value=10)
    panel_area = 1.6  # m²

# File Upload
uploaded_file = st.file_uploader("📄 Upload CSV (Month, Irradiance, ActualGeneration)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        if not {"Month", "Irradiance", "ActualGeneration"}.issubset(df.columns):
            st.error("CSV must have columns: Month, Irradiance, ActualGeneration")
        else:
            # Calculate expected generation
            df["ExpectedGeneration"] = (
                (efficiency / 100) * num_panels * panel_area * df["Irradiance"]
            )
            total_expected = df["ExpectedGeneration"].sum()
            total_actual = df["ActualGeneration"].sum()
            overall_eff = (total_actual / total_expected) * 100 if total_expected else 0

            # Display Data
            st.subheader("📊 Generation Comparison")
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(df["Month"], df["ExpectedGeneration"], label="Expected", alpha=0.6)
            ax.bar(df["Month"], df["ActualGeneration"], label="Actual", alpha=0.6)
            ax.set_ylabel("kWh")
            ax.set_title("Monthly Generation: Expected vs Actual")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

            st.markdown(f"**Total Expected:** {total_expected:.2f} kWh")
            st.markdown(f"**Total Actual:** {total_actual:.2f} kWh")
            st.markdown(f"**Overall Efficiency:** {overall_eff:.2f}%")

            # Generate report
            report = StringIO()
            report.write("Solar Plant Efficiency Report\n")
            report.write(f"Model: {model}\n")
            report.write(f"Efficiency: {efficiency}%\n")
            report.write(f"Panels: {num_panels}\n\n")
            report.write("Month | Irradiance | Expected | Actual\n")
            report.write("-----------------------------------------\n")
            for _, row in df.iterrows():
                report.write(
                    f"{row['Month']:5} | {row['Irradiance']:10.2f} | {row['ExpectedGeneration']:8.2f} | {row['ActualGeneration']:8.2f}\n"
                )
            report.write("\n")
            report.write(f"Total Expected: {total_expected:.2f} kWh\n")
            report.write(f"Total Actual: {total_actual:.2f} kWh\n")
            report.write(f"Overall Efficiency: {overall_eff:.2f}%\n")

            # Download link
            b64 = base64.b64encode(report.getvalue().encode()).decode()
            href = f'<a href="data:file/txt;base64,{b64}" download="solar_efficiency_report.txt">📥 Download Report</a>'
            st.markdown(href, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("Upload a CSV file to begin analysis.")
