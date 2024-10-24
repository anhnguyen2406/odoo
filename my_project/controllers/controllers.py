# -*- coding: utf-8 -*-
# from odoo import http


# class MyProject(http.Controller):
#     @http.route('/my_project/my_project/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/my_project/my_project/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('my_project.listing', {
#             'root': '/my_project/my_project',
#             'objects': http.request.env['my_project.my_project'].search([]),
#         })

#     @http.route('/my_project/my_project/objects/<model("my_project.my_project"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('my_project.object', {
#             'object': obj
#         })
