twisted.python.failure.Failure tracebacks generated by coroutines scheduled with twisted.internet.defer.ensureDeferred - i.e. any Deferred-awaiting coroutine - now contain fewer extraneous frames from the trampoline implementation, and correctly indicate the source of exceptions raised in other call stacks - i.e. the function that raised the exception.  In other words: if you 'await' a function that raises an exception, you'll be able to see where the error came from.