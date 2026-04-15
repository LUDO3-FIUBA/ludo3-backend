# Python implementation of Libreta Universitaria Digital Oficial

## Run Locally

### Requirements
- Python3
- PostgreSQL

### Setup dependencies
```
1. Get Python 3.7+
2. Install pip
3. pip3 install -r requirements.txt
```

### Setup DB
Create role and database 'ludo' with password 'ludo' locally.
```
sudo -u postgres psql;
create database ludo;
```

### Setup initial data
Run the following every time the database is created from scratch:
- python3 manage.py migrate
- python3 manage.py initdata

## Migrate
For each change in your models that implicates a change in the data stored in the database, you will
have to run the following
- `python3 manage.py makemigrations` to create migrations for those changes
- `python3 manage.py migrate` to apply those changes to the database.

## Run Server
Run
```
python3 manage.py runserver
```
The server will start by default on the port 8000

## Run with Docker

### Setup
Duplicate `.env.template` and rename to `.env`. Complete the secrets with the correct values.

### `make up-local`
Starts the full local environment: Django server, PostgreSQL database, and fake SIU service, all in Docker containers. The DB runs in a `postgres:12` container with data persisted in a Docker volume. Uses `.env.compose` + `.env` for configuration.

```bash
make up-local   # or just `make up`
```

### `make up-remote`
Starts the Django server and fake SIU service **without** a local database container. Connects to an external PostgreSQL database configured via the `SQL_*` variables in your `.env` file. Useful for working against a shared or cloud-hosted database.

```bash
make up-remote
```

### `make down`
Stops and removes all containers from both configurations.

```bash
make down
```

In both cases, the server runs on port **8007**. Admin dashboard URL is http://localhost:8007/admin

#### Populate the Database

For the first time, you'll need to run a migration and seed the DB. For this run:
```bash
docker exec -it web python3 manage.py migrate
docker exec -it web python3 manage.py initdata
```

Debug: in case you want to explore the DB using PSQL, you can run:
```bash
docker exec -it db psql --user ludo --db ludo_dev
```

And explore present tables with `\d [TABLE]`:
```
PS C:\Users\PC\Documents\repos\ludo2\ludo2-backend> docker exec -it ludo2-backend-db-1 psql --user ludo --db ludo_dev
psql (12.0)
Type "help" for help.

ludo_dev=# \d
                          List of relations
 Schema |                  Name                   |   Type   | Owner
--------+-----------------------------------------+----------+-------
 public | auth_group                              | table    | ludo
 public | auth_group_id_seq                       | sequence | ludo
 public | auth_group_permissions                  | table    | ludo
 public | auth_group_permissions_id_seq           | sequence | ludo
 public | auth_permission                         | table    | ludo
 public | auth_permission_id_seq                  | sequence | ludo
 public | authtoken_token                         | table    | ludo
 public | backend_final                           | table    | ludo
 public | backend_final_id_seq                    | sequence | ludo
 public | backend_finalexam                       | table    | ludo
 public | backend_finalexam_id_seq                | sequence | ludo
 public | backend_staff                           | table    | ludo
 public | backend_student                         | table    | ludo
 public | backend_teacher                         | table    | ludo
 public | backend_user                            | table    | ludo
 public | backend_user_groups                     | table    | ludo
 public | backend_user_groups_id_seq              | sequence | ludo
 public | backend_user_id_seq                     | sequence | ludo
 public | backend_user_user_permissions           | table    | ludo
 public | backend_user_user_permissions_id_seq    | sequence | ludo
 public | django_admin_log                        | table    | ludo
 public | django_admin_log_id_seq                 | sequence | ludo
 public | django_content_type                     | table    | ludo
 public | django_content_type_id_seq              | sequence | ludo
 public | django_migrations                       | table    | ludo
 public | django_migrations_id_seq                | sequence | ludo
 public | django_session                          | table    | ludo
 public | push_notifications_apnsdevice           | table    | ludo
 public | push_notifications_apnsdevice_id_seq    | sequence | ludo
 public | push_notifications_gcmdevice            | table    | ludo
 public | push_notifications_gcmdevice_id_seq     | sequence | ludo
 public | push_notifications_webpushdevice        | table    | ludo
 public | push_notifications_webpushdevice_id_seq | sequence | ludo
 public | push_notifications_wnsdevice            | table    | ludo
 public | push_notifications_wnsdevice_id_seq     | sequence | ludo
(35 rows)

ludo_dev=# \d backend_user
                                        Table "public.backend_user"
    Column    |           Type           | Collation | Nullable |                 Default
--------------+--------------------------+-----------+----------+------------------------------------------
 id           | integer                  |           | not null | nextval('backend_user_id_seq'::regclass)
 password     | character varying(128)   |           | not null |
 last_login   | timestamp with time zone |           |          |
 is_superuser | boolean                  |           | not null |
 email        | character varying(254)   |           | not null |
 is_staff     | boolean                  |           | not null |
 is_active    | boolean                  |           | not null |
 date_joined  | timestamp with time zone |           | not null |
 is_student   | boolean                  |           | not null |
 is_teacher   | boolean                  |           | not null |
 first_name   | character varying(50)    |           | not null |
 last_name    | character varying(50)    |           | not null |
 username     | character varying(30)    |           | not null |
 dni          | character varying(9)     |           | not null |
 created_at   | timestamp with time zone |           | not null |
 updated_at   | timestamp with time zone |           | not null |
```

## API Specification

------------------------------------------------------------------------------------------

#### Commissions

<details>
 <summary><code>GET</code> <code><b>/api/commissions/</b></code> <code>(lists commissions)</code></summary>

##### Parameters

> | name      |  type     | description                                                           |
> |-----------|-----------|-----------------------------------------------------------------------|
> | None      |  required | N/A  |

</details>

<details>
 <summary><code>GET</code> <code><b>/api/commissions/subject_commissions</b></code> <code>(lists subject commissions)</code></summary>

##### Parameters

> | name      |  type     | description                                                           |
> |-----------|-----------|-----------------------------------------------------------------------|
> | subject_siu_id |  required | Subject id in siu service |

</details>

<details>
 <summary><code>GET</code> <code><b>/api/commissions/teachers</b></code> <code>(lists commission teachers)</code></summary>

##### Parameters

> | name      |  type     | description                                                           |
> |-----------|-----------|-----------------------------------------------------------------------|
> | commission_id |  required | Id of commission to get teachers from |

</details>

<details>
 <summary><code>GET</code> <code><b>/api/teacher/commissions/my_commissions/</b></code> <code>(lists commissions you are a teacher on)</code></summary>

##### Parameters

> | name      |  type     | description                                                           |
> |-----------|-----------|-----------------------------------------------------------------------|
> | None      |  required | N/A  |

</details>

------------------------------------------------------------------------------------------

#### Semesters

<details>
 <summary><code>GET</code> <code><b>/api/semesters/subject_semesters</b></code> <code>(lists subject semesters)</code></summary>

##### Parameters

> | name      |  type     | description                                                           |
> |-----------|-----------|-----------------------------------------------------------------------|
> | subject_siu_id |  required | Subject id in siu service |

</details>

<details>
 <summary><code>GET</code> <code><b>/api/semesters/present_subject_semesters</b></code> <code>(lists current subject semesters)</code></summary>

##### Parameters

> | name      |  type     | description                                                           |
> |-----------|-----------|-----------------------------------------------------------------------|
> | subject_siu_id |  required | Subject id in siu service |

</details>

<details>
 <summary><code>GET</code> <code><b>/api/semesters/commission_present_semester</b></code> <code>(gets current semester for a commission)</code></summary>

##### Parameters

> | name      |  type     | description                                                           |
> |-----------|-----------|-----------------------------------------------------------------------|
> | commission_id |  required | Id of the commission you want to get the semester from |

</details>

<details>
 <summary><code>GET</code> <code><b>/api/teacher/semesters/:id/students</b></code> <code>(list students enrolled in the provided semester)</code></summary>

##### Parameters

> | name      |  type     | description                                                           |
> |-----------|-----------|-----------------------------------------------------------------------|
> | id |  required | Id of the semester you want to list from |

</details>

------------------------------------------------------------------------------------------

#### Commission Inscription

<details>
 <summary><code>GET</code> <code><b>/api/commission_inscription/</b></code> <code>(lists commission inscriptions for student)</code></summary>

##### Parameters

> | name      |  type     | description                                                           |
> |-----------|-----------|-----------------------------------------------------------------------|
> | None      |  required | N/A  |

</details>

<details>
 <summary><code>GET</code> <code><b>/api/commission_inscription/current_inscriptions/</b></code> <code>(lists current commission inscriptions for student)</code></summary>

##### Parameters

> | name      |  type     | description                                                           |
> |-----------|-----------|-----------------------------------------------------------------------|
> | subject_siu_id |  required | Subject id in siu service |

</details>

------------------------------------------------------------------------------------------

#### Evaluation

<details>
 <summary><code>GET</code> <code><b>/api/evaluations/</b></code> <code>(lists evaluations for semester)</code></summary>

##### Parameters

> | name      |  type     | description                                                           |
> |-----------|-----------|-----------------------------------------------------------------------|
> | semester_id |  required | Id of the semester you want the evaluations from |

</details>

<details>
 <summary><code>GET</code> <code><b>/api/evaluations/mis_examenes</b></code> <code>(lists future evaluations for student)</code></summary>

##### Parameters

> | name      |  type     | description                                                           |
> |-----------|-----------|-----------------------------------------------------------------------|
> | None      |  required | N/A  |

</details>

<details>
 <summary><code>POST</code> <code><b>/api/teacher/evaluations/add_evaluation/</b></code> <code>(add evaluation for semester)</code></summary>

##### Parameters

> | name      |  type     |  data type     | description                                                           |
> |-----------|-----------|----------------|-----------------------------------------------------------------------|
> | semester_id |  required |  integer | Id of the semester you want the evaluations from |
> | evaluation_name |  required |  string | Name of the evaluation |
> | is_graded |  required |  boolean | If the evaluation should be graded or not |
> | passing_grade | not required |  integer | Minimum grade in wich the evaluation is considered passed |
> | start_date | not required |  datetime | Start date of the evaluation in case it is take home |
> | end_date |  required |  datetime | Date in which the evaluation is handed in |

</details>

------------------------------------------------------------------------------------------

#### Evaluation Submission

<details>
 <summary><code>POST</code> <code><b>/api/evaluations/submissions/submit_evaluation/</b></code> <code>(post evaluation submission)</code></summary>

##### Parameters

> | name      |  type     |  data type     | description                                                           |
> |-----------|-----------|----------------|-----------------------------------------------------------------------|
> | evaluation |  required |  integer | Id of the evaluation |

</details>

<details>
 <summary><code>GET</code> <code><b>/api/evaluations/submissions/my_evaluations/</b></code> <code>(lists evaluation submissions for student)</code></summary>

##### Parameters

> | name      |  type     | description                                                           |
> |-----------|-----------|-----------------------------------------------------------------------|
> | None      |  required | N/A  |

</details>

<details>
 <summary><code>GET</code> <code><b>/api/evaluations/:id/my_submissions</b></code> <code>(lists evaluation submissions for student in particular evaluation)</code></summary>

##### Parameters

> | name      |  type     | description                                                           |
> |-----------|-----------|-----------------------------------------------------------------------|
> | id |  required | Id of the evaluation  |

</details>

<details>
 <summary><code>GET</code> <code><b>/api/teacher/evaluations/submissions/get_submissions</b></code> <code>(get submissions for an evaluation)</code></summary>

##### Parameters

> | name      |  type     | description                                                           |
> |-----------|-----------|-----------------------------------------------------------------------|
> | evaluation |  required | Id of the evaluation  |

</details>

<details>
 <summary><code>PUT</code> <code><b>/api/teacher/evaluations/submissions/assign_grader</b></code> <code>(assigns a grader to a submission without grading it)</code></summary>

##### Parameters

> | name      |  type     |  data type     | description                                                           |
> |-----------|-----------|----------------|-----------------------------------------------------------------------|
> | evaluation |  required |  integer | Id of the evaluation |
> | student |  required |  integer | Id of the student that sent the submission |
> | grader_teacher |  required |  integer | Id of the teacher that should be assigned as grader |

</details>

<details>
 <summary><code>PUT</code> <code><b>/api/teacher/evaluations/submissions/auto_assign_graders</b></code> <code>(auto-assigns graders to **ALL** submissions in an evaluation)</code></summary>

##### Parameters

> | name      |  type     |  data type     | description                                                           |
> |-----------|-----------|----------------|-----------------------------------------------------------------------|
> | evaluation |  required |  integer | Id of the evaluation |

</details>

<details>
 <summary><code>PUT</code> <code><b>/api/teacher/evaluations/submissions/grade</b></code> <code>(grades a submission, setting the logged-in teacher as grader)</code></summary>

##### Parameters

> | name      |  type     |  data type     | description                                                           |
> |-----------|-----------|----------------|-----------------------------------------------------------------------|
> | evaluation |  required |  integer | Id of the evaluation |
> | student |  required |  integer | Id of the student that sent the submission |
> | grade |  required |  integer | Submission grade (from 0 to 10) |

</details>


------------------------------------------------------------------------------------------

#### Attendance

<details>
 <summary><code>POST</code> <code><b>/api/semesters/attendance</b></code> <code>(as a student, mark attendance for a specific QR code)</code></summary>

##### Parameters

> | name      |  type     |  data type     | description                                                           |
> |-----------|-----------|----------------|-----------------------------------------------------------------------|
> | qr_id |  required |  string | UUID of the QR code you want to mark as scanned |

</details>

------------------------------------------------------------------------------------------

#### Attendance QRs

<details>
 <summary><code>POST</code> <code><b>/api/teacher/semesters/attendance/latest_qr</b></code> <code>(as a teacher, retrieve the latest valid QR code idempotently or create a new one to track attendance)</code></summary>

##### Parameters

> | name      |  type     |  data type     | description                                                           |
> |-----------|-----------|----------------|-----------------------------------------------------------------------|
> | semester |  required |  integer | Id of the semester you want to get or create a QR for |

</details>

<details>
 <summary><code>POST</code> <code><b>/api/teacher/semesters/attendance/qr</b></code> <code>(as a teacher, create a new QR code to track attendance)</code></summary>

##### Parameters

> | name      |  type     |  data type     | description                                                           |
> |-----------|-----------|----------------|-----------------------------------------------------------------------|
> | semester |  required |  integer | Id of the semester you want to create a QR for |

</details>

------------------------------------------------------------------------------------------

## Deployed application
The application is running at `https://ludo-backend.herokuapp.com`

## License
This source code is property of er-inc and cannot be publicly distributed without explicit consent.

This project is maintained by **Federico Esteban** (fede.est@gmail.comn) and **Daniela Riesgo** (daniealp.riesgo@gmail.com)
