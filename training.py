#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from decimal import Decimal
from datetime import datetime, timedelta, date
import operator
from itertools import izip, groupby
from sql import Column, Literal
from sql.aggregate import Sum
from sql.conditionals import Coalesce
from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.wizard import Wizard, StateView, StateAction, StateTransition, \
    Button
from trytond.report import Report
from trytond.tools import reduce_ids
from trytond.pyson import Eval, PYSONEncoder, Date, Id
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond import backend

STATES = {
    'readonly': (Eval('state') != 'draft'),
}

STATES_CONFIRMED = {
    'readonly': (Eval('state') != 'draft'),
    'required': (Eval('state') == 'confirmed'),
}

STATE = [('draft', 'Draft'),
         ('open', 'Opened'),
         ('closed', 'Closed'),
         ('cancel', 'Canceled'),
         ('done', 'Done')]

DEPENDS = ['active']

_DAYS = [
         ('DO','Domingo'),
         ('LU','Lunes'),
         ('MA','Martes'),
         ('MI','Miercoles'),
         ('JU','Jueves'),
         ('VI', 'Viernes'),
         ]
__all__ = ['TrainingCatalog', 'TrainingSession']

class TrainingCatalog(Workflow, ModelView, ModelSQL):
    'Catalog'
    __name__ = 'training.catalog'

    name = fields.Char('Title', required=True, states = STATES)
    code = fields.Char('Code', states=STATES,)
    year = fields.Integer('Year', required=True, states = STATES, 
                                help="The year when the catalog has been published")
    sessions = fields.One2Many('training.session',
                                        'catalog',
                                        'Sessions',
                                        states = STATES, 
                                        help="The sessions in the catalog")
    description = fields.Text('Note', states = STATES, 
                             translate=True,
                             help="Allows to write a description of the catalog"),
    state = fields.Selection(STATE,
                                   'State',
                                   required=True,
                                   readonly=True,
                                   states = STATES, 
                                   help="The status of the catalog",)
    
    @staticmethod
    def default_state(): 
        return 'draft'
    
    @staticmethod
    def default_active():
        return True
    
    @classmethod
    def __setup__(cls):
        super(TrainingCatalog, cls).__setup__()
        cls._transitions |= set((
                ('cancel', 'draft'),
                ('draft', 'cancel'),
                ('draft', 'open'),
                ('open', 'draft'),
                ('open', 'done'),
                ))
        cls._buttons.update({
                'cancel': {
                    'invisible': ~Eval('state').in_(['draft']),
                    },
                'draft': {
                    'invisible': ~Eval('state').in_(['cancel','open']),
                    },
                'open': {
                    'invisible': ~Eval('state').in_(['draft']),
                    },
                'done': {
                    'invisible': Eval('state') != 'open',
                    },
                })
    
    @classmethod
    def create(cls, vlist):
        Sequence = Pool().get('ir.sequence')
        Config = Pool().get('training.sequences')

        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('code'):
                config = Config(1)
                values['code'] = Sequence.get_id(
                    config.catalog_sequence.id)

        return super(TrainingCatalog, cls).create(vlist)
    
    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('cancel')
    def cancel(cls, records):
        pass
        #stop subscriptions 

    @classmethod
    @ModelView.button
    @Workflow.transition('open')
    def open(cls, records):
        pass
    
    @classmethod
    @ModelView.button
    @Workflow.transition('done')
    def done(cls, records):
        pass

class TrainingSession(Workflow, ModelView, ModelSQL):
    'Session'
    __name__ = 'training.session'

    name = fields.Function(fields.Char('Name')
                           ,'get_name', searcher='search_name')
    code = fields.Char('Code', states=STATES,)
    state = fields.Selection(STATE,
                                   'State',
                                   required=True,
                                   readonly=True,
                                   states = STATES, 
                                   help="The status of the session",
                                  )
    offer = fields.Many2One('training.offer',
                                     'Offer',
                                     required=True,
                                     states = STATES,
                                     on_change=['name', 'offer'],
                                     depends=['name','offer'],
                                     help="Allows to select an open offer for the session",
                                     domain=[('state', '=', 'open')]
                                    )
    start_date = fields.Date('Start Date',
                                 required=True,
                                 states = STATES,
                                 help="The date of the planned session"
                                )
    date_end = fields.Date('End Date',
                                 states = STATES, 
                                 help="The end date of the planned session"
                                )
    catalog = fields.Many2One('training.catalog',
                                        'Catalog',
                                        help="The catalog for the session",
                                        states = STATES, 
                                        required=True)
    faculty = fields.Many2One('training.faculty',
                                    'Responsible faculty',
                                    states = STATES,)
    participant_count = fields.Integer('Participant Count',
                                       states = STATES, readonly=True) # modify to function
    min_limit = fields.Integer('Mininum Threshold',
                               states = STATES,
                               help="The minimum threshold is the minimum of the minimum threshold of each seance",
                                )
    max_limit = fields.Integer('Maximum Threshold',
                               states = STATES, 
                                      help="The maximum threshold is the minimum of the maximum threshold of each seance"
                                      )
    #temporary defined times
    session_day = fields.Selection(_DAYS, 'Session Day',
                                    required=True,)
    start_time = fields.Time('Start Hour', required=True)
    end_time = fields.Time('End Time', required=True)
    #pending hourly
    
    @classmethod
    def __setup__(cls):
        super(TrainingSession, cls).__setup__()
        cls._transitions |= set((
                ('cancel', 'draft'),
                ('draft', 'cancel'),
                ('draft', 'open'),
                ('open', 'draft'),
                ('open', 'done'),
                ))
        cls._buttons.update({
                'cancel': {
                    'invisible': ~Eval('state').in_(['draft']),
                    },
                'draft': {
                    'invisible': ~Eval('state').in_(['cancel','open']),
                    },
                'open': {
                    'invisible': ~Eval('state').in_(['draft']),
                    },
                'done': {
                    'invisible': Eval('state') != 'open',
                    },
                })
        
    @classmethod
    def create(cls, vlist):
        Sequence = Pool().get('ir.sequence')
        Config = Pool().get('training.sequences')

        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('code'):
                config = Config(1)
                values['code'] = Sequence.get_id(
                    config.session_sequence.id)

        return super(TrainingSession, cls).create(vlist)
    
    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('cancel')
    def cancel(cls, records):
        pass
        #stop subscriptions 

    @classmethod
    @ModelView.button
    @Workflow.transition('open')
    def open(cls, records):
        pass
    
    @classmethod
    @ModelView.button
    @Workflow.transition('done')
    def done(cls, records):
        pass

    @staticmethod
    def default_active():
        return True
    
    @staticmethod
    def default_state():
        return 'draft'
    
    @staticmethod
    def default_min_limit():
        return 1
    
    @staticmethod
    def default_max_limit():
        return 1
    
    @staticmethod
    def default_interval_number():
        return 1
    
    def on_change_offer(self):
        res = {}
        res['name'] = self.offer.name.name
        return res
    
    def get_name(self, name=None):
        return self.offer.name.name + ' - ' + self.session_day \
                + ' - ' + self.start_time.strftime('%X %Z') \
                + ' / '+ self.end_time.strftime('%X %Z')
                    
    @classmethod
    def search_name(cls, name, clause):
        res = []
        value = clause[2]
        res.append(('offer.name', clause[1], value))
        res.append(('session_day', clause[1], value))
        return res