# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class apoyo(models.Model):
    _name = 'codeson.apoyo'
    name = fields.Char(compute="_calc_name")


    asunto = fields.Text('Asunto',required=True)

    folio = fields.Char(
                        string='Folio',
                        required=True,
                        copy=False,
                        default= lambda self: self.env['ir.sequence'].next_by_code('apoyo')
                        )

    fecha = fields.Date('Fecha de solicitud',required=True,default=datetime.today())
    solicita = fields.Many2one('codeson.solicitante_apoyo','Solicita',required=True)
    autoriza = fields.Many2one('hr.employee', 'Autoriza',required=True)
    puesto_autoriza = fields.Char(related='autoriza.job_id.name',string='Puesto de quien autoriza',readonly=True)

    line_ids = fields.One2many('codeson.apoyo_line','apoyo_id')
    unidad_administrativa = fields.Many2one('codeson.unidad_administrativa',domain="[('id','in',unidad_administrativa_permitidas)]")
    unidad_administrativa_permitidas = fields.Many2many('codeson.unidad_administrativa',related="creador.unidad_administrativa")
    creador = fields.Many2one('res.users',default=lambda self: self.env.user)
    orden_id = fields.Many2one('codeson.orden_pago')





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
        values_evidencia = {
            "apoyo": self.id
        }
        self.env['codeson.evidencia_apoyo'].create(values_evidencia)
        self.state='validado'

    @api.one
    def pagado(self):
        self.state='pagado'

    @api.one
    def cancelar(self):
        self.state='cancelado'

    @api.one
    def _contar_documentos(self):
        count = self.env['codeson.documento_apoyo'].search_count([
            ('apoyo_id','=',self.id)
            ])
        self.documentacion_count = count

    @api.one
    def gen_orden_pago(self):
        orden_id = self.env['codeson.orden_pago'].sudo().create(
            {
                'tipo':'apoyo',
                'solicita':str(self.solicita.id),
                'fecha': fields.datetime.now(),
                'fecha_programada':fields.datetime.now(),
                'descripcion': self.asunto
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
                'orden_pago_id':orden_id
            })
        self.state='proceso_pago'




    #oe_subtotal_footer
    currency_id = currency_id = fields.Many2one('res.currency', string='Currency')
    amount_untaxed = fields.Monetary('Base imponible',compute="_calc_untaxed")
    amount_tax = fields.Monetary('Impuestos',compute="_calc_tax")
    amount_total = fields.Monetary('Total',compute="_total")

    @api.one
    def _calc_untaxed(self):
        foo = 0.0
        for line in self.line_ids:
            foo += (line.cantidad * line.precio_unitario)
        self.amount_untaxed = foo

    @api.one
    def _calc_tax(self):
        foo = 0.0
        for line in self.line_ids:
            bar = 0.0
            for element in line.impuesto:
                bar += element.amount
            foo += (line.cantidad * line.precio_unitario * bar/100.0)
        self.amount_tax = foo

    @api.one
    def _total(self):
        self.amount_total = self.amount_tax + self.amount_untaxed




class solicitante_apoyo(models.Model):
    _name='codeson.solicitante_apoyo'
    name=fields.Char('Solicitante')

class apoyo_line(models.Model):
    _name='codeson.apoyo_line'
    apoyo_id = fields.Integer()
    unidad_administrativa = fields.Many2one('codeson.unidad_administrativa')
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

    product_id = fields.Many2one('product.product', required=True,domain="[('default_code','=like','4%')]")
