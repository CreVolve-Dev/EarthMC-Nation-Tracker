from tortoise import fields, models

class ServerConfiguration(models.Model):
    server_id = fields.BigIntField(pk=True)
    server_name = fields.CharField(max_length=255)

    default_nation = fields.CharField(max_length=255, null=True, default=None)

    player_updates_channel = fields.BigIntField(null=True, default=None)
    player_updates_status = fields.BooleanField(default=False)
    player_updates_tracking = fields.JSONField(null=True, default=[])

    town_updates_channel = fields.BigIntField(null=True, default=None)
    town_updates_status = fields.BooleanField(default=False)
    town_updates_tracking = fields.JSONField(null=True, default=[])

    online_embed_channel = fields.BigIntField(null=True, default=None)
    online_embed_message = fields.BigIntField(null=True, default=None)

    citizen_role = fields.BigIntField(null=True, default=None)
    foreigner_role = fields.BigIntField(null=True, default=None)

    verified_checkup = fields.BooleanField(default=False)
    give_verified_role = fields.BooleanField(default=False)
    online_verify_check = fields.BooleanField(default=False)
    nickname_verified = fields.BooleanField(default=False)

    verified_citizens = fields.JSONField(null=True, default=[])

    class Meta:
        table = "server_configurations"

