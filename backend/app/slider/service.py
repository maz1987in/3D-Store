## service layer of the API
import json
import sqlalchemy as sql

from flask import current_app
from sqlalchemy_filters import apply_pagination, apply_sort
from app.common.enum import PlatformEnum
from app.common.error_handling import ResourceNotFoundError
from app.utilities.common_utils import change_string_to_time, debug_return, validate_file_content
from config import BaseConfig, Config
from .model import Slider, SliderType
from app.common import filters_serialization
from app.common.queries import create_sorters, filter_and_sort_query
from app.utilities import request_utils
from datetime import datetime, timezone
import uuid
from extensions import cache
from app.utilities.db_utils import session_scope
from app.utilities.error_utils import handle_errors  # Import the decorator

ALLOWED_CONTENT_TYPES = {'image/svg+xml', 'image/png', 'image/jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif']

class SliderService:
    def get_slider_model(self, sliders):
        if isinstance(sliders, list):
            return [slider.json() for slider in sliders]
        return sliders.json()

    @handle_errors("Slider")
    def get_sliders(self, id, filter): 
        with session_scope() as session:
            query = session.query(Slider)
            result = None
            if id is None:
                if filter.sort is None:
                    filter.sorters = create_sorters('modified_date', 'desc')
                query = filter_and_sort_query(filter.filters, filter.sorters, query, Slider)

                query, pagination = apply_pagination(query, page_number=int(filter.page), page_size=int(filter.per_page))
                sliders = query.all()
                result = {'sliders': self.get_slider_model(sliders), 'filters': filters_serialization.get_pagination_serialization(pagination, filter.sort, filter.sort_order, filter.queries)}
            else:
                sliders = query.filter_by(id=id).first()
                if sliders is None:
                    raise ResourceNotFoundError("Slider")
                result = {'sliders': self.get_slider_model(sliders)}
            return result, 200

    @handle_errors("Slider")
    def create_slider(self, data, image):
        with session_scope() as session:
            if image and (not allowed_file(image.filename) or not validate_file_content(image, ALLOWED_CONTENT_TYPES)):
                return 'File type is not allowed', 400
            slider = Slider(
                id=uuid.uuid4(),
                enable=request_utils.str_to_bool(data, 'enable', False),
                from_date=change_string_to_time(data['from_date']),
                to_date=change_string_to_time(data['to_date']),
                order=data['order'],
                url=request_utils.not_exisit_in_request(data, 'url'),
                slider_type=data['slider_type'],
                image=image,
                platform=data['platform'],
                create_date=datetime.now(timezone.utc),
                modified_date=datetime.now(timezone.utc)
            )  # type: ignore

            for local in Config.AVAILABLE_LOCALES.keys():
                slider.translations[local].title = data['title'][local]
                slider.translations[local].content = data['content'][local]

            session.add(slider)
            session.commit()
            cache.delete_memoized(self.get_slider_today)

            return 'Slider Created', 201

    @handle_errors("Slider")
    def update_slider(self, id, data, image):
        with session_scope() as session:
            if image and (not allowed_file(image.filename) or not validate_file_content(image, ALLOWED_CONTENT_TYPES)):
                return 'File type is not allowed', 400

            slider = session.query(Slider).filter_by(id=id).first()
            if slider is None:
                raise ResourceNotFoundError("Slider")

            slider.enable = request_utils.str_to_bool(data, 'enable', False)
            slider.order = data['order']
            slider.from_date = change_string_to_time(data['from_date'])
            slider.to_date = change_string_to_time(data['to_date'])
            slider.url = request_utils.not_exisit_in_request(data, 'url')
            slider.slider_type = data['slider_type']
            slider.image = image or slider.image
            slider.platform = data['platform']
            slider.modified_date = datetime.now(timezone.utc)
            for local in Config.AVAILABLE_LOCALES.keys():
                slider.translations[local].title = data['title'][local]
                slider.translations[local].content = data['content'][local]

            session.commit()
            cache.delete_memoized(self.get_slider_today)
            return 'Updated', 200

    @handle_errors("Slider")
    def delete_slider(self, id):
        with session_scope() as session:
            slider = session.query(Slider).filter_by(id=id).first()
            if slider is None:
                raise ResourceNotFoundError("Slider")

            session.delete(slider)
            session.commit()

            return 'Slider deleted', 200

    @cache.memoize(60 * 60)
    @handle_errors("Slider")
    def get_slider_today(self, platform):
        with session_scope() as session:
            query = session.query(Slider).filter(
                Slider.from_date <= datetime.now(timezone.utc),
                Slider.to_date >= datetime.now(timezone.utc),
                Slider.enable == True
            )
            if platform is PlatformEnum.ALL:
                query = query.filter_by(platform=PlatformEnum.ALL)
            elif platform in (PlatformEnum.ANDROID, PlatformEnum.IOS):
                query = query.filter(Slider.platform.in_((PlatformEnum.ALL, PlatformEnum.MOBILE, platform)))
            else:
                query = query.filter(Slider.platform.in_((PlatformEnum.ALL, platform)))
            query = query.order_by(Slider.order)
            sliders = query.all()

            if not sliders:
                raise ResourceNotFoundError("Slider")

            return {'sliders': self.get_slider_model(sliders)}, 200

    @handle_errors("SliderType")
    def get_slider_types(self):
        with session_scope() as session:
            slider_types = session.query(SliderType).all()
            return [{'name': slider_type.name} for slider_type in slider_types], 200

    @handle_errors("SliderType")
    def create_slider_type(self, data):
        with session_scope() as session:
            slider_type = SliderType(name=data['name'])  # type: ignore
            session.add(slider_type)
            session.commit()
            return 'Slider Type Created', 201

    @handle_errors("SliderType")
    def update_slider_type(self, name, data):
        with session_scope() as session:
            slider_type = session.query(SliderType).filter_by(name=name).first()
            if slider_type is None:
                raise ResourceNotFoundError("SliderType")

            slider_type.name = data['name']
            slider_type.modified_date = datetime.now(timezone.utc)
            session.commit()
            return 'Slider Type Updated', 200

    @handle_errors("SliderType")
    def delete_slider_type(self, name):
        with session_scope() as session:
            slider_type = session.query(SliderType).filter_by(name=name).first()
            if slider_type is None:
                raise ResourceNotFoundError("SliderType")

            session.delete(slider_type)
            session.commit()
            return 'Slider Type deleted', 200