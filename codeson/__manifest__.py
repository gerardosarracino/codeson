# -*- coding: utf-8 -*-
{
    'name': "sacgnet",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','purchase_requisition','product','hr'],

    # always loaded
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'vistas/presupuesto.xml',
        'vistas/evidencia_apoyos.xml',
        'vistas/apoyos.xml',
        'vistas/orden_pago.xml',
        'reports/report_paperformat.xml',
        'reports/orden_pago_header.xml',
        'reports/orden_pago.xml',
        'reports/apoyos_header.xml',
        'reports/apoyos.xml',
        'reports/viaticos_header.xml',
        'reports/viaticos.xml',
        'vistas/productos.xml',
        'vistas/viaticos.xml',
        'reports/requisicion_header.xml',
        'reports/requisition.xml',
        'vistas/pagos.xml',
        'vistas/gasto_directo.xml',
        'vistas/gastos_comprobacion.xml',
        'vistas/orden_compra.xml',
        'vistas/impuestos.xml',
        #'views/adjuntos.xml',
        'presupuesto/vistas/gasto_aprobado.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
