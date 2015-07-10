# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from google.appengine.ext import ndb
from gaegraph.model import Node, Arc


class Slug(Node):
    name = ndb.StringProperty(required=True)

    @classmethod
    def query_by_slug(cls, slug):
        return cls.query(cls.name == slug)


class ToSlug(Arc):
    pass

