# Needed to check the file
import os
# Needed for command line paramnteres
import sys
# Needed for data manipulation
import pandas as pd
# Needed to get the current date
from datetime import datetime
# Needed to create the Excel file
def main():
    sales_csv = get_sales_csv()
    orders_dir = create_orders_dir(sales_csv)
    process_sales_data(sales_csv, orders_dir)
# Get path of sales data CSV file from the command line
def get_sales_csv():
    if len(sys.argv) != 2:
        print("Error: Please provide the path to the sales data CSV file.")
        sys.exit(1)
    # Check whether provide parameter is valid path of file
    sales_csv = sys.argv[1]
    if not os.path.isfile(sales_csv):
        print(f"Error: The file '{sales_csv}' does not exist.")
        sys.exit(1)
    
    return sales_csv
# Create the directory to hold the individual order Excel sheets
def create_orders_dir(sales_csv):
    sales_dir = os.path.dirname(sales_csv)
    date_str = datetime.now().strftime("%Y-%m-%d")
    orders_dir = os.path.join(sales_dir, f"Orders_{date_str}")
    
    if not os.path.exists(orders_dir):
        os.makedirs(orders_dir)
    
    return orders_dir
# Split the sales data into individual orders and save to Excel sheets
def process_sales_data(sales_csv, orders_dir):
    # Import the sales data from the CSV file into a DataFrame
    df = pd.read_csv(sales_csv)
    print(f"Sales data loaded. Columns: {df.columns.tolist()}")
    
    # Insert a new "TOTAL PRICE" column into the DataFrame
    df['TOTAL PRICE'] = df['ITEM QUANTITY'] * df['ITEM PRICE']
    print("Added 'TOTAL PRICE' column.")
    
    # Group the rows in the DataFrame by order ID
    order_groups = df.groupby('ORDER ID')
    # For each order ID:
    for order_id, order_df in order_groups:
        print(f"Processing ORDER ID: {order_id}")
        
        # Remove the "ORDER ID" column
        order_df = order_df.drop(columns=['ORDER ID'])
        
        # Sort the items by item number
        order_df = order_df.sort_values(by='ITEM NUMBER')
        
        # Append a "GRAND TOTAL" row
        grand_total = order_df['TOTAL PRICE'].sum()
        
        # Print columns for debugging
        print(f"Columns in order_df for ORDER ID {order_id}: {order_df.columns.tolist()}")
        
        # Adjust the grand_total_row to match the number of columns in order_df
        grand_total_row = pd.DataFrame([{col: '' for col in order_df.columns}])
        grand_total_row.iloc[0, order_df.columns.get_loc('ITEM NUMBER')] = 'GRAND TOTAL'
        grand_total_row.iloc[0, order_df.columns.get_loc('TOTAL PRICE')] = grand_total
        order_df = pd.concat([order_df, grand_total_row])
        
        # Determine the file name and full path of the Excel sheet
        order_file = os.path.join(orders_dir, f"Order_{order_id}.xlsx")
        
        # Export the data to an Excel sheet
        with pd.ExcelWriter(order_file, engine='xlsxwriter') as writer:
            order_df.to_excel(writer, index=False, sheet_name=f"Order {order_id}")
            workbook = writer.book
            worksheet = writer.sheets[f"Order {order_id}"]
            
            # Define formats
            money_format = workbook.add_format({'num_format': '$#,##0.00'})
            header_format = workbook.add_format({'bold': True, 'align': 'center'})
            
            # Set column widths and formats
            column_settings = [
                ('A:A', 11),  # ORDER DATE
                ('B:B', 13),  # ITEM NUMBER
                ('C:C', 15),  # PRODUCT LINE
                ('D:D', 15),  # PRODUCT CODE
                ('E:E', 15),  # ITEM QUANTITY
                ('F:F', 13),  # ITEM PRICE
                ('G:G', 13),  # TOTAL PRICE
                ('H:H', 10),  # STATUS
                ('I:I', 30),  # CUSTOMER NAME
            ]

            for col, width in column_settings:
                worksheet.set_column(col, width)

            # Apply money format to ITEM PRICE and TOTAL PRICE columns
            price_cols = ['F:F', 'G:G']
            for col in price_cols:
                worksheet.set_column(col, 13, money_format)
        
        print(f"Order {order_id} processed and saved to {order_file}")

if __name__ == '__main__':
    main()