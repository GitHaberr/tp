NEW = "new"
IN_PROGRESS = "in_progress"
REVIEW = "review"
DONE = "done"

STATUS_LABELS = {
    NEW: "Новая",
    IN_PROGRESS: "В работе",
    REVIEW: "На проверке",
    DONE: "Выполнена",
}

STATUSES = list(STATUS_LABELS.keys())

ALLOWED_TRANSITIONS = {
    (NEW, IN_PROGRESS),
}

ACTION_LABELS = {
    "created": "Создал поручение",
    "status_changed": "Изменил статус",
    "submitted": "Передал на проверку",
    "approved": "Подтвердил выполнение",
    "rejected": "Вернул в работу",
}
