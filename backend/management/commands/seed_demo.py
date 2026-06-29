"""
DEV COMMAND: puebla la base con datos académicos de demo (que parezca usada).

7 alumnos con historia similar (CBC + 3°-7° + TC018 + TA049 aprobadas; CB024 y TA050
con final pendiente -OPEN- a cargo de Pablo Cosso). Comisiones con varios inscriptos,
2 parciales por cursada, finales, y asistencias en las cursadas recientes.

- Emails @fi.uba.ar. Contraseña de TODOS los usuarios = test123$.
- Determinístico y re-ejecutable: limpia las tablas académicas + docentes falsos
  (siu_id>=9000) y recrea. No toca cuentas admin/bedelía/superuser salvo la contraseña.

    python manage.py seed_demo
"""
import random
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.core.management import BaseCommand
from django.db import transaction

from backend.models import (
    Student, Teacher, Department, Commission, CommissionInscription,
    Semester, Evaluation, EvaluationSubmission, Final, FinalExam,
    Attendance, AttendanceQRCode, Secretary,
)
from backend.models.staff import Staff
from backend.models.auth_identity import AuthIdentity
from backend.models.catalog import Catalog, CatalogItem
from backend.models.form import Form, FormDocumentSource, FormField
from backend.models.form_ownership import FormOwnershipGroup, FormOwnershipMember
from backend.models.form_submission import FormAnswer, FormSubmission
from backend.models.form_types import FormFieldType, FormSubmissionStatus, FormType
from backend.models.semester_schedule import SemesterSchedule
from backend.models.teacher_role import TeacherRole
from backend.models.user import User

PASSWORD = "test123$"
ART = ZoneInfo("America/Argentina/Buenos_Aires")


def _dt(y, m, d, hh=12, mm=0):
    return datetime(y, m, d, hh, mm, tzinfo=ART)


def _plus(base, days=0, hours=0):
    return base + timedelta(days=days, hours=hours)


# code, subject_siu_id (id en fake-siu), nombre, dept ('FIS'|'MAT'|'COM'|None), cuatri
SUBJECTS = [
    ("CBC62", 1,  "Álgebra A", "MAT", "CBC"),
    ("CBC66", 2,  "Análisis Matemático A", "MAT", "CBC"),
    ("CBC03", 3,  "Física", "FIS", "CBC"),
    ("CBC24", 4,  "Introducción al Conocimiento de la Sociedad y el Estado", None, "CBC"),
    ("CBC40", 5,  "Introducción al Pensamiento Científico", None, "CBC"),
    ("CBC90", 6,  "Pensamiento Computacional", "COM", "CBC"),
    ("CB001", 7,  "Análisis Matemático II", "MAT", "3"),
    ("TB021", 8,  "Fundamentos de Programación", "COM", "3"),
    ("TB022", 9,  "Introducción al Desarrollo de Software", "COM", "3"),
    ("CB002", 10, "Álgebra Lineal", "MAT", "4"),
    ("TB023", 11, "Organización del Computador", "COM", "4"),
    ("CB100", 12, "Algoritmos y Estructuras de Datos", "COM", "4"),
    ("CB003", 13, "Probabilidad y Estadística", "MAT", "5"),
    ("TB024", 14, "Teoría de Algoritmos", "COM", "5"),
    ("TA043", 15, "Sistemas Operativos", "COM", "5"),
    ("TB025", 16, "Paradigmas de Programación", "COM", "5"),
    ("TA044", 17, "Base de Datos", "COM", "6"),
    ("CB051", 18, "Modelación Numérica", "MAT", "6"),
    ("TA045", 19, "Taller de Programación", "COM", "6"),
    ("TA046", 20, "Ingeniería de Software I", "COM", "6"),
    ("TA047", 21, "Ciencia de Datos", "COM", "7"),
    ("TC017", 22, "Gestión del Desarrollo de Sistemas Informáticos", "COM", "7"),
    ("TB026", 23, "Programación Concurrente", "COM", "7"),
    ("TA048", 24, "Redes", "COM", "7"),
    ("TC018", 26, "Empresas de Base Tecnológica I", "COM", "8"),
    ("TA049", 27, "Ingeniería de Software II", "COM", "8"),
    ("CB024", 25, "Física para Informática", "FIS", "8P"),   # final pendiente
    ("TA050", 28, "Sistemas Distribuidos I", "COM", "8P"),   # final pendiente
]
APPROVED_CODES = [s[0] for s in SUBJECTS if s[4] != "8P"]

CUATRI = {
    "CBC": ("SS", _dt(2022, 3, 14, 9), _dt(2022, 7, 13, 18)),
    "3":   ("FS", _dt(2023, 3, 13, 9), _dt(2023, 7, 12, 18)),
    "4":   ("SS", _dt(2023, 8, 14, 9), _dt(2023, 12, 6, 18)),
    "5":   ("FS", _dt(2024, 3, 11, 9), _dt(2024, 7, 10, 18)),
    "6":   ("SS", _dt(2024, 8, 12, 9), _dt(2024, 12, 4, 18)),
    "7":   ("FS", _dt(2025, 3, 10, 9), _dt(2025, 7, 9, 18)),
    "8":   ("SS", _dt(2025, 8, 11, 9), _dt(2025, 12, 3, 18)),
    "8P":  ("FS", _dt(2026, 3, 16, 9), None),  # cuatri actual -> "materias en curso"
}
PENDING_FINAL_DATE = {"CB024": _dt(2026, 7, 1, 18), "TA050": _dt(2026, 7, 8, 18)}

# dni, padron, first, last, email, materias_a_restar (de las aprobadas)
STUDENTS = [
    ("41835723", "102707", "Joaquin", "Andresen", "jandresen@fi.uba.ar", 0),
    ("43990892", "108088", "Luca", "Salluzzi", "lsalluzi@fi.uba.ar", 1),
    ("43459394", "108257", "Valentina", "Lanzillotta", "vlanzillotta@fi.uba.ar", 0),
    ("41779246", "104503", "Gonzalo", "Gordyn Biello", "ggordyn@fi.uba.ar", 2),
    ("42150053", "104093", "Matías Sebastián", "Merlo Gonzalez", "mmerlog@fi.uba.ar", 1),
    ("43775927", "107746", "Imanol", "Suarez Pino", "isuarezp@fi.uba.ar", 0),
    ("42817479", "105738", "Martin", "Gonzalez Prieto", "mgonzalezp@fi.uba.ar", 2),
]

# Identidades de Google reales (recuperadas de la base remota) para que el login
# con Google siga funcionando en estas cuentas. dni -> (sub de Google, email)
GOOGLE_IDENTITIES = {
    "41835723": ("101394135503250076613", "jandresen@fi.uba.ar"),
    "41779246": ("102175008748779643011", "ggordyn@fi.uba.ar"),
    "42150053": ("108904364424163819070", "mmerlog@fi.uba.ar"),
}

# Docente que sí o sí dicta los finales pendientes
PABLO_DNI = "13123123"
PABLO_EMAIL = "pcosso@fi.uba.ar"

# first, last, dni, email, dept
FAKE_TEACHERS = [
    ("Silvia", "Romano", "30111111", "sromano@fi.uba.ar", "FIS"),
    ("Ana", "Martínez", "30222222", "amartinez@fi.uba.ar", "MAT"),
    ("Roberto", "Díaz", "30333333", "rdiaz@fi.uba.ar", "MAT"),
    ("Martín", "Gómez", "30444444", "mgomezdoc@fi.uba.ar", "COM"),
    ("Laura", "Pérez", "30555555", "lperez@fi.uba.ar", "COM"),
    ("Diego", "Fernández", "30666666", "dfernandez@fi.uba.ar", "COM"),
]

# Alumnos falsos de la SEGUNDA comisión de Física para Informática (no son los 7
# principales). Sirve para demostrar los finales unificados: dos comisiones de la
# misma materia en el cuatrimestre en curso, con jefes de cátedra distintos.
# dni, padron, first, last, email, notas (1° Parcial, 2° Parcial, TP Final)
SEGUNDA_COMISION_FISICA_STUDENTS = [
    ("46100001", "110001", "Tomás", "Ibarra", "tibarra@fi.uba.ar", [7, 8, 6]),
    ("46100002", "110002", "Camila", "Ríos", "crios@fi.uba.ar", [9, 9, 10]),
    ("46100003", "110003", "Nicolás", "Vega", "nvega@fi.uba.ar", [3, 5, 4]),
    ("46100004", "110004", "Sofía", "Castro", "scastro@fi.uba.ar", [8, 7, 9]),
    ("46100005", "110005", "Lucas", "Moreno", "lmoreno@fi.uba.ar", [6, 4, 7]),
]

# Horarios de cursada por materia (subject_siu_id). Fuente: fake-siu/db.json.
# day_of_week: 0=Lun, 1=Mar, 2=Mié, 3=Jue, 4=Vie, 5=Sáb.
HORARIOS_POR_MATERIA = {
    1:  [(0, "08:00", "11:00"), (3, "08:00", "11:00")],   # Álgebra A
    2:  [(1, "08:00", "11:00"), (4, "08:00", "11:00")],   # Análisis Matemático A
    3:  [(0, "14:00", "17:00"), (2, "14:00", "17:00")],   # Física
    4:  [(1, "18:00", "22:00")],                           # Intro al Conocimiento de la Sociedad y el Estado
    5:  [(2, "18:00", "22:00")],                           # Intro al Pensamiento Científico
    6:  [(3, "18:00", "22:00")],                           # Pensamiento Computacional
    7:  [(0, "08:00", "11:00"), (3, "08:00", "11:00")],   # Análisis Matemático II
    8:  [(1, "08:00", "11:00"), (4, "08:00", "11:00")],   # Fundamentos de Programación
    9:  [(2, "08:00", "11:00"), (4, "11:00", "14:00")],   # Intro al Desarrollo de Software
    10: [(0, "11:00", "14:00"), (3, "11:00", "14:00")],   # Álgebra Lineal
    11: [(1, "11:00", "14:00"), (3, "14:00", "17:00")],   # Organización del Computador
    12: [(0, "18:00", "21:00"), (2, "18:00", "21:00")],   # Algoritmos y Estructuras de Datos
    13: [(0, "14:00", "17:00"), (2, "14:00", "17:00")],   # Probabilidad y Estadística
    14: [(1, "14:00", "17:00"), (3, "18:00", "21:00")],   # Teoría de Algoritmos
    15: [(2, "11:00", "14:00"), (4, "14:00", "17:00")],   # Sistemas Operativos
    16: [(1, "08:00", "11:00"), (4, "08:00", "11:00")],   # Paradigmas de Programación
    17: [(0, "11:00", "14:00"), (2, "18:00", "21:00")],   # Base de Datos
    18: [(0, "08:00", "11:00"), (2, "08:00", "11:00")],   # Modelación Numérica
    19: [(3, "14:00", "17:00")],                           # Taller de Programación
    20: [(2, "18:00", "21:00"), (4, "18:00", "21:00")],   # Ingeniería de Software I
    21: [(0, "18:00", "21:00"), (3, "11:00", "14:00")],   # Ciencia de Datos
    22: [(1, "18:00", "21:00")],                           # Gestión del Desarrollo de Sistemas Informáticos
    23: [(2, "08:00", "11:00"), (4, "08:00", "11:00")],   # Programación Concurrente
    24: [(0, "14:00", "17:00"), (3, "14:00", "17:00")],   # Redes
    25: [(0, "11:00", "14:00"), (2, "11:00", "14:00")],   # Física para Informática
    26: [(1, "18:00", "21:00")],                           # Empresas de Base Tecnológica I
    27: [(0, "18:00", "21:00"), (3, "18:00", "21:00")],   # Ingeniería de Software II
    28: [(2, "18:00", "21:00"), (4, "18:00", "21:00")],   # Sistemas Distribuidos I
}


class Command(BaseCommand):
    help = "DEV COMMAND: puebla la base con datos académicos de demo (ver docstring)."

    @transaction.atomic
    def handle(self, *args, **options):
        dept_id = self._ensure_departments()

        students = self._upsert_students()
        dropped = self._compute_drops()

        self._clear_academic()

        pablo = self._ensure_pablo()
        by_dept = self._create_fake_teachers(dept_id, pablo)

        chief_rng = random.Random(123)

        def chief_for(code, dept_key):
            if code in ("CB024", "TA050"):
                return pablo
            pool = by_dept.get(dept_key) or by_dept["COM"]
            options = [t for t in pool if t != pablo] or pool
            return chief_rng.choice(options)

        c = self._build_academia(students, dropped, dept_id, pablo, chief_for)

        self._restore_google_identities()
        self._seed_secretaries()
        self._seed_forms()
        self._seed_dept_staff()
        self._seed_submissions()
        self._seed_segunda_comision_fisica(dept_id)
        self._seed_horarios()

        n_pwd = 0
        for u in User.objects.all():
            u.set_password(PASSWORD)
            u.save(update_fields=["password"])
            n_pwd += 1
        c["pwd"] = n_pwd

        self._report(c, students, dropped)

    # ---------- helpers ----------

    def _ensure_departments(self):
        names = {"FIS": "Departamento de Física",
                 "MAT": "Departamento de Matemática",
                 "COM": "Departamento de Computación"}
        out = {}
        for key, name in names.items():
            d, _ = Department.objects.get_or_create(name=name)
            out[key] = d.id
        out[None] = None
        return out

    def _upsert_students(self):
        students = {}
        for dni, padron, fn, ln, email, _n in STUDENTS:
            # se keyea por padrón (estable); si cambió el dni, se corrige acá
            st = Student.objects.select_related("user").filter(padron=padron).first()
            if st is not None:
                u = st.user
            else:
                u = User.objects.filter(dni=dni).first() or User(username="", is_active=True)
            u.dni = dni
            u.email = email
            if not u.first_name:
                u.first_name = fn
            if not u.last_name:
                u.last_name = ln
            u.is_student = True
            u.save()  # .save() evita el validador de campo de dni
            if st is None:
                st = Student.objects.filter(user=u).first() or Student(user=u, face_encodings=[])
            st.padron = padron
            st.save()
            students[dni] = st
        return students

    def _compute_drops(self):
        rnd = random.Random(7)
        return {dni: (set(rnd.sample(APPROVED_CODES, n)) if n else set())
                for dni, _p, _f, _l, _e, n in STUDENTS}

    def _clear_academic(self):
        Attendance.objects.all().delete()
        AttendanceQRCode.objects.all().delete()
        EvaluationSubmission.objects.all().delete()
        Evaluation.objects.all().delete()
        FinalExam.objects.all().delete()
        Final.objects.all().delete()
        CommissionInscription.objects.all().delete()
        Semester.objects.all().delete()
        TeacherRole.objects.all().delete()
        Commission.objects.all().delete()
        User.objects.filter(teacher__siu_id__gte=9000).delete()  # docentes falsos previos

    def _ensure_pablo(self):
        u = User.objects.filter(dni=PABLO_DNI).first()
        if u is None:
            u = User(dni=PABLO_DNI, email=PABLO_EMAIL, first_name="Pablo",
                     last_name="Cosso", is_teacher=True, is_active=True, username="")
            u.save()
        else:
            u.email = PABLO_EMAIL
            u.is_teacher = True
            u.save()
        t = Teacher.objects.filter(user=u).first()
        if t is None:
            t = Teacher.objects.create(user=u, siu_id=4, legajo="12348", face_encodings=[])
        return t

    def _create_fake_teachers(self, dept_id, pablo):
        by_dept = {"FIS": [], "MAT": [], "COM": []}
        for i, (fn, ln, dni, email, dept) in enumerate(FAKE_TEACHERS, start=1):
            u = User(dni=dni, email=email, first_name=fn, last_name=ln,
                     is_teacher=True, is_active=True, username="")
            u.save()
            t = Teacher.objects.create(user=u, siu_id=9000 + i, legajo=f"9000{i}", face_encodings=[])
            by_dept[dept].append(t)
        by_dept["FIS"].append(pablo)
        by_dept["COM"].append(pablo)
        return by_dept

    def _build_academia(self, students, dropped, dept_id, pablo, chief_for):
        rnd = random.Random(42)
        siu_counter, final_siu, act_counter = 1000, 5000, 1
        c = dict(com=0, fin_ap=0, fin_pend=0, ev=0, sub=0, fe=0, ins=0, qr=0, att=0)

        for code, ssid, name, dept_key, cuatri in SUBJECTS:
            ym, start, approved_final_date = CUATRI[cuatri]
            chief = chief_for(code, dept_key)
            is_pending = cuatri == "8P"

            enrolled = [students[s[0]] for s in STUDENTS
                        if is_pending or code not in dropped[s[0]]]

            siu_counter += 1
            com = Commission.objects.create(
                chief_teacher=chief, subject_siu_id=ssid, subject_name=name,
                siu_id=siu_counter, department_id=dept_id[dept_key])
            TeacherRole.objects.create(commission=com, teacher=chief, role="Titular", grader_weight=5.0)
            c["com"] += 1

            sem = Semester.objects.create(commission=com, year_moment=ym, start_date=start,
                                          classes_amount=16, minimum_attendance=0.75)
            for st in enrolled:
                CommissionInscription.objects.create(
                    semester=sem, student=st,
                    status=CommissionInscription.InscriptionStatus.ACCEPTED)
                c["ins"] += 1

            for n, off in ((1, 45), (2, 95)):
                ev_date = _plus(start, off)
                ev = Evaluation.objects.create(
                    semester=sem, evaluation_name=f"{n}° Parcial",
                    is_graded=True, is_gradeable=True, passing_grade=4,
                    start_date=ev_date, end_date=_plus(ev_date, hours=3))
                c["ev"] += 1
                for st in enrolled:
                    EvaluationSubmission.objects.create(
                        evaluation=ev, student=st, grade=rnd.randint(6, 10), grader=chief)
                    c["sub"] += 1

            if is_pending:
                fin = Final.objects.create(
                    teacher=pablo, date=PENDING_FINAL_DATE[code], subject_siu_id=ssid,
                    subject_name=name, status=Final.Status.OPEN, siu_id=None, act=None)
                fin.commissions.add(com)
                c["fin_pend"] += 1
                for st in enrolled:
                    FinalExam.objects.create(final=fin, student=st, grade=None)
                    c["fe"] += 1
            else:
                final_siu += 1
                fin = Final.objects.create(
                    teacher=chief, date=approved_final_date, subject_siu_id=ssid,
                    subject_name=name, status=Final.Status.ACT_SENT, siu_id=final_siu,
                    act=f"{act_counter:04d}A")
                act_counter += 1
                fin.commissions.add(com)
                c["fin_ap"] += 1
                for st in enrolled:
                    FinalExam.objects.create(final=fin, student=st, grade=rnd.randint(6, 10))
                    c["fe"] += 1

            if cuatri in ("8", "8P"):
                qrs = []
                for k in range(12):
                    qr = AttendanceQRCode.objects.create(
                        semester=sem, owner_teacher=chief,
                        created_at=_plus(start, 7 * k), expires_at=_plus(start, 7 * k, hours=3),
                        mode="qr")
                    qrs.append(qr)
                    c["qr"] += 1
                for st in enrolled:
                    for qr in qrs:
                        if rnd.random() < 0.9:
                            Attendance.objects.create(semester=sem, student=st, qr_code=qr,
                                                      submitted_at=qr.created_at, location_valid=True)
                            c["att"] += 1
        return c

    def _seed_segunda_comision_fisica(self, dept_id):
        """Segunda comisión de Física para Informática (mismo subject_siu_id que CB024)
        para demostrar los finales unificados: dos comisiones de la misma materia, con
        jefes de cátedra distintos, en el cuatrimestre en curso (2026 FS). Trae sus
        propios alumnos falsos con notas de cursada."""
        chief = Teacher.objects.filter(user__dni="30111111").first()  # Silvia Romano (FIS)
        if chief is None:
            print("Segunda comisión Física: no se encontró a Silvia Romano, se omite.")
            return

        ssid = 25
        name = "Física para Informática"
        ym, start, _approved = CUATRI["8P"]  # cuatri actual

        if Commission.objects.filter(subject_siu_id=ssid, chief_teacher=chief).exists():
            print("Segunda comisión Física: ya existe, se omite.")
            return

        students = []
        for dni, padron, fn, ln, email, _grades in SEGUNDA_COMISION_FISICA_STUDENTS:
            u = User.objects.filter(dni=dni).first() or User(username="", is_active=True)
            u.dni = dni
            u.email = email
            u.first_name = fn
            u.last_name = ln
            u.is_student = True
            u.save()  # .save() evita el validador de dni
            st = Student.objects.filter(user=u).first() or Student(user=u, face_encodings=[])
            st.padron = padron
            st.save()
            students.append(st)

        siu_id = (Commission.objects.order_by("-siu_id")
                  .values_list("siu_id", flat=True).first() or 2000) + 1
        com = Commission.objects.create(
            chief_teacher=chief, subject_siu_id=ssid, subject_name=name,
            siu_id=siu_id, department_id=dept_id["FIS"])
        TeacherRole.objects.create(commission=com, teacher=chief, role="Titular", grader_weight=5.0)

        sem = Semester.objects.create(commission=com, year_moment=ym, start_date=start,
                                      classes_amount=16, minimum_attendance=0.75)
        for st in students:
            CommissionInscription.objects.create(
                semester=sem, student=st,
                status=CommissionInscription.InscriptionStatus.ACCEPTED)

        evals = []
        for ename, off in (("1° Parcial", 45), ("2° Parcial", 95), ("TP Final", 104)):
            ev_date = _plus(start, off)
            ev = Evaluation.objects.create(
                semester=sem, evaluation_name=ename,
                is_graded=True, is_gradeable=True, passing_grade=4,
                start_date=ev_date, end_date=_plus(ev_date, hours=3))
            evals.append(ev)

        n_sub = 0
        for st, (*_meta, grades) in zip(students, SEGUNDA_COMISION_FISICA_STUDENTS):
            for ev, grade in zip(evals, grades):
                status_val = (EvaluationSubmission.SubmissionStatus.APROBADO if grade >= 4
                              else EvaluationSubmission.SubmissionStatus.DESAPROBADO)
                EvaluationSubmission.objects.create(
                    evaluation=ev, student=st, grade=grade, grader=chief,
                    submission_status=status_val)
                n_sub += 1

        print(f"Segunda comisión Física: comisión {com.id} (siu {siu_id}), "
              f"{len(students)} alumnos, {len(evals)} evaluaciones, {n_sub} notas.")

    def _seed_horarios(self):
        """Carga horarios de cursada (SemesterSchedule) para todos los semesters,
        según HORARIOS_POR_MATERIA. Idempotente."""
        n = 0
        for sem in Semester.objects.select_related("commission").all():
            bloques = HORARIOS_POR_MATERIA.get(sem.commission.subject_siu_id)
            if not bloques:
                continue
            for dow, st, et in bloques:
                sh, sm = (int(x) for x in st.split(":"))
                eh, em = (int(x) for x in et.split(":"))
                SemesterSchedule.objects.get_or_create(
                    semester=sem, day_of_week=dow, start_time=time(sh, sm),
                    defaults={"end_time": time(eh, em)})
                n += 1
        print(f"Horarios cargados: {n} bloques en {Semester.objects.count()} semesters.")

    def _restore_google_identities(self):
        """Restaura las identidades de Google (sub real) para que el login con
        Google siga funcionando. Solo toca los usuarios conocidos del dict."""
        for dni, (sub, email) in GOOGLE_IDENTITIES.items():
            u = User.objects.filter(dni=dni).first()
            if u is None:
                continue
            AuthIdentity.objects.update_or_create(
                user=u,
                defaults=dict(provider=AuthIdentity.Provider.GOOGLE,
                              provider_user_id=sub, email=email))

    def _seed_secretaries(self):
        """Crea las secretarías reales de FIUBA según la demo spec."""
        location = "Paseo Colón"
        schedule = "Lunes a Viernes de 8 a 16"

        # Los padres deben aparecer antes que sus hijos.
        entries = [
            dict(name="Secretaría Administrativa", parent_name=None,
                 contact_info="Lic. Guido Regazzoli"),
            dict(name="Secretaría de Coordinación General", parent_name=None,
                 contact_info="Xavier A. Pérez"),
            dict(name="Secretaría de Gestión Académica", parent_name=None,
                 contact_info="Ing. Lucas A. Macias"),
            dict(name="Secretaría de Hábitat", parent_name=None,
                 contact_info="Fernando A. López"),
            dict(name="Secretaría de Bienestar Estudiantil", parent_name=None,
                 contact_info="Gabriel A. González"),
            dict(name="Secretaría de Extensión Universitaria", parent_name=None,
                 contact_info="Prof. Univ. Sofía Della Villa"),
            dict(name="Secretaría de Investigación, Posgrado y Doctorado", parent_name=None,
                 contact_info="Dra. Celina Raquel Bernal"),
            dict(name="Secretaría de Planificación Académica y de Investigación", parent_name=None,
                 contact_info="Inga. Silvia Susana Isaurralde"),
            dict(name="Secretaría de Relaciones Institucionales", parent_name=None,
                 contact_info="Ing. Fernando Horman"),
            dict(name="Subsecretaría de Tecnologías de la Información y Comunicaciones", parent_name=None,
                 contact_info="Ing. Rodrigo Calero"),
            dict(name="Subsecretaría Técnica Legal", parent_name=None,
                 contact_info="Abog. Alejandra Cejas"),
            dict(name="Área de Coordinación para el Proyecto Edilicio", parent_name=None,
                 contact_info="Ing. Luis Nelson Sosti"),
            dict(name="Intercambios Académicos",
                 parent_name="Secretaría de Gestión Académica",
                 contact_info="interac@fi.uba.ar"),
        ]

        n = 0
        for e in entries:
            parent = (Secretary.objects.filter(name=e["parent_name"]).first()
                      if e["parent_name"] else None)
            _, created = Secretary.objects.get_or_create(
                name=e["name"],
                defaults=dict(parent_secretary=parent, location=location,
                              schedule=schedule, contact_info=e["contact_info"]),
            )
            n += created
        total = len(entries)
        print(f"Secretaries: {total} ({total - n} already existed)")

    def _seed_forms(self):
        """Crea los grupos de propiedad y formularios de la demo spec.

        Fuentes:
        - Campos de 'Solicitud cuenta de correo' e 'Intercambios académicos': migración 0066.
        - URL de 'Excepción de correlatividad': migración 0065.
        """
        sec_tic = Secretary.objects.get(
            name="Subsecretaría de Tecnologías de la Información y Comunicaciones")
        sec_interc = Secretary.objects.get(name="Intercambios Académicos")
        departments = list(Department.objects.all())

        def _entity_type(obj):
            if isinstance(obj, Department):
                return FormOwnershipMember.DEPARTMENT
            return FormOwnershipMember.SECRETARY

        ownership_groups = [
            dict(name="Mesa de Ayuda - Subsecretaría TIC",
                 members=[dict(entity=sec_tic, is_editor=True)]),
            dict(name="Intercambios Académicos",
                 members=[dict(entity=sec_interc, is_editor=True)]),
            dict(name="Todos los departamentos",
                 members=[dict(entity=d, is_editor=True) for d in departments]),
        ]

        ng = 0
        for g in ownership_groups:
            group, created = FormOwnershipGroup.objects.get_or_create(name=g["name"])
            ng += created
            for m in g["members"]:
                FormOwnershipMember.objects.get_or_create(
                    group=group,
                    entity_type=_entity_type(m["entity"]),
                    entity_id=m["entity"].pk,
                    defaults={"is_editor": m["is_editor"]},
                )
        total_g = len(ownership_groups)
        print(f"Ownership groups: {total_g} ({total_g - ng} already existed)")

        digital = FormType.objects.get(form_type_value="Digital")
        document = FormType.objects.get(form_type_value="Documento")

        group_tic = FormOwnershipGroup.objects.get(name="Mesa de Ayuda - Subsecretaría TIC")
        group_interc = FormOwnershipGroup.objects.get(name="Intercambios Académicos")
        group_depts = FormOwnershipGroup.objects.get(name="Todos los departamentos")

        def _field_type(value):
            ft, _ = FormFieldType.objects.get_or_create(form_field_type_value=value)
            return ft

        forms = [
            dict(
                form_name="Solicitud cuenta de correo FI.UBA.AR",
                form_description="Solicitud de mail institucional FIUBA",
                form_information=(
                    "El alta tiene un tiempo estimado maximo de 72hs habiles. Una vez generada la cuenta se le enviara "
                    "desde el remitente de Mesa de Ayuda o Google Workspace un correo con los datos de acceso. "
                    "Verificar siempre la carpeta de spam o correos no deseados en caso de que hayan transcurrido mas "
                    "de las 72hs habiles.\n\n"
                    "NOTA: En el caso de los alumnos de grado, es condicion necesaria tener numero de legajo asignado "
                    "para obtener un correo Fiuba.\n\n"
                    "Informacion importante:\n"
                    "1- Los campos nombre y apellido deben ser completados de forma completa.\n"
                    "2- NO completar el formulario mas de una vez. El completar el formulario varias veces solo "
                    "perjudica el procesamiento de datos y hace que los tiempos de creacion sean aun mayores.\n"
                    "3- En caso de ser alumno de posgrado, una vez completado el formulario deberan enviar a "
                    "ayuda@fi.uba.ar la constancia de que se encuentra realizando un Posgrado en la Facultad.\n"
                    "4- En caso de ser alumno del CBC los correos electronicos FIUBA son otorgados solamente a los "
                    "alumnos del CBC que esten cursando una materia en la Facultad (no incluye materias del CBC) o "
                    "bien para aquellos que lo necesiten para algun tramite administrativo."
                ),
                ownership_group=group_tic,
                form_type=digital,
                requires_teacher_validation=False,
                document_source=None,
                fields=[
                    dict(label="Correo", field_type="mail", required=True, catalog_key=None),
                    dict(label="Nombre", field_type="texto", required=True, catalog_key=None),
                    dict(label="Apellido", field_type="texto", required=True, catalog_key=None),
                    dict(label="DNI", field_type="numero", required=True, catalog_key=None),
                    dict(label="Rol en la comunidad FIUBA", field_type="catalog", required=True,
                         catalog_key="rol_en_comunidad"),
                    dict(label="Legajo o Padron", field_type="padron", required=True, catalog_key=None),
                    dict(label="Email de contacto", field_type="mail", required=True, catalog_key=None),
                ],
            ),
            dict(
                form_name="Solicitud de información de intercambios académicos",
                form_description="Solicitud de información sobre programas de intercambio académico",
                form_information=(
                    "¿Querés estar al tanto de las novedades de los intercambios para alumnos de FIUBA sin beca? "
                    "Completá el siguiente formulario para que podamos mantenerte informado."
                ),
                ownership_group=group_interc,
                form_type=digital,
                requires_teacher_validation=False,
                document_source=None,
                fields=[
                    dict(label="Correo", field_type="mail", required=True, catalog_key=None),
                    dict(label="Nombre", field_type="texto", required=True, catalog_key=None),
                    dict(label="Apellido", field_type="texto", required=True, catalog_key=None),
                    dict(label="Padrón", field_type="padron", required=True, catalog_key=None),
                    dict(label="Carrera", field_type="catalog", required=True, catalog_key="carreras"),
                    dict(label="Promedio con CBC y aplazos", field_type="numero", required=True, catalog_key=None),
                    dict(label="¿Podrías realizar un intercambio sin la ayuda económica de una beca?",
                         field_type="checkbox", required=True, catalog_key=None),
                    dict(label="¿Cuántos créditos aprobados tenés?", field_type="numero", required=True,
                         catalog_key=None),
                    dict(label="Correo electrónico FIUBA", field_type="mail", required=True, catalog_key=None),
                    dict(label="¿En qué cuatrimestre te gustaría irte de intercambio?",
                         field_type="texto", required=True, catalog_key=None),
                    dict(label="¿Sabés a qué universidad te gustaría ir?",
                         field_type="texto", required=True, catalog_key=None),
                    dict(label="¿A qué país te gustaría viajar?", field_type="texto", required=True,
                         catalog_key=None),
                    dict(label="¿Tenes pensado postularte a alguna beca?", field_type="checkbox",
                         required=False, catalog_key=None),
                    dict(label="Tipo de beca", field_type="catalog", required=True, catalog_key="tipo_de_beca"),
                    dict(label="Añadir programa de interés en caso de que no esté en las opciones anteriores",
                         field_type="texto", required=False, catalog_key=None),
                    dict(label="Subí tu analítico de materias aprobadas pedido en el Departamento de Alumnos "
                               "(no obligatorio)",
                         field_type="adjunto", required=False, catalog_key=None),
                ],
            ),
            dict(
                form_name="Excepción de correlatividad",
                form_description="Pedido de excepción de correlatividad",
                form_information=None,
                ownership_group=group_depts,
                form_type=document,
                requires_teacher_validation=True,
                document_source="https://cms.fi.uba.ar/uploads/Pedido_de_excepcion_2016_f77cee96e0_b6a398efe5.pdf",
                fields=[
                    dict(label="Adjunto", field_type="adjunto", required=True, catalog_key=None),
                ],
            ),
        ]

        nf = 0
        for f in forms:
            form, created = Form.objects.get_or_create(
                form_name=f["form_name"],
                defaults=dict(
                    form_description=f["form_description"],
                    form_information=f["form_information"],
                    ownership_group=f["ownership_group"],
                    form_type=f["form_type"],
                    requires_teacher_validation=f["requires_teacher_validation"],
                ),
            )
            nf += created
            if created:
                if f["document_source"]:
                    FormDocumentSource.objects.create(
                        form=form, form_document_source=f["document_source"])
                for order, field in enumerate(f["fields"], start=1):
                    catalog = (Catalog.objects.get(catalog_key=field["catalog_key"])
                               if field["catalog_key"] else None)
                    FormField.objects.create(
                        form=form,
                        form_field_label=field["label"],
                        form_field_type=_field_type(field["field_type"]),
                        form_field_require=field["required"],
                        form_field_order=order,
                        catalog=catalog,
                    )

        total_f = len(forms)
        print(f"Forms: {total_f} ({total_f - nf} already existed)")

    def _seed_dept_staff(self):
        """Crea un usuario staff del Departamento de Computación si no existe."""
        dept = Department.objects.get(name="Departamento de Computación")
        user, created = User.objects.get_or_create(
            email="carlos.rodriguez@dept.fi.uba.ar",
            defaults=dict(
                first_name="Carlos",
                last_name="Rodriguez",
                dni="28456123",
                is_staff=True,
                is_active=True,
            ),
        )
        if not hasattr(user, 'staff'):
            Staff.objects.create(user=user, department=dept, department_siu_id=0)
        print(f"Dept staff: 1 ({int(not created)} already existed)")

    def _seed_submissions(self):
        """Puebla con respuestas pre-cargadas los dos formularios digitales de la demo."""

        def _cat(catalog_key, label):
            return str(CatalogItem.objects.get(
                catalog__catalog_key=catalog_key, catalog_item_label=label).pk)

        status_sent = FormSubmissionStatus.objects.get(
            form_submission_status_value=FormSubmissionStatus.SENT)
        status_pending = FormSubmissionStatus.objects.get(
            form_submission_status_value=FormSubmissionStatus.PENDING_APPROVAL)
        status_approved = FormSubmissionStatus.objects.get(
            form_submission_status_value=FormSubmissionStatus.APPROVED)
        status_denied = FormSubmissionStatus.objects.get(
            form_submission_status_value=FormSubmissionStatus.DENIED)

        form_correo = Form.objects.get(form_name="Solicitud cuenta de correo FI.UBA.AR")
        form_interc = Form.objects.get(form_name="Solicitud de información de intercambios académicos")

        sec_tic = Secretary.objects.get(
            name="Subsecretaría de Tecnologías de la Información y Comunicaciones")
        sec_interc = Secretary.objects.get(name="Intercambios Académicos")

        # Idempotente: borra las respuestas previas de estos dos formularios demo.
        FormSubmission.objects.filter(form__in=[form_correo, form_interc]).delete()

        def _fields(form):
            return {f.form_field_label: f for f in form.fields.all()}

        def _submit(form, user, status, recipient_sec, answers, fields):
            sub = FormSubmission.objects.create(
                form=form,
                user=user,
                status=status,
                recipient_entity_type=FormSubmission.RECIPIENT_ENTITY_SECRETARY,
                recipient_entity_id=recipient_sec.pk,
            )
            for label, value in answers.items():
                FormAnswer.objects.create(
                    submission=sub, field=fields[label], answer_value=value)

        # ── Solicitud cuenta de correo FI.UBA.AR ─────────────────────────────
        fc = _fields(form_correo)
        ROL_ALUMNO = _cat("rol_en_comunidad", "Alumno de Grado")

        CORREO_SUBS = [
            dict(
                dni="41835723",
                status=status_approved,
                answers={
                    "Correo": "jandresen@gmail.com",
                    "Nombre": "Joaquin",
                    "Apellido": "Andresen",
                    "DNI": "41835723",
                    "Rol en la comunidad FIUBA": ROL_ALUMNO,
                    "Legajo o Padron": "102707",
                    "Email de contacto": "jandresen@gmail.com",
                },
            ),
            dict(
                dni="43990892",
                status=status_pending,
                answers={
                    "Correo": "lsalluzi@gmail.com",
                    "Nombre": "Luca",
                    "Apellido": "Salluzzi",
                    "DNI": "43990892",
                    "Rol en la comunidad FIUBA": ROL_ALUMNO,
                    "Legajo o Padron": "108088",
                    "Email de contacto": "lsalluzi@gmail.com",
                },
            ),
            dict(
                dni="41779246",
                status=status_sent,
                answers={
                    "Correo": "ggordyn@gmail.com",
                    "Nombre": "Gonzalo",
                    "Apellido": "Gordyn Biello",
                    "DNI": "41779246",
                    "Rol en la comunidad FIUBA": ROL_ALUMNO,
                    "Legajo o Padron": "104503",
                    "Email de contacto": "ggordyn@gmail.com",
                },
            ),
            dict(
                dni="42817479",
                status=status_denied,
                answers={
                    "Correo": "mgonzalezp@gmail.com",
                    "Nombre": "Martin",
                    "Apellido": "Gonzalez Prieto",
                    "DNI": "42817479",
                    "Rol en la comunidad FIUBA": ROL_ALUMNO,
                    "Legajo o Padron": "105738",
                    "Email de contacto": "mgonzalezp@gmail.com",
                },
            ),
        ]

        for s in CORREO_SUBS:
            _submit(form_correo, User.objects.get(dni=s["dni"]), s["status"], sec_tic, s["answers"], fc)
        print(f"Form submissions created: {len(CORREO_SUBS)} ({form_correo.form_name})")

        # ── Solicitud de información de intercambios académicos ───────────────
        fi = _fields(form_interc)
        INFORMATICA = _cat("carreras", "Ing. en Informática")

        INTERC_SUBS = [
            dict(
                dni="43459394",
                status=status_sent,
                answers={
                    "Correo": "vlanzillotta@gmail.com",
                    "Nombre": "Valentina",
                    "Apellido": "Lanzillotta",
                    "Padrón": "108257",
                    "Carrera": INFORMATICA,
                    "Promedio con CBC y aplazos": "8.2",
                    "¿Podrías realizar un intercambio sin la ayuda económica de una beca?": "false",
                    "¿Cuántos créditos aprobados tenés?": "160",
                    "Correo electrónico FIUBA": "vlanzillotta@fi.uba.ar",
                    "¿En qué cuatrimestre te gustaría irte de intercambio?": "1C2027",
                    "¿Sabés a qué universidad te gustaría ir?": "Universidad Politécnica de Madrid",
                    "¿A qué país te gustaría viajar?": "España",
                    "¿Tenes pensado postularte a alguna beca?": "true",
                    "Tipo de beca": _cat("tipo_de_beca", "Doble Diploma"),
                    "Añadir programa de interés en caso de que no esté en las opciones anteriores": "",
                    "Subí tu analítico de materias aprobadas pedido en el Departamento de Alumnos (no obligatorio)": None,
                },
            ),
            dict(
                dni="42150053",
                status=status_pending,
                answers={
                    "Correo": "mmerlog@gmail.com",
                    "Nombre": "Matías Sebastián",
                    "Apellido": "Merlo Gonzalez",
                    "Padrón": "104093",
                    "Carrera": INFORMATICA,
                    "Promedio con CBC y aplazos": "7.5",
                    "¿Podrías realizar un intercambio sin la ayuda económica de una beca?": "true",
                    "¿Cuántos créditos aprobados tenés?": "140",
                    "Correo electrónico FIUBA": "mmerlog@fi.uba.ar",
                    "¿En qué cuatrimestre te gustaría irte de intercambio?": "2C2026",
                    "¿Sabés a qué universidad te gustaría ir?": "Tecnológico de Monterrey",
                    "¿A qué país te gustaría viajar?": "México",
                    "¿Tenes pensado postularte a alguna beca?": "false",
                    "Tipo de beca": _cat("tipo_de_beca", "Programa sin beca"),
                    "Añadir programa de interés en caso de que no esté en las opciones anteriores": "",
                    "Subí tu analítico de materias aprobadas pedido en el Departamento de Alumnos (no obligatorio)": None,
                },
            ),
            dict(
                dni="43775927",
                status=status_approved,
                answers={
                    "Correo": "isuarezp@gmail.com",
                    "Nombre": "Imanol",
                    "Apellido": "Suarez Pino",
                    "Padrón": "107746",
                    "Carrera": INFORMATICA,
                    "Promedio con CBC y aplazos": "9.1",
                    "¿Podrías realizar un intercambio sin la ayuda económica de una beca?": "false",
                    "¿Cuántos créditos aprobados tenés?": "170",
                    "Correo electrónico FIUBA": "isuarezp@fi.uba.ar",
                    "¿En qué cuatrimestre te gustaría irte de intercambio?": "1C2027",
                    "¿Sabés a qué universidad te gustaría ir?": "Université Paris-Saclay",
                    "¿A qué país te gustaría viajar?": "Francia",
                    "¿Tenes pensado postularte a alguna beca?": "true",
                    "Tipo de beca": _cat("tipo_de_beca", "Programa UBAInt"),
                    "Añadir programa de interés en caso de que no esté en las opciones anteriores": "",
                    "Subí tu analítico de materias aprobadas pedido en el Departamento de Alumnos (no obligatorio)": None,
                },
            ),
            dict(
                dni="42817479",
                status=status_sent,
                answers={
                    "Correo": "mgonzalezp@gmail.com",
                    "Nombre": "Martin",
                    "Apellido": "Gonzalez Prieto",
                    "Padrón": "105738",
                    "Carrera": INFORMATICA,
                    "Promedio con CBC y aplazos": "8.8",
                    "¿Podrías realizar un intercambio sin la ayuda económica de una beca?": "true",
                    "¿Cuántos créditos aprobados tenés?": "155",
                    "Correo electrónico FIUBA": "mgonzalezp@fi.uba.ar",
                    "¿En qué cuatrimestre te gustaría irte de intercambio?": "2C2026",
                    "¿Sabés a qué universidad te gustaría ir?": "KTH Royal Institute of Technology",
                    "¿A qué país te gustaría viajar?": "Suecia",
                    "¿Tenes pensado postularte a alguna beca?": "true",
                    "Tipo de beca": _cat("tipo_de_beca", "Beca Aelarg"),
                    "Añadir programa de interés en caso de que no esté en las opciones anteriores": "",
                    "Subí tu analítico de materias aprobadas pedido en el Departamento de Alumnos (no obligatorio)": None,
                },
            ),
        ]

        for s in INTERC_SUBS:
            _submit(form_interc, User.objects.get(dni=s["dni"]), s["status"], sec_interc, s["answers"], fi)
        print(f"Form submissions created: {len(INTERC_SUBS)} ({form_interc.form_name})")

    def _report(self, c, students, dropped):
        w = self.stdout.write
        w(self.style.SUCCESS("Seed académico OK:"))
        for k in ("com", "fin_ap", "fin_pend", "ev", "sub", "fe", "ins", "qr", "att", "pwd"):
            w(f"  {k:<9}: {c[k]}")
        w("Alumnos:")
        for dni, padron, fn, ln, _e, _n in STUDENTS:
            ap = FinalExam.objects.filter(student__user__dni=dni, grade__gte=4).count()
            pend = FinalExam.objects.filter(student__user__dni=dni, grade__isnull=True).count()
            drops = ", ".join(sorted(dropped[dni])) or "—"
            w(f"  {fn} {ln:<18} pad {padron} aprobadas={ap} pendientes={pend} sin: {drops}")
