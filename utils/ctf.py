#!/usr/bin/env python3
import requests
import sys
import json

# Функция побайтного XOR двух байтовых строк
xor = lambda A, B: bytes(a ^ b for a, b in zip(A, B))

URL = "https://t-capybit-kdot8z7j.spbctf.org"

# Регистрация и получение cookie в виде байтов
def get_cookie_hex(username: str) -> str:
    res = requests.post(f"{URL}/register", data={"username": username}, allow_redirects=False)
    cookie_hex = res.cookies.get('session')
    if not cookie_hex:
        print(f"[!] Ошибка получения cookie для {username}", file=sys.stderr)
        sys.exit(1)
    return cookie_hex

# 1) Генерируем длинное имя, чтобы получить полный keystream
username = "q" * 300
long_cookie_hex = get_cookie_hex(username)
long_cookie = bytes.fromhex(long_cookie_hex)
print(f"[*] Длинная cookie длиной {len(long_cookie)} байт")

# 2) Деривируем keystream как xor(long_cipher, known_plain)
known_plain = username.encode()
keystream = xor(long_cookie, known_plain)

# 3) Дешифруем полный plaintext
long_plain = xor(long_cookie, keystream)
print(f"[*] Расшифрованный полный plaintext: {long_plain[:200]}{'...' if len(long_plain)>200 else ''}")

# 4) Извлекаем JSON через подсчет скобок
start = long_plain.find(b'{')
if start < 0:
    print("[!] JSON не найден в plaintext", file=sys.stderr)
    sys.exit(1)
balance = 0
end = None
for i in range(start, len(long_plain)):
    if long_plain[i] == ord('{'):
        balance += 1
    elif long_plain[i] == ord('}'):
        balance -= 1
    if balance == 0:
        end = i + 1
        break
if end is None:
    print("[!] Несбалансированные скобки в plaintext", file=sys.stderr)
    sys.exit(1)
json_segment = long_plain[start:end]
print(f"[*] Извлечённый JSON: {json_segment}")

data = json.loads(json_segment.decode())
print(f"[*] Оригинальные данные: {data}")

# 5) Модифицируем роль и allow-flag
data.setdefault('attributes', {})
# Перемещаем роль в nested attributes, если нужно
data['attributes']['role'] = 'root'
# Удаляем корневое role, если есть
if 'role' in data and data.get('role') != data['attributes']['role']:
    del data['role']
# Добавляем allow-flag
data['allow-flag'] = 'yes'
print(f"[*] Изменённые данные: {data}")

# 6) Сериализуем JSON без пробелов
new_json = json.dumps(data, separators=(',',':')).encode()
print(f"[*] Новый JSON: {new_json}")

# 7) Собираем новый plaintext: префикс + new_json + суффикс
new_plain = long_plain[:start] + new_json + long_plain[end:]
print(f"[*] Новый полный plaintext: {new_plain[:200]}{'...' if len(new_plain)>200 else ''}")

# 8) Шифруем новый plaintext: xor с keystream
new_cipher = xor(new_plain, keystream)
new_cookie_hex = new_cipher.hex()
print(f"[*] Новая длинная cookie (hex): {new_cookie_hex}")

# 9) Делаем запрос к /funds с новой cookie
res = requests.get(f"{URL}/funds", cookies={"session": new_cookie_hex})
print("[.] Ответ /funds:")
print(res.text)
