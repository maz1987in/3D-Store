import json 
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g
from app.common.enum import PlatformEnum

from app.security import roles, permissions
from app.common import filters

from .model import PrintJob, PrintJobLog, Printer, PrinterMaterial
from app.utilities.db_utils import get_session_with_retries
import uuid
from datetime import datetime, timezone

__uri__ = 'print-jobs'
__blueprint__ = 'print_jobs'

print_jobs = Blueprint(__uri__, __name__)

@print_jobs.route('/', methods=['GET'])
def get_print_jobs():
    """Get all print jobs"""
    try:
        with get_session_with_retries() as session:
            jobs = session.query(PrintJob).all()
            return jsonify({
                'status': 200,
                'message': 'Success',
                'data': [job.json() for job in jobs]
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error retrieving print jobs: {str(e)}',
            'data': []
        }), 500

@print_jobs.route('/<job_id>', methods=['GET'])
def get_print_job(job_id):
    """Get a specific print job by ID"""
    try:
        with get_session_with_retries() as session:
            job = session.query(PrintJob).filter(PrintJob.id == job_id).first()
            if not job:
                return jsonify({
                    'status': 404,
                    'message': 'Print job not found',
                    'data': None
                }), 404
            
            return jsonify({
                'status': 200,
                'message': 'Success',
                'data': job.json()
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error retrieving print job: {str(e)}',
            'data': None
        }), 500

@print_jobs.route('/', methods=['POST'])
def create_print_job():
    """Create a new print job"""
    try:
        data = request.get_json()
        
        with get_session_with_retries() as session:
            job = PrintJob(
                id=uuid.uuid4(),
                order_id=data.get('order_id'),
                user_id=data.get('user_id'),
                model_file_name=data.get('model_file_name'),
                model_file_size=data.get('model_file_size'),
                model_file_type=data.get('model_file_type'),
                material_id=data.get('material_id'),
                print_settings_id=data.get('print_settings_id'),
                packaging_id=data.get('packaging_id'),
                quantity=data.get('quantity', 1),
                scale_x=data.get('scale_x', 1.0),
                scale_y=data.get('scale_y', 1.0),
                scale_z=data.get('scale_z', 1.0),
                custom_instructions=data.get('custom_instructions'),
                priority=data.get('priority', 0)
            )
            
            session.add(job)
            session.commit()
            
            return jsonify({
                'status': 201,
                'message': 'Print job created successfully',
                'data': job.json()
            }), 201
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error creating print job: {str(e)}',
            'data': None
        }), 500

@print_jobs.route('/<job_id>/status', methods=['PUT'])
def update_print_job_status(job_id):
    """Update print job status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        with get_session_with_retries() as session:
            job = session.query(PrintJob).filter(PrintJob.id == job_id).first()
            if not job:
                return jsonify({
                    'status': 404,
                    'message': 'Print job not found',
                    'data': None
                }), 404
            
            old_status = job.status.value if job.status else None
            job.status = new_status
            
            # Update timestamps based on status
            now = datetime.now(timezone.utc)
            if new_status == 'queued':
                job.queued_at = now
            elif new_status == 'printing':
                job.started_at = now
            elif new_status == 'completed':
                job.completed_at = now
            elif new_status == 'failed':
                job.failed_at = now
            
            # Create log entry
            log = PrintJobLog(
                id=uuid.uuid4(),
                print_job_id=job_id,
                status_from=old_status,
                status_to=new_status,
                message=f'Status changed from {old_status} to {new_status}',
                log_type='status_change'
            )
            session.add(log)
            session.commit()
            
            return jsonify({
                'status': 200,
                'message': 'Print job status updated successfully',
                'data': job.json()
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error updating print job status: {str(e)}',
            'data': None
        }), 500

@print_jobs.route('/printers', methods=['GET'])
def get_printers():
    """Get all available printers"""
    try:
        with get_session_with_retries() as session:
            printers = session.query(Printer).filter(Printer.is_active == True).all()
            return jsonify({
                'status': 200,
                'message': 'Success',
                'data': [printer.json() for printer in printers]
            })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error retrieving printers: {str(e)}',
            'data': []
        }), 500

@print_jobs.route('/printers', methods=['POST'])
def create_printer():
    """Create a new printer"""
    try:
        data = request.get_json()
        
        with get_session_with_retries() as session:
            printer = Printer(
                id=uuid.uuid4(),
                name=data.get('name'),
                model=data.get('model'),
                manufacturer=data.get('manufacturer'),
                build_volume_x=data.get('build_volume_x'),
                build_volume_y=data.get('build_volume_y'),
                build_volume_z=data.get('build_volume_z'),
                layer_resolution=data.get('layer_resolution'),
                nozzle_diameter=data.get('nozzle_diameter'),
                status=data.get('status', 'available'),
                location=data.get('location'),
                branch_id=data.get('branch_id'),
                hourly_rate=data.get('hourly_rate', 0),
                electricity_cost_per_hour=data.get('electricity_cost_per_hour', 0)
            )
            
            session.add(printer)
            session.commit()
            
            return jsonify({
                'status': 201,
                'message': 'Printer created successfully',
                'data': printer.json()
            }), 201
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error creating printer: {str(e)}',
            'data': None
        }), 500

@print_jobs.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for print job service"""
    return jsonify({
        'status': 200,
        'message': 'Print Job service is running',
        'data': {
            'service': '3D Store Print Job Service',
            'version': '1.0.0',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    })






