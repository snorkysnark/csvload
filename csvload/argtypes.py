import argparse


class keyvalue(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, {})

        if values:
            for value in list(values):
                # split it into key and value
                key, value = value.split("=")
                # assign into dictionary
                getattr(namespace, self.dest)[key] = value
