import os
import yaml


def get_links(node, keys=()):
    """
    Return a dict of {keys: link} containing each link in the document.
    """
    links = {}
    for key, link in getattr(node, 'links', {}).items():
        index = keys + (key,)
        links[index] = link
    for key, data in getattr(node, 'data', {}).items():
        index = keys + (key,)
        links.update(get_links(data, index))
    return links


def get_url_to_links_mapping(links):
    """
    Given a dict of {keys: link} containing each link in the document.
    Return a dict of {url: [(keys, link), ...]}
    """
    urls = {}
    for keys, link in links.items():
        if link.url not in urls:
            urls[link.url] = []
        urls[link.url].append((keys, link))
    return urls


def get_path_components(urls):
    """
    Return a list of path component lists, giving a tree structure
    for the given list of urls.

    For example,
    ['/users', '/users/{pk}', '/groups', '/groups/{pk}']

    ==>

    [
        ['/users'],
        ['/users', '/{pk}'],
        ['/groups'],
        ['/groups', '/{pk}'],
    ]
    """
    ret = []
    parents = ['']

    for url in sorted(set(urls)):
        while parents:
            parent_url = ''.join(parents)
            if url.startswith(parent_url):
                component = url[len(parent_url):]
                parents.append(component)
                ret.append(parents[1:])
                break
            parents.pop()

    return ret


def get_resource(keys, link):
    display_name = '_'.join(keys)
    return {
        'displayName': display_name,
        'description': link.description
    }


def encode_raml(document):
    links = get_links(document)
    urls = [link.url for link in links.values()]
    urls_to_links = get_url_to_links_mapping(links)

    for components in get_path_components(urls):
        url = ''.join(components)
        links = urls_to_links[url]
        for keys, link in links:
            index = ['/' + component.lstrip('/') for component in components]
            index.append(link.action)
            print index, get_resource(keys, link)

        ##print components, [link.action for keys, link in urls_to_links[url]]

    structure = {
        'title': document.title,
        'baseUri': document.url,
    }
    return yaml.safe_dump(structure, default_flow_style=False)
