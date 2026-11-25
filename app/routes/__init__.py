from app.routes.main import main_bp
from app.routes.geo import geo_bp
from app.routes.legal import legal_bp
from app.routes.seo import seo_bp
from app.routes.admin import admin_bp


def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(geo_bp)
    app.register_blueprint(legal_bp)
    app.register_blueprint(seo_bp)
    app.register_blueprint(admin_bp)
