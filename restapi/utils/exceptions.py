class CustomException(Exception):
    """
    @attributes
    message: contains cause/reason/solution regarding the exception
    """

    def __init__(self, message="Shit happened"):
        self.message = message
        super().__init__(self.message)
