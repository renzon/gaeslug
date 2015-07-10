# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from gaebusiness.business import CommandExecutionException
from gaegraph.model import Node
from google.appengine.ext import ndb
from mommygae import mommy
from base import GAETestCase
from gaeslug.commands import FindSlug, Tip, SaveSlugCommand, FindObjBySlugOrIdUnsecure, UpdateSlugCommand, \
    FindObjBySlugOrId, FindSlugFromObject
from gaeslug.model import Slug


def flood_slugs():
    def slugs():
        yield 'appengine-fundamental'
        for i in xrange(2, 20):
            yield 'appengine-fundamental-%s' % i

    ndb.put_multi([Slug(name=s) for s in slugs()])


class TipTests(GAETestCase):
    def test_success(self):
        cmd = Tip('Appengine Fundamental')
        self.assertEqual('appengine-fundamental', cmd())
        Slug(name='appengine-fundamental').put()
        self.assertEqual('appengine-fundamental-2', cmd())
        Slug(name='appengine-fundamental-2').put()
        self.assertEqual('appengine-fundamental-3', cmd())

        Slug(name='appengine-fundamental-3').put()
        self.assertEqual('appengine-fundamental-4', cmd())

    def test_max_attempts_error(self):
        flood_slugs()
        self.assertRaises(CommandExecutionException, Tip('Appengine Fundamental'))


class SaveSlugTests(GAETestCase):
    def test_error_null_destination(self):
        cmd = SaveSlugCommand('Appengine Fundamental', '')
        self.assertRaises(CommandExecutionException, cmd)

    def test_success(self):
        node = mommy.save_one(Node)
        arc = SaveSlugCommand('Appengine Fundamental', node)()
        self.assertEqual(node, arc.origin.get())
        self.assertEqual(FindSlug('Appengine Fundamental')(), arc.destination.get())


class UpdateSlugsTests(GAETestCase):
    def test_update(self):
        node = mommy.save_one(Node)
        SaveSlugCommand('Appengine Fundamental', node)()
        slug = FindSlug('Appengine Fundamental')()
        UpdateSlugCommand(slug, 'Appengine')()
        self.assertEqual(node, FindObjBySlugOrIdUnsecure('appengine')())
        SaveSlugCommand('Appengine Fundamental', node)()
        UpdateSlugCommand(slug, 'Appengine Fundamental')()
        self.assertEqual(node, FindObjBySlugOrIdUnsecure('appengine-fundamental-2')())


class FindSlugFromObjectTests(GAETestCase):
    def test_existing_obj(self):
        node = mommy.save_one(Node)
        save_command = SaveSlugCommand('Appengine Fundamental', node)
        save_command()
        cmd=FindSlugFromObject(node)
        self.assertEqual(Slug.query().get(), cmd())


class FindBySlugOrIdUnsecureTests(GAETestCase):
    def test_find_by_id(self):
        node = mommy.save_one(Node)
        SaveSlugCommand('Appengine Fundamental', node)()
        cmd = FindObjBySlugOrIdUnsecure(node)
        self.assertEqual(node, cmd())

    def test_not_existing_id(self):
        cmd = FindObjBySlugOrIdUnsecure('1')
        self.assertIsNone(cmd())

    def test_find_by_slug(self):
        node = mommy.save_one(Node)
        SaveSlugCommand('Appengine Fundamental', node)()
        cmd = FindObjBySlugOrIdUnsecure('Appengine Fundamental')
        self.assertEqual(node, cmd())

    def test_not_existing_slug(self):
        cmd = FindObjBySlugOrIdUnsecure('not-existing')
        self.assertIsNone(cmd())


class ProtectedEntity(Node):
    pass


class FindBySlugOrIdTests(GAETestCase):
    def test_find_by_id(self):
        node = mommy.save_one(ProtectedEntity)
        SaveSlugCommand('Appengine Fundamental', node)()
        cmd = FindObjBySlugOrId(node, ProtectedEntity)
        self.assertEqual(node, cmd())

    def test_hack_for_retrienving_protected_obj(self):
        class UnprotectedEntity(Node):
            pass

        protected = mommy.save_one(ProtectedEntity)
        SaveSlugCommand('Appengine Fundamental', protected)()

        cmd = FindObjBySlugOrId(protected, UnprotectedEntity)
        self.assertRaises(CommandExecutionException, cmd)

    def test_not_existing_id(self):
        cmd = FindObjBySlugOrId('1', ProtectedEntity)
        self.assertIsNone(cmd())

    def test_find_by_slug(self):
        node = mommy.save_one(ProtectedEntity)
        SaveSlugCommand('Appengine Fundamental', node)()
        cmd = FindObjBySlugOrId('Appengine Fundamental', ProtectedEntity)
        self.assertEqual(node, cmd())

    def test_not_existing_slug(self):
        cmd = FindObjBySlugOrId('not-existing', ProtectedEntity)
        self.assertIsNone(cmd())


class FindSlugTests(GAETestCase):
    def test_success(self):
        cmd = FindSlug('appengine-fundamental')
        self.assertIsNone(cmd())
        slug = Slug(name='appengine-fundamental')
        slug.put()
        self.assertEqual(slug, cmd())
        self.assertEqual(slug, FindSlug('Appengine Fundamental')())
        self.assertEqual(slug, FindSlug('APPENGINE FUNDAMENTAL')())


