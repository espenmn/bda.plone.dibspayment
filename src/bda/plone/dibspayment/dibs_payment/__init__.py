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
        order_uid = self.request['uid']
        base_url = self.context.absolute_url()
        
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDibsSettings)
        #password =  settings.shop_account_password
        id =  settings.dibs_id
        
        url = CREATE_PAY_INIT_URL
        
        data = IPaymentData(self.context).data(order_uid)
        amount = data['amount']
        currency = data['currency']
        description = data['description']
        ordernumber = data['ordernumber']
        
        current_language = "nb_NO"

        parameters = {
            'amount': amount,
            'currency': currency,
            'merchant': id,
            'language': current_language,
            'acceptReturnUrl': self.context.absolute_url() + '/dibsed?uid=' +  order_uid,
            'cancelreturnurl': self.context.absolute_url() + '/dibs_payment_aborted',
            'orderId': ordernumber,
            'test' : 1,
        }
        
        #assembles final url
        param = []
        for k, v in parameters.items():
            param.append("%s=%s" % (k, v))
        
        param = "&".join(param)
        
        self.request.response.redirect("%s?%s" % (url, param))
        


class DibsFinished(BrowserView):
    def id(self):
        uid = self.request.get('uid', None)
        payment = Payments(self.context).get('dibs')
        payment.succeed(self.request, uid)
        
        try:
            order = get_order(self.context, uid)
        except ValueError:
            return None
        return order.attrs.get('ordernumber')

  
        
class IDibsSettings(model.Schema):
    # Settings for Dibs payment method 

    model.fieldset(
        'dibs',
        label=_(u'Dibs', default=u'Dibs'),
        fields=[
            'dibs_id',
        ],
    )

    dibs_id = schema.TextLine(
        title=_(u"label_dibsid",
                default=u"Dibs merchant Id"),
        description=_(u"help_dibs_id",
                      default=u"Dibs merchant ID"),
        required=True,
    )

alsoProvides(IDibsSettings, IShopSettingsProvider)
   