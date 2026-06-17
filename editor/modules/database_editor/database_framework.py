class DatabaseRecord:
    def __init__(self, record_id, title, summary_parts, detail_rows, flags=None):
        self.id = record_id
        self.title = title
        self.summary_parts = summary_parts
        self.detail_rows = detail_rows
        self.flags = flags or {}


class DatabaseCategory:
    def __init__(self, category_id, label, provider=None, planned=False):
        self.id = category_id
        self.label = label
        self.provider = provider
        self.planned = planned

    def is_active(self):
        return self.provider is not None

    def get_records(self):
        if self.provider is None:
            return []

        return self.provider.get_records()

    def update_record_field(self, record_id, path, text_value):
        if self.provider is None:
            return False, "Categoria sin proveedor."

        return self.provider.update_record_field(record_id, path, text_value)

    def save_record(self, record_id):
        if self.provider is None:
            return False, "Categoria sin proveedor."

        return self.provider.save_record(record_id)

    def is_record_dirty(self, record_id):
        if self.provider is None:
            return False

        return self.provider.is_record_dirty(record_id)


class StaticPlannedProvider:
    def __init__(self, message="Categoria prevista. Sin funcionalidad activa todavia."):
        self.message = message

    def get_records(self):
        return []
