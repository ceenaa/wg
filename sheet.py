from __future__ import print_function
from googleapiclient.discovery import build

from google.oauth2 import service_account

import analysis


def main():
    SERVICE_ACCOUNT_FILE = 'keys.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = None
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # The ID spreadsheet.
    SAMPLE_SPREADSHEET_ID = '1JMfbph5fxaqu1MrQFIMn6Ju5ZiFbCJsxqpnE82FTeQo'

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    peers = analysis.sortedPeer

    body = {
        'values': peers
    }

    result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet3!A2", body=body,
                                   valueInputOption="USER_ENTERED").execute()
