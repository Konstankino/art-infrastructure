import os
import os.path
from PIL import Image
import urllib
import datetime, calendar
import random
import time
import re
import feedparser
import unicodedata
import traceback
import logging
import pprint

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.files import File
from django.db import models
from django.db.models import signals
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.dispatch import dispatcher
from django.core.mail import send_mail
from django.utils.encoding import force_unicode
from django.db.models import Q
from django.db.models.fields.files import ImageFieldFile
from django.core.urlresolvers import reverse

from front.models import EventModel
from pjlink import PJLinkController

class BACNetLight(models.Model):
	"""A lighting fixture which is controlled using the BACNet protocols.
	In BACNet speak: we're reading and writing Present-Value on Analog Outputs which range in value from 0 to 100."""
	name = models.CharField(max_length=1024, null=False, blank=False)
	device_id = models.PositiveIntegerField(null=False, blank=False, default=0)
	property_id = models.PositiveIntegerField(null=False, blank=False, default=0)
	@models.permalink
	def get_absolute_url(self): return ('lighting.views.bacnet_light', (), { 'id':self.id })
	def __unicode__(self): return '%s' % self.name
	class Meta:
		ordering = ['name']
		verbose_name = "BACNet Light"
		verbose_name_plural = "BACNet Lights"
	class HydrationMeta:
		attributes = ['id', 'name', 'device_id', 'property_id']

class Projector(models.Model):
	"""A light projection system which is controlled via the net."""
	name = models.CharField(max_length=1024, null=False, blank=False)
	pjlink_host = models.CharField(max_length=1024, null=False, blank=False)
	pjlink_port = models.IntegerField(null=False, blank=False, default=4352)
	pjlink_password = models.CharField(max_length=512, blank=True, null=True)
	@models.permalink
	def get_absolute_url(self): return ('lighting.views.projector', (), { 'id':self.id })
	def __unicode__(self): return '%s' % self.name
	class Meta:
		ordering = ['name']
	class HydrationMeta:
		attributes = ['id', 'name', 'pjlink_host', 'pjlink_port']

class ProjectorEvent(EventModel):
	COMMAND_CHOICES = (('on', 'Turn On'), ('off', 'Turn Off'))
	command = models.CharField(max_length=12, blank=False, null=False, choices=COMMAND_CHOICES, default='off')
	device = models.ForeignKey(Projector, blank=False, null=False)

	def execute(self):
		print 'running ', self
		try:
			controller = PJLinkController(host=self.device.pjlink_host, port=self.device.pjlink_port, password=self.device.pjlink_password)
			if self.command == 'on':
				controller.power_on()
			elif self.command == 'off':
				controller.power_off()
			else:
				self.tries = self.tries + 1
				self.save()
				return False
			print 'ran command', self.command
		except:
			traceback.print_exc()
			self.tries = self.tries + 1
			self.save()
			return False
			
		self.last_run = datetime.datetime.now()
		self.tries = 1
		self.save()
		return True

	def __unicode__(self): return 'Projector Event: [%s],[%s],[%s]' % (self.days, self.hours, self.minutes)
