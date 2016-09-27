# RAML Codec

**A RAML codec for Core API.**

[![travis-image]][travis]
[![pypi-image]][pypi]

## Introduction

This is a Python [Core API][coreapi] codec for the [RAML][raml] schema format.

It currently supports RAML 0.8.

## Installation

Install using pip:

    $ pip install raml-codec

## Using with the Python Client Library

Install `coreapi` and the `raml-codec`.

    $ pip install coreapi
    $ pip install raml-codec

To use the Python client library to interact with a service that exposes a Swagger schema,
include the codec in [the `decoders` argument][decoders].

    >>> from raml_codec import RAMLCodec
    >>> from coreapi.codecs import JSONCodec
    >>> from coreapi import Client
    >>> decoders = [RAMLCodec(), JSONCodec()]
    >>> client = Client(decoders=decoders)

If the server exposes the schema without properly using an `application/raml+yaml` content type, then you'll need to make sure to include `format='raml'` on the initial request,
to force the correct codec to be used.

    >>> url = 'https://raw.githubusercontent.com/spotify/web-api/master/specifications/raml/api.raml'
    >>> schema = client.get(url, format='raml')

At this point you can now start to interact with the API:

    >>> client.action(schema, ['search-item'], params={'q': 'Deadmaus', 'type': 'artist'})

## Using with the Command Line Client

Once the `openapi-codec` package is installed, the codec will automatically become available to the command line client.

    $ pip install coreapi-cli
    $ pip install openapi-codec
    $ coreapi codecs show
    Codec name   Media type                 Support              Package
    corejson   | application/coreapi+json | encoding, decoding | coreapi==2.0.7
    openapi    | application/raml+yaml    | encoding, decoding | raml-codec==0.1.0
    json       | application/json         | decoding           | coreapi==2.0.7
    text       | text/*                   | decoding           | coreapi==2.0.7
    download   | */*                      | decoding           | coreapi==2.0.7

If the server exposes the schema without properly using an `application/raml+yaml` content type, then you'll need to make sure to include `format=raml` on the initial request, to force the correct codec to be used.

    $ coreapi get https://raw.githubusercontent.com/spotify/web-api/master/specifications/raml/api.raml --format raml
    <Spotify Web API "https://raw.githubusercontent.com/spotify/web-api/master/specifications/raml/api.raml">
        album(id, [market])
        album-tracks(id, [market], [limit], [offset])
        artist(id)
        artist-albums(id, [album_type], [market], [limit], [offset])
    ...

At this point you can start to interact with the API.

    coreapi action search-item --param q="Deadmaus" --param type=artist
    {
        "artists": {
            "href": "https://api.spotify.com/v1/search?query=Deadmaus&offset=0&limit=20&type=artist",
            "items": [
                {
                    "external_urls": {
                        "spotify": "https://open.spotify.com/artist/2CIMQHirSU0MQqyYHq0eOx"
                    },
                    "followers": {
                        "href": null,
                        "total": 1496502
                    },
                    "genres": [
                        "big room",
                        "breakbeat",
    ...

Use the `--debug` flag to see the full HTTP request and response.

    > GET /v1/search?q=Deadmaus&type=artist HTTP/1.1
    > Accept-Encoding: gzip, deflate
    > Connection: keep-alive
    > Accept: application/coreapi+json, application/vnd.coreapi+json, */*
    > Host: api.spotify.com
    > User-Agent: coreapi
    < 200 OK
    < Access-Control-Allow-Credentials: true
    < Access-Control-Allow-Headers: Accept, Authorization, Origin, Content-Type
    < Access-Control-Allow-Methods: GET, POST, OPTIONS, PUT, DELETE
    < Access-Control-Allow-Origin: *
    < Access-Control-Max-Age: 604800
    < Cache-Control: public, max-age=7200
    < Connection: keep-alive
    < Content-Encoding: gzip
    < Content-Type: application/json; charset=utf-8
    < Date: Tue, 27 Sep 2016 11:27:07 GMT
    < Keep-Alive: timeout=600
    < Server: nginx
    < Strict-Transport-Security: max-age=31536000;
    < Transfer-Encoding: chunked
    < X-Content-Type-Options: nosniff
    < 
    < {
    <   "artists" : {
    <     "href" : "https://api.spotify.com/v1/search?query=Deadmaus&offset=0&limit=20&type=artist",
    <     "items" : [ {
    ...


[travis-image]: https://secure.travis-ci.org/core-api/raml-codec.svg?branch=master
[travis]: http://travis-ci.org/core-api/raml-codec?branch=master
[pypi-image]: https://img.shields.io/pypi/v/raml-codec.svg
[pypi]: https://pypi.python.org/pypi/raml-codec

[coreapi]: http://www.coreapi.org/
[raml]: http://raml.org/
[decoders]: http://core-api.github.io/python-client/api-guide/client/#instantiating-a-client
