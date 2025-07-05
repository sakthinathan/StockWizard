# Biscuit Stock Management System

A Streamlit-based web application for managing biscuit inventory and calculating stock excess/shortage using the updated Material No template format.

## Features

- Excel file upload and processing with automatic data cleaning
- Stock excess/shortage calculation using Target - Current logic
- Interactive target quantity input forms
- Results export to Excel with detailed analysis
- User-friendly web interface with color-coded status indicators

## Required Excel Format

Your Excel file must contain these columns:
- **Material No**: Material number (automatically converts from float to integer format)
- **Material Description**: Name/description of the material
- **Stock in CBB**: Current inventory in boxes
- **Stock in PKT**: Current inventory in pieces
- **Alt UOM1 Num**: Number of pieces per box

## Data Handling
- Automatically removes rows with missing Material No or descriptions
- Converts Material No from float format (9000579.0) to clean integer format (9000579)
- Shows warnings for excluded rows but continues processing valid data
- Handles duplicate Material No entries (keeps first occurrence)

## Installation and Deployment

### Quick Git Deployment Guide

1. **Create a new repository on GitHub/GitLab**

2. **Clone this deployment package:**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```

3. **Copy all files from deployment_package to your repository:**
   - Copy all files from this deployment_package folder to your Git repository
   - Ensure the .streamlit/config.toml file is included

4. **Install dependencies and run locally:**
   ```bash
   pip install -r requirements.txt
   streamlit run app.py --server.port 5000
   ```

5. **Push to Git:**
   ```bash
   git add .
   git commit -m "Initial stock management system"
   git push origin main
   ```

### Deployment Options

#### Option 1: Streamlit Cloud (Recommended - Free)
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy with one click
5. Get a public URL for mobile access

#### Option 2: Replit (Mobile-Friendly)
1. Create new Repl and upload all files
2. Set run command: `streamlit run app.py --server.port 5000`
3. Install dependencies: `pip install streamlit pandas openpyxl`
4. Click Run to deploy instantly

#### Option 3: Railway/Render (Professional)
1. Connect your GitHub repository
2. These platforms auto-detect Streamlit apps
3. Uses the included requirements.txt for dependencies

## Usage Instructions

1. **Upload Excel File**: Click "Browse files" and select your inventory Excel file with Material No format
2. **Review Loaded Data**: Check the displayed materials and their current stock levels
3. **Set Target Quantities**: Enter desired stock levels (boxes and pieces) for each material
4. **Calculate Results**: Click "Calculate Stock Status" to see excess/shortage analysis
5. **Export Results**: Download the complete analysis as an Excel file

## Calculation Logic

**Formula: Target - Current**
- **Positive result = Shortage** (need more stock)
- **Negative result = Excess** (have too much stock)  
- **Zero = Balanced** (perfect stock level)

Example:
- Current: 100 pieces, Target: 150 pieces → +50 (Shortage of 50 pieces)
- Current: 200 pieces, Target: 100 pieces → -100 (Excess of 100 pieces)

## File Structure

```
├── app.py                    # Main Streamlit application
├── utils/
│   ├── excel_processor.py    # Excel file handling and validation
│   └── stock_calculator.py   # Stock calculations and analysis
├── .streamlit/
│   └── config.toml          # Streamlit server configuration
├── requirements.txt         # Python dependencies
├── sample_data.xlsx         # Example Excel format
└── README.md               # This documentation
```

## Technical Features

- **Smart Data Cleaning**: Automatically handles float-to-integer conversion for Material No
- **Flexible Validation**: Shows warnings for invalid data but continues processing
- **Session Management**: Maintains data across user interactions
- **Export Functionality**: Generates downloadable Excel reports
- **Mobile Responsive**: Works on phones and tablets through web deployment

## Troubleshooting

- **Excel Upload Issues**: Ensure your file contains the required columns with correct names
- **Calculation Errors**: Check that numeric fields contain valid numbers
- **Missing Data Warnings**: Review excluded rows and fix in source Excel file if needed

## Support

For deployment assistance or technical questions, refer to your hosting platform's documentation or ensure your Excel file follows the Material No template format.