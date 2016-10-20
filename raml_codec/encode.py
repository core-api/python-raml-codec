import yaml


def get_resources(node, keys=()):
    """
    Return a dict of {url: resource}.
    """
    resources = {}
    for key, link in getattr(node, 'links', {}).items():
        # Get all the resources at this level
        index = keys + (key,)
        if link.url not in resources:
            resources[link.url] = {}
        resources[link.url][link.action] = get_resource(index, link)
    for key, data in getattr(node, 'data', {}).items():
        # Descend into any nested structures.
        index = keys + (key,)
        resources.update(get_resources(data, index))
    return resources


def get_params(fields):
    return {
        field.name: {
            'description': field.description,
            'type': field.type,
            'required': field.required
        } for field in fields
    }


def get_resource(keys, link):
    ret = {
        'description': link.description
    }

    query_fields = [field for field in link.fields if field.location == 'query']
    form_fields = [field for field in link.fields if field.location == 'form']

    # path fields are awkward to handle, because of the way RAML collates
    # them into particular sections.

    # We also need to handle mapping application/json form fields and body
    # fields into a JSON schema representation.

    if query_fields:
        ret['queryParameters'] = get_params(query_fields)
    if form_fields and link.encoding in ('multipart/form-data', 'application/x-www-form-urlencoded'):
        ret['body'] = {
            link.encoding: {
                'formParameters': get_params(form_fields)
            }
        }
    return ret


def insert_into(target, keys, value):
    """
    Nested dictionary insertion.

    >>> example = {}
    >>> insert_into(example, ['a', 'b', 'c'], 123)
    >>> example
    {'a': {'b': {'c': 123}}}
    """
    for key in keys[:-1]:
        if key not in target:
            target[key] = {}
        target = target[key]
    target[keys[-1]] = value


def layout_resources(resources):
    """
    Transform a URL-dict of resources into a RAML layout of resources.

    {
        '/users': {'get': ...},
        '/users/{pk}': {'get': ..., 'delete': ...},
        '/groups': {'get': ...},
    ]

    ==>

    {
        '/users': {
            'get': ...
            '/{pk}': {
                'get': ...
                'delete': ...
        '/groups': {
            'get': ...
        }
    ]
    """
    output = {}
    parents = ['']

    items = sorted(resources.items(), key=lambda item: item[0])
    for url, resource in items:
        while parents:
            parent_url = ''.join(parents)
            if url.startswith(parent_url):
                component = '/' + url[len(parent_url):].strip('/')
                parents.append(component)
                insert_into(output, parents[1:], resource)
                break
            parents.pop()

    return output


def encode_raml(document, base_url):
    resources = get_resources(document)
    resources = layout_resources(resources)
    structure = {
        'title': document.title,
        'baseUri': base_url or document.url,
    }
    structure.update(resources)
    output = '#%RAML 0.8\n'
    output += yaml.safe_dump(structure, default_flow_style=False)
    return output
