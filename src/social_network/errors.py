

class ApplicationError(Exception):

    def __init__(self, description, **kwargs):
        super().__init__(description)
        self.description = description
        self.__dict__.update(kwargs)

    def __str__(self):
        attributes = dir(self)
        content = ";\n".join([
            f"{attr}: {getattr(self, attr)}"
            for attr in attributes
            if (
                not attr.startswith("_") 
                and attr != "args" 
                and not callable(getattr(self, attr))
            )
        ])
        return f"{type(self)}:\n{content};\n"
