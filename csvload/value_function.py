class Environment:
    def __init__(self, args: dict):
        self.args = args

    def get_arg(self, arg: str):
        return self.args.get(arg)

    def create_lambda_from_annotation(self, annotation: str, field: str):
        def get_field():
            return field

        return eval(
            "lambda row: " + annotation, {}, {"auto": get_field, "arg": self.get_arg}
        )
