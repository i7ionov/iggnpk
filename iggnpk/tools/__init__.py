from django.db.models import Field

from tools.NotEqualLookup import NotEqual

Field.register_lookup(NotEqual)
