##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, orm
import openerp.addons.decimal_precision as dp


class account_invoice_line(orm.Model):
    _inherit = 'account.invoice.line'

    def _compute_line_amount_in_company_currency(self, cr, uid, ids, field_names, args, context=None):
        """Compute the amounts in the currency of the company
        """
        if context is None:
            context = {}
        currency_obj = self.pool['res.currency']
        res = {}
        ctx = context.copy()
        for item in self.browse(cr, uid, ids, context=context):
            try:
                invoice_currency_id = item.invoice_id.currency_id.id
                company_currency_id = item.company_id.currency_id.id
            except AttributeError:
                # no currency for one
                res[item.id] = False
                continue

            ctx['date'] = item.invoice_id.date_invoice

            if invoice_currency_id == company_currency_id:
                res[item.id] = item.price_subtotal
            else:
                res[item.id] = currency_obj.compute(
                    cr, uid,
                    invoice_currency_id, company_currency_id, item.price_subtotal,
                    context=ctx)

        return res

    _columns = {
        'price_subtotal_in_currency': fields.function(
            _compute_line_amount_in_company_currency,
            string="Total Without Tax", type='float',
            digits_compute=dp.get_precision('Account'),
            store={
                "account.invoice.line": (
                    lambda self, cr, uid, ids, c={}: ids,
                    ["invoice_id", "company_id", "price_subtotal"],
                    10),
                "account.invoice": (
                    lambda self, cr, uid, ids, c={}: self.pool["account.invoice.line"].search(
                        cr, uid, [('invoice_id', 'in', ids)], context=c),
                    ["date_invoice", "invoice_line", "state", "currency_id"],
                    5),
            }),
    }
