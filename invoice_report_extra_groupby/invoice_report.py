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
import re
from openerp.osv import fields, orm


RATE = r'(?P<field>sub.price_(total|average))\s*/\s*cr.rate as (?P<field_as>price_*)'
RATE_SUB = '\g<field> as \g<field_as>'


class account_invoice_report(orm.Model):
    _inherit = 'account.invoice.report'
    _columns = {
        'partner_country_id': fields.many2one('res.country', 'Partner Country'),
        'section_id': fields.many2one('crm.case.section', 'Sales Team'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True),
        'total_in_currency': fields.float('Total', readonly=True),
    }

    def _select(self):
        select = super(account_invoice_report, self)._select()
        select = re.sub(RATE, RATE_SUB, select, flags=re.I)
        invoice = ", sub.invoice_id as invoice_id"
        country = ", sub.partner_country_id as partner_country_id"
        section = ", sub.section_id as section_id"
        total = ", sub.price_total_in_currency as total_in_currency"
        res = [select, invoice, country, total]
        if section not in select:
            res.append(section)

        return "".join(res)

    def _sub_select(self):
        select = super(account_invoice_report, self)._sub_select()
        invoice = ", ai.id as invoice_id"
        section = ", ai.section_id as section_id"
        country = ", rp.country_id as partner_country_id"
        total = """, SUM(CASE
            WHEN ai.type::text = ANY (
                ARRAY['out_refund'::character varying::text,
                'in_invoice'::character varying::text]
            )
            THEN - ail.price_subtotal_in_currency
            ELSE ail.price_subtotal_in_currency
            END) AS price_total_in_currency
        """
        res = [select, invoice, country, total]
        if section not in select:
            res.append(section)

        return "".join(res)

    def _from(self):
        return super(account_invoice_report, self)._from() + """
            LEFT JOIN res_partner rp ON ai.partner_id = rp.id
        """

    def _group_by(self):
        group = super(account_invoice_report, self)._group_by()
        section = ", ai.section_id"
        country = ", rp.country_id"
        if section in group:
            return group + country
        else:
            return group + country + section

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
