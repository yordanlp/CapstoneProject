from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*", engineio_logger=True)
