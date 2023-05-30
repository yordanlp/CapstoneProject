from ...utils import object_to_dict

class GenericResponse:
    def __init__( self, data = None, errors = None, code = 200 ):
        self.data = None
        self.errors = None
        self.success = False
        self.code = code

        if code == 500:
            errors = ["Something wrong happend, contact the administrator if it persists"]
        
        if errors == None:
            self.success = True
            self.data = data
        else:
            self.success = False
            self.errors = errors

    def to_dict(self):
        return { 'success': self.success, 'data': self.data, 'errors': self.errors }