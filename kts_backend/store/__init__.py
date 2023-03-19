class Store:
    def __init__(self, *args, **kwargs):
        from kts_backend.game.accessor import UserAccessor

        self.user = UserAccessor(self)
