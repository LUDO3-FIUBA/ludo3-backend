import os

from backend.client.client_handler import ClientHandler


class SiuClient:
    SIU_URL = os.environ.get("SIU_URL")
    API_KEY = os.environ.get("SIU_API_KEY")

    def __init__(self, handler=ClientHandler()):
        self.handler = handler

    def list_subjects(self, filters=None, query=""):
        query = "?" + "&".join(f"{k}={v}" for k, v in filters.items()) if filters else query
        return self._get(f"materias/{query}")

    def get_subject(self, subject_siu_id):
        return self._get(f"materias/{subject_siu_id}")

    def list_correlatives(self, subject):
        if not subject['correlatives']:
            return []
        query = "?codigo[]=" + "&codigo[]=".join(subject['correlatives'])
        return self.list_subjects(None, query)

    def create_final(self, teacher_siu_id, subject_siu_id, timestamp):
        data = {'materia_id': subject_siu_id, 'timestamp': timestamp}
        return self._post(f"docentes/{teacher_siu_id}/finales", data=data)

    def save_final_grades(self, final_siu_id, teacher_siu_id, grades):
        return self._post(f"docentes/{teacher_siu_id}/finales/{final_siu_id}/cargar_notas", data=grades)

    def create_act(self, final_siu_id, teacher_siu_id, grades): # TODO: fix no grades only padrones
        data = {"finalId": final_siu_id, "notas": grades}
        return self._post(f"docentes/{teacher_siu_id}/finales/{final_siu_id}/subir_acta", data=data)

    def _post(self, url, params=None, data=None, headers={}):
        return self.handler.post(f"{self.SIU_URL}/{url}", params, data, self._add_api_key_header(headers))

    def _get(self, url, params=None, headers={}):
        return self.handler.get(f"{self.SIU_URL}/{url}", params, self._add_api_key_header(headers))

    def _add_api_key_header(self, headers):
        return {**headers, **{'api_key': self.API_KEY}}
