import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import base64
import numpy as np

st.set_page_config(page_title="Solar Plant Efficiency Analyzer", page_icon="⚡")

st.title("🔆 Solar Plant Efficiency Analyzer")

# Input Panel Info
with st.sidebar:
    st.header("Solar Panel Info")
    panel_power = st.number_input("Solar Panel Power (W)", min_value=1, value=400)  # Power per panel in watts
    efficiency = st.number_input("Panel Efficiency (%)", min_value=0.0, max_value=100.0, value=18.0)  # Efficiency of panel
    num_panels = st.number_input("Number of Panels", min_value=1, value=10)  # Number of panels
    panel_area = 1.6  # Average panel area in m²

# File Upload for CSVs
irradiance_file = st.file_uploader("📄 Upload Irradiance Data CSV", type="csv")
generation_file = st.file_uploader("📄 Upload Monthly Generation Data CSV", type="csv")

if irradiance_file and generation_file:
    try:
        # Read the CSV files
        irradiance_df = pd.read_csv(irradiance_file)
        generation_df = pd.read_csv(generation_file)

        # Ensure both CSVs have a 'Month' column and that they match
        if "Month" not in irradiance_df.columns or "Month" not in generation_df.columns:
            st.error("CSV files must have a 'Month' column")
        elif len(irradiance_df) != len(generation_df):
            st.error("Both CSV files must have the same number of months")
        else:
            # Merge the two dataframes on the 'Month' column
            merged_df = pd.merge(irradiance_df, generation_df, on="Month")

            # Calculate the expected generation per month based on the panel info
            merged_df["ExpectedGeneration"] = (
                (efficiency / 100) * num_panels * panel_area * merged_df["Irradiance"]
            )

            total_expected = merged_df["ExpectedGeneration"].sum()
            total_actual = merged_df["ActualGeneration"].sum()
            overall_eff = (total_actual / total_expected) * 100 if total_expected else 0

            # Display Data
            st.subheader("📊 Generation Comparison")
            fig, ax = plt.subplots(figsize=(10, 6))

            # Plot bars with color scaling based on efficiency
            color_map = plt.get_cmap("RdYlGn_r")  # Green to Red color map (inverse)

            for i, month in enumerate(merged_df["Month"]):
                eff_diff = (merged_df["ActualGeneration"][i] / merged_df["ExpectedGeneration"][i]) * 100 if merged_df["ExpectedGeneration"][i] > 0 else 0
                color = color_map(np.clip(eff_diff / 100, 0, 1))  # Scale to 0 (green) to 1 (red)
                ax.bar(month, merged_df["ExpectedGeneration"][i], label="Expected", alpha=0.6, color=color)
                ax.bar(month, merged_df["ActualGeneration"][i], label="Actual", alpha=0.6, color="blue")

            ax.set_ylabel("Energy (kWh)")
            ax.set_title("Monthly Generation: Expected vs Actual")
            ax.legend()
            ax.grid(True)

            # Display total expected, actual, and efficiency
            st.markdown(f"**Total Expected:** {total_expected:.2f} kWh")
            st.markdown(f"**Total Actual:** {total_actual:.2f} kWh")
            st.markdown(f"**Overall Efficiency:** {overall_eff:.2f}%")

            # Generate report as downloadable text
            report = StringIO()
            report.write("Solar Plant Efficiency Report\n")
            report.write(f"Panel Power: {panel_power} W\n")
            report.write(f"Efficiency: {efficiency}%\n")
            report.write(f"Panels: {num_panels}\n\n")
            report.write("Month | Irradiance | Expected | Actual | Efficiency\n")
            report.write("----------------------------------------------\n")
            for _, row in merged_df.iterrows():
                report.write(
                    f"{row['Month']:5} | {row['Irradiance']:10.2f} | {row['ExpectedGeneration']:8.2f} | {row['ActualGeneration']:8.2f} | {((row['ActualGeneration'] / row['ExpectedGeneration']) * 100) if row['ExpectedGeneration'] > 0 else 0:10.2f}%\n"
                )
            report.write("\n")
            report.write(f"Total Expected: {total_expected:.2f} kWh\n")
            report.write(f"Total Actual: {total_actual:.2f} kWh\n")
            report.write(f"Overall Efficiency: {overall_eff:.2f}%\n")

            # Provide download link for the report
            b64 = base64.b64encode(report.getvalue().encode()).decode()
            href = f'<a href="data:file/txt;base64,{b64}" download="solar_efficiency_report.txt">📥 Download Report</a>'
            st.markdown(href, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("Upload both the irradiance and generation CSV files to begin analysis.")
