import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os

def engineer_modeling_features(df):
    """
    Engineers time-series and historical features required for the predictive model.
    Since predictions happen at the time of booking, this function only creates 
    features that would be known *before* the shipment actually moves.
    
    Parameters
    ----------
    df : pandas.DataFrame
        The cleaned dataset containing historical shipment records.
        
    Returns
    -------
    df : pandas.DataFrame
        The dataframe with newly appended features: 'Pickup_Day_of_Week', 
        'Pickup_Month', 'Lane_Historical_Avg', and 'Postal_Rolling_7D_Delay_Rate'.
    """
    print("Engineering temporal and historical features...")
    
    # Ensure date column is datetime
    df['Ship_date'] = pd.to_datetime(df['Ship_date'])
    
    # Sort chronologically (Critical for rolling time-series calculations)
    df = df.sort_values(by='Ship_date').reset_index(drop=True)
    
    # 1. Temporal Features
    df['Pickup_Day_of_Week'] = df['Ship_date'].dt.dayofweek
    df['Pickup_Month'] = df['Ship_date'].dt.month
    df['Is_Weekend_Pickup'] = df['Pickup_Day_of_Week'].isin([5, 6]).astype(int)
    
    # Target variables for historical calculations
    actual_col = 'Calculated_Actual_Days' if 'Calculated_Actual_Days' in df.columns else 'Actual_Transit_Days'
    df['Is_Delayed'] = (df['Delivered_in_Commit'] == 0).astype(int)
    
    # 2. Historical Lane Average (What is the average time for this origin->dest historically?)
    # Using expanding().mean().shift(1) ensures we only look at past data, not the current row
    lane_group = df.groupby(['orig_cntry_cd', 'dest_cntry_cd'])
    df['Lane_Historical_Avg'] = lane_group[actual_col].transform(
        lambda x: x.expanding().mean().shift(1)
    )
    df['Lane_Historical_Avg'] = df['Lane_Historical_Avg'].fillna(df[actual_col].mean())
    
    # 3. Rolling 7-Day Delay Rate per Destination Postal Code
    # Measures active network congestion at the destination
    df_temp = df.set_index('Ship_date')
    df['Postal_Rolling_7D_Delay_Rate'] = df_temp.groupby('dest_pstl_cd')['Is_Delayed'].transform(
        lambda x: x.rolling('7D', closed='left').mean()
    ).values
    df['Postal_Rolling_7D_Delay_Rate'] = df['Postal_Rolling_7D_Delay_Rate'].fillna(0.0)
    
    return df

def perform_chronological_split(df, target_col, split_ratio=0.8):
    """
    Splits the dataset into training and testing sets based on time.
    Random sampling cannot be used in logistics ML, as training on December data 
    to predict October shipments causes "future data leakage."
    
    Parameters
    ----------
    df : pandas.DataFrame
        The feature-engineered dataset, sorted chronologically.
    target_col : str
        The name of the column we are trying to predict (e.g., 'Actual_Transit_Days').
    split_ratio : float, optional (default=0.8)
        The proportion of the dataset to include in the train split.
        
    Returns
    -------
    train_df, test_df : tuple of pandas.DataFrame
        The split dataframes ready for modeling.
    """
    print(f"Performing chronological split (Train: {split_ratio*100}%, Test: {(1-split_ratio)*100}%)...")
        
    # Label Encode Categorical String Columns so the ML model can read them
    categorical_cols = ['orig_cntry_cd', 'dest_cntry_cd', 'dest_pstl_cd']
    for col in categorical_cols:
        le = LabelEncoder()
        # Convert to string to handle mixed types safely
        df[col] = le.fit_transform(df[col].astype(str))
        
    # Chronological Split
    split_idx = int(len(df) * split_ratio)
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()
    
    return train_df, test_df


# --- Execution Block ---
if __name__ == "__main__":
    # Define file paths
    input_file = "Cleaned_IEF_Shipments_FY26.csv"
    input_path = os.path.join("..", "Data", "Processed", input_file)
    train_out_path = os.path.join("..", "Data", "Processed", "train_data.csv")
    test_out_path = os.path.join("..", "Data", "Processed", "test_data.csv")
    
    try:
        # 1. Load Cleaned Data
        print(f"Loading data from {input_path}...")
        df = pd.read_csv(input_path)
        actual_col = 'Calculated_Actual_Days' if 'Calculated_Actual_Days' in df.columns else 'Actual_Transit_Days'
        
        # 2. Feature Engineering
        df_featured = engineer_modeling_features(df)
        
        # 3. Chronological Split
        train_data, test_data = perform_chronological_split(df_featured, actual_col)
        
        # 4. Save splits for the modeling script
        train_data.to_csv(train_out_path, index=False)
        test_data.to_csv(test_out_path, index=False)
        print(f"\nSuccess! Training data saved to: {train_out_path}")
        print(f"Testing data saved to: {test_out_path}")
        
    except FileNotFoundError:
        print(f"[ERROR] Could not find {input_path}. Please check your directory structure.")