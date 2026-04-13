import rule_engine

from backend.utils import datetime_format, is_before_current_datetime


class RuleEngineService:
    
    def __init__(self):
        self.rules = []
        self.evaluation_rules = []


    def generate_passed_rules(self, semester):
        print("PASSED RULES:")
        if(semester['classes_amount'] and semester['minimum_attendance']):
            max_absences = semester['classes_amount'] - (semester['classes_amount'] * semester['minimum_attendance'])
            self.add_remaining_assistance_threshold(max_absences)

        evaluations_accounted_for = []
        evaluations = semester['evaluations']
        evaluations.sort(key=lambda x: datetime_format(x['end_date']))
        for evaluation in evaluations:
            if (evaluation not in evaluations_accounted_for) and evaluation['is_graded']:
                evaluations_for_rule = []
                evaluations_for_rule.append(evaluation)
                while evaluation['make_up_evaluation']:
                    evaluation = evaluation['make_up_evaluation']
                    evaluations_for_rule.append(evaluation)
                self.add_evaluation_passed_rule(evaluations_for_rule)
                evaluations_accounted_for.extend(evaluations_for_rule)


    def add_evaluation_passed_rule(self, evaluations):
        rule_string = ""
        for evaluation in evaluations:
            rule_string += f'(evaluation.evaluation_name == "{evaluation["evaluation_name"]}" and grade != null and grade >= {evaluation["passing_grade"]}) or '
        rule_string = rule_string[:-4]
        rule = rule_engine.Rule(rule_string)
        print(rule_string)
        self.evaluation_rules.append(rule)


    def add_remaining_assistance_threshold(self, max_absences):
        rule = rule_engine.Rule(f'(absences + remaining_lectures) <= {max_absences}')
        print(f'(absences + remaining_lectures) <= {max_absences}')
        self.rules.append(rule)


    
    def is_student_passed(self, attendanceQRs, evaluation_submissions, student, semester):
        print("PASSED EVALUATION:")
        model_for_rules = {}
        model_for_rules['absences'] = self.get_absences(attendanceQRs, student)
        model_for_rules['remaining_lectures'] = semester['classes_amount'] - len(attendanceQRs)
        print(model_for_rules)
        is_passing = True

        for rule in self.rules:
            is_passing = is_passing and rule.evaluate(model_for_rules)

        print(is_passing)

        for rule in self.evaluation_rules:
            passing_evaluations = rule.filter(evaluation_submissions)
            is_empty = True
            for evaluation in passing_evaluations:
                is_empty = False
            is_passing = is_passing and not is_empty

        print(is_passing)
        
        return is_passing


    def add_evaluation_failed_rule(self, evaluations):
        rule_string = ""
        for evaluation in evaluations:
            rule_string += f'(evaluation.evaluation_name == "{evaluation["evaluation_name"]}" and (grader == null or grade >= {evaluation["passing_grade"]})) or '
        rule_string = rule_string[:-4]
        rule = rule_engine.Rule(rule_string)
        print(rule_string)
        self.evaluation_rules.append(rule)
    

    def add_assistance_threshold(self, max_absences):
        rule = rule_engine.Rule(f'absences <= {max_absences}')
        print(f'absences <= {max_absences}')
        self.rules.append(rule)


    def generate_failed_rules(self, semester):
        print("FAILED RULES:")
        if(semester['classes_amount'] and semester['minimum_attendance']):
            max_absences = semester['classes_amount'] - (semester['classes_amount'] * semester['minimum_attendance'])
            self.add_assistance_threshold(max_absences)

        evaluations_accounted_for = []
        evaluations = semester['evaluations']
        evaluations.sort(key=lambda x: datetime_format(x['end_date']))
        for evaluation in evaluations:
            if (evaluation not in evaluations_accounted_for) and evaluation['is_graded']:
                add_rule = True
                evaluations_for_rule = []
                evaluations_for_rule.append(evaluation)
                if(not is_before_current_datetime(evaluation['end_date'])):     #Todavia se puede entregar
                    add_rule = False
                while evaluation['make_up_evaluation']:
                    evaluation = evaluation['make_up_evaluation']
                    evaluations_for_rule.append(evaluation)
                    if(not is_before_current_datetime(evaluation['end_date'])): #Todavia se puede recuperar
                        add_rule = False
                if add_rule:
                    self.add_evaluation_failed_rule(evaluations_for_rule)
                evaluations_accounted_for.extend(evaluations_for_rule)

    
    def is_student_failed(self, attendanceQRs, evaluation_submissions, student):
        print("FAILED EVALUATION:")
        model_for_rules = {}
        model_for_rules['absences'] = self.get_absences(attendanceQRs, student)
        is_still_passing = True

        for rule in self.rules:
            is_still_passing = is_still_passing and rule.evaluate(model_for_rules)

        for rule in self.evaluation_rules:
            passing_evaluations = rule.filter(evaluation_submissions)
            is_empty = True
            for evaluation in passing_evaluations:
                is_empty = False
            is_still_passing = is_still_passing and not is_empty

        print(not is_still_passing)
        print(model_for_rules)
        
        return not is_still_passing
        

    
    def get_absences(self, attendanceQRs, student):
        absences = 0
        for attendances in attendanceQRs:
            is_absent = True
            for attendance in attendances['attendances']:
                a_student = attendance['student']
                if a_student['id'] == student['id']:
                    is_absent = False
            if is_absent:
                absences = absences + 1
        return absences



""" rule = rule_engine.Rule(f'average.exam >= 7 and average.name == "Examen 1"')
isValid = rule.is_valid(f'average.exam >= 7 and average.name == "Examen 1"')
evaluateReturn = rule.evaluate({'average': {'exam': 7, 'name': 'Examen 1'}})
matchesReturn = rule.matches({'average': {'exam': 6}})
filterReturn = rule.filter([{'average': {'exam': 7, 'name': 'Examen 1'}}, {'average': {'exam': 7, 'name': 'Examen 2'}}])
isValid = True
isEmpty = True
for result in filterReturn:
    isEmpty = False
    currentResult = result
isTrue = isValid and not isEmpty
isValid = True """