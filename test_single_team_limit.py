import requests
import database

# 1. Leader Arjun (leads NeuralCore AI & TeamY, id=10)
s_arjun = requests.Session()
s_arjun.post('http://127.0.0.1:5000/login', data={'email': 'arjun.sharma@iitb.ac.in', 'password': 'password123'})

# 2. Member Neha (member of NeuralCore AI, id=11)
s_neha = requests.Session()
s_neha.post('http://127.0.0.1:5000/login', data={'email': 'neha.patel@bits.ac.in', 'password': 'password123'})

# 3. Free candidate Priya (no squad, id=3)
s_priya = requests.Session()
s_priya.post('http://127.0.0.1:5000/login', data={'email': 'priya.s@iitd.ac.in', 'password': 'password123'})

print('--- Test 1: Leader Arjun visits /team/create ---')
r_arjun_get = s_arjun.get('http://127.0.0.1:5000/team/create')
print('HTTP Status:', r_arjun_get.status_code)
print('Shows ACTIVE SQUAD LIMIT REACHED:', 'ACTIVE SQUAD LIMIT REACHED' in r_arjun_get.text)
print('Shows MANAGE SQUAD button:', 'MANAGE SQUAD' in r_arjun_get.text)
print('Shows DISBAND SQUAD button:', 'DISBAND SQUAD' in r_arjun_get.text)

print('\n--- Test 2: Leader Arjun tries POST /team/create (Should be blocked) ---')
r_arjun_post = s_arjun.post('http://127.0.0.1:5000/team/create', data={'team_name': 'DuplicateSquad', 'team_size': '4', 'theme': 'AI'})
print('Blocked with error in page:', 'cannot create more than one squad' in r_arjun_post.text or 'already lead' in r_arjun_post.text)

print('\n--- Test 3: Member Neha visits /team/create ---')
r_neha_get = s_neha.get('http://127.0.0.1:5000/team/create')
print('HTTP Status:', r_neha_get.status_code)
print('Shows ACTIVE SQUAD MEMBERSHIP:', 'ACTIVE SQUAD MEMBERSHIP' in r_neha_get.text)
print('Shows VIEW TEAMMATES button:', 'VIEW TEAMMATES' in r_neha_get.text)
print('Shows LEAVE SQUAD button:', 'LEAVE SQUAD' in r_neha_get.text)

print('\n--- Test 4: Member Neha tries POST /team/create (Should be blocked) ---')
r_neha_post = s_neha.post('http://127.0.0.1:5000/team/create', data={'team_name': 'NehaSquad', 'team_size': '4', 'theme': 'AI'})
print('Blocked with error in page:', 'Please leave your current squad' in r_neha_post.text or 'currently a member' in r_neha_post.text)

print('\n--- Test 5: Free Candidate Priya visits /team/create ---')
r_priya_get = s_priya.get('http://127.0.0.1:5000/team/create')
print('HTTP Status:', r_priya_get.status_code)
print('Shows creation form for Priya:', 'Squad Setup Details' in r_priya_get.text)
print('Has submit button:', 'CREATE SQUAD' in r_priya_get.text)
