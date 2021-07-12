from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
import psycopg2


con = None
cur = None
try:
    con = psycopg2.connect("user='username' password='password' host='localhost' port='5432'")
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
    print("Database System Connected!")
except Exception as e:
    print(e)
    print("Database is not connected")
if con is not None:
    cur = con.cursor()
    cur.execute("SELECT datname FROM pg_database;")
    list_database = cur.fetchall()
    if('stcon',) in list_database:
        con = psycopg2.connect("user='username' password='password' host='localhost' port='5432' dbname='stcon'");
        cur = con.cursor()
    else:
        cur.execute("create database stcon;")
        con = psycopg2.connect("user='username' password='password' host='localhost' port='5432' dbname='stcon'");
        cur = con.cursor()
        cur.execute("CREATE TABLE contacts(id SERIAL PRIMARY KEY, cname VARCHAR NOT NULL, cnumber VARCHAR NOT NULL UNIQUE);")
        con.commit()
else:
    print("Database is not connected")

async def homepage(request):
    return JSONResponse({'hello': 'world'})

async def contacts(request):
    global con
    global cur
    if request.method == "GET":
        cur.execute("SELECT * FROM contacts;")
        all = cur.fetchall()
        if len(all)<1: return PlainTextResponse("Nothing in contacts!")
        all = json.dumps(all)
        return PlainTextResponse(all)

    elif request.method == "POST":
        form_data = await request.form()
        name = form_data.get('name')
        phone = form_data.get('phone')

        try:
            cur.execute("INSERT INTO contacts(cname, cnumber) VALUES('" + name + "','" + phone + "');")
            con.commit()
        except:
            con = psycopg2.connect("user='postgres' password='alixan22' host='localhost' port='5432' dbname='stcon'");
            cur = con.cursor()
            return PlainTextResponse("The phone number you entered already exists in Contacts.")
        return PlainTextResponse("Contact Created")


async def with_id(request):
    global con
    global cur
    cid = request.path_params['id']
    cur.execute("SELECT * FROM contacts WHERE id=" + cid + ";")
    single = cur.fetchall()
    print(single)
    if len(single) == 0:
        return PlainTextResponse("There's no contact with id: "+cid+".")

    if request.method == "GET":
        return JSONResponse(single)

    elif request.method == "DELETE":
        cur.execute("DELETE FROM contacts WHERE id=%s;"%cid)
        con.commit()
        return PlainTextResponse("The Contact has been deleted!")
    elif request.method == "PATCH":
        form_data = await request.form()
        name = form_data.get('name')
        phone = form_data.get('phone')
        try:
            cur.execute("UPDATE contacts SET cname='" + name + "', cnumber='"+ phone +"' WHERE id=" + cid+";")
            con.commit()
        except:
            con = psycopg2.connect("user='postgres' password='alixan22' host='localhost' port='5432' dbname='stcon'");
            cur = con.cursor()
            return PlainTextResponse("The phone number you entered already exists in Contacts.")
        return PlainTextResponse("Contact has been updated!")

app = Starlette(debug=True, routes=[
    Route('/', homepage),
    Route('/contacts', contacts, methods=["GET", "POST"]),
    Route('/contacts/{id}', with_id, methods=["GET", "DELETE", "PATCH"]),
])
