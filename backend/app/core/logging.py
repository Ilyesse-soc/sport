import logging
import re


class RedactFilter(logging.Filter):
    PATTERNS = [
        re.compile(r"(authorization\s*[:=]\s*bearer\s+)[A-Za-z0-9\-_.=]+", re.IGNORECASE),
        re.compile(r"(api[_-]?key\s*[:=]\s*)[^\s,;]+", re.IGNORECASE),
        re.compile(r"(token\s*[:=]\s*)[^\s,;]+", re.IGNORECASE),
        re.compile(r"(password\s*[:=]\s*)[^\s,;]+", re.IGNORECASE),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        message = str(record.getMessage())
        for pattern in self.PATTERNS:
            message = pattern.sub(r"\1[REDACTED]", message)
        record.msg = message
        record.args = ()
        return True


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logging.getLogger().addFilter(RedactFilter())
