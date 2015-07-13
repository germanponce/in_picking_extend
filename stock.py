# -*- encoding: utf-8 -*-
############################################################################
#    (c) 2015 German Ponce Dominguez
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@outlook.com)
############################################################################


from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp


class stock_pack_operation(osv.osv):
    _name = 'stock.pack.operation'
    _inherit ='stock.pack.operation'
    _columns = {
        'list_price': fields.float('Precio Publico', help='Precio de Venta definido en la ficha del Producto.' ),
        'list_price_client': fields.float('Precio Cliente', help='Precio de Venta asignado al Cliente.' ),
        }

    _defaults = {
        }


    def total_price(self, price, qty):
        return price*qty

    def total_price_global(self, moves):
        total_price = 0.0
        for line in moves:
            total = line.list_price*line.product_qty
            total_price += total
        return 

    def total_price_client_global(self, moves):
        total_price_client = 0.0
        for line in moves:
            total = line.list_price_client*line.product_qty
            total_price_client += total
        return 


    def create(self, cr, uid, vals, context=None):
        context = context or {}
        res_id = super(stock_pack_operation, self).create(cr, uid, vals, context=context)
        if vals.get("picking_id"):
            #picking_br = self.pool.get("stock.picking").browse(cr, uid, [vals['picking_id']], context=context)[0]
            self_br = self.browse(cr, uid, res_id, context=context)
            move_obj = self.pool.get('stock.move')
            move_ids = move_obj.search(cr, uid, [('product_id','=',self_br.product_id.id),
                ('picking_id','=',self_br.picking_id.id),('product_uom_qty','=',self_br.product_qty)])
            move_br = move_obj.browse(cr, uid, move_ids, context=None)[0]
            self.write(cr, uid, [res_id], {'list_price': move_br.list_price,'list_price_client': move_br.list_price_client,})
        return res_id

class stock_move(osv.osv):
    _name = 'stock.move'
    _inherit ='stock.move'
    _columns = {
        'list_price': fields.float('Precio Publico', digits=(14,2), help='Precio de Venta definido en la ficha del Producto.' ),
        'list_price_client': fields.float('Precio Cliente', digits=(14,2), help='Precio de Venta asignado al Cliente.' ),
        }

    _defaults = {
        }

    def total_price(self, price, qty):
        return price*qty

    def total_price_global(self, moves):
        total_price = 0.0
        for line in moves:
            total = line.list_price*line.product_uom_qty
            total_price += total
        return 

    def total_price_client_global(self, moves):
        total_price_client = 0.0
        for line in moves:
            total = line.list_price_client*line.product_uom_qty
            total_price_client += total
        return 

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False,
                            loc_dest_id=False, partner_id=False):
        """ On change of product id, if finds UoM, UoS, quantity and UoS quantity.
        @param prod_id: Changed Product id
        @param loc_id: Source location id
        @param loc_dest_id: Destination location id
        @param partner_id: Address id of partner
        @return: Dictionary of values
        """
        if not prod_id:
            return {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        lang = user and user.lang or False
        if partner_id:
            addr_rec = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if addr_rec:
                lang = addr_rec and addr_rec.lang or False
        ctx = {'lang': lang}

        product = self.pool.get('product.product').browse(cr, uid, [prod_id], context=ctx)[0]
        uos_id  = product.uos_id and product.uos_id.id or False
        result = {
            'product_uom': product.uom_id.id,
            'product_uos': uos_id,
            'product_qty': 1.00,
            'product_uos_qty' : self.pool.get('stock.move').onchange_quantity(cr, uid, ids, prod_id, 1.00, product.uom_id.id, uos_id)['value']['product_uos_qty'],
            'prodlot_id' : False,
            'list_price': product.list_price,
        }
        if not ids:
            result['name'] = product.partner_ref
        if loc_id:
            result['location_id'] = loc_id
        if loc_dest_id:
            result['location_dest_id'] = loc_dest_id
        return {'value': result}

class stock_picking(osv.osv):
    _name = 'stock.picking'
    _inherit ='stock.picking'

    def _amount(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):          
            total_price_global = 0.0
            total_price_client_global = 0.0
            qty_total = 0.0
            if record.pack_operation_ids:
                for line in record.move_lines:
                    total = line.list_price*line.product_qty
                    total2 = line.list_price_client*line.product_qty
                    total_price_global += total
                    total_price_client_global += total2
                    qty_total += line.product_qty
            else:
                for line in record.move_lines:
                    total = line.list_price*line.product_uom_qty
                    total2 = line.list_price_client*line.product_uom_qty
                    total_price_global += total
                    total_price_client_global += total2
                    qty_total += line.product_uom_qty
            res[record.id] =   {
                            'total_price_global'  :   total_price_global,
                            'total_price_client_global':   total_price_client_global,
                            'qty_total': qty_total,
                    }
        return res

    _columns = {
        'total_price_global'      : fields.function(_amount, method=True, string='Total Publico', type='float', digits=(14,2), multi=True, store=True),
        'total_price_client_global'    : fields.function(_amount, method=True, string='Total Cliente', type='float', digits=(14,2), multi=True, store=True),
        'qty_total'    : fields.function(_amount, method=True, string='Cantidad Total', type='float', digits=(14,2), multi=True, store=True),
        }

    _defaults = {
        }


# class report_stock_picking(osv.osv):
#     _name = 'report.stock.picking'
#     _description = 'Albaranes Internos'
#     _columns = {
#         }

#     _defaults = {
#         }

#     def init(self, cr,):
#         report_obj = self.pool.get('ir.actions.report.xml')
#         report_id = report_obj.search(cr, SUPERUSER_ID, [('report_file','=','stock/report/picking.rml')])
#         if report_id:
#             report_obj.write(cr, SUPERUSER_ID, report_id, {'report_file':'in_picking_extend/report/picking.rml'})
#         return True

# report_stock_picking()