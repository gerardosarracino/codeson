# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ejercicio(models.Model):
   _name = 'codeson.ejercicio'
   name = fields.Char(string="ejercicio")

class f_financiamiento(models.Model):
   _name = 'codeson.f_financiamiento'
   name = fields.Char(string="Nombre")
   clave = fields.Char(string="Clave")

class gasto_aprobado(models.Model):
    _name = 'codeson.gasto_aprobado'
    clave_presupuestal = fields.Char(compute="_calc_cp",store=True)
    financiamiento = fields.Many2one('codeson.f_financiamiento',string="Fuente de financiamiento", required=True)
    proyecto = fields.Many2one('codeson.proyecto_proceso',string="Proyecto/Proceso", required=True)
    unidad = fields.Many2one('codeson.unidad_administrativa',required=True)
    obj_gasto = fields.Many2one('codeson.clas_obj_gasto', required=True)

    @api.one
    def _calc_cp(self):
        #self.clave_presupuestal = financiamiento.
        self.clave_presupuestal = "xxx-xxx-xxx"

    ejercicio = fields.Many2one('codeson.ejercicio')
    programa = fields.Many2one('codeson.programa')
    subprograma = fields.Many2one('codeson.subprograma')
    finalidad = fields.Many2one('codeson.finalidad')
    funcion = fields.Many2one('codeson.funcion')
    subfuncion = fields.Many2one('codeson.subfuncion')
    f_especifica = fields.Many2one('codeson.f_especifica')
    currency_id = fields.Many2one('res.currency', string='Currency')
    anual = fields.Monetary('Anual')
    enero = fields.Monetary('Enero')
    febrero = fields.Monetary('Febrero')
    marzo = fields.Monetary('Marzo')
    abril = fields.Monetary('Abril')
    mayo = fields.Monetary('Mayo')
    junio = fields.Monetary('Junio')
    julio = fields.Monetary('Julio')
    agosto = fields.Monetary('Agosto')
    septiembre = fields.Monetary('Septiembre')
    octubre = fields.Monetary('Octubre')
    noviembre = fields.Monetary('Noviembre')
    diciembre = fields.Monetary('Diciembre')

class gasto_modificacion(models.Model):
    _name = 'codeson.gasto_modificacion'
    gasto_modificado = fields.Many2one('codeson.gasto_modificado')
    gasto_aprobado = fields.Many2one('codeson.gasto_aprobado')
    currency_id = fields.Many2one('res.currency', string='Currency')
    monto_anual_anterior = fields.Monetary(related="gasto_aprobado.anual")
    nuevo_monto = fields.Monetary('Nuevo monto')

class gasto_modificado(models.Model):
    _name = 'codeson.gasto_modificado'
    ejercicio = fields.Many2one('codeson.ejercicio')
    fecha = fields.Date('Fecha')
    tipo_d = fields.Selection([
        ('cabildo','ACTA DE CABILDO'),
        ('gobierno','ACTA JUNTA DE GOBIERNO'),
        ('otro','OTRO')
    ])
    tipo = fields.Selection([
        ('ampliacion','AMPLIACION'),
        ('reduccion','REDUCCION'),
        ('traspaso','TRASPASO')
    ])
    documento_fuente = fields.Char('Documento fuente')
    folio_documento = fields.Char('Folio de documento')
    modificaciones = fields.One2many('codeson.gasto_modificacion',"gasto_modificado")
