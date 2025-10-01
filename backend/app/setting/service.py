## service layer of the API
import json
import sqlalchemy as sql
from flask import current_app
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import debug_return
from .model import Setting
from datetime import datetime, timezone
from app.utilities.db_utils import session_scope
from app.utilities.error_utils import handle_errors  # Import the decorator

class SettingService:
    def get_setting_model(self, settings):
        if isinstance(settings, list):
            return [setting.json() for setting in settings]
        return settings.json()

    def get_setting_config_model(self, settings):
        result = {}
        for setting in settings:
            result.setdefault(setting.category, {})
            result[setting.category][setting.key] = setting.value
        return result

    @handle_errors("Setting")
    def get_settings(self, key): 
        with session_scope() as session:
            query = session.query(Setting)
            if key is None:
                settings = query.all()
            else:
                settings = query.filter_by(key=key).first()
            if settings is None:
                raise ResourceNotFoundError("Setting")
            result = {'settings': self.get_setting_model(settings)}
            return result, 200

    @handle_errors("Setting")
    def get_setting_for_config(self):
        with session_scope() as session:
            query = session.query(Setting).order_by(Setting.category)
            settings = query.all()
            return self.get_setting_config_model(settings)

    @handle_errors("Setting")
    def get_settings_by_category_list(self, category_list):
        with session_scope() as session:
            settings = session.query(Setting).filter(Setting.category.in_(category_list)).all()
            result = {i.key: i.value for i in settings} if settings else None
            return result, 200

    @handle_errors("Setting")
    def get_settings_by_category(self, category): 
        with session_scope() as session:
            settings = session.query(Setting).filter_by(category=category).all()
            result = {i.key: i.value for i in settings} if settings else None
            if result is None:
                raise ResourceNotFoundError("Setting")
            result = {'settings': result}
            return result, 200

    @handle_errors("Setting")
    def update_setting(self, category, data):
        with session_scope() as session:
            items = data['items']
            for item in items:
                setting = session.query(Setting).filter(Setting.category == category, Setting.key == item['key']).first()
                if setting.value != item['value']:
                    setting.value = item['value']
                    setting.last_modified = datetime.now(timezone.utc)
            session.commit()
            return 'Updated', 200

    @handle_errors("Setting")
    def update_setting_key(self, key, data):
        with session_scope() as session:
            setting = session.query(Setting).filter(Setting.key == key).first()
            if setting is None:
                raise ResourceNotFoundError("Setting")
            setting.value = data['value']
            session.commit()
            return 'Updated', 200

    @handle_errors("Setting")
    def create_setting(self, data):
        with session_scope() as session:
            category = data['category'].strip()
            items = data['items']
            for item in items:
                setting = Setting(
                    key=item['key'].strip().upper(),
                    category=category,
                    value=item['value'],
                    last_modified=datetime.now(timezone.utc)
                )
                session.add(setting)
            session.commit()
            return 'Setting Created', 201

    @handle_errors("Setting")
    def create_setting_from_config(self, dict_data):
        with session_scope() as session:
            for category, values in dict_data.items():
                for key, value in values.items():
                    setting = session.query(Setting).filter(Setting.category == category, Setting.key == key).first()
                    if setting:
                        setting.value = str(value)
                    else:
                        setting = Setting(
                            key=key,
                            category=category,
                            value=str(value),
                            last_modified=datetime.now(timezone.utc)
                        )
                        session.add(setting)
            session.commit()
            return 'Setting Created', 201

    @handle_errors("Setting")
    def delete_setting(self, key):
        with session_scope() as session:
            setting = session.query(Setting).filter(Setting.key == key).first()
            if setting is None:
                raise ResourceNotFoundError("Setting")
            session.delete(setting)
            session.commit()
            return 'Setting deleted', 200

    @handle_errors("Setting")
    def setup_config_from_db(self):
        settings = self.get_setting_for_config()
        for key, value in settings.items():
            current_app.config[key] = value
        return 'Setting reconfig', 201