import pandas as pd
import numpy as np
from typing import Dict, Any

class StockCalculator:
    """Handles stock calculations and analysis"""
    
    def calculate_stock_status(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate stock excess/shortage for each product
        
        Args:
            df: DataFrame with stock data
            
        Returns:
            DataFrame with calculated results
        """
        results = df.copy()
        
        # Ensure all numeric columns are properly converted
        results['Stock in CBB'] = pd.to_numeric(results['Stock in CBB'], errors='coerce')
        results['Stock in PKT'] = pd.to_numeric(results['Stock in PKT'], errors='coerce')
        results['Target Stock (Boxes)'] = pd.to_numeric(results['Target Stock (Boxes)'], errors='coerce')
        results['Target Stock (Pieces)'] = pd.to_numeric(results['Target Stock (Pieces)'], errors='coerce')
        results['Alt UOM1 Num'] = pd.to_numeric(results['Alt UOM1 Num'], errors='coerce')
        
        # Calculate total current stock in pieces
        results['Total Current Pieces'] = (
            results['Stock in CBB'] * results['Alt UOM1 Num'] + 
            results['Stock in PKT']
        )
        
        # Calculate total target stock in pieces
        results['Total Target Pieces'] = (
            results['Target Stock (Boxes)'] * results['Alt UOM1 Num'] + 
            results['Target Stock (Pieces)']
        )
        
        # Calculate difference in pieces (Target - Current)
        # Target = What you need, Current = What you have
        # Positive = Shortage (need more), Negative = Excess (have more than needed)
        results['Difference (Pieces)'] = (
            results['Total Target Pieces'] - results['Total Current Pieces']
        )
        

        
        # Convert difference to boxes and remaining pieces
        results['Difference (Boxes)'] = results['Difference (Pieces)'] // results['Pieces per Box']
        results['Difference (Remaining Pieces)'] = results['Difference (Pieces)'] % results['Pieces per Box']
        
        # Determine status
        results['Status'] = results['Difference (Pieces)'].apply(self._determine_status)
        
        # Create formatted difference strings
        results['Excess/Shortage (Boxes)'] = results.apply(self._format_box_difference, axis=1)
        results['Excess/Shortage (Pieces)'] = results.apply(self._format_piece_difference, axis=1)
        
        # Calculate percentage difference
        results['Percentage Difference'] = (
            (results['Difference (Pieces)'] / results['Total Target Pieces']) * 100
        ).round(2)
        
        # Select and reorder columns for final output
        output_columns = [
            'SKU',
            'Product Name',
            'Current Stock (Boxes)',
            'Current Stock (Pieces)',
            'Target Stock (Boxes)',
            'Target Stock (Pieces)',
            'Total Current Pieces',
            'Total Target Pieces',
            'Status',
            'Excess/Shortage (Boxes)',
            'Excess/Shortage (Pieces)',
            'Percentage Difference'
        ]
        
        return results[output_columns]
    
    def _determine_status(self, difference: int) -> str:
        """
        Determine stock status based on difference
        
        Args:
            difference: Difference in pieces (Target - Current)
            
        Returns:
            Status string
        """
        if difference > 0:
            return 'Shortage'  # Need more stock
        elif difference < 0:
            return 'Excess'    # Have more than needed
        else:
            return 'Balanced'
    
    def _format_box_difference(self, row: pd.Series) -> str:
        """
        Format box difference for display
        
        Args:
            row: Row data
            
        Returns:
            Formatted string
        """
        boxes = abs(row['Difference (Boxes)'])
        status = row['Status']
        
        if status == 'Balanced':
            return '0 boxes'
        elif status == 'Shortage':
            return f'+{boxes} boxes needed'
        else:  # Excess
            return f'-{boxes} boxes extra'
    
    def _format_piece_difference(self, row: pd.Series) -> str:
        """
        Format piece difference for display
        
        Args:
            row: Row data
            
        Returns:
            Formatted string
        """
        pieces = abs(row['Difference (Remaining Pieces)'])
        status = row['Status']
        
        if status == 'Balanced':
            return '0 pieces'
        elif status == 'Shortage':
            return f'+{pieces} pieces needed'
        else:  # Excess
            return f'-{pieces} pieces extra'
    
    def get_summary_statistics(self, results: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate summary statistics
        
        Args:
            results: Results DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        total_products = len(results)
        excess_products = len(results[results['Status'] == 'Shortage'])
        shortage_products = len(results[results['Status'] == 'Excess'])
        balanced_products = len(results[results['Status'] == 'Balanced'])
        
        # Calculate total excess and shortage in pieces
        total_excess_pieces = results[results['Status'] == 'Excess']['Difference (Pieces)'].sum()
        total_shortage_pieces = abs(results[results['Status'] == 'Shortage']['Difference (Pieces)'].sum())
        
        return {
            'total_products': total_products,
            'excess_products': excess_products,
            'shortage_products': shortage_products,
            'balanced_products': balanced_products,
            'excess_percentage': round((excess_products / total_products) * 100, 2) if total_products > 0 else 0,
            'shortage_percentage': round((shortage_products / total_products) * 100, 2) if total_products > 0 else 0,
            'total_excess_pieces': total_excess_pieces,
            'total_shortage_pieces': total_shortage_pieces
        }
    
    def get_top_excess_products(self, results: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
        """
        Get top products with highest excess
        
        Args:
            results: Results DataFrame
            top_n: Number of top products to return
            
        Returns:
            DataFrame with top excess products
        """
        excess_products = results[results['Status'] == 'Excess'].copy()
        if len(excess_products) == 0:
            return pd.DataFrame()
        return excess_products.nlargest(top_n, 'Difference (Pieces)')
    
    def get_top_shortage_products(self, results: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
        """
        Get top products with highest shortage
        
        Args:
            results: Results DataFrame
            top_n: Number of top products to return
            
        Returns:
            DataFrame with top shortage products
        """
        shortage_products = results[results['Status'] == 'Shortage'].copy()
        if len(shortage_products) == 0:
            return pd.DataFrame()
        return shortage_products.nsmallest(top_n, 'Difference (Pieces)')
