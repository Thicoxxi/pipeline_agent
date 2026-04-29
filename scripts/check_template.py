from src.app import app

print('template_folder=', app.template_folder)
with app.test_client() as c:
    r = c.get('/')
    print('status', r.status_code)
    print(r.data.decode('utf-8')[:400])
