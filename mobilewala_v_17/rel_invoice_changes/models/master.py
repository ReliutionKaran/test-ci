from odoo import fields, models, api


class RelWarranty(models.Model):
    _name = "rel.warranty"
    _rec_name = "warranty"

    warranty = fields.Char(string='Warranty')


class RelColor(models.Model):
    _name = "rel.color"
    _rec_name = "color"

    color = fields.Char(string="Color")
