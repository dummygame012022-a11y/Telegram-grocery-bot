import os
import requests, time, sqlite3
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN', '')
API_URL = f'https://api.telegram.org/bot{TOKEN}/'
PRODUCTS = {'Coffee': 10, 'Bread': 3, 'Egg': 12, 'Milk': 25}
CARTS = {}
db = sqlite3.connect('orders.db')
db.execute('''create table if not exists orders(
  id integer primary key, chat text, items text,
  total real, ts text default current_timestamp)''')
db.commit()

def api(m, **d):
    return requests.post(API_URL + m, json=d, timeout=40).json()

def kb():
    rows = [[{'text': f'{k} - P{v}', 'callback_data': 'add:' + k}]
            for k, v in PRODUCTS.items()]
    rows.append([{'text': 'View Cart', 'callback_data': 'cart'},
                 {'text': 'Place Order', 'callback_data': 'order'}])
    return {'inline_keyboard': rows}

def cart(c):
    it = CARTS.get(c, {})
    if not it:
        return 'Your cart is empty.', 0
    ls = [f'{k} x{q} = P{PRODUCTS[k]*q}' for k, q in it.items()]
    t = sum(PRODUCTS[k] * q for k, q in it.items())
    return '\n'.join(ls) + f'\nTotal: P{t}', t

def send(c, t, k=None):
    d = {'chat_id': c, 'text': t}
    if k:
        d['reply_markup'] = k
    api('sendMessage', **d)

def on_msg(m):
    c = m['chat']['id']
    t = m.get('text', '').lower()
    if t in ('/start', '/menu'):
        send(c, 'Welcome! Choose items to order:', kb())
    else:
        send(c, 'Type /menu to start ordering.')

def on_btn(q):
    c = q['message']['chat']['id']
    d = q['data']
    note = ''
    if d.startswith('add:'):
        k = d[4:]
        CARTS.setdefault(c, {})
        CARTS[c][k] = CARTS[c].get(k, 0) + 1
        note = 'Added: ' + k
    elif d == 'cart':
        send(c, cart(c)[0])
    elif d == 'order':
        txt, t = cart(c)
        if t:
            cur = db.execute(
                'insert into orders(chat,items,total) values(?,?,?)',
                (str(c), txt, t))
            db.commit()
            CARTS[c] = {}
            send(c, f'Thank you! Order #{cur.lastrowid}\n{txt}')
        else:
            send(c, txt)
    api('answerCallbackQuery', callback_query_id=q['id'], text=note)

o = 0
print('running')
while True:
    try:
        r = requests.get(API_URL + 'getUpdates',
            params={'offset': o, 'timeout': 30},
            timeout=40).json()
        for u in r.get('result', []):
            o = u['update_id'] + 1
            if 'message' in u:
                on_msg(u['message'])
            elif 'callback_query' in u:
                on_btn(u['callback_query'])
    except Exception as e:
        print(e)
        time.sleep(3)
