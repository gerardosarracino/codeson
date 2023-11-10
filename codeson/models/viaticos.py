# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class viatico(models.Model):
    _name = 'codeson.viatico'
    name = fields.Char(compute="_calc_name")
    asunto = fields.Text('Motivo de comisión',required=True)
    folio = fields.Char(
                        string='Folio',
                        required=True,
                        copy=False,
                        default= lambda self: self.env['ir.sequence'].next_by_code('viatico')
                        )

    fecha = fields.Date('Fecha de solicitud',required=True,default=datetime.today())
    fecha_salida = fields.Date('Fecha de salida',required=True)
    fecha_regreso = fields.Date('Fecha de regreso',required=True)
    trabajo = fields.Text('Trabajo a desempeñar')
    transporte = fields.Selection([
        ('autobus','Autobus'),
        ('automovil','Automóvil'),
        ('avion','Avión')
        ])
    empleado = fields.Many2one('hr.employee','Empleado',required=True)
    autoriza = fields.Many2one('hr.employee', 'Autoriza',required=True)
    puesto_autoriza = fields.Char(related='autoriza.job_id.name',string='Puesto de quien autoriza',readonly=True)

    line_ids = fields.One2many('codeson.viatico_line','viatico_id')
    unidad_administrativa = fields.Many2one('codeson.unidad_administrativa',domain="[('id','in',unidad_administrativa_permitidas)]")
    unidad_administrativa_permitidas = fields.Many2many('codeson.unidad_administrativa',related="creador.unidad_administrativa")
    creador = fields.Many2one('res.users',default=lambda self: self.env.user)






    state = fields.Selection([
        ('borrador','Borrador'),
        ('confirmado','Confirmado'),
        ('validado','Validado'),
        ('proceso_pago','En proceso de pago'),
        ('pagado','Pagado'),
        ('cancelado','Cancelado')
    ],default='borrador')

    estado_facturacion = fields.Selection([
        ('nada','Nada por facturar'),
        ('facturado','Facturado')
    ],default="nada")

    documentacion = fields.Selection([
        ('proceso','En proceso'),
        ('completado','Completado')
    ],default='proceso')

    documentacion_count = fields.Integer(compute="_contar_documentos")

    @api.one
    def _calc_name(self):
        self.name = str(self.folio)


    @api.one
    def confirmar(self):
        self.state='confirmado'

    @api.one
    def validar(self):
        self.state='validado'

    @api.one
    def pagado(self):
        self.state='pagado'


    orden_id = fields.Many2one('codeson.orden_pago')

    @api.one
    def nada(self):
        pass

    @api.one
    def gen_orden_pago(self):
        orden_id = self.env['codeson.orden_pago'].sudo().create(
            {
                'tipo':'viatico',
                'solicita':self.empleado.id,
                'para':str(self.empleado.name),
                'fecha': fields.datetime.now(),
                'fecha_programada':fields.datetime.now(),
                'descripcion': self.asunto,
                'viatico_id':self.id,
                'unidad_administrativa':self.unidad_administrativa.id,
                'documento_origen':self.folio,
                'amount_tax':self.amount_tax,
                'amount_untaxed':self.amount_untaxed
            }
        )

        self.orden_id = orden_id
        for line in self.line_ids:
            self.orden_id.line_ids.create({
                'unidad_administrativa':line.unidad_administrativa.id,
                'product_id': line.product_id.id,
                'detalles': line.detalles,
                'cantidad': line.cantidad,
                'unidad_medida':line.unidad_medida.id,
                'precio_unitario':line.precio_unitario,
                'impuesto':line.impuesto,
                'orden_pago_id':orden_id,
            })
        self.state='proceso_pago'
        subtotal = self.orden_id._calc_untaxed()
        impuestos = self.orden_id._calc_tax()
        total = subtotal + impuestos
        self.orden_id._calc_total_de_factura_esp()

    @api.one
    def cancelar(self):
        self.state='cancelado'

    @api.one
    def _contar_documentos(self):
        count = self.env['codeson.documento_viatico'].search_count([
            ('viatico_id','=',self.id)
            ])
        self.documentacion_count = count




    #oe_subtotal_footer
    currency_id = fields.Many2one('res.currency', string='Currency',store=True)
    amount_untaxed = fields.Monetary('Base imponible',compute="_calc_untaxed",store=True)
    amount_tax = fields.Monetary('Impuestos',compute="_calc_tax",store=True)
    amount_total = fields.Monetary('Total',compute="_total",store=True)

    @api.one
    @api.depends('line_ids')
    def _calc_untaxed(self):
        foo = 0.0
        for line in self.line_ids:
            foo += line.subtotal
        self.amount_untaxed = foo
        return foo

    @api.one
    @api.depends('amount_untaxed')
    def _calc_tax(self):
        foo = 0.0
        for line in self.line_ids:
            foo += line.impuestos
        self.amount_tax = foo
        return foo

    @api.one
    @api.depends('amount_tax')
    def _total(self):
        self.amount_total = self.amount_tax + self.amount_untaxed




class solicitante_viatico(models.Model):
    _name='codeson.solicitante_viatico'
    name=fields.Char('Solicitante')

class viatico_line(models.Model):
    _name='codeson.viatico_line'
    viatico_id = fields.Integer()
    unidad_administrativa = fields.Many2one('codeson.unidad_administrativa')

    obj_gasto = fields.Char(related="product_id.obj_gasto",string="Partida")
    detalles = fields.Text(string="Detalles")
    cantidad = fields.Integer(string="Cantidad",required=True,default=1)
    unidad_medida =fields.Many2one('codeson.unidad_medida',string="Unidad de medida")
    precio_unitario = fields.Float(string="Precio unitario")
    impuesto = fields.Many2many('account.tax',domain=[('type_tax_use','=','purchase')])
    subtotal = fields.Float(compute='_subtotal',store=True)
    impuestos = fields.Float(compute='_impuestos',store=True)

    @api.one
    @api.depends('cantidad','precio_unitario')
    def _subtotal(self):
        self.subtotal = self.cantidad * self.precio_unitario

    @api.onchange('product_id')
    def _actualizar_precio(self):
        self.precio_unitario = self.product_id.standard_price

    @api.one
    @api.depends('subtotal','impuesto')
    def _impuestos(self):
        foo = 0.0
        for line in self.impuesto:
            foo += line.amount
        self.impuestos = (self.cantidad * self.precio_unitario) * (foo/100.0)


    product_id = fields.Many2one('product.product', required=True)


##evidencia_viatico


class evidencia_viatico(models.Model):
    _name='codeson.evidencia_viatico'
    folio = fields.Char(
                        string='Folio',
                        required=True,
                        copy=False,
                        default= lambda self: self.env['ir.sequence'].next_by_code('evidencia_viatico')
                        )
    fecha_vencimiento = fields.Date()
    viatico = fields.Many2one('codeson.viatico')
    fecha_viatico = fields.Date(related="viatico.fecha")
    currency_id = currency_id = fields.Many2one('res.currency', string='Currency')
    monto = fields.Monetary('Total',related="viatico.amount_total")
    estado_evidencia = fields.Selection([
        ('no_iniciado','No iniciado'),
        ('cancelado','Cancelado'),
        ('completado','Completado')
    ],default="no_iniciado")

    documentacion_count = fields.Integer(compute="_contar_documentos")

    @api.one
    def _contar_documentos(self):
        count = self.env['codeson.documento_viatico'].search_count([
            ('viatico_id','=',self.viatico.id)
            ])
        self.documentacion_count = count


class documento_viatico(models.Model):
    _name='codeson.documento_viatico'
    name=fields.Char(string="Nombre")
    file=fields.Binary(required=True)
    file_name=fields.Char(required=True)
    viatico_id=fields.Many2one('codeson.viatico')
