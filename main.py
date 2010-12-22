
import os, sys
import shutil, glob
import time
import pickle
import sqlite3
import webbrowser
from Backup_DropBox import upload_file
from Backup_GoogleDocs import gdata_excel
from bottle import run, route, get, post, debug, error
from bottle import request, redirect, template, send_file, static_file
user = os.getenv('USERNAME').lower()


@route(':filename#.*\.png|.*\.gif|.*\.jpg|.*\.css|.*\.js#')
@route('/browse/:filename#.*\.png|.*\.gif|.*\.jpg|.*\.css|.*\.js#')
@route('/item/:filename#.*\.png|.*\.gif|.*\.jpg|.*\.css|.*\.js#')
@route('/view/:filename#.*\.png|.*\.gif|.*\.jpg|.*\.css|.*\.js#')
@route('/cart/:filename#.*\.png|.*\.gif|.*\.jpg|.*\.css|.*\.js#')
@route('/hide/:filename#.*\.png|.*\.gif|.*\.jpg|.*\.css|.*\.js#')
@route('/new/:filename#.*\.png|.*\.gif|.*\.jpg|.*\.css|.*\.js#')
@route('/edit/:what/:filename#.*\.png|.*\.gif|.*\.jpg|.*\.css|.*\.js#')
@route('/delete/:what/:filename#.*\.png|.*\.gif|.*\.jpg|.*\.css|.*\.js#')
@route('/admin/:filename#.*\.png|.*\.gif|.*\.jpg|.*\.css|.*\.js#')
@route('/export/:filename#.*\.png|.*\.gif|.*\.jpg|.*\.css#')
def server_static(filename=None, what=None):
    return static_file(filename, root=os.getcwd())


@route('/')
@route('/home')
def home():

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()

    # Select all objects, but replace the Category ID with Category Name.
    c.execute("SELECT id,name,price,lbl FROM object WHERE hidden<>1 ORDER BY date DESC LIMIT 4")
    rows = c.fetchall()

    c.close() ; del c
    return template('home.htm', rows=rows)


@route('/item/:id#[A-Za-z0-9]+#')
def item(id):

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()

    # Select object, but replace the Category ID with Category Name.
    c.execute("SELECT object.id,object.name,categories.name,lbl,date,price,descr,object.cat,hidden FROM "
        " object,categories WHERE object.id=? AND object.cat=categories.id", [id])
    cdescr = c.fetchone()
    # Select all categories.
    c.execute("SELECT id,name FROM categories")
    cats = c.fetchall()
    # Select similar objects.
    c.execute("SELECT id,name,price,lbl FROM object WHERE cat=? AND hidden<>1 AND id<>? ORDER BY date DESC LIMIT 4",
        [cdescr[7], id])
    rows = c.fetchall()
    # Find all pictures for this ID.
    pics = [p.split('/')[1:2] or p.split('\\')[1:2] for p in glob.glob('database/%s_[0-9]*.jpg' % id)]

    c.close() ; del c
    return template('item.htm', cats=cats, categ=cdescr[7], c=cdescr, pics=pics, rows=rows)


@route('/browse')
@get('/browse/:cat#[A-Za-z0-9]+#')
def browse(cat='all'):

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()

    categ = cat.upper()
    f_title = request.GET.get('title','').strip()
    f_lbl = request.GET.get('lbl','').strip()
    f_action = ''

    if f_title:
        f_action += "name LIKE '%%%s%%' AND " % f_title
    if f_lbl:
        f_action += "lbl LIKE '%%%s%%' AND " % f_lbl

    # Select all objects in this category.
    if categ != 'ALL':
        if c.execute("SELECT * FROM categories WHERE id = ?", [categ]).fetchone():
            c.execute("SELECT id,name,price,lbl,hidden FROM object WHERE %s cat = '%s' ORDER BY date,name" % (f_action, categ))
        else:
            return template('base_redirect.htm', what='obj', type='Error', message="Category `%s` doesn't exist !" % categ)
    else:
        if f_action:
            c.execute("SELECT id,name,price,lbl,hidden FROM object WHERE %s ORDER BY date,name" % f_action.rstrip('AND '))
        else:
            c.execute("SELECT id,name,price,lbl,hidden FROM object ORDER BY date,name")

    rows = c.fetchall()
    # Select all categories.
    c.execute("SELECT id,name FROM categories")
    cats = c.fetchall()
    # Select all labels.
    c.execute("SELECT name FROM labels")
    lbls = c.fetchall()

    c.close()
    return template('browse.htm', cats=cats, lbls=lbls, rows=rows, categ=categ,
        f_title=f_title, f_lbl=f_lbl)


@route('/export')
@route('/export/:ses#[-\.A-Za-z0-9]+#')
def export_session(ses=None):

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()

    # Select all objects, but replace the Category ID with Category Name.
    if not ses:
        c.execute("SELECT object.id,object.name,categories.name,lbl,date,price,descr,object.cat FROM "
            " object,categories WHERE object.cat=categories.id ORDER BY date desc,object.cat,price")
    else:
        c.execute("SELECT object.id,object.name,categories.name,lbl,date,price,descr,object.cat FROM "
            " object,categories WHERE object.cat=categories.id AND date=? ORDER BY object.cat,price",[ses])
    rows = c.fetchall()
    # Select all sessions.
    c.execute("SELECT DISTINCT date FROM object ORDER BY date")
    sess = c.fetchall()
    c.close() ; del c

    return template('export.htm', sess=sess, rows=rows)


@route('/view')
@route('/view/:what#obj|cat|lbl|img|tranz|clients#')
def view_tables(what='obj'):

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()

    if what == 'obj':
        # Select all objects, but replace the Category ID with Category Name.
        c.execute("SELECT object.id,object.name,categories.name,lbl,date,price FROM "
            " object,categories WHERE object.cat=categories.id")
        cdescr=['id','name','cat','lbl','date','price']
    elif what == 'cat':
        c.execute("SELECT * FROM categories")
        cdescr=['id','name']
    elif what == 'lbl':
        c.execute("SELECT * FROM labels")
        cdescr=['id','name']

    # For Images, simply redirect.
    elif what == 'img':
        redirect('/view/obj')
    # Tranzactions.
    elif what == 'tranz':
        c.execute("SELECT * FROM tranzactions")
        cdescr=['id','tranz','quantity','price']
    # Clients.
    elif what == 'clients':
        c.execute("SELECT * FROM clients")
        cdescr=['id','name']

    rows = c.fetchall()
    c.close()
    return template('view.htm', what=what, rows=rows, cdescr=cdescr)


@get('/cart')
def shopping_cart():

    # Load shopping cart.
    d = list(pickle.load(open('database/cart.pck','rb')))

    for i in range(len(d)):
        # Delete ?
        if request.GET.get('delete_%i' % i):
            d[i] = 0
            continue
        # Get Quantity.
        q = request.GET.get('q_%i' % i)
        if q and q.strip():
            try: d[i]['q'] = int(q.strip())
            except: d[i]['q'] = 1
        # Get Price.
        p = request.GET.get('p_%i' % i)
        if p and p.strip():
            try: d[i]['p'] = int(p.strip())
            except: d_new[i]['p'] = 0
        # Get Client.
        c = request.GET.get('c_%i' % i)
        if c and c.strip():
            d[i]['c'] = c.strip()

    # Cleanup list.
    d = [val for val in d if val]

    # If CHECKOUT:
    if request.GET.get('submit') == 'Proceed to checkout':
        print '!!! Proceed to checkout DETECTED !!!'

    rows = []
    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()

    c.execute("SELECT name FROM clients")
    clients = c.fetchall()

    for r in d:
        # Every record contains : obj id, obj name, quantity, price, client name.
        record = [r['obj_id']]
        c.execute("SELECT name from object where id = ?", [r['obj_id']])
        try: record.append(c.fetchone()[0])
        except: record.append('Invalid Obj ID')
        record.append(r['q'])
        record.append(r['p'])
        record.append(r['c'])
        # Add record.
        rows.append(record)

    # Save shopping cart.
    pickle.dump(d, open('database/cart.pck','wb'), 2)
    # Close database.
    c.close() ; del c
    return template('cart.htm', rows=rows, clients=clients)


@route('/buy/:id#[A-Za-z0-9]+#')
def buy(id):

    # Load shopping cart.
    d = list(pickle.load(open('database/cart.pck','rb')))

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()
    c.execute("SELECT price from object where id = ?", [id])
    p = c.fetchone()
    if p:
        p = p[0]
    else:
        p = 0
    c.close() ; del c

    # Add this item in list.
    r = {}
    r['obj_id'] = id
    r['q'] = 1
    r['p'] = p
    r['c'] = 'Ana Mititichi'
    d.append(r)

    # Save shopping cart.
    pickle.dump(d, open('database/cart.pck','wb'), 2)

    redirect('/cart')


@route('/hide/:id#[A-Za-z0-9]+#')
def hide(id):

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()
    c.execute("SELECT hidden FROM object WHERE id = ?", [id])
    h = c.fetchone()[0]

    # If object is visible, it must become hidden.
    if h:
        c.execute("UPDATE object SET hidden='' WHERE id=?", [id])
    # If object is hidden, it must become visible.
    else:
        c.execute("UPDATE object SET hidden=1 WHERE id=?", [id])

    conn.commit()
    c.close()

    if h:
        return template('base_redirect.htm', what='obj', id=id, type='Message',
            message='The object with ID %s is now VISIBLE.' % (id))
    else:
        return template('base_redirect.htm', what='obj', id=id, type='Message',
            message='The object with ID %s is now HIDDEN.' % (id))


@get('/delete/:what#obj|cat|lbl|img|tranz|clients#/:id#[%\._A-Za-z0-9]+#')
def delete_item(what, id):

    if request.GET.get('action','').strip() == 'Delete':

        conn = sqlite3.connect('database/database.db')
        c = conn.cursor()
        if what == 'obj':
            c.execute("DELETE FROM object WHERE id = ?", [id])
        elif what == 'cat':
            c.execute("DELETE FROM categories WHERE id = ?", [id])
        elif what == 'lbl':
            c.execute("DELETE FROM labels WHERE id = ?", [id])
        elif what == 'img':
            id = id.replace('%', '.')
            try: os.remove('database/'+id) ; img_deleted = True
            except: img_deleted = False
        conn.commit()
        c.close()

        # Find all remaining pictures for this ID.
        pics = glob.glob('database/%s_*.jpg' % id) + glob.glob('database/%s_*.png' % id)

        if what == 'img':
            return template('''%rebase error.htm
<h3><span class="ui-icon ui-icon-info" style="float:left;margin-right:.4em;"></span>
%if deleted:
    Message:<br /><br />The image <b>{{id}}</b> was deleted !
%else:
    Message:<br /><br />The image <b>{{id}}</b> could not be deleted !
%end
</h3>''', id=id, deleted=img_deleted)

        elif pics:
            return template('''%rebase error.htm
<h3><span class="ui-icon ui-icon-info" style="float:left;margin-right:.4em;"></span>
    Message :<br /><br />
    Item of type <b>{{what}}</b> with ID <b>{{id}}</b> was deleted !<br />
    There are <b>{{len_pics}}</b> pictures left in database : {{pics}}.<br />
    You have to delete them manually.
</h3>''', what=what, id=id, len_pics=len(pics), pics=str(pics))

        else:
            return template('''%rebase error.htm
<h3><span class="ui-icon ui-icon-info" style="float:left;margin-right:.4em;"></span>
    Message :<br /><br />
    Item of type <b>{{what}}</b> with ID <b>{{id}}</b> was deleted !
</h3>''', what=what, id=id)

    elif request.GET.get('action','').strip() == 'Cancel':

        redirect('/view/'+what)

    else:

        conn = sqlite3.connect('database/database.db')
        c = conn.cursor()
        if what == 'obj':
            c.execute("SELECT id,name FROM object WHERE id = ?", [id])
        elif what == 'cat':
            c.execute("SELECT id,name FROM categories WHERE id = ?", [id])
        elif what == 'lbl':
            c.execute("SELECT id,name FROM labels WHERE id = ?", [id])
        result = c.fetchone()
        c.close()

        if what != 'img' and not result:
            return template('''%rebase error.htm
<h3><span class="ui-icon ui-icon-alert" style="float:left;margin-right:.4em;"></span>
    Warning :<br /><br />
    Item of type <b>{{what}}</b> with ID <b>{{id}}</b> does't exist !
</h3>''', what=what, id=id)

        elif what == 'img':
            return template('delete.htm', id=id, what=what, name='Image')

        else:
            return template('delete.htm', id=id, what=what, name=result[1])


@route('/new/:what#obj|cat|lbl|tranz|clients#')
def new_item(what):

    if what == 'obj':
        conn = sqlite3.connect('database/database.db')
        c = conn.cursor()
        c.execute("SELECT id,name FROM categories")
        cats = c.fetchall()
        c.execute("SELECT id,name FROM labels")
        lbls = c.fetchall()
        c.close()
        return template('new.htm', what=what, cats=cats, lbls=lbls)
    else:
        return template('new.htm', what=what)


@post('/new/:what#obj|cat|lbl|tranz|clients#')
def new_item_post(what):

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()

    if request.POST.get('action','').strip() == 'Submit':

        if what == 'obj':
            # Save all information.
            name = request.POST.get('name', '').strip()
            descr = request.POST.get('descr', '').strip()
            cat = request.POST.get('cat', '').strip()
            lbl = request.POST.getall('lbl')
            lbl = ', '.join(lbl) ; lbl = ' '.join(lbl.split())
            date = request.POST.get('date', time.strftime('%Y-%m-%d')).strip()
            p = request.POST.get('p', '0').strip()
            # Add all information into database.
            c.execute("INSERT INTO object (name,descr,cat,lbl,date,price,hidden) VALUES (?,?,?,?,?,?,?)",
                [name,descr,cat,lbl,date,p,0])
            # Process pictures.
            pictures = request.files.getall('pictures')
            nr = 0
            for pic in pictures:
                f = open(('database/%i_%i.jpg' % (c.lastrowid, nr)), 'wb')
                f.write(pic.file.read())
                f.close()
                nr += 1

        elif what == 'cat':
            id = request.POST.get('id', '').strip()
            name = request.POST.get('name', '').strip()
            c.execute("INSERT INTO categories (id,name) VALUES (?,?)", [id,name])

        elif what == 'lbl':
            name = request.POST.get('name', '').strip()
            c.execute("INSERT INTO labels (name) VALUES (?)", [name])

        conn.commit()
        c.close()

        return template('base_redirect.htm', what=what, id=c.lastrowid, type='Message',
            message='New %s was added into database, the ID is %i.' % (what.title(), c.lastrowid))

    else:

        redirect('/view/'+what)


@get('/edit/:what#obj|cat|lbl|tranz|clients#/:id#[A-Za-z0-9]+#')
def edit_item(what, id):

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()

    if what == 'obj':
        # Select all categories.
        c.execute("SELECT id,name FROM categories")
        all_categories = c.fetchall()
        # Select all labels.
        c.execute("SELECT id,name FROM labels")
        all_labels = c.fetchall()
        # Select all information about object.
        c.execute("SELECT name,descr,cat,lbl,date,price FROM object WHERE id = ?", [id])
        c_data =    c.fetchone()
        vname =     c_data[0]
        vdescr =    c_data[1]
        cat =       c_data[2]
        lbl =       c_data[3]
        vdate =     c_data[4]
        vp =        c_data[5]
        # Find all pictures for this ID.
        pics = [p.split('/')[1:2] or p.split('\\')[1:2] for p in glob.glob('database/%s_*.jpg' % id)]

        return template('edit.htm', what=what,id=id,vname=vname,vdescr=vdescr,
            cat=cat,lbl=lbl.split(', '),vdate=vdate,vp=vp,
            cats=all_categories,lbls=all_labels,pics=pics)

    elif what == 'cat':
        c.execute("SELECT name FROM categories WHERE id = ?", [id])

    elif what == 'lbl':
        c.execute("SELECT name FROM labels WHERE id = ?", [id])

    elif what == 'clients':
        c.execute("SELECT name FROM clients WHERE id = ?", [id])

    c_data = c.fetchone()
    return template('edit.htm', what=what, id=id, vname=c_data[0])


@post('/edit/:what#obj|cat|lbl|tranz|clients#/:id#[A-Za-z0-9]+#')
def edit_item_post(what, id):

    # Save all information.
    name = request.POST.get('name', '').strip()
    descr = request.POST.get('descr', '').strip()
    pictures = request.POST.getall('pictures')
    cat = request.POST.get('cat', '').strip()
    lbl = request.POST.getall('lbl')
    lbl = ', '.join(lbl) ; lbl = ' '.join(lbl.split())
    date = request.POST.get('date', time.strftime('%Y-%m-%d')).strip()
    q = request.POST.get('q', '0').strip()
    p = request.POST.get('p', '0').strip()

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()

    if what == 'obj':
        # Add all information into database.
        c.execute("UPDATE object SET name = ?,descr = ?,cat = ?,lbl = ?,date = ?,price = ?  WHERE id = ?",
            [name,descr,cat,lbl,date,p,id])
        # Process pictures.
        pictures = request.files.getall('pictures')
        nr = 0
        # Searching number of pictures already in pictures folder.
        while 1:
            if os.path.exists('database/%s_%i.jpg' % (id, nr)):
                nr += 1
                continue
            else:
                break
        # Writing picture in pictures folder.
        for pic in pictures:
            f = open(('database/%s_%i.jpg' % (id, nr)), 'wb')
            f.write(pic.file.read())
            f.close()
            nr += 1
    elif what == 'cat':
        c.execute("UPDATE categories SET name = ? WHERE id = ?", [name,id])
    elif what == 'lbl':
        c.execute("UPDATE labels SET name = ? WHERE id = ?", [name,id])

    conn.commit()
    c.close() ; del c

    return template('base_redirect.htm', what=what, id=id, type='Message',
        message='The %s with ID %s was successfully updated.' % (what.title(), id))


@get('/admin')
def admin():

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()
    d = pickle.load(open('database/pu.pck','rb'))

    # Do Cleanup.
    if request.GET.get('action','').strip() == 'Cleanup':
        for f in glob.glob('database/*_tmb.jpg'):
            try: os.remove(f)
            except: pass
        c.execute('VACUUM')
        return template('admin.htm', msg='Vacuum finished width SUCCES !', pck=d)

    # Backup on DropBox.
    elif request.GET.get('action','').strip() == 'Backup_DropBox':
        d_usr = request.GET.get('d_usr','').strip()
        d_pwd = request.GET.get('d_pwd','').strip()
        d['d']['u'] = d_usr
        d['d']['p'] = d_pwd
        pickle.dump(d, open('database/pu.pck','wb'), 2)
        if user=='ana':
            try: shutil.copy2('database/database.db', 'D:/My Documents/My Dropbox/database_%s.db' % time.strftime('%Y-%m-%d_%H-%M'))
            except: pass
        else:
            upload_file('database/database.db','/','database_%s.db' % time.strftime('%Y-%m-%d_%H-%M'), d_usr,d_pwd)
        return template('admin.htm', msg='Backup on DropBox finished width SUCCES !', pck=d)

    # Backup on Google Docs.
    elif request.GET.get('action','').strip() == 'Backup_GoogleDocs':
        g_usr = request.GET.get('g_usr','').strip()
        g_pwd = request.GET.get('g_pwd','').strip()
        d['d']['u'] = g_usr
        d['d']['p'] = g_pwd
        pickle.dump(d, open('database/pu.pck','wb'))
        gdata_excel(conn, g_usr, g_pwd)
        return template('admin.htm', msg='Backup on Google Docs finished width SUCCES !', pck=d)

    c.close() ; del c
    return template('admin.htm', msg='', pck=d)


@error(403)
@error(404)
def mistake(code):
    return template('''%rebase error.htm
<h3><span class="ui-icon ui-icon-alert" style="float:left;margin-right:.5em;"></span>
Error <strong>{{code}}</strong> !<br /><br />There is a mistake in your url !
</h3>''', code=code)


if user=='ana':
    webbrowser.open_new_tab('http://localhost:333/')
    run(host='localhost', port=333)
else:
    debug(True)
    run(host='localhost', port=333, reloader=True)

# Eof()
