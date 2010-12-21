
import os
import sqlite3

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A5
from reportlab.lib.colors import Color, HexColor, black, white

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('Lucida Calligraphy', 'LCALLIG.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu Sans', 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu Serif Condensed', 'DejaVuSerifCondensed.ttf'))

FILENAME = "Catalog_Jewelry_from_the_Heart.pdf"
W, H = A5[1], A5[0]

# Mellon template.
TEMPLATE_MELLON = {
    'MAIN_BG' :     '#FFC48C',
    'RECT_COLOR1' : '#F56991',
    'RECT_COLOR2' : '#F56991',
    'TITLE_COLOR' : '#000000',
    'TEXT_COLOR1' : '#000000',
    'TEXT_COLOR2' : '#000000',
    }

# Use template.
TMPL = TEMPLATE_MELLON
G_BORDER =     2
MAIN_BG =      TMPL['MAIN_BG']
RECT_COLOR1 =  TMPL['RECT_COLOR1']
RECT_COLOR2 =  TMPL['RECT_COLOR2']
TITLE_COLOR =  TMPL['TITLE_COLOR']
TITLE_SIZE =   22
TEXT_COLOR1 =  TMPL['TEXT_COLOR1']
TEXT_COLOR2 =  TMPL['TEXT_COLOR2']
TEXT_SIZE1 =   16
TEXT_SIZE2 =   14


def Generate_Catalog(rows):

    # Setup PDF Canvas.
    c = canvas.Canvas(FILENAME, pagesize=(W, H))
    c.setAuthor('Jewelry from the Heart')
    c.setTitle('Catalog')
    c.setSubject('Catalog Jewelry from the Heart')
    c.setCreator('Trinkets-in-a-Bottle')
    c.setKeywords('jewelry, catalog, Jewelry from the Heart')
    c.setFont('Lucida Calligraphy', TITLE_SIZE)

    # ----- First Page -----
    # Main background.
    c.setFillColor(MAIN_BG)
    c.rect(G_BORDER*5, G_BORDER*5, W-G_BORDER*10, H-G_BORDER*10, fill=True, stroke=False)
    # Image container.
    c.setStrokeColor(white)
    c.setFillColor(RECT_COLOR1)
    c.roundRect(1.0/20.0*W-G_BORDER*5, 1.0/14.0*H, W-G_BORDER*20, 15.5/20.0*H+G_BORDER*5, radius=5, fill=True, stroke=1)
    # Draw title.
    c.setFillColor(TITLE_COLOR)
    c.drawCentredString(1.0/2.0*W, 1.0/2.0*H, 'Catalog')
    c.drawCentredString(1.0/2.0*W, 4.0/10.0*H, 'Jewelry from the Heart')
    # End page.
    c.showPage()

    # ----- Loop with products -----
    for row in rows:
        # Save page number.
        p = c.getPageNumber() - 1

        # Main background.
        c.setFillColor(MAIN_BG)
        c.rect(G_BORDER*5, G_BORDER*5, W-G_BORDER*10, H-G_BORDER*10, fill=True, stroke=False)

        # Image container.
        c.setStrokeColor(white)
        c.setFillColor(RECT_COLOR1)
        c.roundRect(1.0/20.0*W-G_BORDER*5, 1.0/14.0*H, W/2.0-G_BORDER*15, 15.5/20.0*H+G_BORDER*5, radius=5, fill=True, stroke=1)
        # Text container.
        c.setFillColor(RECT_COLOR2)
        c.roundRect(10.7/20.0*W-G_BORDER*5, 1.0/14.0*H, W/2.0-G_BORDER*15, 15.5/20.0*H+G_BORDER*5, radius=5, fill=True, stroke=1)

        # Draw title.
        c.setFillColor(TITLE_COLOR)
        c.setFont("DejaVu Serif Condensed", TITLE_SIZE)
        c.drawCentredString(1.0/2.0*W, 9.0/10.0*H, row[1])
        # Draw page number.
        c.setFont("DejaVu Sans", 12)
        c.drawCentredString(1.0/2.0*W, inch/4.0, 'pag %i' % p)

        # Draw titles.
        xpos = 10.5/20.0*W
        ypos = 12.0/14.0*H
        c.setFillColor(TEXT_COLOR1)
        c.setFont("DejaVu Sans", TEXT_SIZE1)
        c.drawString(xpos, ypos-1.0/2.0*inch, 'Cod produs:')
        c.drawString(xpos, ypos-1.0*inch, 'Tip produs:')
        c.drawString(xpos, ypos-3.0/2.0*inch, 'Data produs:')
        c.drawString(xpos, ypos-2.0*inch, 'Pret:')

        # Price is big.
        xpos = W-inch/3.0
        c.setFillColor(TEXT_COLOR2)
        c.drawRightString(xpos, ypos-2.0*inch, str(row[4])+' RON')

        # Draw details.
        c.setFont("DejaVu Sans", TEXT_SIZE2)
        c.drawRightString(xpos, ypos-1.0/2.0*inch, '#'+str(row[0]))
        c.drawRightString(xpos, ypos-1.0*inch, row[2])
        c.drawRightString(xpos, ypos-3.0/2.0*inch, row[3])

        # Draw image.
        img_path = 'database/%i_0.jpg' % row[0]
        if os.path.exists(img_path):
            maxw =  W/2.0-G_BORDER*19
            maxh = 15.5/20.0*H+G_BORDER*3
            img = c.drawImage(img_path, 1.0/20.0*W-G_BORDER*3, 1.0/14.0*H+G_BORDER,
                maxw, maxh, preserveAspectRatio=True)

        # End page.
        c.showPage()

    # Save catalog.
    c.save()


# Connection to database.
conn = sqlite3.connect('database/database.db')
cu = conn.cursor()
cu.execute("SELECT object.id,object.name,categories.name,date,price,descr,object.hidden FROM "
    " object,categories WHERE object.hidden<>1 AND object.cat=categories.id "
    " ORDER BY date desc,object.cat,price")

rows = cu.fetchall()
print 'S-au gasit %i inregistrari.' % len(rows)
Generate_Catalog(rows)
cu.close() ; del cu

raw = open(FILENAME, 'rb').read()
raw = raw.replace('ReportLab Generated PDF document http://www.reportlab.com', 'Trinkets-in-a-Bottle')
raw = raw.replace('(ReportLab PDF Library - www.reportlab.com)', '(Trinkets-in-a-Bottle)')
raw = raw.replace('ReportLab generated PDF document -- digest (http://www.reportlab.com)', 'Trinkets-in-a-Bottle catalog -- digest (http://jewelry-from-the-heart.blogspot.com)')
open(FILENAME, 'wb').write(raw)
del raw

print 'Done !'
os.system('pause')
