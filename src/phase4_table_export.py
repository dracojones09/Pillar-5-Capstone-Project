import pandas as pd
import matplotlib.pyplot as plt
import os


def create_stylized_table_image(csv_path, output_image_path, top_n=10):
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

    # 1. Filter and Prepare the Data
    # Safely check if Pickup_Day_Name exists (depending on how Phase 4 generated it)
    cols_to_keep = ['dest_pstl_cd']
    if 'Pickup_Day_Name' in df.columns:
        cols_to_keep.append('Pickup_Day_Name')
    cols_to_keep.append('Avg_Days_Added')

    # Grab the top N worst bottlenecks
    display_df = df[cols_to_keep].head(top_n).copy()

    # Rename columns for a clean presentation look
    rename_map = {
        'dest_pstl_cd': 'Postal Code',
        'Pickup_Day_Name': 'Day of Week',
        'Avg_Days_Added': 'Avg Days Added (+)'
    }
    display_df = display_df.rename(columns=rename_map)

    # Add a '+' sign to the days added for visual impact
    display_df['Avg Days Added (+)'] = display_df['Avg Days Added (+)'].apply(lambda x: f"+{x:.1f} Days")

    # 2. Setup the Matplotlib Table Figure
    print("Rendering stylized table image...")
    # Dynamic height based on the number of rows to keep aspect ratio clean
    fig, ax = plt.subplots(figsize=(8, 0.6 * (top_n + 1)))
    ax.axis('off')  # Hide the standard chart axes

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
    table.set_fontsize(12)

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

            # Make the 'Days Added' column bold and red for emphasis
            if col == len(display_df.columns) - 1:
                cell.set_text_props(weight='bold', color='#c0392b')

                # Title
    plt.title('Top 10 Postal Code Adjustments Recommended by AI',
              fontweight='bold', fontsize=16, pad=20, color='#2c3e50')

    # 4. Save the Image
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    plt.savefig(output_image_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Success! Stylized table exported to: {output_image_path}")

    # Display it in the notebook/console as well
    plt.show()


# --- Execution Block ---
if __name__ == "__main__":
    # Define paths based on your project structure
    input_csv = os.path.join("..", "Data", "Processed", "Phase4_Postal_Adjustments.csv")
    output_png = os.path.join("..", "Data", "Processed", "Phase4_Adjustments_Table.png")

    # Generate a table of the top 10 adjustments
    create_stylized_table_image(input_csv, output_png, top_n=10)