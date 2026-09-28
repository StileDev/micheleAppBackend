from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/parcelles/(?P<parcelle_id>\d+)/$', consumers.ParcelleConsumer.as_asgi()),
]
