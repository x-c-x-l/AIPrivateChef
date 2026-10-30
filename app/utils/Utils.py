import uuid


class Utils:
    @classmethod
    def getUUId(cls):
        return str(uuid.uuid4())