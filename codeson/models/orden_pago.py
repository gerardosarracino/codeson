# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

#from num2es import TextNumber

#En proceso de pago cuando se cree orden, para filtrarla. mostrar facturas solo de proveedor y que no hayan sido pagadas ni en proceso de

class orden_pago(models.Model):
    _name = 'codeson.orden_pago'
    name = fields.Char(
                        string='Folio',
                        copy=False,
                        default= lambda self: self.env['ir.sequence'].next_by_code('orden_pago')
                        )
    facturado = fields.Boolean(string="¿Es facturado?")
    referencia_proveedor = fields.Char()

    documento_origen=fields.Char(related='factura.origin',string='Documento de origen')
    proveedor = fields.Many2one('res.partner',domain="[('supplier','=',True)]")
    fecha_factura = fields.Date()
    cheque_nombre = fields.Char('Cheque a nombre de')
    factura = fields.Many2many('account.invoice') #many2many
    currency_id = currency_id = fields.Many2one('res.currency', string='Currency')
    total_de_factura = fields.Monetary('Total de factura',related='factura.amount_total_signed')
    restante = fields.Monetary('Por cubrir',related='factura.residual')
    abono = fields.Monetary('A abonar')
    fecha = fields.Date('Fecha',required=True,default=datetime.today())
    fecha_programada = fields.Date('Fecha programada',required=True,default=datetime.today())
    observaciones = fields.Text()
    referencia = fields.Char('Documento de referencia',compute='_calc_ref',store=True)
    unidad_administrativa = fields.Many2one('codeson.unidad_administrativa')
    autoriza = fields.Many2one('hr.employee', 'Autoriza')
    puesto_autoriza = fields.Char(related='autoriza.job_id.name',string='Puesto de quien autoriza',readonly=True)
    solicita = fields.Many2one('hr.employee','Solicita')
    beneficiario = fields.Many2one('hr.employee','Beneficiario')

    multiunidad = fields.Boolean('Aplica a varias unidades')
    unidad_administrativa = fields.Many2one('codeson.unidad_administrativa')

    dir_finanzas = fields.Many2one('hr.employee', default=4) 
    dir_general = fields.Many2one('hr.employee', default=10) #GENARO ALBERTO ENRIQUEZ RASCON 
    directores = fields.Selection([('genaro_rascon', 'GENARO ALBERTO ENRIQUEZ RASCON '), ('jose_montiel', 'JOSÉ GABRIEL TAPIA MONTIEL')], default='jose_montiel')
    nombre_director =  fields.Char(compute='director_estatus')

    #Trabajando JFernández traer propiedad del boton active
    @api.onchange('directores')
    def director_estatus(self):
        if self.directores == 'genaro_rascon':
            self.nombre_director =  self.env['hr.employee'].browse(3081).name
        else:
            self.nombre_director = self.env['hr.employee'].browse(3082).name


    
     
         


    para = fields.Char()
    descripcion = fields.Text('Descripción')

    total_de_factura_esp = fields.Char(compute="_calc_total_de_factura_esp")
    
    
    

    @api.depends('amount_total')
    def _calc_total_de_factura_esp(self):
        [pesos,centavos] = str(round(self.amount_total, 2)).split('.')
        pesos = int(pesos)
        if len(centavos) == 1:
        	centavos = centavos + "0"
        salida = ""
        #salida += str(TextNumber(pesos)) + " pesos"
        salida += str(pesos) + " pesos"
        #salida += " con " + str(TextNumber(int(centavos))) + " centavos"
        salida += " con " + str(int(centavos)) + " centavos"
        self.total_de_factura_esp = salida

    @api.one
    @api.depends('tipo','viatico_id','apoyo_id','compra_id')
    def _calc_ref(self):
        if self.tipo == 'viatico':
            try:
                self.referencia = self.viatico_id.name
                self.unidad_administrativa = self.viatico_id.unidad_administrativa
            except:
                pass
        if self.tipo == 'apoyo':
            try:
                self.referencia = self.apoyo_id.name
                self.unidad_administrativa = self.apoyo_id.unidad_administrativa
            except:
                pass
        if self.tipo == 'compra':
            try:
                self.referencia = self.compra_id.name
                self.unidad_administrativa = False
            except:
                pass

    line_ids = fields.One2many('codeson.orden_pago_line','orden_pago_id')
    pagos = fields.One2many('account.payment','orden_pago_id')
    pagos_count = fields.Monetary(compute='_calc_pagos')

    @api.one
    @api.depends('pagos')
    def _calc_pagos(self):
        pagado = 0.0
        for pago in self.pagos:
            pagado += pago.amount
        self.pagos_count = pagado


    state = fields.Selection([
        ('borrador','Borrador'),
        ('confirmado','Confirmado'),
        ('validado','Validado'),
        ('pagado','Pagado'),
        ('cancelado','Cancelado'),
    ],default='borrador')
    state_gasto_comprobar = fields.Selection([
        ('sin_comprobar','Sin comprobar'),
        ('parcial','Parcialmente comprobado'),
        ('comprobado','Comprobado')
    ])


    tipo = fields.Selection([
        ('gasto_directo','Gasto directo'),
        ('viatico','de Viatico'),
        ('apoyo','de Apoyo'),
        ('compra','Pedido de compra'),
        ('gasto_comprobar','Gasto por comprobar')
        ],default="gasto_directo")
    viatico_id = fields.Many2one('codeson.viatico',default=False,domain="[('state','=','validado')]")
    comisionado = fields.Many2one('hr.employee',related="viatico_id.empleado")
    apoyo_id = fields.Many2one('codeson.apoyo',default=False,domain="[('state','=','validado')]")
    compra_id = fields.Many2one('purchase.order',domain="[('state','=','purchase')]")
    monto_comprobar = fields.Monetary('Monto')

    @api.depends('viatico_id','apoyo_id','se_origina','o_pago_folio','compra_id')
    def _fill(self):
        self.line_ids = False
        if self.tipo != 'compra':
            values = []
            lines = []
            if self.tipo == 'viatico':
                lines = self.viatico_id.line_ids
            if self.tipo == 'apoyo':
                lines = self.apoyo_id.line_ids
            for line in lines:
                value = {
                    'product_id': line.product_id,
                    'detalles': line.detalles,
                    'cantidad': line.cantidad,
                    'unidad_medida':line.unidad_medida,
                    'precio_unitario':line.precio_unitario,
                    'impuesto':line.impuesto
                }
                values.append( (0,0,value) )
            self.line_ids = values
        else:
            values=[]
            for line in self.compra_id.order_line:
                value = {
                    'product_id': line.product_id,
                    'detalles': line.name,
                    'cantidad': line.product_qty,
                    'precio_unitario':line.price_unit,
                    'impuesto':line.taxes_id
                }
                values.append( (0,0,value) )
            self.line_ids = values



    @api.one
    def confirmar(self):
        self.state='confirmado'

    @api.one
    def validar(self):
        self.state='validado'

    @api.one
    def pagado(self):
        self.state='pagado'

    @api.one
    def cancelar(self):
        self.state='cancelado'



    #oe_subtotal_footer
    currency_id = currency_id = fields.Many2one('res.currency', string='Currency')
    amount_untaxed = fields.Monetary('Base imponible',compute="_calc_untaxed")
    amount_tax = fields.Monetary('Impuestos',compute="_calc_tax")
    amount_total = fields.Monetary('Total',compute="_total")

    @api.one
    @api.depends('line_ids')
    def _calc_untaxed(self):
        foo = 0.0
        for line in self.line_ids:
            foo += (line.cantidad * line.precio_unitario)
        self.amount_untaxed = foo

    @api.one
    @api.depends('amount_untaxed')
    def _calc_tax(self):
        foo = 0.0
        for line in self.line_ids:
            bar = 0.0
            for element in line.impuesto:
                bar += element.amount
            foo += (line.cantidad * line.precio_unitario * bar/100.0)
        self.amount_tax = foo

    @api.one
    @api.depends('amount_untaxed','amount_tax')
    def _total(self):
        self.amount_total = self.amount_tax + self.amount_untaxed




class orden_pago_line(models.Model):
    _name='codeson.orden_pago_line'
    unidad_administrativa = fields.Many2one('codeson.unidad_administrativa')
    orden_pago_id = fields.Integer()
    obj_gasto = fields.Char(related="product_id.obj_gasto",string="Partida")
    detalles = fields.Text(string="Detalles")
    cantidad = fields.Integer(string="Cantidad",required=True)
    unidad_medida =fields.Many2one('codeson.unidad_medida',string="Unidad de medida")
    precio_unitario = fields.Float(string="Precio unitario")
    impuesto = fields.Many2many('account.tax',domain=[('type_tax_use','=','purchase')])

    subtotal = fields.Float(compute='_subtotal',store=True)
    impuestos = fields.Float(compute='_impuestos',store=True)

    @api.one
    @api.depends('cantidad','precio_unitario')
    def _subtotal(self):
        self.subtotal = self.cantidad * self.precio_unitario

    @api.one
    @api.depends('subtotal','impuesto')
    def _impuestos(self):
        foo = 0.0
        for line in self.impuesto:
            foo += line.amount
        self.impuestos = (self.cantidad * self.precio_unitario) * (foo/100.0)




    product_id = fields.Many2one('product.product', required=True)

class pago(models.Model):
    _inherit = 'account.payment'
    orden_pago_id = fields.Many2one('codeson.orden_pago')
    fecha = fields.Date(string="Fecha",default=datetime.today()) #payment_date
    #currency_id = currency_id = fields.Many2one('res.currency', string='Currency')
    monto = fields.Monetary('Monto') #amount
    #name = fields.Char(compute="_calc_name")

    #@api.one
    #def _calc_name(self):
        #self.name = str(self.fecha) + " $" + str(self.monto)
