#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from google.appengine.ext import ndb


sessionState = ["run", "stop"]

class Session(ndb.Model):
	externalId = ndb.IntegerProperty()
	account = ndb.StringProperty(default="")
	dataFlow = ndb.StringProperty(default="")
	state = ndb.StringProperty(default="stop", choices=sessionState)
	status = ndb.BooleanProperty(default=False)
	timeStart = ndb.DateTimeProperty()
	timeStop = ndb.DateTimeProperty()

class Order(ndb.Model):
	name = ndb.StringProperty(default="")
	sessions = ndb.KeyProperty(kind='Session', repeated=True)

class WorkOrder(ndb.Model):
	name = ndb.StringProperty(default="")
	sessions = ndb.KeyProperty(kind='Session', repeated=True)

class Card(ndb.Model):
	PAN = ndb.StringProperty(default="")
	lastName = ndb.StringProperty(default="")
	firstName = ndb.StringProperty(default="")
	order = ndb.KeyProperty(kind='Order')
	workOrder = ndb.KeyProperty(kind='WorkOrder')
	sessions = ndb.KeyProperty(kind='Session', repeated=True)

class ModuleStatus(ndb.Model):
	name = ndb.StringProperty(default="")
	status = ndb.StringProperty(default="")
	timeStart = ndb.DateTimeProperty()
	timeStop = ndb.DateTimeProperty()
	sessions = ndb.KeyProperty(kind='Session', repeated=True)




