import streamlit as st
import pandas as pd
import io
from utils.excel_processor import ExcelProcessor
from utils.stock_calculator import StockCalculator

# Page configuration
st.set_page_config(
    page_title="Biscuit Stock Management System",
    page_icon="🍪",
    layout="wide"
)

# Initialize session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'results' not in st.session_state:
    st.session_state.results = None

def main():
    st.title("🍪 Biscuit Stock Management System")
    st.markdown("Upload an Excel file with Material details and set target quantities for each product")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload an Excel file containing SKU stock data"
    )
    
    if uploaded_file is not None:
        try:
            # Process the uploaded file
            processor = ExcelProcessor()
            data = processor.read_excel_file(uploaded_file)
            
            if data is not None and not data.empty:
                st.success(f"File uploaded successfully! Found {len(data)} Materials.")
                
                # Display uploaded data
                st.subheader("📊 Uploaded Material Data")
                st.dataframe(data, use_container_width=True)
                
                # Validate required columns
                if processor.validate_columns(data):
                    # Clean the data
                    clean_data = processor.clean_data(data)
                    
                    # Show target quantity input form
                    st.subheader("🎯 Set Target Quantities")
                    st.markdown("Enter the target quantities for each SKU:")
                    
                    # Create input form for target quantities
                    target_data = create_target_input_form(clean_data)
                    
                    if target_data is not None:
                        # Calculate stock differences
                        calculator = StockCalculator()
                        results = calculator.calculate_stock_status(target_data)
                        
                        st.session_state.processed_data = target_data
                        st.session_state.results = results
                        
                        # Display results
                        display_results(results)
                    
                else:
                    st.error("❌ Invalid file format. Please ensure your Excel file has the required columns.")
                    display_required_format()
            else:
                st.error("❌ The uploaded file appears to be empty or corrupted.")
                
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            display_required_format()
    
    else:
        display_required_format()

def create_target_input_form(data):
    """Create input form for target quantities"""
    st.markdown("---")
    
    # Store target inputs in session state
    if 'target_inputs' not in st.session_state:
        st.session_state.target_inputs = {}
    
    # Create columns for better layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("**Enter target quantities for each Material:**")
    
    with col2:
        if st.button("Calculate Stock Analysis", type="primary"):
            # Validate that all targets are set
            missing_targets = []
            for _, row in data.iterrows():
                material_no = str(row['Material No'])
                if material_no not in st.session_state.target_inputs or not st.session_state.target_inputs[material_no]:
                    missing_targets.append(material_no)
            
            if missing_targets:
                st.error(f"Please set target quantities for Materials: {', '.join(missing_targets)}")
                return None
            
            # Create target data
            target_data = data.copy()
            target_boxes = []
            target_pieces = []
            
            for _, row in data.iterrows():
                material_no = str(row['Material No'])
                targets = st.session_state.target_inputs[material_no]
                target_boxes.append(targets['boxes'])
                target_pieces.append(targets['pieces'])
            
            target_data['Target Stock (Boxes)'] = target_boxes
            target_data['Target Stock (Pieces)'] = target_pieces
            
            return target_data
    
    # Display input form for each Material
    st.markdown("---")
    
    for idx, row in data.iterrows():
        material_no = str(row['Material No'])
        material_desc = row['Material Description']
        current_boxes = row['Stock in CBB']
        current_pieces = row['Stock in PKT']
        pieces_per_box = row['Alt UOM1 Num']
        
        # Create expandable section for each Material
        with st.expander(f"Material: {material_no} - {material_desc}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Current Stock:**")
                st.write(f"CBB: {current_boxes}")
                st.write(f"PKT: {current_pieces}")
                st.write(f"Pieces per Box: {pieces_per_box}")
            
            with col2:
                st.markdown("**Target Quantities:**")
                target_boxes = st.number_input(
                    "Target Boxes",
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"target_boxes_{material_no}_{idx}"
                )
                
                target_pieces = st.number_input(
                    "Target Pieces",
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"target_pieces_{material_no}_{idx}"
                )
            
            with col3:
                # Calculate preview
                total_current = current_boxes * pieces_per_box + current_pieces
                total_target = target_boxes * pieces_per_box + target_pieces
                difference = total_target - total_current  # Target - Current
                
                st.markdown("**Preview:**")
                st.write(f"Total Current: {total_current} pieces")
                st.write(f"Total Target: {total_target} pieces")
                
                if difference > 0:
                    st.error(f"Shortage: {difference} pieces")
                elif difference < 0:
                    st.success(f"Excess: {abs(difference)} pieces")
                else:
                    st.info("Balanced")
            
            # Store the inputs
            st.session_state.target_inputs[material_no] = {
                'boxes': target_boxes,
                'pieces': target_pieces
            }
    
    return None

def display_results(results):
    """Display the calculated stock results"""
    if results is None or results.empty:
        st.warning("No results to display.")
        return
    
    st.subheader("📈 Stock Analysis Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_products = len(results)
        st.metric("Total Products", total_products)
    
    with col2:
        excess_count = len(results[results['Status'] == 'Excess'])
        st.metric("Products with Excess", excess_count)
    
    with col3:
        shortage_count = len(results[results['Status'] == 'Shortage'])
        st.metric("Products with Shortage", shortage_count)
    
    with col4:
        balanced_count = len(results[results['Status'] == 'Balanced'])
        st.metric("Balanced Products", balanced_count)
    
    # Detailed results table
    st.subheader("📋 Detailed Results")
    
    # Color coding for status
    def highlight_status(val):
        if val == 'Excess':
            return 'background-color: #d4edda; color: #155724'
        elif val == 'Shortage':
            return 'background-color: #f8d7da; color: #721c24'
        else:
            return 'background-color: #d1ecf1; color: #0c5460'
    
    styled_results = results.style.map(highlight_status, subset=['Status'])
    st.dataframe(styled_results, use_container_width=True)
    
    # Filter options
    st.subheader("🔍 Filter Results")
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            options=['All', 'Excess', 'Shortage', 'Balanced'],
            index=0
        )
    
    with col2:
        if status_filter != 'All':
            filtered_results = results[results['Status'] == status_filter]
            st.dataframe(filtered_results, use_container_width=True)
    
    # Export functionality
    if st.button("📥 Export Results to Excel"):
        export_to_excel(results)

def export_to_excel(results):
    """Export results to Excel file"""
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            results.to_excel(writer, sheet_name='Stock Analysis', index=False)
            
            # Add summary sheet
            summary_data = {
                'Metric': ['Total Products', 'Products with Excess', 'Products with Shortage', 'Balanced Products'],
                'Count': [
                    len(results),
                    len(results[results['Status'] == 'Excess']),
                    len(results[results['Status'] == 'Shortage']),
                    len(results[results['Status'] == 'Balanced'])
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        output.seek(0)
        
        st.download_button(
            label="📥 Download Excel Report",
            data=output.getvalue(),
            file_name="stock_analysis_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.success("✅ Excel report generated successfully!")
        
    except Exception as e:
        st.error(f"❌ Error generating Excel report: {str(e)}")

def display_required_format():
    """Display the required Excel file format"""
    st.subheader("📋 Required Excel File Format")
    st.markdown("""
    Your Excel file should contain the following columns:
    
    | Column Name | Description | Example |
    |------------|-------------|---------|
    | Material No | Material Number/Code | "9000579" |
    | Material Description | Name of the product | "MARIE BISCUIT 75GM" |
    | Stock in CBB | Current number of boxes in stock | 50 |
    | Stock in PKT | Current number of pieces in stock | 120 |
    | Alt UOM1 Num | Number of pieces in one box | 24 |
    """)
    
    st.info("💡 After uploading the file, you'll be able to set target quantities for each Material individually.")
    
    # Sample data for demonstration
    sample_data = {
        'Material No': ['9000579', '9000741', '9001048'],
        'Material Description': ['MARIE BISCUIT 75GM', 'GLUCOSE BISCUIT 100GM', 'CREAM CRACKERS 200GM'],
        'Stock in CBB': [50, 30, 25],
        'Stock in PKT': [120, 80, 60],
        'Alt UOM1 Num': [24, 20, 16]
    }
    
    sample_df = pd.DataFrame(sample_data)
    st.subheader("📊 Sample Data Format")
    st.dataframe(sample_df, use_container_width=True)

if __name__ == "__main__":
    main()
