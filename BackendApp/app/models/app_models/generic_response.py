from ...utils import object_to_dict

class GenericResponse:
    def __init__( self, data = None, errors = None ):
        self.data = None
        self.errors = None
        self.success = False
        
        if errors == None:
            self.success = True
            self.data = data
        else:
            self.success = False
            self.errors = errors

    def to_dict(self):
        return { 'success': self.success, 'data': self.data, 'errors': self.errors }