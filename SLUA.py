import sys
import requests

r = requests.get('https://itunes.apple.com/search?term=' + sys.argv[1] + '&entity=song&limit=1')

print('https://itunes.apple.com/search?term=' + sys.argv[1] + '&entity=song&limit=1')

results = r.json().get('results')
apple_id = -1


if len(results) > 0:
    apple_id = results[0].get(u'trackId')

    payload = {'apple_id': str(apple_id)}

    p = requests.post('http://localhost:8000/api/data/00000', data=payload)

    print(p.text)

# print(r.json())
