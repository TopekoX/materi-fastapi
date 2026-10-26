import contextvars
import json
import logging
import logging.config
import re
from datetime import datetime, timezone

# Pengenal request yang sedang diproses; setiap request punya nilainya sendiri.
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")

POLA_RAHASIA = re.compile(r"(?i)\b(kata_sandi|password|token|authorization|secret_key)(\s*[=:]\s*)\S+")


class FilterRequestId(logging.Filter):
    """Menambahkan request_id ke setiap catatan log."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


class FilterRahasia(logging.Filter):
    """Jaring pengaman: menyamarkan nilai yang tampak rahasia. Tetap jangan mencatat rahasia."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = POLA_RAHASIA.sub(r"\1\2***", record.getMessage())
        record.args = ()
        return True


class FormatJson(logging.Formatter):
    """Satu baris JSON per catatan log."""

    def format(self, record: logging.LogRecord) -> str:
        isi = {
            "waktu": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "request_id": getattr(record, "request_id", "-"),
            "pesan": record.getMessage(),
        }
        if record.exc_info:
            isi["galat"] = self.formatException(record.exc_info)
        return json.dumps(isi, ensure_ascii=False)


def atur_logging(level: str = "INFO", format_log: str = "teks") -> None:
    formatter = "json" if format_log == "json" else "teks"
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "request_id": {"()": FilterRequestId},
                "rahasia": {"()": FilterRahasia},
            },
            "formatters": {
                "teks": {"format": "%(asctime)s %(levelname)-8s [%(request_id)s] %(name)s: %(message)s"},
                "json": {"()": FormatJson},
            },
            "handlers": {
                "konsol": {
                    "class": "logging.StreamHandler",
                    "formatter": formatter,
                    "filters": ["request_id", "rahasia"],
                    "stream": "ext://sys.stdout",
                }
            },
            "loggers": {
                "tugasku": {"handlers": ["konsol"], "level": level, "propagate": False},
            },
        }
    )
