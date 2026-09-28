import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Parcelle


class ParcelleConsumer(AsyncWebsocketConsumer):
    """Un client se connecte à ws/parcelles/<id>/?token=<access_token> et
    reçoit, en temps réel, chaque nouvelle mesure (température, humidité
    de l'air, humidité du sol) dès qu'elle est publiée côté serveur —
    que ce soit via POST /mesures/ ou PATCH /mesures/temps-reel/."""

    async def connect(self):
        self.parcelle_id = self.scope['url_route']['kwargs']['parcelle_id']
        user = self.scope.get('user')

        if user is None or not user.is_authenticated:
            await self.close(code=4401)  # non authentifié
            return

        owns = await self._user_owns_parcelle(user, self.parcelle_id)
        if not owns:
            await self.close(code=4403)  # cette parcelle n'appartient pas à cet utilisateur
            return

        self.group_name = f'parcelle_{self.parcelle_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def mesure_update(self, event):
        """Reçu depuis group_send (voir views.diffuser_mesure) et
        retransmis tel quel au client connecté."""
        await self.send(text_data=json.dumps(event['payload']))

    @database_sync_to_async
    def _user_owns_parcelle(self, user, parcelle_id):
        return Parcelle.objects.filter(id=parcelle_id, user=user).exists()
