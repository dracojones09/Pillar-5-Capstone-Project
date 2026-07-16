import pandas as pd
import matplotlib.pyplot as plt
import os


def create_top10_table_image(csv_path, output_image_path, top_n=10):
    """
    Reads the Phase 4 Postal Adjustments CSV and generates a stylized,
    presentation-ready PNG table image of the top bottlenecks.
    """
    print(f"Loading adjustment data from {csv_path}...")

    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"[ERROR] Could not find {csv_path}. Please run Phase 4 first.")
        return

    # Take the top N rows (already sorted in Phase 4 by worst bottlenecks)
    display_df = df.head(top_n).copy()

    # Rename columns for a clean presentation look
    rename_map = {
        'dest_pstl_cd': 'Dest. Postal Code',
        'Pickup_Day_Name': 'Pickup Day',
        'Total_Shipments': 'Total Shipments',
        'Historical_Avg_Quote': 'Historical Quote',
        'AI_Avg_Quote': 'AI Quote',
        'Avg_Days_Added': 'Avg Days Added'
    }

    # Only rename columns that actually exist in the dataframe
    columns_to_rename = {k: v for k, v in rename_map.items() if k in display_df.columns}
    display_df = display_df.rename(columns=columns_to_rename)

    # Add a '+' sign to the days added for visual impact
    if 'Avg Days Added (+)' in display_df.columns:
        display_df['Avg Days Added (+)'] = display_df['Avg Days Added (+)'].apply(lambda x: f"+{x:.1f} Days")

    # Setup the Matplotlib Table Figure
    print("Rendering stylized table image...")

    # Dynamic width and height based on the data to keep the aspect ratio clean
    fig, ax = plt.subplots(figsize=(10, 0.6 * (top_n + 1.5)))
    ax.axis('off')  # Hide the standard chart axes

    # Create the table
    table = ax.table(
        cellText=display_df.values,
        colLabels=display_df.columns,
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1]
    )

    # Apply Styling (Colors, Fonts, Borders)
    table.auto_set_font_size(False)
    table.set_fontsize(8)

    for (row, col), cell in table.get_celld().items():
        # Header Row Styling
        if row == 0:
            cell.set_text_props(weight='bold', color='white', fontsize=9)
            cell.set_facecolor('#2c3e50')  # Sleek dark blue/grey
        # Data Rows Styling
        else:
            # Alternating row colors for readability
            if row % 2 == 0:
                cell.set_facecolor('#f8f9fa')  # Very light grey
            else:
                cell.set_facecolor('#ffffff')  # White

            # Make the 'Days Added' column bold and red for emphasis
            if display_df.columns[col] == 'Avg Days Added (+)':
                cell.set_text_props(weight='bold', color='#c0392b')

                # Title
    plt.title(f'Top {top_n} Postal Codes Requiring Transit Time Increases',
              fontweight='bold', fontsize=16, pad=20, color='#2c3e50')

    # Save the Image
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    plt.savefig(output_image_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Success! Stylized table exported to: {output_image_path}")


# --- Execution Block ---
if __name__ == "__main__":
    # Define paths based on your project structure
    input_csv = os.path.join("..", "Data", "Processed", "Phase4_Postal_Adjustments.csv")
    output_png = os.path.join("..", "Data", "Processed", "Phase4_Top10_Adjustments_Table.png")

    # Generate a table of the top 10 adjustments
    create_top10_table_image(input_csv, output_png, top_n=10)