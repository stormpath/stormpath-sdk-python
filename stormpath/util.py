try:
    from urllib import parse
except ImportError:
    import urlparse as parse
    from urllib2 import quote as urllib2_quote
    parse.quote = urllib2_quote

def assert_not_none(p_object, message):
    if p_object is None:
        raise ValueError(message)

def assert_instance(p_object, class_or_type_or_tuple, parameter_name):
    if not isinstance(p_object, class_or_type_or_tuple):
        full_name = class_or_type_or_tuple.__module__ + "." + class_or_type_or_tuple.__name__
        raise TypeError("{} must be an instance of {}.".format(parameter_name, full_name))

def assert_subclass(C, B, parameter_name):
    if not issubclass(C, B):
        full_name = B.__module__ + "." + B.__name__
        raise TypeError("{} must be a subclass of {}.".format(parameter_name, full_name))

def assert_true(statement, message):
    if (not statement):
        raise ValueError(message)

def search_in_dict(dict_to_search, keys):

    result = None

    if isinstance(dict_to_search, dict) and keys:
        for key in keys:
            if key in dict_to_search:
                result = dict_to_search[key]
            elif isinstance(result, dict) and key in result:
                result = result[key]

    #only a 'primitive' value is accepted here
    if isinstance(result, dict) or not result:
        raise NestedValueNotFoundError()

    return result

def is_default_port(parsed_url):
    """
    Returns True if the specified URI uses a standard port (i.e. http == 80 or https == 443),
    False otherwise.

    :param parsed_url
    :returns True if the specified URI is using a non-standard port, False otherwise.
    """
    scheme = parsed_url.scheme.lower()
    port = parsed_url.port
    return not port or (port == 80 and scheme == 'http') or (port == 443 and scheme == 'https')

def encode_url(value, path = True, canonical = True):

    if not value:
        return ''

    encoded = parse.quote(value)

    if canonical:

        str_dict = {'+' : '%20', '*' : '%2A', '%7E' : '~'}

        for key, value in str_dict.items():

            if key in encoded:
                encoded = encoded.replace(key, value)

        if path:

            str = '%2F'
            encoded = encoded.replace(str, '/') if str in encoded else encoded

    return encoded

def str_query_string(query_string, canonical = True):

    result = ''

    if (query_string):

        for key, value in query_string.items():

            encoded_key = encode_url(key, False, canonical)
            encoded_value = encode_url(value, False, canonical)

            if result:

                result += '&'

            result += ''.join((encoded_key, '=', encoded_value))

    return result

class NestedValueNotFoundError(RuntimeError):
    pass
