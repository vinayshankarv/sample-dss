"""
Retry and backoff logic for Review II scraper.
"""

import time
import random
import logging
from typing import Callable, Any, Optional
from functools import wraps


class RetryHandler:
    """Handles retry logic with exponential backoff."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def retry_on_failure(self, 
                        func: Callable,
                        max_retries: Optional[int] = None,
                        backoff_factor: Optional[float] = None,
                        exceptions: tuple = (Exception,)) -> Callable:
        """Decorator for retrying functions with exponential backoff."""
        max_retries = max_retries or self.config.max_retries
        backoff_factor = backoff_factor or self.config.retry_delay
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        self.logger.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                        break
                    
                    # Calculate backoff delay with jitter
                    delay = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                    self.logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}, retrying in {delay:.2f}s: {str(e)}")
                    time.sleep(delay)
            
            # Return None or raise the last exception based on configuration
            if last_exception:
                raise last_exception
            return None
        
        return wrapper
    
    def circuit_breaker(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """Circuit breaker pattern to prevent cascading failures."""
        def decorator(func: Callable) -> Callable:
            func._failures = 0
            func._last_failure_time = 0
            func._state = 'closed'  # closed, open, half-open
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                current_time = time.time()
                
                # Check if circuit should move from open to half-open
                if (func._state == 'open' and 
                    current_time - func._last_failure_time > recovery_timeout):
                    func._state = 'half-open'
                    self.logger.info(f"Circuit breaker for {func.__name__} moving to half-open state")
                
                # If circuit is open, fail fast
                if func._state == 'open':
                    raise Exception(f"Circuit breaker open for {func.__name__}")
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Success - reset failure count and close circuit
                    if func._state == 'half-open':
                        func._state = 'closed'
                        func._failures = 0
                        self.logger.info(f"Circuit breaker for {func.__name__} closed after successful call")
                    
                    return result
                    
                except Exception as e:
                    func._failures += 1
                    func._last_failure_time = current_time
                    
                    # Open circuit if failure threshold reached
                    if func._failures >= failure_threshold:
                        func._state = 'open'
                        self.logger.error(f"Circuit breaker opened for {func.__name__} after {func._failures} failures")
                    
                    raise e
            
            return wrapper
        return decorator
    
    def timeout_handler(self, timeout_seconds: int):
        """Timeout handler for long-running operations."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Function {func.__name__} timed out after {timeout_seconds} seconds")
                
                # Set up timeout signal
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout_seconds)
                
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    # Restore old handler and cancel alarm
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
            
            return wrapper
        return decorator