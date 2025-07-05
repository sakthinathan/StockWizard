import pandas as pd
import streamlit as st
from typing import Optional

class ExcelProcessor:
    """Handles Excel file processing and validation"""
    
    REQUIRED_COLUMNS = [
        'Material No',
        'Material Description', 
        'Stock in CBB',
        'Stock in PKT',
        'Alt UOM1 Num'
    ]
    
    def read_excel_file(self, uploaded_file) -> Optional[pd.DataFrame]:
        """
        Read and validate Excel file
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            DataFrame with processed data or None if error
        """
        try:
            # Read Excel file
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            
            # Basic validation
            if df.empty:
                st.error("The uploaded file is empty.")
                return None
            
            # Clean column names (remove extra spaces)
            df.columns = df.columns.str.strip()
            
            # Remove empty rows
            df = df.dropna(how='all')
            
            return df
            
        except Exception as e:
            st.error(f"Error reading Excel file: {str(e)}")
            return None
    
    def validate_columns(self, df: pd.DataFrame) -> bool:
        """
        Validate that all required columns are present
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if all required columns are present, False otherwise
        """
        missing_columns = []
        
        for col in self.REQUIRED_COLUMNS:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            return False
        
        # Validate data types and values
        return self._validate_data_types(df)
    
    def _validate_data_types(self, df: pd.DataFrame) -> bool:
        """
        Validate data types and ranges
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        try:
            # Check for non-negative numeric values
            numeric_columns = [
                'Stock in CBB',
                'Stock in PKT',
                'Alt UOM1 Num'
            ]
            
            for col in numeric_columns:
                # Convert to numeric, errors='coerce' will make invalid values NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Check for NaN values
                nan_count = df[col].isna().sum()
                if nan_count > 0:
                    st.error(f"Invalid numeric values found in column: {col}")
                    return False
                
                # Check for negative values
                negative_count = df[col].lt(0).sum()
                if negative_count > 0:
                    st.error(f"Negative values found in column: {col}")
                    return False
            
            # Check for zero pieces per box
            zero_pieces_count = (df['Alt UOM1 Num'] == 0).sum()
            if zero_pieces_count > 0:
                st.error("Alt UOM1 Num (Pieces per Box) cannot be zero")
                return False
            
            # Check for empty Material No - convert to numeric first to handle float values properly
            df_temp = df.copy()
            df_temp['Material No'] = pd.to_numeric(df_temp['Material No'], errors='coerce')
            empty_material_count = df_temp['Material No'].isna().sum()
            if empty_material_count > 0:
                st.warning(f"Found {empty_material_count} rows with empty/invalid Material No. These will be excluded from analysis.")
                # Don't return False here, let the clean_data function handle the removal
                
            empty_desc_count = df['Material Description'].isna().sum() + (df['Material Description'] == '').sum()
            if empty_desc_count > 0:
                st.warning(f"Found {empty_desc_count} rows with empty Material Description. These will be excluded from analysis.")
                # Don't return False here, let the clean_data function handle the removal
            
            return True
            
        except Exception as e:
            st.error(f"Data validation error: {str(e)}")
            return False
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare data for processing
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        # Convert Material No to string and remove any null/nan rows first
        # First convert to numeric to handle float values, then to int, then to string to remove .0
        df['Material No'] = pd.to_numeric(df['Material No'], errors='coerce')
        df = df.dropna(subset=['Material No'])  # Remove rows with null Material No
        df['Material No'] = df['Material No'].astype(int).astype(str)
        
        # Also remove rows with empty Material Description
        df = df.dropna(subset=['Material Description'])
        df = df[df['Material Description'].str.strip() != '']
        
        # Remove duplicate Material No (keep first occurrence)
        df = df.drop_duplicates(subset=['Material No'], keep='first')
        
        # Ensure integer values for pieces and boxes
        integer_columns = [
            'Stock in CBB',
            'Stock in PKT',
            'Alt UOM1 Num'
        ]
        
        for col in integer_columns:
            df[col] = df[col].astype(int)
        
        # Trim whitespace from Material No and descriptions
        df['Material No'] = df['Material No'].str.strip()
        df['Material Description'] = df['Material Description'].str.strip()
        
        return df
