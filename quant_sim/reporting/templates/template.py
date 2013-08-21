from os import environ
from django.template import Context, Template
#from django.conf import settings

environ['DJANGO_SETTINGS_MODULE'] = '__main__'
#settings.configure(Debug=False, TEMPLATE_DEBUG=False)

f = open('test_template.html','r')
temp_raw = f.read()
t = Template(temp_raw)
env = {'first_name':'Justin',
       'last_name':'Lanahan'}
print t.render(Context(env))