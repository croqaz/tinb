
import sqlite3
import gdata.spreadsheet
import gdata.spreadsheet.service


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = str(row[idx])
    return d

def gdata_excel(conn, usr, pwd):

    spr_client = gdata.spreadsheet.service.SpreadsheetsService()
    print 'Starting Spreadsheet Service...'
    spr_client.email = usr
    spr_client.password = pwd
    spr_client.ProgrammaticLogin()
    print 'Login...'

    # File and sheet.
    spreadsheet_key = '0Ap41PJJ47IoCdHUzMk9VaUliTnJpLXZhX3ZkWlU0eGc'
    worksheet_id = 'od6'
    # Save feed.
    feed = spr_client.GetListFeed(key=spreadsheet_key, wksht_id=worksheet_id)
    # New SQLITE database connection.
    conn.row_factory = dict_factory
    c = conn.cursor()
    # Get all records.
    c.execute("SELECT id,name,descr,cat,lbl,date,price FROM object")

    i = 0
    for row in c.fetchall():
        # Try to update.
        try:
            entry = spr_client.UpdateRow(feed.entry[i], row)
        # If cannot update, try to insert.
        except:
            entry = spr_client.InsertRow(row, key=spreadsheet_key, wksht_id=worksheet_id)
        if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
            print 'Updated record id %s!' % row['id']
        else:
            print 'Insert record id %s failed!' % row['id']
        # Next row.
        i += 1

    c.close() ; del c
    del spr_client
