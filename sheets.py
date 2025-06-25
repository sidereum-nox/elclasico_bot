mport gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)


SHEET_NAME = "расписание EL CLASICO" 
sheet = client.open(SHEET_NAME).sheet1  

def get_all_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data)


if __name__ == "__main__":
    df = get_all_data()
    print(df.head())  