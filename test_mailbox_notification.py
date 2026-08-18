import requests

# 1. Login as Priya Sharma (who was invited to NeuralCore AI)
s_priya = requests.Session()
s_priya.post('http://127.0.0.1:5000/login', data={'email': 'priya.s@iitd.ac.in', 'password': 'password123'})

# Check Candidate Home
r_home = s_priya.get('http://127.0.0.1:5000/candidate/home')
print('--- Priya Dashboard (Incoming Invitation) ---')
print('Home Status:', r_home.status_code)
print('PROFILE button has notification badge:', 's30-profile-menu-btn' in r_home.text and 'pulseNotification' in r_home.text)
print('Shows NEW notification pill in drawer:', 'NEW' in r_home.text)
print('Shows Unread Mailbox Banner on dashboard:', 'You have' in r_home.text and 'new squad invitation' in r_home.text)
print('Button is named MAILBOX (not Squad Mailbox):', '📬 MAILBOX' in r_home.text)

# Check Mailbox page
r_mb = s_priya.get('http://127.0.0.1:5000/mailbox')
print('\n--- Priya Mailbox Page ---')
print('Mailbox Status:', r_mb.status_code)
print('Page Title is Mailbox:', '<title>Mailbox' in r_mb.text)
print('H1 is Mailbox:', 'Mailbox' in r_mb.text)
print('Tab has invitations received:', 'INVITATIONS RECEIVED' in r_mb.text)

# 2. Test Join Request Notification for Squad Leader (Arjun)
# Have candidate Marcus Vance send a join request to NeuralCore AI (SQD-AI99)
s_marcus = requests.Session()
s_marcus.post('http://127.0.0.1:5000/login', data={'email': 'marcus.vance@nyu.edu', 'password': 'password123'})
s_marcus.post('http://127.0.0.1:5000/api/team/request-join', json={'team_code': 'SQD-AI99', 'message': 'Hey Arjun, I want to join NeuralCore AI!'})

# Now login as Leader Arjun and check his notifications
s_arjun = requests.Session()
s_arjun.post('http://127.0.0.1:5000/login', data={'email': 'arjun.sharma@iitb.ac.in', 'password': 'password123'})

r_arjun_home = s_arjun.get('http://127.0.0.1:5000/candidate/home')
print('\n--- Leader Arjun Dashboard (Incoming Join Request) ---')
print('Leader Status:', r_arjun_home.status_code)
print('PROFILE button has notification badge for Arjun:', 's30-profile-menu-btn' in r_arjun_home.text and 'pulseNotification' in r_arjun_home.text)
print('Leader Mailbox drawer shows NEW badge:', 'NEW</span>' in r_arjun_home.text)
