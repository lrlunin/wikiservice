# WikiService
Lightweight python library for simple MediaWiki-API requests. 

Example of usage
------
```python
from wikiservice import APIService
s = APIService.WikiAPIService(username='John Doe', password='seceretpass',
domain='INC-DOMAIN', api_url='https://wiki-url.org/api.php')

s.login()
s.createPage(title='Sample page', text='There is a sample text')

s.logout()
```

