from coreapi.compat import urlparse
from ramlfications.config import setup_config
from ramlfications.loader import RAMLLoader as RAMLFileLoader
from ramlfications.parser import parse_raml
import coreapi
import jsonref
import posixpath
import requests
import yaml


class RAMLLoader(RAMLFileLoader):
    """
    Extends ramlfications.RAMLLoader, but uses network fetchs to resolve
    any "!include" directives.
    """
    def __init__(self, base_url):
        self.session = requests.Session()
        self.base_url = base_url

    def _yaml_include(self, loader, node):
        url = urlparse.urljoin(self.base_url, node.value)
        path = urlparse.urlparse(url).path
        ext = posixpath.splitext(path)[1]

        response = requests.get(url)
        if ext in [".yaml", ".yml", ".raml"]:
            return yaml.load(response.content, self._ordered_loader)
        elif ext == '.json':
            return jsonref.loads(response.text, base_uri=self.base_url, jsonschema=True)
        return response.text


def get_dict(item, key):
    value = item.get(key, {})
    if not isinstance(value, dict):
        return {}
    return value


def get_list(item, key):
    value = item.get(key, [])
    if not isinstance(value, list):
        return []
    return value


def expand_schema(schema):
    """
    Expand the parameters of a type="object" schema into individual fields.
    """
    schema_type = schema.get('type')
    schema_properties = get_dict(schema, 'properties')
    schema_required = get_list(schema, 'required')

    if ((schema_type == ['object']) or (schema_type == 'object')) and schema_properties:
        # If the schema is type="object", then return a field for each parameter.
        fields = []
        for key in schema_properties.keys():
            fields.append(coreapi.Field(
                name=key,
                location='form',
                required=schema_properties.get('required', key in schema_required),
                description=schema_properties[key].get('description')
            ))
        return fields

    # If the schema is not type="object", then return a single field.
    return coreapi.Field(name='data', location='body', required=True)


def decode_raml(bytestring, base_url=None):
    loader = RAMLLoader(base_url)
    data = loader.load(bytestring)
    config = setup_config()
    config['validate'] = False
    raml = parse_raml(data, config)

    content = {}
    for resource in raml.resources:
        fields = []
        encoding = ''

        for param in resource.uri_params or []:
            field = coreapi.Field(param.name, param.required, location='path')
            fields.append(field)

        for param in resource.query_params or []:
            field = coreapi.Field(param.name, param.required, location='query')
            fields.append(field)

        if resource.body:
            body = resource.body[0]
            encoding = body.mime_type

            for form_param in body.form_params or []:
                field = coreapi.Field(param.name, param.required, location='form')
                fields.append(field)

            if body.schema:
                schema_fields = expand_schema(body.schema)
                fields.extend(schema_fields)

        link = coreapi.Link(
            url=resource.absolute_uri,
            action=resource.method.lower(),
            encoding=encoding,
            fields=fields
        )
        content[resource.display_name] = link

    return coreapi.Document(title=raml.title, url=base_url, content=content)
