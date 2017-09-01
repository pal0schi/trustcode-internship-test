import xmlrpclib

url = 'https://batata.odoo.com'
db = 'batata'
username = 'paloschifelipe@outlook.com'
password = 'cdnn792458'

server = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))

uid = server.authenticate(db, username, password, {})

models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))


#Create a new client and return his identifier:
#{'name': "Novo cliente", 'phone': '2131231', 'email':'papa@papa.com', 'street': 'rua rosa, legal, massa, 2'}
def createClient(**kwargs):
    return models.execute_kw(db, uid, password, 'res.partner', 'create', [kwargs])

#Update client information:
def updateClient(identifier, **kwargs):
    models.execute_kw(db, uid, password, 'res.partner', 'write', [[identifier], kwargs])

def countClients():
    return models.execute_kw(db, uid, password,
    'res.partner', 'search_count',
    [[['customer', '=', True]]])

def clientList(limit=10):
    ids = models.execute_kw(db, uid, password,
        'res.partner', 'search',
        [[['customer', '=', True]]],
        {'limit': limit})

    #list comprehensions, getting client data using the ids from the previous search
    clientData = [models.execute_kw(db, uid, password,
                'res.partner', 'read',
                [i], {'fields': ['name', 'street']}) for i in ids]


    #the previous 'read' returns every dict inside of a list, so we need to get them
    #out of the list before sorting
    clientData = [x[0] for x in clientData]

    return sorted(clientData, key = lambda k: k['name']) 

def biggestSale():
    sales = models.execute_kw(db, uid, password,
        'sale.order', 'search_read',
        [],
        {'fields': ['name', 'partner_id', 'amount_total'], 'order':'amount_total'})

    return sales[-1]

def saleInfo(identifier):
    sales =  models.execute_kw(db, uid, password,
        'sale.order', 'read', [identifier], {'fields':['order_line']})

    return [models.execute_kw(db, uid, password, 'product.product', 'read', [i], 
        {'fields':['product_id', 'lst_price']}) for i in sales[0]['order_line']]

#Returns the absolute (considering only the number os sales) and the price (considers the price of 
#each sale) percent of sales
def closedSalesPercent():
    salesOrders = models.execute_kw(db, uid, password,
        'sale.order', 'search_read',
        [],
        {'fields': ['id', 'amount_total', 'state']})
    
    sales = [i for i in salesOrders if i['state']=='sale']
    draft = [i for i in salesOrders if i['state']=='draft']

    absolutPercent = ((float(len(sales)))/(float(len(sales))+float(len(draft))))*100
    
    total_sales = sum(i['amount_total'] for i in sales)
    total_draft = sum(i['amount_total'] for i in draft)
    
    pricePercent = float((total_sales/(total_sales + total_draft))*100)

    return {'absolutPercent':absolutPercent, 'pricePercent':pricePercent}

def invoiceAmountPerMonth(month):
    invoice = models.execute_kw(db, uid, password,
        'account.invoice', 'search_read',
        [],
        {'fields': ['create_date', 'amount_total']})

    invoiceThisMonth = [i for i in invoice if int(i['create_date'][5:7])==month]

    return sum(i['amount_total'] for i in invoiceThisMonth)