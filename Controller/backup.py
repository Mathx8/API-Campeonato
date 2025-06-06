from flask import Blueprint, jsonify
from Backup.backup import *

Backup_Blueprint = Blueprint('backup', __name__)

@Backup_Blueprint.route('/', methods=['POST'])
def backup():
    try:
        backup_file = create_sqlite_backup()
        return {
            "status": "Backup concluído!",
            "backup_file": backup_file,
            "timestamp": datetime.now().isoformat()
        }, 200
    except Exception as e:
        return {
            "status": "Erro no backup",
            "error": str(e)
        }, 500