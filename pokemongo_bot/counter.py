class Pokemon(object):
    def __init__(self, name, cp):
        self.name = name
        self.cp = cp
        self.amount = 1

    def catched(self, cp):
        self.amount += 1
        if cp > self.cp:
            self.cp = cp

    def __repr__(self):
        return self.name


class Pokestop(object):
    def __init__(self, name):
        self.name = name
        self.amount = 1

    def visited(self):
        self.amount += 1

    def __repr__(self):
        return self.name


class Counter(object):
    """
    This class will count catched pokemons and visited pokestops.
    """
    pokemon = []
    pokestop = []

    @classmethod
    def catch_pokemon(cls, name, cp):
        for pokemon in cls.pokemon:
            if pokemon.name == name:
                pokemon.catched(cp)
                return
        cls.pokemon.append(Pokemon(name, cp))

    @classmethod
    def visit_pokestop(cls, name):
        for pokestop in cls.pokestop:
            if pokestop.name == name:
                pokestop.visited()
                return
        cls.pokestop.append(Pokestop(name))

    @classmethod
    def print_pokemon(cls):
        count = 0
        for pokemon in cls.pokemon:
            print('{pokemon.name}: amount: {pokemon.amount}, highest CP: {pokemon.cp}'.format(pokemon=pokemon))
            count += pokemon.amount
        print('Overall catched amount: {}'.format(count))

    @classmethod
    def print_pokestop(cls):
        count = 0
        for pokestop in cls.pokestop:
            print('{pokestop.name}: {pokestop.amount} times'.format(pokestop=pokestop))
            count += pokestop.amount
