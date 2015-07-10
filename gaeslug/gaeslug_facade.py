# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from gaegraph.business_base import NodeSearch, DeleteNode
from slug_app.commands import SaveSlugCommand, SlugFormDetail, UpdateSlugCommand, SlugFormShort, ListSlugCommand, Tip, \
    FindSlugBySlugNameOrId, FindSlugFromObject, FindObjBySlugOrIdUnsecure, FindObjBySlugOrId, FindSlugStringFromObject


def save_slug_cmd(name=None, destination=None, **slug_properties):
    """
    Command to save Slug entity
    :param slug_properties: a dict of properties to save on model
    :param destination: destination Node or a Command that saves a Node
    :return: a Command that save Slug, validating and localizing properties received as strings
    """
    return SaveSlugCommand(name, destination, **slug_properties)


def update_slug_cmd(slug_id, **slug_properties):
    """
    Command to update Slug entity with id equals 'slug_id'
    :param slug_properties: a dict of properties to update model
    :return: a Command that update Slug, validating and localizing properties received as strings
    """
    return UpdateSlugCommand(slug_id, **slug_properties)


def list_slugs_cmd():
    """
    Command to list Slug entities ordered by their creation dates
    :return: a Command proceed the db operations when executed
    """
    return ListSlugCommand()


_detail_slug_form = SlugFormDetail()


def detail_slug_dct(slug):
    """
    Function to localize Slug's detail properties.
    :param slug: model Slug
    :return: dictionary with Slug's detail properties localized
    """
    return _detail_slug_form.fill_with_model(slug)


_short_slug_form = SlugFormShort()


def short_slug_dct(slug):
    """
    Function to localize Slug's short properties. Common used to show data in tables.
    :param slug: model Slug
    :return: dictionary with Slug's short properties localized
    """
    return _short_slug_form.fill_with_model(slug)


def get_slug_from_obj(obj):
    """
    Find slug by the obj it refers to
    :param obj: the refered obj
    :return: Command
    """
    return FindSlugFromObject(obj)

def get_slug_str_from_obj(obj):
    """
    Find slug by the obj it refers to and returns its name
    :param obj: the refered obj
    :return: Command
    """
    return FindSlugStringFromObject(obj)


def get_obj_from_id_or_slug(id_or_slug, expected_obj_class):
    """
    Find a object given its id or slug. If object is not from expected_obj_class, raises CommandExecutionException
    @param id_or_slug: id or slug of the object
    @param expected_obj_class: expected object's class
    @return: Command to get the object
    """
    return FindObjBySlugOrId(id_or_slug, expected_obj_class)


def get_slug_cmd(slug_id_or_name):
    """
    Find slug by its id
    :param slug_id_or_name: the slug id
    :return: Command
    """
    return FindSlugBySlugNameOrId(slug_id_or_name)


def delete_slug_cmd(slug_id):
    """
    Construct a command to delete a Slug
    :param slug_id: slug's id
    :return: Command
    """
    return DeleteNode(slug_id)


def tip_cmd(slug):
    """
    Returns a command to calculate a tip for the slug
    @param slug: the base text to calculate slug
    @return: a Command
    """
    return Tip(slug)