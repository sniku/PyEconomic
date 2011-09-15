"""
E-conomic python abstraction layer.
Login to E-conomic and turn on API access:
  Settings -> Add-on modules -> API
API documentation: https://www.e-conomic.com/secure/api1/EconomicWebService.asmx
"""

from suds.client import Client

class PyEconomic:
    """
        Simple abstraction layer that exposes e-conimic SOAP API to python.
        Usage:
        e = PyEconomic(agreement_id, user_id, password, wsdl_url)
        debtors = e.call('Debtor_GetAll') # get all customers
        e.create_customer(7, u"Mr. White Hat Spammer") # create new customer
        my_customer = e.call('Debtor_FindByNumber', number=7) # get newly created customer
    """


    def __init__(self, agreement_id, user_id, password, wsdl_url):
        self.client = Client(wsdl_url, headers={'Content-Type': 'text/xml; charset=utf-8'})
        self.client.service.Connect(agreementNumber = agreement_id, userName = user_id, password = password)

    def call(self, soap_method_name, **kwargs):
        """
            Use this method to call any method of the e-conomic API.
            usage:
            e.call('TermOfPayment_FindByName', name='GAN term of payment')
        """

        method = getattr(self.client.service, soap_method_name, None)
        if not method:
            raise Exception("No such method in WSDL specification")
        #print u'Calling %s with arguments %s'%(soap_method_name, kwargs)
        return method(**kwargs)

    def get_customer(self, name=None, number=None, cinumber=None, ean=None, email=None, partialname=None):
        ''' returns DebtorHandle. You must provide exactly one argument '''
        # can this code be more evil?
        args = {
            'Name':        {'arg': 'name', 'val': name},
            'Number':      {'arg': 'number', 'val': number},
            'CINumber':    {'arg': 'ciNumber', 'val': cinumber},
            'Ean':         {'arg': 'ean', 'val': ean},
            'Email':       {'arg': 'email', 'val': email},
            'PartialName': {'arg': 'partialName', 'val': partialname},
        }
        arg = filter(lambda x: x[1]['val'], [(k,v) for k,v in args.iteritems()])
        if len(arg) != 1:
            raise Exception('You must provide exactly one argument to the get_customer method')
        method_name, arg_key, arg_value = arg[0][0], arg[0][1]['arg'], arg[0][1]['val']

        return self.call('Debtor_FindBy%s'%method_name, **{arg_key: arg_value})

    #TODO: term_of_payment_id must be specified
    def create_customer(self, number, name, term_of_payment_id=None, group_handle_id=None,
                        vat_zone='HomeCountry', currency_code=None, email=None, www=None,
                        address=None, postal_code=None, city=None, country=None, vat_number=None):
        """ Creates a new debtor """
        if not group_handle_id:
            group_handle = self._get_default_group_handle()
        else:
            group_handle = {'Number': group_handle_id}

        debtor = self.call('Debtor_Create', number=number, name=name, vatZone=vat_zone, debtorGroupHandle=group_handle)

        if term_of_payment_id: self.call('Debtor_SetTermOfPayment', debtorHandle=debtor, valueHandle={'Id':term_of_payment_id})# This one must be provided
        if currency_code:      self.call('Debtor_SetCurrency', debtorHandle=debtor, valueHandle={'Code':currency_code})
        if address:            self.call('Debtor_SetAddress', debtorHandle=debtor, value=address)
        if city:               self.call('Debtor_SetCity', debtorHandle=debtor, value=city)
        if postal_code:        self.call('Debtor_SetPostalCode', debtorHandle=debtor, value=postal_code)
        if country:            self.call('Debtor_SetCountry', debtorHandle=debtor, value=country)
        if email:              self.call('Debtor_SetEmail', debtorHandle=debtor, value=email)
        if www:                self.call('Debtor_SetWebsite', debtorHandle=debtor, value=www)
        if vat_number:         self.call('Debtor_SetVatNumber', debtorHandle=debtor, value=vat_number)
        return debtor

    def update_customer(self, debtor_handle, name=None, term_of_payment_id=None, group_handle_id=None,
                        vat_zone=None, currency_code=None, email=None, www=None,
                        address=None, postal_code=None, city=None, country=None, vat_number=None):
        """ Updates existing debtor """

        if name:               self.call('Debtor_SetName', debtorHandle=debtor_handle, value=name)
        if group_handle_id:    self.call('Debtor_SetDebtorGroup', debtorHandle=debtor_handle, valueHandle={'Number':group_handle_id})
        if vat_zone:           self.call('Debtor_SetVatZone', debtorHandle=debtor_handle, value=vat_zone)
        if term_of_payment_id: self.call('Debtor_SetTermOfPayment', debtorHandle=debtor_handle, valueHandle={'Id':term_of_payment_id})
        if currency_code:      self.call('Debtor_SetCurrency', debtorHandle=debtor_handle, valueHandle={'Code':currency_code})
        if address:            self.call('Debtor_SetAddress', debtorHandle=debtor_handle, value=address)
        if city:               self.call('Debtor_SetCity', debtorHandle=debtor_handle, value=city)
        if postal_code:        self.call('Debtor_SetPostalCode', debtorHandle=debtor_handle, value=postal_code)
        if country:            self.call('Debtor_SetCountry', debtorHandle=debtor_handle, value=country)
        if email:              self.call('Debtor_SetEmail', debtorHandle=debtor_handle, value=email)
        if www:                self.call('Debtor_SetWebsite', debtorHandle=debtor_handle, value=www)
        if vat_number:         self.call('Debtor_SetVatNumber', debtorHandle=debtor_handle, value=vat_number)
        return debtor_handle


    def _get_default_group_handle(self):
        """ returns the first GroupHandle """
        return self.call('DebtorGroup_GetAll')['DebtorGroupHandle'][0]
