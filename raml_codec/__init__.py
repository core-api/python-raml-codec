from coreapi.codecs import BaseCodec
from raml_codec.decode import decode_raml
from raml_codec.encode import encode_raml


__version__ = "0.1.2"


class RAMLCodec(BaseCodec):
    media_type = 'application/raml+yaml'
    format = 'raml'

    def decode(self, bytestring, **options):
        base_url = options.get('base_url', None)
        return decode_raml(bytestring, base_url)

    def encode(self, document, **options):
        base_url = options.get('base_url', None)
        return encode_raml(document, base_url)
