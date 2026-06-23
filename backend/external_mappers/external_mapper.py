class ExternalMapper:
    MAPPINGS = {
        'codigo': 'code', 'nombre': 'name', 'correlativas': 'correlatives',
        'materiaId': 'subject_id', 'docenteId': 'teacher_id', 'materia': 'subject', 'finalId': 'final_id',
        'notas': 'grades', 'departamento': 'department', 'codigos': 'codes'
    }

    def map(self, data):
        if type(data) is list:
            return [self._map(el) for el in data]
        elif type(data) is dict:
            return self._map(data)
        else:
            return data

    def _map(self, data):
        res = {}
        for key, val in data.items():
            if type(val) is list:
                res[self.MAPPINGS.get(key, key)] = [self.map(el) for el in val]
            elif type(val) is dict:
                res[self.MAPPINGS.get(key, key)] = self.map(val)
            else:
                res[self.MAPPINGS.get(key, key)] = val
        return res
