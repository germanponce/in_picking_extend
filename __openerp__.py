# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@outlook.com)
############################################################################

{
    'name': 'Extension de  Albaranes',
    'version': '1',
    "author" : "German Ponce Dominguez",
    "category" : "Almacen",
    'description': """

Este modulo extiende los Albaranes y agrega 2 Campos:

1. Precio Publico.
2. Precio Cliente.

Estos datos son meramente Informativos, estos son llevados a la Impresión del reporte.

    """,
    "website" : "http://integra.avalos.co",
    "license" : "AGPL-3",
    "depends" : ["stock"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "stock.xml",
                    ],
    "installable" : True,
    "active" : False,
}
