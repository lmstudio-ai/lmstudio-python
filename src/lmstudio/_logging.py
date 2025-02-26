"""SDK logging support."""

import json
import logging

from typing import Any

# It's difficult to make a general purpose structured logging
# library play nice with arbitrary applications, so we instead
# implement rudimentary structured logging support based on the
# relevant standard library recipe:
#
# https://docs.python.org/3/howto/logging-cookbook.html#implementing-structured-logging

# TODO: Consider using context variables to pass event context state between API layers
#       In particular, associating json_api endpoint processing with the corresponding
#       multiplexing IDs in sync_api and async_api. Explicitly passing the IDs to the
#       message handling APIs purely for logging purposes would be outright annoying.

LogEventContext = dict[str, Any]


class StructuredLogEvent:
    def __init__(self, event: str, event_dict: LogEventContext) -> None:
        event_dict["event"] = event
        self.event = event
        self.event_dict = event_dict

    def as_formatted_json(self) -> str:
        return json.dumps(self.event_dict, sort_keys=True)

    def __str__(self) -> str:
        return str(self.as_formatted_json())


class StructuredLogger:
    def __init__(self, logger: logging.Logger) -> None:
        self._stdlib_logger = logger
        self.event_context: LogEventContext = {}

    def update_context(
        self, log_context: LogEventContext | None = None, /, **additional_context: Any
    ) -> None:
        event_context = self.event_context
        if log_context is not None:
            event_context.update(log_context)
        event_context.update(additional_context)

    def _log(
        self,
        level: int,
        msg: str,
        exc_info: bool,
        stack_info: bool,
        stacklevel: int,
        event_dict: LogEventContext,
    ) -> None:
        event_data = self.event_context.copy()
        event_data.update(event_dict)
        logged_msg = StructuredLogEvent(msg, event_data)
        stacklevel = stacklevel + 1
        self._stdlib_logger.log(
            level,
            logged_msg,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=event_data,
        )

    def log(
        self,
        level: int,
        msg: str,
        *,
        exc_info: bool = False,
        stack_info: bool = False,
        stacklevel: int = 1,
        **event_dict: Any,
    ) -> None:
        stacklevel = stacklevel + 1
        self._log(level, msg, exc_info, stack_info, stacklevel, event_dict)

    def debug(
        self,
        msg: str,
        *,
        exc_info: bool = False,
        stack_info: bool = False,
        stacklevel: int = 1,
        **event_dict: Any,
    ) -> None:
        stacklevel = stacklevel + 1
        self._log(logging.DEBUG, msg, exc_info, stack_info, stacklevel, event_dict)

    def info(
        self,
        msg: str,
        *,
        exc_info: bool = False,
        stack_info: bool = False,
        stacklevel: int = 1,
        **event_dict: Any,
    ) -> None:
        stacklevel = stacklevel + 1
        self._log(logging.INFO, msg, exc_info, stack_info, stacklevel, event_dict)

    def warn(
        self,
        msg: str,
        *,
        exc_info: bool = False,
        stack_info: bool = False,
        stacklevel: int = 1,
        **event_dict: Any,
    ) -> None:
        stacklevel = stacklevel + 1
        self._log(logging.WARN, msg, exc_info, stack_info, stacklevel, event_dict)

    def error(
        self,
        msg: str,
        *,
        exc_info: bool = False,
        stack_info: bool = False,
        stacklevel: int = 1,
        **event_dict: Any,
    ) -> None:
        stacklevel = stacklevel + 1
        self._log(logging.ERROR, msg, exc_info, stack_info, stacklevel, event_dict)

    def exception(self, msg: str, *, stacklevel: int = 1, **event_dict: Any) -> None:
        stacklevel = stacklevel + 1
        # Setting exc_info and stack_info is implied by calling this method instead of `error()`
        self._log(logging.ERROR, msg, True, True, stacklevel, event_dict)

    def critical(
        self,
        msg: str,
        *,
        exc_info: bool = False,
        stack_info: bool = False,
        stacklevel: int = 1,
        **event_dict: Any,
    ) -> None:
        stacklevel = stacklevel + 1
        self._log(logging.CRITICAL, msg, exc_info, stack_info, stacklevel, event_dict)


def get_logger(name: str, /, *args: Any, **kwds: Any) -> StructuredLogger:
    return StructuredLogger(logging.getLogger(name, *args, **kwds))
