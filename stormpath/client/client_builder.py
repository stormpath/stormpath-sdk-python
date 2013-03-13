__author__ = 'ecrisostomo'

class ClientBuilder:

    def __init__(self):
        self.api_key_id_property_name = "apiKey.id"
        self.api_key_secret_property_name = "apiKey.secret"
        self.api_key_properties, self.api_key_file, self.api_key_file_location, self.base_url = None, None, None, None

    def set_api_key_properties(self, properties):
        self.api_key_properties = properties
        return self

    def set_api_key_file(self, file):
        if not hasattr(file, 'readline'):
            raise ValueError("file argument must be a File object")
        self.api_key_file = file
        return self

    def set_api_key_file_location(self, location):
        self.api_key_file_location = location
        return self

    def set_api_key_id_property_name(self, *api_key_id_property_name):
        self.api_key_id_property_name = api_key_id_property_name
        return self

    def set_api_key_secret_property_name(self, *api_key_secret_property_name):
        self.api_key_secret_property_name = api_key_secret_property_name
        return self

    def set_base_url(self, base_url):
        self.base_url = base_url
        return self

    def build(self):
        pass #TODO: implement


