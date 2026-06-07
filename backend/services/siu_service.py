from backend.client.siu_client import SiuClient
from backend.external_mappers.external_mapper import ExternalMapper


class SiuService:
    def __init__(self):
        self.client = SiuClient()

    def list_subjects(self, filters=None):
        return ExternalMapper().map(self.client.list_subjects(filters))

    def get_subject(self, subject_siu_id):
        return ExternalMapper().map(self.client.get_subject(subject_siu_id))

    def correlative_subjects(self, subject):
        return ExternalMapper().map(self.client.list_correlatives(subject))

    def create_final(self, teacher_siu_id, subject_siu_id, timestamp):
        return self.client.create_final(teacher_siu_id, subject_siu_id, timestamp)

    def create_final_act(self, final):
        return ExternalMapper().map(self.client.create_act(final.siu_id, final.teacher.siu_id, self._build_grades(final.final_exams.all())))

    def save_final_grades(self, final):
        return ExternalMapper().map(self.client.save_final_grades(final.siu_id, final.teacher.siu_id, self._build_grades(final.final_exams.all())))

    def _build_grades(self, final_exams):
        return {fe.student.padron: fe.grade for fe in final_exams}
