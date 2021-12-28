# exctrap: Trap exceptions for retry

It is not uncommon to have Python code that requires exceptions to be
trapped, with the code triggering it retried, e.g., to handle
temporary network or host failures when fetching web resources.  There
are quite a few Python packages that provide this functionality.  Or
actually, two functionalities: (1) trapping the exception, and (2)
retrying the triggering code upon failure.

Typically, they work in the level of function: the code that needs to
be retried is written as a function, and it is either wrapped within a
context manager or passed to a retry function so that the function is
invoked repeatedly until it succeeds or fail sufficiently many times.
In this way, the two functionalities are packed into one function or
context manager for the user.

We take a slightly different approach: the two functionalities are
separated into two entities: a context manager that traps exception,
and a function that returns the context manager.  We argue that this
leads to neater code.

## Recipe

This provides most of what we normally need.

    for etrapper in exctrap.trial():
        with etrapper:
            # Do whatever that may fail.
        # Will reach here whether or not an exception is raised.
        # If you want to reraise the exception here, use etrapper.reraise().
    # If retry fails, the last exception is reraised so this is not reached.

## Options

The `trial()` function provides all the options.  These include:

  * `num_tries`: Maximum number of trials, if the code keeps raising
    exceptions for this many tries the exception is reraised without
    further retry.
  * `retry_period`: Number of seconds to wait between tries (adjusted
    by `period_noise`).
  * `period_noise`: Add or subtract at most this fraction of the
    `retry_period` to get the actual amount of seconds to sleep.
  * `etypes`: Exception types to trap.  By default, trap all
    exceptions derived from `Exception`.  This is passed to the
    constructor of `ExcTrapper` when creating exception trappers.

Note that this does not require any function to be created for the
code needs to be exception-proof.  Experience shows that code can be a
lot more neat as a result: the code can access the required variables
much more easily when it does not sit within a separate global
function or an inner function.

## Implementation

The "etrapper" is the context manager which traps exceptions when
running under the "with" statement.  This is done simply by recording
exceptions in the trapper object, and returning True to swallow it, in
the `__exit__` function.  If needed, the exception can be asked to be
`reraised()`.

The `trial()` function provides the retry logic and create exception
trappers.  Because the exception would be trapped in the trapper, all
trial needs to do is to check whether an exception is trapped, and
decide whether to retry or reraise.
