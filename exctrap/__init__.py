"""Exctrap: Trap exceptions for retry.

Recipe for a basic retry invocation looks like this:

    for etrapper in exctrap.trial():
        with etrapper:
            # Do whatever that may fail.
        # Will reach here whether or not an exception is raised.
        # If you want to reraise the exception here, use etrapper.reraise().
    # If retry fails, the last exception is reraised so this is not reached.

If you want to know the trial number, simply iterate over
enumerate(exctrap.trial()):

    for cnt, etrapper in enumerate(exctrap.trial()):
        # cnt starts from 0
        with etrapper:
            # The rest is as above

There are various options to adjust how long trial() waits to repeat
the operation.  See the documentation for trial().
"""

import random
import time
import types
import typing


class ExcTrapper:
    """Trap exceptions.

    When used as a context manager, exceptions are trapped and is kept
    in the object for inspection.  E.g.,

        with exctrap.ExcTrapper() as etrapper:
            raise RuntimeError('foo')
        print(str(etrapper.exc[0]))  # Print foo

    The "exc" tuple contains two elements: the exception trapped, and
    the associated traceback object.  The normal way to use it is to
    call reraise().

    Args:
        etypes: The exception types to trap.
    """
    def __init__(
            self,
            etypes: typing.Tuple[typing.Type[BaseException], ...] = (Exception,)
    ):
        self._etypes = etypes
        self.exc: typing.Optional[
            typing.Tuple[BaseException, types.TracebackType]
        ] = None

    def __enter__(self) -> None:
        """Enter the context manager."""

    def __exit__(
            self, etype: typing.Type[BaseException], value: BaseException,
            traceback: types.TracebackType
    ) -> typing.Optional[bool]:
        """Exit the context manager.

        Swallow an exception if one is found to be raised, exposing it
        in the exc field.
        """
        if isinstance(value, self._etypes):
            self.exc = (value, traceback)
            return True  # Swallow exception
        return None

    def reraise(self) -> None:
        """Re-raise the stored exception, if any."""
        if self.exc:
            raise self.exc[0].with_traceback(self.exc[1])


def trial(
        num_tries: int = 3, retry_period: float = 3, *,
        period_noise: float = 0.25,
        backoff: int = 0, backoff_ratio: float = 2,
        etypes: typing.Tuple[typing.Type[BaseException], ...] = (Exception,)
) -> typing.Iterator[ExcTrapper]:
    """Retry logic

    Generator which yield exception trappers, and stops when no
    exception is trapped by it for an iteration.  Users are supposed
    to use "for" to iterate through the exception trappers, and have
    an immediate "with" statement for the exception trapper following
    it to trap exceptions thrown by whatever to be run in it, like:

        for cnt, etrapper in atm.trial():  # cnt starts from 0
            with etrapper:
                ... # The operations that need retrying

    Args:

        num_tries: Maximum number of retries.

        retry_period: Number of seconds to wait between tries, to be
            modified by period_noise.

        period_noise: Add or subtract at most this fraction of the
            retry_period to get the actual amount of seconds to sleep.

        backoff: Change (normally, increase) retry_period this many
            times from the second trial.  After that the retry_period
            will stay the same as the last one.

        backoff_ratio: When changing the retry_period, multiply by
            this number.

        etypes: Exception types to trap.  Other exceptions are raised
            directly without attempts for retry.
    """
    for cnt in range(num_tries):
        if cnt:
            if 1 < cnt < backoff + 2:
                retry_period *= backoff_ratio
            rnum = random.uniform(1 - period_noise, 1 + period_noise)
            time.sleep(max(rnum * retry_period, 0))
        etrapper = ExcTrapper(etypes)
        yield etrapper
        if not etrapper.exc:
            return
    etrapper.reraise()
