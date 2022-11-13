import tkinter as tk
from tkinter import messagebox
import redis as rd
import psycopg2 as psg
import random as rnd

root = tk.Tk()
root.geometry("1000x600")

s1_var = tk.StringVar()
s2_var = tk.StringVar()
host_var, port_var, db_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
host1_var, port1_var, db1_var, uname_var, key_var = tk.StringVar(), tk.StringVar(), tk.StringVar(), \
                                                    tk.StringVar(), tk.StringVar()


def generate_mac():
    mac = ''
    for index in range(0, 5):
        a = str(hex(rnd.randint(1, 255))[2::])
        if len(a) == 1:
            a = '0' + a
        mac += a + ':'
    a = str(hex(rnd.randint(1, 255))[2::])
    if len(a) == 1:
        a = '0' + a
    mac += a
    return mac


def are_anagrams(string1, string2):
    flags1 = [0]*len(string1)
    flags2 = [0]*len(string2)
    for index in range(0, len(string1)):
        for j in range(0, len(string2)):
            if string1[index] == string2[j] and flags1[index] == 0 and flags2[j] == 0:
                flags1[index] = 1
                flags2[j] = 1
    if all(flags1) and all(flags2):
        res = True
    else:
        res = False
    return res


def json_wrapper(answer, counter):
    res = '{' + '\'are_anagrams\':{0},'.format(answer)
    res += '\'counter\':{0}'.format(counter) + '}'
    return res


def list_to_select(select0, list0):
    s = '(' + ''.join(str(list0[index]) + ',' for index in range(0, len(list0)))
    select0 += s[:-1] + ');'
    return select0


def connect_to_redis():
    global redis_conn
    host = host_var.get()
    port = int(port_var.get())
    db = int(db_var.get())

    print(host, port, db)
    redis_conn = rd.Redis(host, port, db)

    messagebox.showinfo('ans', 'connected to db={0}'.format(db))


def connect_to_postgre():
    global pg_conn
    global pg_cur
    host = host1_var.get()
    port = int(port1_var.get())
    db = db1_var.get()
    username = uname_var.get()
    key = key_var.get()

    pg_conn = psg.connect(database=db, user=username, password=key, host=host, port=port)
    pg_cur = pg_conn.cursor()

    messagebox.showinfo('ans', 'connected to {0} database'.format(db))


def submit():
    s1 = s1_var.get()
    s2 = s2_var.get()

    print(s1, s2)
    print(are_anagrams(s1, s2))

    if not redis_conn.exists('anagram_counter'):
        redis_conn.set('anagram_counter', 0)

    if len(s1) != len(s2) or len(s1) == 0 or len(s2) == 0:
        ans = False
    else:
        ans = are_anagrams(s1, s2)

    count = int(redis_conn.get('anagram_counter').decode())
    if ans:
        count += 1
        redis_conn.set('anagram_counter', count)
    print(json_wrapper(ans, count))

    messagebox.showinfo('ans', json_wrapper(ans, count))

    s1_var.set('')
    s2_var.set('')


def add_devices():
    types = ['emeter', 'zigbee', 'lora', 'gsm']

    for i in range(0, 10):
        dev_type = types[rnd.randint(0, 3)]
        dev_id = generate_mac()
        command = 'INSERT INTO devices (dev_id, dev_type) VALUES (\'{0}\', \'{1}\');'.format(dev_id, dev_type)
        print(command)
        pg_cur.execute(command)
        pg_conn.commit()
        messagebox.showinfo('ans', 'code 201')
        print('Code 201')  # HTML answer

    pg_cur.execute('SELECT * FROM devices;')
    ans = pg_cur.fetchall()
    print(ans)
    indexes = [i for i in range(0, len(ans))]
    print(indexes)
    count = 0
    while count < 5:
        index = indexes[rnd.randint(0, len(indexes) - 1)]
        print(index)

        if index is not None:
            table_id = ans[index][0]

            command = 'INSERT INTO endpoints (device_id) VALUES ({0});'.format(table_id)
            print(command)
            pg_cur.execute(command)
            pg_conn.commit()
            messagebox.showinfo('ans', 'code 201')
            print('code: 201')
            count += 1

            indexes[index] = None


def check_devices():
    types = ['emeter', 'zigbee', 'lora', 'gsm']
    pg_cur.execute('SELECT * FROM endpoints;')
    ans = pg_cur.fetchall()
    connected = [ans[i][1] for i in range(0, len(ans))]
    sel = list_to_select('SELECT * FROM devices WHERE id NOT IN ', connected)
    pg_cur.execute(sel)
    ans = pg_cur.fetchall()
    grouped_ans = {types[i]: 0 for i in range(0, len(types))}
    for t in types:
        command = 'SELECT COUNT(dev_type) FROM devices WHERE dev_type = \'{}\' AND id NOT IN '.format(t)
        sel = list_to_select(command, connected)
        pg_cur.execute(sel)
        count = pg_cur.fetchone()
        grouped_ans[t] = count[0]
    messagebox.showinfo('ans', grouped_ans)
    print(grouped_ans)


# Redis entry
host_label = tk.Label(root, text='host')
host_entry = tk.Entry(root, textvariable=host_var)

port_label = tk.Label(root, text='port')
port_entry = tk.Entry(root, textvariable=port_var)

db_label = tk.Label(root, text='db')
db_entry = tk.Entry(root, textvariable=db_var)

rd_btn = tk.Button(root, text='Connect to Redis', command=connect_to_redis)

# Strings entry
first_string_label = tk.Label(root, text='first string')
first_entry = tk.Entry(root, textvariable=s1_var)

second_string_label = tk.Label(root, text='second string')
second_entry = tk.Entry(root, textvariable=s2_var)

sub_btn = tk.Button(root, text='Anagrams?', command=submit)

# Postgre entry
host1_label = tk.Label(root, text='host')
host1_entry = tk.Entry(root, textvariable=host1_var)

port1_label = tk.Label(root, text='port')
port1_entry = tk.Entry(root, textvariable=port1_var)

db1_label = tk.Label(root, text='db')
db1_entry = tk.Entry(root, textvariable=db1_var)

uname_label = tk.Label(root, text='username')
uname_entry = tk.Entry(root, textvariable=uname_var)

key_label = tk.Label(root, text='key')
key_entry = tk.Entry(root, textvariable=key_var, show='*')

pg_btn = tk.Button(root, text='Connect to Postgre', command=connect_to_postgre)

# SQL Operations
add_devices_btn = tk.Button(root, text='Add devices to db', command=add_devices)
check_devices_btn = tk.Button(root, text='Check unconnected devices', command=check_devices)

# Placement
row1, row2, row3, row4, row5, row6, row7 = 4, 14, 24, 28, 32, 36, 40

tips1_label = tk.Label(root, text='Connect to redis \n(i.e. localhost, 6379, 0)')
tips2_label = tk.Label(root, text='Connect to postgreSQL database \n(i.e. localhost, 6379, test, postgres, ***)')

tips1_label.grid(row=0, column=2)

host_label.grid(row=row1, column=0)
host_entry.grid(row=row1, column=1)
port_label.grid(row=row1, column=2)
port_entry.grid(row=row1, column=3)
db_label.grid(row=row1, column=4)
db_entry.grid(row=row1, column=5)

rd_btn.grid(row=row2, column=1)

first_string_label.grid(row=row3, column=0)
first_entry.grid(row=row3, column=1)
second_string_label.grid(row=row3, column=2)
second_entry.grid(row=row3, column=3)

sub_btn.grid(row=row3, column=5)

# Postgre

tips2_label.grid(row=row4, column=2)

host1_label.grid(row=row5, column=0)
host1_entry.grid(row=row5, column=1)

port1_label.grid(row=row5, column=2)
port1_entry.grid(row=row5, column=3)

db1_label.grid(row=row5, column=4)
db1_entry.grid(row=row5, column=5)

uname_label.grid(row=row6, column=0)
uname_entry.grid(row=row6, column=1)

key_label.grid(row=row6, column=2)
key_entry.grid(row=row6, column=3)

pg_btn.grid(row=row6, column=4)

add_devices_btn.grid(row=row7, column=1)
check_devices_btn.grid(row=row7, column=2)

root.mainloop()
