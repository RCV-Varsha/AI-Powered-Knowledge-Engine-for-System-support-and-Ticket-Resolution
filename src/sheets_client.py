# sheets_client.py
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dotenv import load_dotenv  

SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

load_dotenv()   
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE") or r"C:\Users\rgukt\OneDrive\Desktop\AI PROJECT_BATCH1\keys\service-account.json"

print(f"Service account file exists: {os.path.exists(SERVICE_ACCOUNT_FILE)}")
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# Use your spreadsheet ID
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID") or "1hLe_XDskjwP4IDD_iDpMUJ1ALgPsJUlBzc-Z8rvaPgo"

def get_worksheet():
    """Get the worksheet when needed"""
    try:
        spreadsheet = client.open_by_key(SPREADSHEET_ID)  # Use open_by_key for ID
        return spreadsheet.worksheet("AI support")
    except gspread.SpreadsheetNotFound:
        print(f"❌ Spreadsheet with ID '{SPREADSHEET_ID}' not found")
        print("Make sure you've shared it with: sheets-access@supportsystemapi.iam.gserviceaccount.com")
        raise
    except gspread.WorksheetNotFound:
        print(f"❌ Worksheet 'AI support' not found in the spreadsheet")
        raise
    except Exception as e:
        print(f"❌ Error accessing spreadsheet: {e}")
        raise

def create_tickets_worksheet():
    """Create the tickets worksheet with headers if it doesn't exist"""
    try:
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        
        # Try to get the worksheet first
        try:
            worksheet = spreadsheet.worksheet("AI support")
            print("✅ 'AI support' worksheet already exists")
            return worksheet
        except gspread.WorksheetNotFound:
            # Create the worksheet
            print("Creating 'AI support' worksheet...")
            worksheet = spreadsheet.add_worksheet(title="AI support", rows=1000, cols=10)
            # Add headers
            headers = ["ticket_id", "ticket_content", "ticket_cat", "ticket_timestamp", "ticket_by", "ticket_status", "solution"]
            worksheet.append_row(headers)
            print("✅ 'AI support' worksheet created with headers")
            return worksheet
            
    except Exception as e:
        print(f"❌ Error creating worksheet: {e}")
        raise

def now_ist_iso():
    """Return current timestamp in ISO format"""
    return datetime.now().isoformat()
def append_ticket(ticket_dict):
    """Append a ticket as a new row to the sheet"""
    try:
        worksheet = get_worksheet()  # Get worksheet when needed
        row = [
            ticket_dict.get("ticket_id"),
            ticket_dict.get("ticket_content"),
            ticket_dict.get("ticket_cat", ""),
            ticket_dict.get("ticket_timestamp", now_ist_iso()),
            ticket_dict.get("ticket_by", "email"),
            ticket_dict.get("ticket_status", "open"),
            ticket_dict.get("solution", "")
        ]
        worksheet.append_row(row)
        print("✅ Ticket appended:", row)
    except Exception as e:
        print("❌ Failed to append ticket:", e)


def find_ticket_row(ticket_id):
    """Find a row number for a given ticket_id"""
    worksheet = get_worksheet()  # Get worksheet when needed
    records = worksheet.get_all_records()
    for idx, row in enumerate(records, start=2):  # +2 (since header is row 1)
        if row["ticket_id"] == ticket_id:
            return idx
    return None

def update_ticket_fields(ticket_id, updates: dict):
    """Update specific fields for a given ticket_id"""
    worksheet = get_worksheet()  # Get worksheet when needed
    records = worksheet.get_all_records()
    headers = worksheet.row_values(1)  # get header row
    row_idx = find_ticket_row(ticket_id)

    if row_idx:
        for key, val in updates.items():
            if key in headers:
                col_idx = headers.index(key) + 1
                worksheet.update_cell(row_idx, col_idx, val)
        print(f"✅ Ticket {ticket_id} updated with {updates}")
    else:
        print(f"⚠️ Ticket {ticket_id} not found")

# Test the connection
if __name__ == "__main__":
    print("Testing Google Sheets connection...")
    
    # Test 1: List available spreadsheets
    def list_available_sheets():
        try:
            sheets = client.openall()
            print("Available spreadsheets:")
            for sheet in sheets:
                print(f"  - {sheet.title} (ID: {sheet.id})")
            return sheets
        except Exception as e:
            print(f"Error listing sheets: {e}")
            return []
    
    # Test 2: Try to connect to your specific sheet
    def test_connection():
        try:
            # First, create the worksheet if it doesn't exist
            worksheet = create_tickets_worksheet()
            
            # Then test the connection
            worksheet = get_worksheet()
            print("✅ Successfully connected to Google Sheet!")
            print(f"Sheet has {worksheet.row_count} rows")
            headers = worksheet.row_values(1)
            print(f"Headers: {headers}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    # Run tests
    print("\n1. Listing available spreadsheets...")
    available_sheets = list_available_sheets()
    
    print("\n2. Testing connection to your specific sheet...")
    if test_connection():
        print("✅ All tests passed!")
    else:
        print("❌ Connection test failed.")
        
        if not available_sheets:
            print("\n🔧 SOLUTION: Share your spreadsheet with:")
            print("   sheets-access@supportsystemapi.iam.gserviceaccount.com")
            print("   Give it 'Editor' permissions")