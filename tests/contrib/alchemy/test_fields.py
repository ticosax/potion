from flask_sqlalchemy import SQLAlchemy

from flask_potion import Api, fields
from flask_potion.resource import ModelResource
from flask_potion.contrib.alchemy.fields import ToOne as SAToOne
from tests import BaseTestCase, DBQueryCounter


class SQLAlchemyToOneRemainNoPrefetchTestCase(BaseTestCase):
    """
    """

    def setUp(self):
        super(SQLAlchemyToOneRemainNoPrefetchTestCase, self).setUp()
        self.app.config['SQLALCHEMY_ENGINE'] = 'sqlite://'
        self.api = Api(self.app)
        self.sa = sa = SQLAlchemy(
            self.app, session_options={"autoflush": False})

        class Type(sa.Model):
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.String(60), nullable=False)

        class Machine(sa.Model):
            id = sa.Column(sa.Integer, primary_key=True)
            name = sa.Column(sa.String(60), nullable=False)

            type_id = sa.Column(sa.Integer, sa.ForeignKey(Type.id))
            type = sa.relationship(Type, foreign_keys=[type_id])

        sa.create_all()

        class MachineResource(ModelResource):
            class Meta:
                model = Machine

            class Schema:
                type = SAToOne('type')

        class TypeResource(ModelResource):
            class Meta:
                model = Type

        self.MachineResource = MachineResource
        self.TypeResource = TypeResource

        self.api.add_resource(MachineResource)
        self.api.add_resource(TypeResource)

    def test_relation_serialization_does_not_load_remote_object(self):
        response = self.client.post('/type', data={"name": "aaa"})
        aaa_uri = response.json["$uri"]
        self.client.post(
            '/machine', data={"name": "foo", "type": {"$ref": aaa_uri}})
        with DBQueryCounter(self.sa.session) as counter:
            response = self.client.get('/machine')
            self.assert200(response)
            self.assertJSONEqual(
                [{'$uri': '/machine/1', 'type': {'$ref': aaa_uri}, 'name': 'foo'}],
                response.json)
        counter.assert_count(1)

