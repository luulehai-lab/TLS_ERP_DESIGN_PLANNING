E402 Module level import not at top of file
  --> scratch\test_db.py:14:1
   |
12 |     sys.path.insert(0, str(BASE_DIR))
13 |
14 | from core.database import engine, Base, SessionLocal
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
15 | from core.models import Project, Drawing, DrawingLog, BOMDetail
   |

E402 Module level import not at top of file
  --> scratch\test_db.py:15:1
   |
14 | from core.database import engine, Base, SessionLocal
15 | from core.models import Project, Drawing, DrawingLog, BOMDetail
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
16 |
17 | def test_db_setup():
   |

F401 [*] `core.models.BOMDetail` imported but unused
  --> scratch\test_db.py:15:55
   |
14 | from core.database import engine, Base, SessionLocal
15 | from core.models import Project, Drawing, DrawingLog, BOMDetail
   |                                                       ^^^^^^^^^
16 |
17 | def test_db_setup():
   |
help: Remove unused import: `core.models.BOMDetail`

F401 [*] `core.models.Project` imported but unused
  --> scratch\test_services.py:17:25
   |
16 | from core.database import Base
17 | from core.models import Project, Drawing, DrawingLog
   |                         ^^^^^^^
18 | from core.services import project_service, drawing_service
   |
help: Remove unused import

F401 [*] `core.models.Drawing` imported but unused
  --> scratch\test_services.py:17:34
   |
16 | from core.database import Base
17 | from core.models import Project, Drawing, DrawingLog
   |                                  ^^^^^^^
18 | from core.services import project_service, drawing_service
   |
help: Remove unused import

Found 5 errors.
[*] 3 fixable with the `--fix` option.
