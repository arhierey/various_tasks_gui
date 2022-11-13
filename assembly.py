import redis as rd
import random as rnd
import psycopg2 as psg


def get_key(location):
    with open(location, 'r') as f:
        res = f.read()
    return res


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


def list_to_select(select0, list0):
    s = '(' + ''.join(str(list0[i]) + ',' for index in range(0, len(list0)))
    select0 += s[:-1] + ');'
    return select0


# 1. Проверка анаграммы - принимает две строки, определяет являются ли они анаграммами.
# Если являются - необходимо увеличить счетчик в Redis.
# Возвращает JSON - являются ли они анаграммами и счетчик из Redis.

print('Redis segment...')
host = str(input('Enter host(\'localhost\' by default): \n'))
port = int(input('Enter port(6379 by default): \n'))
db_num = int(input('Enter db number(0 by default): \n'))

r = rd.Redis(host, port, db_num)

count = 0

ans = r.exists('anagram_counter')
if not r.exists('anagram_counter'):
    r.set('anagram_counter', 0)

while True:
    print('Enter \'q\' to end this segment\n')
    s1 = str(input('Enter first string: \n'))
    if s1 == 'q':
        break
    s2 = str(input('Enter second string: \n'))

    if len(s1) != len(s2) or len(s1) == 0 or len(s2) == 0:
        ans = False
    else:
        ans = are_anagrams(s1, s2)

    count = int(r.get('anagram_counter').decode())
    if ans:
        print(s1, s2)
        print(ans)
        count += 1
        r.set('anagram_counter', count)
    print(json_wrapper(ans, count))

# 2. Занести в базу данных 10 устройств (таблица devices), тип (dev_type) определяется случайно из списка:
# emeter, zigbee, lora, gsm. Поле dev_id - случайные 48 бит в hex-формате (MAC-адрес).
# К пяти устройствам из добавленных необходимо привязать endpoint (таблица endpoints).
# После записи необходимо возвращать HTTP код состояния 201.

print('Postgre segment...')
host = str(input('Enter host(\'localhost\' by default): \n'))
port = int(input('Enter port(5432 by default): \n'))
db_name = str(input('Enter db name(\'test\' by default): \n'))
user_name = str(input('Enter db name(\'postgres\' by default): \n'))
key = str(input('Enter key(by default): \n'))

cnct = psg.connect(database=db_name, user=user_name, password=key, host=host, port=port)
cur = cnct.cursor()

types = ['emeter', 'zigbee', 'lora', 'gsm']
for i in range(0, 10):
    dev_type = types[rnd.randint(0, 3)]
    dev_id = generate_mac()
    command = 'INSERT INTO devices (dev_id, dev_type) VALUES (\'{0}\', \'{1}\');'.format(dev_id, dev_type)
    print(command)
    cur.execute(command)
    cnct.commit()
    print('Code 201')

indexes = [i for i in range(0, len(ans))]
count = 0
while count < 5:
    index = indexes[rnd.randint(0, len(indexes)-1)]

    if index is not None:
        table_id = ans[index][0]

        command = 'INSERT INTO endpoints (device_id) VALUES ({0});'.format(table_id)
        print(command)
        cur.execute(command)
        cnct.commit()
        print('code: 201')
        count += 1

        indexes[index] = None

# 3. В базе данных получить список всех устройств, которые не привязаны к endpoint.
# Вернуть количество, сгруппированное по типам устройств.

cur.execute('SELECT * FROM endpoints;')
ans = cur.fetchall()

connected = [ans[i][1] for i in range(0, len(ans))]

sel = list_to_select('SELECT * FROM devices WHERE id NOT IN ', connected)

cur.execute(sel)
ans = cur.fetchall()

grouped_ans = {types[i]: 0 for i in range(0, len(types))}

for t in types:
    command = 'SELECT COUNT(dev_type) FROM devices WHERE dev_type = \'{}\' AND id NOT IN '.format(t)
    sel = list_to_select(command, connected)
    cur.execute(sel)
    count = cur.fetchone()
    grouped_ans[t] = count[0]

print(grouped_ans)

cur.close()
cnct.close()
