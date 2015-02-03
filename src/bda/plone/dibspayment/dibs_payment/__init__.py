import logging
from lxml import etree
from zExceptions import Redirect
from zope.i18nmessageid import MessageFactory
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from bda.plone.payment.interfaces import IPaymentData

from bda.plone.shop.interfaces import IShopSettings
from bda.plone.shop.interfaces import IShopSettingsProvider
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
    
from bda.plone.payment import (
    Payment,
    Payments,
)

#from zope.interface import provider
from zope.interface import alsoProvides
from zope import schema
from plone.supermodel import model

#from ZTUtils import make_query
from bda.plone.orders.common import get_order


logger = logging.getLogger('bda.plone.payment')
_ = MessageFactory('bda.plone.payment')


CREATE_PAY_INIT_URL = "https://sat1.dibspayment.com/dibspaymentwindow/entrypoint"

class IDibsPaymentData(IPaymentData):
    """Data adapter interface for DIBS payment.
    """
    
    def uid_for(ordernumber):
        """Return order_uid for ordernumber.
        """
    
    def data(order_uid):
        """Return dict in following format:
        
        {
            'amount': '1000',
            'currency': 'NOK',
            'description': 'description',
            'ordernumber': '1234567890',
        }
        """


class DibsPayment(Payment):
    pid = 'dibs_payment'
    label = _('dibs_payment', 'Dibs Payment')
    
    def init_url(self, uid):
        return '%s/@@dibs_payment?uid=%s' % (self.context.absolute_url(), uid)


class DibsPayError(Exception):
    """Raised if DIBS payment return an error.
    """


class DibsPay(BrowserView):
    """
    Assembles an url to dibs.
    Need to check how to use (in line 109)
    make_query() 
    """

    def __call__(self, **kw):
        import pdb; pdb.set_trace()
        uid = self.request['uid']
        base_url = self.context.absolute_url()
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IShopSettings)
        password =  settings.shop_account_password
        id =  settings.shop_account_id
        currency =  settings.shop_currency
        
        url = CREATE_PAY_INIT_URL
        
        parameters = {
            'accountid':    '4255617',
            'amount':       amount,
            'currency':     currency,
            'orderid':      'order_uid',
            'merchant':     id,
            'acceptReturnUrl': base_url + '/dibs_payment_success',
            'cancelreturnurl': base_url + '/dibs_payment_aborted',
            'billingLastName': 'Etternavn',
            'billingFirstName':	'Firsstname',
            'orderId':      'testorder',
            'test': 1,
        }
        
        #assembles final url
        param = []
        for k, v in parameters.items():
            param.append("%s=%s" % (k, v))
        
        param = "&".join(param)
        
        self.request.response.redirect("%s?%s" % (url, param))
        
        
        
class IDibsSettings(model.Schema):
    # Settings for Dibs payment method 

    model.fieldset(
        'dibs',
        label=_(u'Dibs', default=u'Dibs'),
        fields=[
            'dibs_id',
        ],
    )

    dibs_id = schema.Text(
        title=_(u"label_dibsid",
                default=u"Dibs Id"),
        description=_(u"help_dibs_id",
                      default=u"Dibs ID"),
        required=True,
    )

alsoProvides(IDibsSettings, IShopSettingsProvider)
   