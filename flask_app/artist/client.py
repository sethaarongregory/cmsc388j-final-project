
class Artist(object):
    def __init__(self, name, desc, birth_date, birth_place):
        self.name = name
        self.desc = desc
        self.birth_date = birth_date
        self.birth_place = birth_place


class ArtistClient(object):
    def __init__(self, table):
        self.table = table

    def search(self, search_string):
        search_strings = search_string.split()

        results = []
        exact_match = False

        for idx, row in self.table.iterrows():
            name = str(row['name'])
            t = False
            if search_string.lower() == name.lower():
                t = True
                exact_match = True
            else:
                for s in search_strings:
                    if s.lower() in name.lower():
                        t = True
            if t:
                desc = row['description']
                birth_date = str(row['birthDate'])
                birth_place = str(row['birthPlaceName'])
                artist = Artist(name, desc, birth_date, birth_place)
                if exact_match:
                    results = [artist]
                    break
                else:
                    results.append(artist)

        if not results:
            raise ValueError("No results found")

        return results

    def retrieve_artist_by_name(self, name):
        for idx, row in self.table.iterrows():
            if str(row['name']) == name:
                desc = row['description']
                birth_date = int(row['birthDate'])
                birth_place = str(row['birthPlaceName'])
                artist = Artist(name, desc, birth_date, birth_place)
                return artist

        raise ValueError("Error retrieving results")



