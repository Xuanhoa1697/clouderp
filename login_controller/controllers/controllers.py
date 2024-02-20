# Copyright 2021 Artem Shurshilov

import werkzeug
from odoo import _, http
from odoo.http import request
import odoo


class Login(http.Controller):

    @http.route('/web/api/v1/mobile_authen',  type='json', auth="none")
    def enapp_authenticate(self, db, login, password, base_location=None):
        message = 'Success'
        code = 200
        session_id = ''
        uid = False
        display_name = ''
        company = ''
        images = False
        try:
            if not http.db_filter([db]):
                message = 'Access Denied'
            uid = request.session.authenticate(request.db, request.params['login'], request.params['password'])
            if uid and uid != request.session.uid:
                message = 'Access Denied'
                code = 500
            if (uid):
                request.session.db = db
                registry = odoo.modules.registry.Registry(db)
                with registry.cursor() as cr:
                    env = odoo.api.Environment(cr, request.session.uid, request.session.context)
                    session_info = env['ir.http'].session_info()
                    display_name =  env.user.sudo().login
                    company = env.company.sudo().display_name
                    images = env['ir.config_parameter'].sudo().get_param('web.base.url') + '/web/image?model=res.partner&id=%s&field=avatar_128' % env.user.sudo().partner_id.id
                    if session_info:
                        session_id = request.session.sid
        except odoo.exceptions.AccessDenied as e:
            message = 'Access Denied'
            code = 500
        
        return {
            'code': code,
            'msg': message,
            'user': {
                'session_id': session_id,
                'display_name': display_name,
                'company': company,
                'images': images
            }
        }

    @http.route("/web/api/v1/odoo_app_authenticate", type="http", auth="none", methods=["GET"], csrf=False)
    def login_action(self, login, password, db=None, url=None, force="", mod_file=None, **kw):
        if db and db != request.db:
            raise Exception(_("Could not select database '%s'") % db)
        request.session.authenticate(request.db, login, password)
        return werkzeug.utils.redirect("/web")