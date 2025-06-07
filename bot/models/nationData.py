from tortoise import fields
from tortoise.models import Model

class Nation(Model):
    name = fields.CharField(max_length=255, pk=True)
    player_updates_audience = fields.JSONField(null=True, default=[])
    town_updates_audience = fields.JSONField(null=True, default=[])
    embed_audience = fields.JSONField(null=True, default=[])
    citizens: fields.ReverseRelation["Citizen"]

    class Meta:
        table = "nations"

class Town(Model):
    name = fields.CharField(pk=True, max_length=255)
    nation: fields.ForeignKeyRelation[Nation] = fields.ForeignKeyField("models.Nation", related_name="towns")

    class Meta:
        table = "towns"

class Citizen(Model):
    name = fields.CharField(pk=True, max_length=255)
    nation: fields.ForeignKeyRelation[Nation] = fields.ForeignKeyField("models.Nation", related_name="citizens")

    class Meta:
        table = "citizens"