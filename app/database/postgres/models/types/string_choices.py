import sqlalchemy.types as types


class StringChoiceType(types.TypeDecorator):

    impl = types.String

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(StringChoiceType, self).__init__(**kw)

    def process_bind_param(self, value: str, dialect):
        for k, v in self.choices.items():
            if v == value:
                return k
        raise Exception(f"Value {value} not in choices")

    def process_result_value(self, value: str, dialect):
        return self.choices[value]
