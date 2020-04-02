import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_creds():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Obtain from https://developers.google.com/sheets/api/quickstart/python
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return creds


class SheetReader:
    def __init__(self, content_id, sheet_name="Sheet1"):
        self.service = build("sheets", "v4", credentials=get_creds())
        self.content_id = content_id
        sheet = self.service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=self.content_id, range="{}!A:Z".format(sheet_name),)
            .execute()
        )
        values = result.get("values", [])
        if not values:
            raise ValueError("No data found.")

        self.rows = values[1:]
        self.col_label = list(map(lambda s: s.lower(), values[0]))
        self.i = 0

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            row = self.rows[self.i]
        except IndexError:
            raise StopIteration()
        self.i += 1
        return {self.col_label[c]: v for c, v in enumerate(row)}
