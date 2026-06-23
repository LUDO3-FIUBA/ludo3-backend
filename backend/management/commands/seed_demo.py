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
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.core.management import BaseCommand
from django.db import transaction

from backend.models import (
    Student, Teacher, Department, Commission, CommissionInscription,
    Semester, Evaluation, EvaluationSubmission, Final, FinalExam,
    Attendance, AttendanceQRCode,
)
from backend.models.auth_identity import AuthIdentity
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
