from djantic import ModelSchema
from .models import ParliamentSession


class ParliamentSessionSchema(ModelSchema):
    class Config:
        model = ParliamentSession
        include = "__all__"