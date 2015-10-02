"""Stormpath AccountStore resource mappings."""


def AccountStore(client, properties=None):
    """AccountStore resource factory.

    Returns either a Group or a Directory or an Organization resource,
    based on the resource href.
    """
    from .directory import Directory
    from .group import Group
    from .organization import Organization

    if not properties or 'href' not in properties:
        raise ValueError('AccountStore called without resource href')

    href = properties['href']

    if href.startswith(client.BASE_URL):
        href = href[len(client.BASE_URL):]

    if href.startswith('/directories'):
        return Directory(client, properties=properties)
    elif href.startswith('/groups'):
        return Group(client, properties=properties)
    elif href.startswith('/organizations'):
        return Organization(client, properties=properties)
    else:
        raise ValueError('AccountStore called for non-account store href %s' %
            href)
