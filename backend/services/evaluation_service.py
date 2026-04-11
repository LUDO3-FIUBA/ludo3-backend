from backend.models import Evaluation


class EvaluationService:
    def create(self, validated_data):
        evaluation = Evaluation(**validated_data)
        evaluation.full_clean()
        evaluation.save()
        return evaluation

    def update(self, evaluation: Evaluation, validated_data):
        for attr, value in validated_data.items():
            setattr(evaluation, attr, value)

        if not evaluation.is_gradeable:
            evaluation.passing_grade = None

        evaluation.full_clean()
        evaluation.save()
        return evaluation
