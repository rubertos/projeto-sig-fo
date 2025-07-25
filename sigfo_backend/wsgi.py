"""
WSGI config for sigfo_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigfo_backend.settings')

application = get_wsgi_application()


"""import os
import sys

# -- Substitua 'rubertos' pelo seu nome de utilizador no PythonAnywhere --
# -- Confirme que 'projeto-sig-fo' é o nome da sua pasta de projeto --
path = '/home/rubertos/projeto-sig-fo'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'sigfo_backend.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()"""