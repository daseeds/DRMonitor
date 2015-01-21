#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import urllib
import logging
import webapp2
import datetime
import random
from  models import *

from webapp2_extras.routes import RedirectRoute
from webapp2_extras import jinja2

#from models import Locale, Page, Menu, Picture
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import mail
from google.appengine.api import memcache

HTTP_DATE_FMT = "%a, %d %b %Y %H:%M:%S GMT"

def jinja2_factory(app):
	j = jinja2.Jinja2(app)
	j.environment.filters.update({
        #'naturaldelta':naturaldelta,
        })
	j.environment.globals.update({
        # 'Post': Post,
        #'ndb': ndb, # could be used for ndb.OR in templates
        })
	return j

class BaseHandler(webapp2.RequestHandler):
	@webapp2.cached_property
	def jinja2(self):
	# Returns a Jinja2 renderer cached in the app registry.
		return jinja2.get_jinja2(factory=jinja2_factory)

	def render_response(self, _template, **context):
		# Renders a template and writes the result to the response.
		rv = self.jinja2.render_template(_template, **context)
		self.response.write(rv)
	# def handle_exception(self, exception, debug):
	# 	# Log the error.
	# 	logging.exception(exception)
	# 	# Set a custom message.
	# 	self.response.write("An error occurred.")
	# 	# If the exception is a HTTPException, use its error code.
	# 	# Otherwise use a generic 500 error code.
	# 	if isinstance(exception, webapp2.HTTPException):
	# 		self.response.set_status(exception.code)
	# 	else:
	# 		self.response.set_status(500)
	def render_error(self, message):
		logging.exception("Error 500: {0}".format(message))
		self.response.write("Error 500: {0}".format(message))
		return self.response.set_status(500)



class MainPage(BaseHandler):
   	def get(self):


		self.redirect('/dashboard')

class Dashboard(BaseHandler):
   	def get(self):

   		sessionsRunning = Session.query(Session.state=="run").fetch()
   		sessionsFinished = Session.query(Session.state=="stop").fetch()

   		for session in sessionsRunning:
   			moduleStatuses = ModuleStatus.query(ModuleStatus.sessions == session.key).count_async()
   			orders = Order.query(Order.sessions == session.key).count_async()
   			workOrders = WorkOrder.query(WorkOrder.sessions == session.key).count_async()
   			cards = Card.query(Card.sessions == session.key).count_async()

   		for session in sessionsFinished:
   			moduleStatuses = ModuleStatus.query(ModuleStatus.sessions == session.key).count_async()
   			orders = Order.query(Order.sessions == session.key).count_async()
   			workOrders = WorkOrder.query(WorkOrder.sessions == session.key).count_async()
   			cards = Card.query(Card.sessions == session.key).count_async()

		for session in sessionsRunning:
   			session.moduleStatuses = moduleStatuses.get_result()
   			session.orders = orders.get_result()
   			session.workOrders = workOrders.get_result()
   			session.cards = cards.get_result()

		for session in sessionsFinished:
   			session.moduleStatuses = moduleStatuses.get_result()
   			session.orders = orders.get_result()
   			session.workOrders = workOrders.get_result()
   			session.cards = cards.get_result()

   		template_values = {
			'sessionsRunning': sessionsRunning,
			'sessionsFinished': sessionsFinished,
		}
		return self.render_response('dashboard.html', **template_values)

class SessionPage(BaseHandler):
   	def get(self, session_id):

   		session = self.get_session_by_id(session_id)
   		orders_futur = Order.query(Order.sessions == session.key).fetch_async()
   		workOrders_futur = WorkOrder.query(WorkOrder.sessions == session.key).fetch_async()
   		cards_futur = Card.query(Card.sessions == session.key).count_async()
   		modules_futur = ModuleStatus.query(ModuleStatus.sessions == session.key).fetch_async()

   		orders = orders_futur.get_result()
   		for order in orders:
   			order.cards = Card.query(Card.order == order.key).count()

		workOrders = workOrders_futur.get_result()
   		for workorder in workOrders:
   			workorder.cards = Card.query(Card.workOrder == workorder.key).count()

   		cards = cards_futur.get_result()
   		modules = modules_futur.get_result()

   		template_values = {
			'session': session,
			'orders': orders,
			'workOrders': workOrders,
			'cards': cards,
			'modules': modules,
		}
		return self.render_response('session.html', **template_values)

	def get_session_by_id(self, session_id):
		session = memcache.get("{0}".format(session_id))
		if session is None:
			session = Session.get_by_id(int(session_id))
			memcache.set(key="{0}".format(session_id), value=session)
		return session		

class OrderPage(BaseHandler):
	def get(self, order_id):

		order = Order.get_by_id(int(order_id))
		cards = Card.query(Card.order == order.key).fetch()

   		template_values = {
			'order': order,
			'cards': cards,
		}
		return self.render_response('order.html', **template_values)

class fillDB(BaseHandler):
   	def get(self):

   		ndb.delete_multi(ndb.Query(default_options=ndb.QueryOptions(keys_only=True)))

   		for x in range(0, 10):
			session=Session()
			session.account="NATIXIS"
			session.dataFlow="CNCE CARD"
			state = random.randint(1, 2)
			if state == 1:
				session.state="run"
			else:
				session.state="stop"
			state = random.randint(1, 2)
			if state == 1:
				session.status=True
			else:
				session.status=False
			session.put() 

			# Modules
			module = ModuleStatus(
				name='Import',
				status="00",
				timeStart=datetime.datetime.now(),
				timeStop=datetime.datetime.now()
				)
			module.sessions.append(ndb.Key(Session, session.key.id()))
			module.put()
			module = ModuleStatus(
				name='Batching',
				status="00",
				timeStart=datetime.datetime.now(),
				timeStop=datetime.datetime.now()
				)
			module.sessions.append(ndb.Key(Session, session.key.id()))
			module.put()
			module = ModuleStatus(
				name='DataGen',
				status="00",
				timeStart=datetime.datetime.now(),
				timeStop=datetime.datetime.now()
				)
			module.sessions.append(ndb.Key(Session, session.key.id()))
			module.put()
			order = Order()
			order.sessions.append(ndb.Key(Session, session.key.id()))
			order.put()


			#session.orders.append(ndb.Key(Order, order.key.id()))

   			for y in range (0, random.randint(6, 15)):
   				workOrder = WorkOrder()
   				workOrder.sessions.append(ndb.Key(Session, session.key.id()))
   				workOrder.put()

      				# session.workOrders.append(ndb.Key(WorkOrder, workOrder.key.id()))				

   				for z in range (0, random.randint(5, 40)):
   					card = Card()
   					card.PAN = "1234123412341234"
   					card.firstName = "John"
   					card.lastName = "Difool"
   					card.sessions.append(ndb.Key(Session, session.key.id()))
   					card.order = ndb.Key(Order, order.key.id())
   					card.workOrder = ndb.Key(WorkOrder, workOrder.key.id())
   					card.put()
   					#session.cards.append(ndb.Key(Card, card.key.id()))
   					


   			

		self.redirect('/dashboard')




application = webapp2.WSGIApplication([
    webapp2.Route(r'/', MainPage),
    webapp2.Route(r'/dashboard', Dashboard),
    webapp2.Route(r'/fillDB', fillDB),
    webapp2.Route(r'/session/<session_id:([^/]+)?>', SessionPage),
    webapp2.Route(r'/order/<order_id:([^/]+)?>', OrderPage),
#    webapp2.Route(r'/<locale_id:([^/]+)?>/<page_id:([^/]+)?>', ModelViewer),
#    webapp2.Route(r'/<locale_id:([^/]+)?>', LocaleViewer),

	], debug=True)


