from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = "account.move.line"

    warranty_id = fields.Many2one('rel.warranty', related='product_id.warranty_id', string='Warranty')