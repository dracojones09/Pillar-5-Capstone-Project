import pandas as pd
import matplotlib.pyplot as plt
import os
from sklearn.preprocessing import LabelEncoder


def render_stylized_table(df, title, output_path):
    """Generates a high-resolution PNG image of a pandas DataFrame."""
    print(f"Rendering: {title}...")

    # Dynamic sizing based on rows
    fig, ax = plt.subplots(figsize=(10, 0.7 * (len(df) + 1.5)))
    ax.axis('off')

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(8)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            # Header styling
            cell.set_text_props(weight='bold', color='white', fontsize=9)
            cell.set_facecolor('#2c3e50')  # Dark slate
        else:
            # Alternating row colors
            cell.set_facecolor('#f8f9fa' if row % 2 == 0 else '#ffffff')

            # Highlight Net Improvement in Green
            if df.columns[col] == 'Net Improvement':
                cell.set_text_props(weight='bold', color='#27ae60')
            # Highlight Avg Buffer in a muted Red/Orange
            elif df.columns[col] == 'Avg Buffer Added':
                cell.set_text_props(weight='bold', color='#c0392b')

    plt.title(title, fontweight='bold', fontsize=15, pad=20, color='#2c3e50')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f" -> Saved to {output_path}")


def generate_fairness_reports(sim_csv_path, original_csv_path, output_dir):
    """Reads the simulation data, computes fairness, and exports tables."""
    try:
        df = pd.read_csv(sim_csv_path)
    except FileNotFoundError:
        print(f"[ERROR] Could not find {sim_csv_path}. Run Phase 4 simulation first.")
        return

    # Decode Origin Country Codes back to their abbreviations if they are numeric
    if 'orig_cntry_cd' in df.columns and pd.api.types.is_numeric_dtype(df['orig_cntry_cd']):
        if os.path.exists(original_csv_path):
            print("Decoding Origin Country numeric codes to actual abbreviations...")
            orig_df = pd.read_csv(original_csv_path)
            le = LabelEncoder()
            le.fit(orig_df['orig_cntry_cd'].astype(str))
            df['orig_cntry_cd'] = le.inverse_transform(df['orig_cntry_cd'].astype(int))
        else:
            print(f"[WARNING] Original data not found at {original_csv_path}. Cannot decode country codes.")

    actual_col = 'Calculated_Actual_Days' if 'Calculated_Actual_Days' in df.columns else 'Actual_Transit_Days'

    # Auto-detect the best model by finding the highest NSL
    best_model = None
    highest_nsl = -1
    for model in ['LGBM', 'IsolationForest', 'Survival']:
        if f'{model}_Delivered_in_Commit' in df.columns:
            nsl = df[f'{model}_Delivered_in_Commit'].mean()
            if nsl > highest_nsl:
                highest_nsl = nsl
                best_model = model

    if not best_model:
        print("[ERROR] Could not detect any AI model predictions in the dataset.")
        return

    quoted_col = f'{best_model}_Quoted_Transit_Days'

    # ---------------------------------------------------------
    # 1. Volume-Based Fairness
    # ---------------------------------------------------------
    volume_df = df.groupby('dest_pstl_cd').size().reset_index(name='Total_Volume')

    def categorize_volume(v):
        if v <= 10:
            return 'Low Volume (<= 10)'
        elif v <= 100:
            return 'Medium Volume (11-100)'
        else:
            return 'High Volume (> 100)'

    volume_df['Volume_Tier'] = volume_df['Total_Volume'].apply(categorize_volume)
    fairness_df = df.merge(volume_df[['dest_pstl_cd', 'Volume_Tier']], on='dest_pstl_cd', how='left')

    tier_metrics = []
    for tier in ['Low Volume (<= 10)', 'Medium Volume (11-100)', 'High Volume (> 100)']:
        tier_data = fairness_df[fairness_df['Volume_Tier'] == tier]
        if len(tier_data) == 0: continue

        hist_nsl = (tier_data[actual_col] <= tier_data['Quoted_Transit_Days']).mean() * 100
        ai_nsl = (tier_data[actual_col] <= tier_data[quoted_col]).mean() * 100
        improvement = ai_nsl - hist_nsl
        avg_days_added = (tier_data[quoted_col] - tier_data['Quoted_Transit_Days']).mean()

        tier_metrics.append([
            tier, f"{hist_nsl:.2f}%", f"{ai_nsl:.2f}%",
            f"+{improvement:.2f}%", f"+{avg_days_added:.2f} Days"
        ])

    tier_df = pd.DataFrame(tier_metrics,
                           columns=['Volume Tier', 'Historical NSL', 'AI NSL', 'Net Improvement', 'Avg Buffer Added'])
    render_stylized_table(tier_df, f"Bias Analysis: Fairness by Postal Volume ({best_model})",
                          os.path.join(output_dir, "Fairness_Volume_Table.png"))

    # ---------------------------------------------------------
    # 2. Geographic Fairness (Origin Country)
    # ---------------------------------------------------------
    if 'orig_cntry_cd' in df.columns:
        top_countries = df['orig_cntry_cd'].value_counts().head(5).index
        geo_metrics = []
        for country in top_countries:
            geo_data = df[df['orig_cntry_cd'] == country]
            hist_nsl = (geo_data[actual_col] <= geo_data['Quoted_Transit_Days']).mean() * 100
            ai_nsl = (geo_data[actual_col] <= geo_data[quoted_col]).mean() * 100
            improvement = ai_nsl - hist_nsl
            avg_days_added = (geo_data[quoted_col] - geo_data['Quoted_Transit_Days']).mean()

            geo_metrics.append([
                country, f"{hist_nsl:.2f}%", f"{ai_nsl:.2f}%",
                f"+{improvement:.2f}%", f"+{avg_days_added:.2f} Days"
            ])

        geo_df = pd.DataFrame(geo_metrics, columns=['Origin Country', 'Historical NSL', 'AI NSL', 'Net Improvement',
                                                    'Avg Buffer Added'])
        render_stylized_table(geo_df, f"Bias Analysis: Fairness by Origin Geography ({best_model})",
                              os.path.join(output_dir, "Fairness_Origin_Table.png"))


# --- Execution Block ---
if __name__ == "__main__":
    sim_csv = os.path.join("..", "Data", "Processed", "Phase4_Final_Simulation.csv")
    orig_csv = os.path.join("..", "Data", "Processed", "Cleaned_IEF_Shipments_FY26.csv")
    out_dir = os.path.join("..", "Data", "Processed")

    generate_fairness_reports(sim_csv, orig_csv, out_dir)