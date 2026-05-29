import logging
from unittest import mock

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase

from backend.services.evaluation_submission_service import EvaluationSubmissionService
from backend.services.grader_assignment_service import GraderAssignmentService
from tests.factories import (
    CommissionFactory,
    EvaluationFactory,
    SemesterFactory,
    SubmissionFactory,
    TeacherFactory,
    TeacherRoleFactory,
    StudentFactory,
)


class GraderAssignmentServiceTests(APITestCase):
    def setUp(self) -> None:
        # Setup necessary objects for testing
        self.teacher = TeacherFactory()
        self.commission = CommissionFactory(chief_teacher=self.teacher)
        self.semester = SemesterFactory(commission=self.commission)
        self.student = StudentFactory()

        self.evaluation = EvaluationFactory(semester=self.semester, is_gradeable=True)
        self.non_numeric_evaluation = EvaluationFactory(semester=self.semester, is_gradeable=False)
        
        self.submissions = SubmissionFactory.create_batch(5, evaluation=self.evaluation)
        
        self.numeric_submission = SubmissionFactory(
            evaluation=self.evaluation,
            student=self.student,
            grade=None,
            submission_status=None,
        )
        
        self.non_numeric_submission = SubmissionFactory(
            student=self.student,
            evaluation=self.non_numeric_evaluation,
            grade=None,
            submission_status=None,
        )
        self.teacher_roles = TeacherRoleFactory.create_batch(
            5, commission=self.commission
        )

        # Define the URI for the auto_assign_graders endpoint
        self.auto_assign_graders_uri = (
            "/api/teacher/evaluations/submissions/auto_assign_graders/"
        )

        self.grade_uri = "/api/teacher/evaluations/submissions/grade/"
        self.add_submission_uri = "/api/teacher/evaluations/submissions/add_evaluation_submission/"

    @mock.patch.object(GraderAssignmentService, "auto_assign")
    def test_auto_assign_graders_success(self, mocked_grader_assignment_service):
        """
        Should successfully auto-assign graders to submissions.
        """
        self.client.force_authenticate(user=self.teacher.user)

        # Make the API request
        response = self.client.put(
            self.auto_assign_graders_uri,
            {"evaluation": self.evaluation.id},
            format="json",
        )

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the GraderAssignmentService was called with the correct arguments
        mocked_grader_assignment_service.assert_called_once()

    @mock.patch.object(GraderAssignmentService, "auto_assign")
    def test_auto_assign_graders_not_found(self, mocked_grader_assignment_service):
        """
        Should return 404 if the evaluation is not found.
        """
        self.client.force_authenticate(user=self.teacher.user)

        # Define a non-existent evaluation ID
        non_existent_evaluation_id = 9999

        # Make the API request
        response = self.client.put(
            self.auto_assign_graders_uri,
            {"evaluation": non_existent_evaluation_id},
            format="json",
        )

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @mock.patch.object(GraderAssignmentService, "auto_assign")
    def test_auto_assign_graders_unauthorized(self, mocked_grader_assignment_service):
        """
        Should return 401 if the user is not authenticated.
        """
        # Make the API request without authentication
        response = self.client.put(
            self.auto_assign_graders_uri,
            {"evaluation": self.evaluation.id},
            format="json",
        )

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auto_assign_graders_different_numbers(self):
        """
        Should correctly assign graders to submissions with varying numbers of submissions and teacher roles.
        """
        # Create a varying number of submissions and teacher roles
        submissions = SubmissionFactory.create_batch(10, evaluation=self.evaluation)
        teacher_roles = TeacherRoleFactory.create_batch(5, commission=self.commission)

        # Call the service directly without mocking
        service = GraderAssignmentService()
        assigned_submissions = service.auto_assign(teacher_roles, submissions)

        # Assert that each submission has a grader assigned
        for submission in assigned_submissions:
            self.assertIsNotNone(submission.grader)

    def test_auto_assign_graders_more_roles_than_submissions(self):
        """
        Should correctly handle the case where there are more teacher roles than submissions.
        """
        # Create more teacher roles than submissions
        submissions = SubmissionFactory.create_batch(5, evaluation=self.evaluation)
        teacher_roles = TeacherRoleFactory.create_batch(10, commission=self.commission)

        # Call the service directly without mocking
        service = GraderAssignmentService()
        assigned_submissions = service.auto_assign(teacher_roles, submissions)

        # Assert that each submission has a grader assigned and no teacher is assigned to a non-existent submission
        for submission in assigned_submissions:
            self.assertIsNotNone(submission.grader)

    def test_auto_assign_graders_weighted_roles(self):
        """
        Should correctly assign graders based on the weight of each teacher role.
        """
        # Create teacher roles with varying weights
        teacher_a = TeacherRoleFactory(commission=self.commission, grader_weight=1.0)
        teacher_b = TeacherRoleFactory(commission=self.commission, grader_weight=2.0)
        teacher_c = TeacherRoleFactory(commission=self.commission, grader_weight=3.0)

        teacher_roles = [
            teacher_a,
            teacher_b,
            teacher_c,
        ]
        submissions = SubmissionFactory.create_batch(6, evaluation=self.evaluation)

        # Call the service directly without mocking
        service = GraderAssignmentService()
        assigned_submissions = service.auto_assign(teacher_roles, submissions)

        # Assert that the submissions are assigned based on the weight of the teacher roles
        # This is a simplified assertion. You might need to implement more complex logic to verify the distribution.
        self.assertEqual(len(assigned_submissions), len(submissions))

        teacher_a_subs = [
            sub for sub in assigned_submissions if sub.grader == teacher_a.teacher
        ]
        teacher_b_subs = [
            sub for sub in assigned_submissions if sub.grader == teacher_b.teacher
        ]
        teacher_c_subs = [
            sub for sub in assigned_submissions if sub.grader == teacher_c.teacher
        ]
        self.assertEqual(len(teacher_a_subs), 1)
        self.assertEqual(len(teacher_b_subs), 2)
        self.assertEqual(len(teacher_c_subs), 3)

    def test_auto_assign_many_teachers(self):
        """
        Should correctly assign graders when there are more teachers than subs.
        """
        # Create teacher roles with varying weights
        teacher_a = TeacherRoleFactory(commission=self.commission, grader_weight=1.0)
        teacher_b = TeacherRoleFactory(commission=self.commission, grader_weight=2.0)
        teacher_c = TeacherRoleFactory(commission=self.commission, grader_weight=3.0)

        teacher_roles = [
            teacher_a,
            teacher_b,
            teacher_c,
        ]
        submissions = SubmissionFactory.create_batch(2, evaluation=self.evaluation)

        # Call the service directly without mocking
        service = GraderAssignmentService()
        assigned_submissions = service.auto_assign(teacher_roles, submissions)

        # Assert that the submissions are assigned based on the weight of the teacher roles
        # This is a simplified assertion. You might need to implement more complex logic to verify the distribution.
        self.assertEqual(len(assigned_submissions), len(submissions))

        teacher_a_subs = [
            sub for sub in assigned_submissions if sub.grader == teacher_a.teacher
        ]
        teacher_b_subs = [
            sub for sub in assigned_submissions if sub.grader == teacher_b.teacher
        ]
        teacher_c_subs = [
            sub for sub in assigned_submissions if sub.grader == teacher_c.teacher
        ]
        self.assertEqual(len(teacher_a_subs), 0)
        self.assertEqual(len(teacher_b_subs), 1)
        self.assertEqual(len(teacher_c_subs), 1)

    def test_auto_assign_many_submissions(self):
        """
        Should correctly assign graders when there are many subs.
        """
        # Create teacher roles with varying weights
        teacher_a = TeacherRoleFactory(commission=self.commission, grader_weight=1.0)
        teacher_b = TeacherRoleFactory(commission=self.commission, grader_weight=2.0)
        teacher_c = TeacherRoleFactory(commission=self.commission, grader_weight=3.0)

        teacher_roles = [
            teacher_a,
            teacher_b,
            teacher_c,
        ]
        submissions = SubmissionFactory.create_batch(55, evaluation=self.evaluation)

        # Call the service directly without mocking
        service = GraderAssignmentService()
        assigned_submissions = service.auto_assign(teacher_roles, submissions)

        teacher_a_subs = [
            sub for sub in assigned_submissions if sub.grader == teacher_a.teacher
        ]
        teacher_b_subs = [
            sub for sub in assigned_submissions if sub.grader == teacher_b.teacher
        ]
        teacher_c_subs = [
            sub for sub in assigned_submissions if sub.grader == teacher_c.teacher
        ]
        self.assertEqual(len(teacher_a_subs), 9)
        self.assertEqual(len(teacher_b_subs), 18)
        self.assertEqual(len(teacher_c_subs), 28)

    def test_auto_assign_one_teacher(self):
        """
        Should correctly assign graders when there is only one teacher.
        """
        # Create teacher roles with varying weights
        teacher_a = TeacherRoleFactory(commission=self.commission, grader_weight=5.0)

        teacher_roles = [
            teacher_a,
        ]
        submissions = SubmissionFactory.create_batch(20, evaluation=self.evaluation)

        # Call the service directly without mocking
        service = GraderAssignmentService()
        assigned_submissions = service.auto_assign(teacher_roles, submissions)

        teacher_a_subs = [
            sub for sub in assigned_submissions if sub.grader == teacher_a.teacher
        ]
        self.assertEqual(len(teacher_a_subs), 20)

    def test_auto_assign_zero_submissions(self):
        """
        Should handle the case with zero submissions gracefully.
        """
        teacher_roles = TeacherRoleFactory.create_batch(3, commission=self.commission)
        submissions = []
        service = GraderAssignmentService()
        assigned_submissions = service.auto_assign(teacher_roles, submissions)
        self.assertEqual(len(assigned_submissions), 0)

    def test_auto_assign_zero_teacher_roles(self):
        """
        Should handle the case with zero teacher roles gracefully.
        """
        teacher_roles = []
        submissions = SubmissionFactory.create_batch(5, evaluation=self.evaluation)
        service = GraderAssignmentService()
        assigned_submissions = service.auto_assign(teacher_roles, submissions)
        for submission in assigned_submissions:
            self.assertIsNone(submission.grader)

    def test_auto_assign_equal_weights(self):
        """
        Should distribute submissions evenly among teachers with equal weights.
        """
        teacher_roles = TeacherRoleFactory.create_batch(
            3, commission=self.commission, grader_weight=1.0
        )
        submissions = SubmissionFactory.create_batch(3, evaluation=self.evaluation)
        service = GraderAssignmentService()
        assigned_submissions = service.auto_assign(teacher_roles, submissions)
        grader_ids = [submission.grader.user.id for submission in assigned_submissions]
        unique_grader_ids = set(grader_ids)
        self.assertEqual(len(unique_grader_ids), 3)  # Expecting 3 unique graders
        for grader_id in unique_grader_ids:
            self.assertEqual(
                grader_ids.count(grader_id), 1
            )  # Each grader should have exactly one submission

    def test_auto_assign_one_submission_multiple_teachers(self):
        """
        Should correctly assign the single submission to one of the teachers based on weight.
        """
        teacher_a = TeacherRoleFactory(commission=self.commission, grader_weight=1.0)
        teacher_b = TeacherRoleFactory(commission=self.commission, grader_weight=2.0)
        teacher_roles = [teacher_a, teacher_b]
        submissions = SubmissionFactory.create_batch(1, evaluation=self.evaluation)
        service = GraderAssignmentService()
        assigned_submissions = service.auto_assign(teacher_roles, submissions)
        self.assertEqual(len(assigned_submissions), 1)
        self.assertEqual(assigned_submissions[0].grader, teacher_b.teacher)

    def tearDown(self) -> None:
        # Stop the mock
        mock.patch.stopall()

    def test_auto_assign_graders_weighted_roles_with_0(self):
        """
        Should correctly assign graders based on the weight of each teacher role.
        """
        # Create teacher roles with varying weights
        teacher_a = TeacherRoleFactory(commission=self.commission, grader_weight=0.0)
        teacher_b = TeacherRoleFactory(commission=self.commission, grader_weight=2.0)
        teacher_c = TeacherRoleFactory(commission=self.commission, grader_weight=3.0)

        teacher_roles = [
            teacher_a,
            teacher_b,
            teacher_c,
        ]
        submissions = SubmissionFactory.create_batch(6, evaluation=self.evaluation)

        # Call the service directly without mocking
        service = GraderAssignmentService()
        assigned_submissions = service.auto_assign(teacher_roles, submissions)

        # Assert that the submissions are assigned based on the weight of the teacher roles
        # This is a simplified assertion. You might need to implement more complex logic to verify the distribution.
        self.assertEqual(len(assigned_submissions), len(submissions))

        teacher_a_subs = [
            sub for sub in assigned_submissions if sub.grader == teacher_a.teacher
        ]
        teacher_b_subs = [
            sub for sub in assigned_submissions if sub.grader == teacher_b.teacher
        ]
        teacher_c_subs = [
            sub for sub in assigned_submissions if sub.grader == teacher_c.teacher
        ]
        self.assertEqual(len(teacher_a_subs), 0)
        self.assertEqual(len(teacher_b_subs), 2)
        self.assertEqual(len(teacher_c_subs), 4)

    def test_auto_assign_graders_skips_existing_grades(self):
        """
        Should not change the grader if a submission already has a grader assigned.
        """
        # Create teacher roles
        teacher_a = TeacherRoleFactory(commission=self.commission, grader_weight=1.0)
        teacher_b = TeacherRoleFactory(commission=self.commission, grader_weight=2.0)
        teacher_roles = [teacher_a, teacher_b]
        # Create submissions and assign a grader to one of them
        submissions = SubmissionFactory.create_batch(3, evaluation=self.evaluation)

        submissions_service = EvaluationSubmissionService()
        submissions_service.set_grade(submissions[0], teacher_a.teacher, 1)
        submissions_service.set_grade(submissions[1], teacher_a.teacher, 2)

        # Call the service directly without mocking
        service = GraderAssignmentService()
        assigned_submissions = service.auto_assign(teacher_roles, submissions)

        # Assert that the existing grader is not changed
        self.assertEqual(assigned_submissions[0].grader, teacher_b.teacher)
        self.assertEqual(assigned_submissions[0].grade, None)
        self.assertEqual(assigned_submissions[1].grader, teacher_a.teacher)
        self.assertEqual(assigned_submissions[1].grade, 1)
        self.assertEqual(assigned_submissions[2].grader, teacher_a.teacher)
        self.assertEqual(assigned_submissions[2].grade, 2)

    def test_auto_assign_graders_with_many_submissions(self):
        """
        Should correctly assign graders when there are many submissions.
        """
        # Create teacher roles
        teacher_a = TeacherRoleFactory(commission=self.commission, grader_weight=55.0)
        teacher_b = TeacherRoleFactory(commission=self.commission, grader_weight=35.0)
        teacher_c = TeacherRoleFactory(commission=self.commission, grader_weight=10.0)
        teacher_roles = [teacher_a, teacher_b, teacher_c]

        # Create submissions and assign a grader to one of them
        submissions = SubmissionFactory.create_batch(30, evaluation=self.evaluation)

        # Call the service directly without mocking
        service = GraderAssignmentService()
        assigned_submissions = service.auto_assign(teacher_roles, submissions)

        teacher_a_subs = [
            sub for sub in assigned_submissions if sub.grader == teacher_a.teacher
        ]
        teacher_b_subs = [
            sub for sub in assigned_submissions if sub.grader == teacher_b.teacher
        ]
        teacher_c_subs = [
            sub for sub in assigned_submissions if sub.grader == teacher_c.teacher
        ]

        self.assertEqual(len(teacher_a_subs), 17)
        self.assertEqual(len(teacher_b_subs), 10)
        self.assertEqual(len(teacher_c_subs), 3)
    
    def test_grade_numeric_evaluation_rejects_status(self):
        """
        Should reject a status when grading a numeric evaluation.
        """
        self.client.force_authenticate(user=self.teacher.user)

        response = self.client.put(
            self.grade_uri,
            {
                "student": self.student.user.id,
                "evaluation": self.evaluation.id,
                "submission_status": "APROBADO",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_grade_non_numeric_evaluation_rejects_numeric_grade(self):
        """
        Should reject a numeric grade when grading a non-numeric evaluation.
        """
        self.client.force_authenticate(user=self.teacher.user)

        response = self.client.put(
            self.grade_uri,
            {
                "student": self.student.user.id,
                "evaluation": self.non_numeric_evaluation.id,
                "grade": 8,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_grade_preserves_previously_assigned_grader(self):
        """
        Should keep an already assigned grader when a grade is set.
        """
        other_teacher = TeacherFactory()
        TeacherRoleFactory(commission=self.commission, teacher=other_teacher)

        submissions_service = EvaluationSubmissionService()
        submissions_service.set_grader(self.numeric_submission, other_teacher)

        self.client.force_authenticate(user=self.teacher.user)
        response = self.client.put(
            self.grade_uri,
            {
                "student": self.student.user.id,
                "evaluation": self.evaluation.id,
                "grade": 8,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.numeric_submission.refresh_from_db()
        self.assertIsNotNone(self.numeric_submission.grader)
        self.assertEqual(self.numeric_submission.grader.user_id, other_teacher.user_id)

    def test_grade_non_numeric_evaluation_accepts_status(self):
        """
        Should accept a valid status when grading a non-numeric evaluation and update the submission status accordingly.
        """
        self.client.force_authenticate(user=self.teacher.user)

        response = self.client.put(
            self.grade_uri,
            {
                "student": self.student.user.id,
                "evaluation": self.non_numeric_evaluation.id,
                "submission_status": "APROBADO",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["grade"])
        self.assertEqual(response.data["submission_status"], "APROBADO")
        self.non_numeric_submission.refresh_from_db()
        self.assertEqual(self.non_numeric_submission.submission_status, "APROBADO")
        self.assertIsNone(self.non_numeric_submission.grade)

    def test_grade_requires_exactly_one_of_grade_or_submission_status(self):
        """
        Should reject requests that provide both grade and submission_status.
        """
        self.client.force_authenticate(user=self.teacher.user)

        response = self.client.put(
            self.grade_uri,
            {
                "student": self.student.user.id,
                "evaluation": self.non_numeric_evaluation.id,
                "grade": 8,
                "submission_status": "APROBADO",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_grade_allows_feedback_only_update(self):
        """
        Should allow updating only the feedback text without changing grade or submission status.
        """
        self.client.force_authenticate(user=self.teacher.user)

        feedback_text = "# Evaluaci\u00f3n\nTe fue muy mal\n- Hiciste todo mal\n- No entregaste a tiempo"

        response = self.client.put(
            self.grade_uri,
            {
                "student": self.student.user.id,
                "evaluation": self.non_numeric_evaluation.id,
                "feedback_text": feedback_text,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["feedback_text"], feedback_text)
        self.assertIsNone(response.data["grade"])
        self.assertIsNone(response.data["submission_status"])

        self.non_numeric_submission.refresh_from_db()
        self.assertEqual(self.non_numeric_submission.feedback_text, feedback_text)
        self.assertIsNone(self.non_numeric_submission.grade)
        self.assertIsNone(self.non_numeric_submission.submission_status)

    def test_grade_requires_grade_submission_status_or_feedback_text(self):
        """
        Should reject requests that provide neither grade, submission_status, nor feedback_text.
        """
        self.client.force_authenticate(user=self.teacher.user)

        response = self.client.put(
            self.grade_uri,
            {
                "student": self.student.user.id,
                "evaluation": self.non_numeric_evaluation.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_grade_non_numeric_evaluation_rejects_invalid_status(self):
        """
        Should reject an invalid status when grading a non-numeric evaluation.
        """
        self.client.force_authenticate(user=self.teacher.user)

        response = self.client.put(
            self.grade_uri,
            {
                "student": self.student.user.id,
                "evaluation": self.non_numeric_evaluation.id,
                "submission_status": "INVALID",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch("backend.views.evaluation_submission_teacher_views.EvaluationSubmission.full_clean")
    def test_add_evaluation_submission_returns_400_when_model_validation_fails(self, mocked_full_clean):
        self.client.force_authenticate(user=self.teacher.user)
        mocked_full_clean.side_effect = ValidationError({"grade": ["invalid"]})

        new_student = StudentFactory()
        self.semester.students.add(new_student)

        response = self.client.post(
            self.add_submission_uri,
            {
                "student": new_student.user.id,
                "evaluation": self.evaluation.id,
                "grade": 8,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("grade", response.data)
