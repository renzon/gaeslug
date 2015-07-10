# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from gaebusiness.business import Command, CommandSequential, CommandParallel
from gaebusiness.gaeutil import SaveCommand, ModelSearchCommand, SingleModelSearchCommand
from gaeforms.ndb.form import ModelForm
from gaegraph.business_base import UpdateNode, CreateSingleArc, SingleDestinationSearch, NodeSearch, SingleOriginSearch
from slugify import slugify
from gaeslug.model import Slug, ToSlug
from webapp2_extras.i18n import gettext as _


def _slugfy(text):
    return slugify(text, max_length=500, word_boundary=True)  # limit from db


class SlugForm(ModelForm):
    """
    Form used do save and update operations
    """
    _model_class = Slug
    _include = [Slug.name]


class SlugFormDetail(ModelForm):
    """
    Form used to show entity details
    """
    _model_class = Slug
    _include = [Slug.creation,
                Slug.name]


class SlugFormShort(ModelForm):
    """
    Form used to show entity short version, mainly for tables
    """
    _model_class = Slug
    _include = [Slug.creation,
                Slug.name]


class Tip(Command):
    """
    Command to return a valid slug tip based on string
    """

    def __init__(self, text, max_attempts=20):
        super(Tip, self).__init__()
        self.max_attempts = max_attempts
        self.text = text

    def do_business(self):
        cmd = FindSlug(self.text)

        for i in xrange(2, self.max_attempts + 1):
            model = cmd()
            if model is None:
                self.result = cmd.slug
                return
            cmd = FindSlug(self.text + ('-%s' % i))
        self.add_error('name', _('It was impossible generate a slug'))


class FindSlug(SingleModelSearchCommand):
    def __init__(self, slug):
        self.slug = _slugfy(slug)
        super(FindSlug, self).__init__(Slug.query_by_slug(self.slug))


class FindSlugBySlugNameOrId(CommandParallel):
    def __init__(self, slug_or_id):
        try:
            cmd = NodeSearch(slug_or_id)
        except:
            cmd = FindSlug(slug_or_id)
        super(FindSlugBySlugNameOrId, self).__init__(cmd)


class FindSlugOrigin(SingleOriginSearch):
    arc_class = ToSlug


class FindObjBySlug(FindSlug):
    def do_business(self, stop_on_error=True):
        super(FindObjBySlug, self).do_business(stop_on_error)
        if self.result:
            cmd = FindSlugOrigin(self.result)
            self.result = cmd()


class NaiveSaveSlugCommand(SaveCommand):
    _model_form_class = SlugForm

    def handle_previous(self, command):
        self.form.name = command.result


class CreateToSlug(CreateSingleArc):
    arc_class = ToSlug


class SaveSlugCommand(CommandSequential):
    def __init__(self, name, origin):
        tip = Tip(name)
        naive = NaiveSaveSlugCommand()
        create_arc = CreateToSlug(origin, naive)
        super(SaveSlugCommand, self).__init__(tip, create_arc)


class FindSlugFromObject(SingleDestinationSearch):
    arc_class = ToSlug

class FindSlugStringFromObject(FindSlugFromObject):
    def do_business(self):
        super(FindSlugStringFromObject, self).do_business()
        self.result = self.result and self.result.name


class FindObjBySlugOrIdUnsecure(CommandParallel):
    def __init__(self, slug_or_id):
        try:
            cmd = NodeSearch(slug_or_id)
        except:
            cmd = FindObjBySlug(slug_or_id)
        super(FindObjBySlugOrIdUnsecure, self).__init__(cmd)


class FindObjBySlugOrId(FindObjBySlugOrIdUnsecure):
    def __init__(self, slug_or_id, expected_obj_class):
        super(FindObjBySlugOrId, self).__init__(slug_or_id)
        self.expected_obj_class = expected_obj_class

    def do_business(self):
        super(FindObjBySlugOrId, self).do_business()
        if self.result and not isinstance(self.result, self.expected_obj_class):
            error_msg = 'someone trying to reach object %s, but expected class is %s' % (self.result,
                                                                                         self.expected_obj_class)
            self.add_error('security', error_msg)


class NaiveUpdateSlugCommand(UpdateNode):
    _model_form_class = SlugForm

    def handle_previous(self, command):
        self.form.name = command.result


class UpdateSlugCommand(CommandSequential):
    def __init__(self, model_key, name, **form_parameters):
        super(UpdateSlugCommand, self).__init__(Tip(name), NaiveUpdateSlugCommand(model_key, **form_parameters))


class ListSlugCommand(ModelSearchCommand):
    def __init__(self, page_size=100, start_cursor=None, offset=0, use_cache=True, cache_begin=True, **kwargs):
        super(ListSlugCommand, self).__init__(Slug.query_by_creation(), page_size, start_cursor, offset, use_cache,
                                              cache_begin, **kwargs)

