from api.json_encodable import JSONEncodable


class Incubator(JSONEncodable):
    def __init__(self, data):
        self.unique_id = data.get("id", 0)
        self.item_id = data.get("item_id")
        self.incubator_type = data.get("incubator_type")
        self.uses_remaining = data.get("uses_remaining")
        self.pokemon_id = data.get("pokemon_id", 0)
        self.start_km_walked = data.get("start_km_walked", 0.0)
        self.target_km_walked = data.get("target_km_walked", 0.0)

    # below function are for jsonpickle,
    # because long field are not compatible with JSON and get rounded by browser
    def __getstate__(self):
        state = self.__dict__.copy()
        state["unique_id"] = str(self.unique_id)
        state["pokemon_id"] = str(self.pokemon_id)
        return state

    def __setstate__(self, state):
        state["unique_id"] = int(state["unique_id"])
        state["pokemon_id"] = int(state["pokemon_id"])
        self.__dict__.update(state)
