from marshmallow import Schema, fields


class QuestionSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)
    answer = fields.Str(required=True)


class QuestionListSchema(Schema):
    questions = fields.Nested("QuestionSchema", many=True)


class GameSchema(Schema):
    id = fields.Int(required=False)
    created_at = fields.DateTime(required=False)
    chat_id = fields.Int(required=True)
    is_active = fields.Bool(required=False)
    question_id = fields.Int(required=True)
    creator_id = fields.Int(required=False)
    players = fields.Nested("PlayerSchema", many=True, required=False)


class GameGetSchema(Schema):
    game_id = fields.Int(required=True)


class PlayerSchema(Schema):
    tg_id = fields.Int(required=True)
    username = fields.Str(required=True)
    first_name = fields.Str(required=True)
    second_name = fields.Str(required=False)


class PlayerAddSchema(Schema):
    game_id = fields.Int(required=True)
    player_id = fields.Int(required=True)
    player_username = fields.Str(required=True)
    player_firstname = fields.Str(required=True)
    player_secondname = fields.Str(required=False)
