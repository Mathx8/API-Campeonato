from flask_restx import Namespace, Resource, fields
from datetime import datetime
from Backup.backup import create_sqlite_backup
from Controller.decorators import editor_ou_admin

backup_ns = Namespace('Backup', description='Operações de backup do banco de dados')

backup_success_model = backup_ns.model('BackupSuccess', {
    'status': fields.String(description='Status do backup', example='Backup concluído!'),
    'backup_file': fields.String(description='Caminho do arquivo de backup gerado', example='backups/backup_20240525_143022.db'),
    'timestamp': fields.String(description='Timestamp da operação', example='2024-05-25T14:30:22')
})

backup_error_model = backup_ns.model('BackupError', {
    'status': fields.String(description='Status de erro', example='Erro no backup'),
    'error': fields.String(description='Mensagem detalhada do erro', example='Falha ao acessar o banco de dados')
})

@backup_ns.route('/')
class BackupResource(Resource):
    @backup_ns.doc(description='Cria um backup completo do banco em formato SQLite')
    @backup_ns.response(200, 'Backup realizado com sucesso', backup_success_model)
    @backup_ns.response(500, 'Erro durante o backup', backup_error_model)
    @editor_ou_admin
    def post(self):
        """Backup para o banco local"""
        try:
            backup_file = create_sqlite_backup()
            return {
                'status': 'Backup concluído!',
                'backup_file': backup_file,
                'timestamp': datetime.now().isoformat()
            }, 200
        except Exception as e:
            return {
                'status': 'Erro no backup',
                'error': str(e)
            }, 500