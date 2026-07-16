import pandas as pd
import matplotlib.pyplot as plt
import os


def create_forecast_table_image(sim_csv_path, adj_csv_path, output_image_path, top_n=5, buffer_options=[1, 2]):
    """
    Reads the Phase 4 simulation data, calculates the manual buffer forecasting,
    and generates a stylized PNG table image of the results.
    """
    print("Loading simulation data...")

    try:
        df = pd.read_csv(sim_csv_path)
        postal_summary = pd.read_csv(adj_csv_path)
    except FileNotFoundError:
        print("[ERROR] Could not find required CSVs. Please run Phase 4 first.")
        return

    # 1. Calculate Forecast Scenarios
    # Identify the correct column for actual days
    actual_col = 'Calculated_Actual_Days' if 'Calculated_Actual_Days' in df.columns else 'Actual_Transit_Days'

    # Grab the worst postal codes
    worst_postals = postal_summary['dest_pstl_cd'].unique()[:top_n]

    # Baseline NSL
    historical_nsl = (df[actual_col] <= df['Quoted_Transit_Days']).mean() * 100

    # Prepare data rows for the table
    results = []
    results.append(['Baseline (Static Matrix)', f"{historical_nsl:.2f}%", "Baseline"])

    for buffer in buffer_options:
        hypothetical_quotes = df['Quoted_Transit_Days'].copy()
        mask = df['dest_pstl_cd'].isin(worst_postals)
        hypothetical_quotes.loc[mask] += buffer

        hypothetical_nsl = (df[actual_col] <= hypothetical_quotes).mean() * 100
        improvement = hypothetical_nsl - historical_nsl

        results.append([
            f"+{buffer} Day(s) to Top {top_n} Postals",
            f"{hypothetical_nsl:.2f}%",
            f"+{improvement:.2f}%"
        ])

    display_df = pd.DataFrame(results, columns=['Strategy / Scenario', 'Simulated NSL %', 'Net Improvement'])

    # 2. Setup the Matplotlib Table Figure
    print("Rendering stylized forecasting table image...")
    # Keep the figure relatively compact
    fig, ax = plt.subplots(figsize=(8, 2.5))
    ax.axis('off')  # Hide axes

    # Create the table
    table = ax.table(
        cellText=display_df.values,
        colLabels=display_df.columns,
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1]
    )

    # 3. Apply Styling (Colors, Fonts, Borders)
    table.auto_set_font_size(False)
    table.set_fontsize(11)

    for (row, col), cell in table.get_celld().items():
        # Header Row Styling
        if row == 0:
            cell.set_text_props(weight='bold', color='white', fontsize=13)
            cell.set_facecolor('#2c3e50')  # Sleek dark blue/grey
        # Data Rows Styling
        else:
            # Alternating row colors for readability
            if row % 2 == 0:
                cell.set_facecolor('#f8f9fa')  # Very light grey
            else:
                cell.set_facecolor('#ffffff')  # White

            # Make the 'Net Improvement' column bold and green for emphasis (if not baseline)
            if col == 2 and row > 0:
                cell.set_text_props(weight='bold', color='#27ae60')

                # Title
    plt.title('Forecasting NSL Impact: Manual Buffer Strategies',
              fontweight='bold', fontsize=16, pad=20, color='#2c3e50')

    # 4. Save the Image
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    plt.savefig(output_image_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Success! Stylized forecast table exported to: {output_image_path}")

    # Display it in the notebook/console as well
    plt.show()


# --- Execution Block ---
if __name__ == "__main__":
    # Define paths based on your project structure
    sim_csv = os.path.join("..", "Data", "Processed", "Phase4_Final_Simulation.csv")
    adj_csv = os.path.join("..", "Data", "Processed", "Phase4_Postal_Adjustments.csv")
    output_png = os.path.join("..", "Data", "Processed", "Phase4_Forecast_Table.png")

    # Generate the forecasting table
    create_forecast_table_image(sim_csv, adj_csv, output_png)