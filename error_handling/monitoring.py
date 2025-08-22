"""
Monitoring and metrics collection for the Garage Grown Gear scraper.
Tracks performance, success rates, and system health.
"""

import time
import psutil
import threading
import gc
import sys
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import contextmanager
import tracemalloc


@dataclass
class ScrapingMetrics:
    """Data class for storing scraping operation metrics."""
    start_time: float
    end_time: Optional[float] = None
    pages_scraped: int = 0
    products_found: int = 0
    products_processed: int = 0
    products_failed: int = 0
    network_requests: int = 0
    network_failures: int = 0
    sheets_operations: int = 0
    sheets_failures: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        """Calculate operation duration."""
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time
    
    @property
    def success_rate(self) -> float:
        """Calculate overall success rate."""
        total_operations = self.products_processed + self.products_failed
        if total_operations == 0:
            return 0.0
        return self.products_processed / total_operations
    
    @property
    def network_success_rate(self) -> float:
        """Calculate network success rate."""
        if self.network_requests == 0:
            return 0.0
        return (self.network_requests - self.network_failures) / self.network_requests
    
    @property
    def sheets_success_rate(self) -> float:
        """Calculate Google Sheets success rate."""
        if self.sheets_operations == 0:
            return 0.0
        return (self.sheets_operations - self.sheets_failures) / self.sheets_operations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            'duration_seconds': self.duration,
            'pages_scraped': self.pages_scraped,
            'products_found': self.products_found,
            'products_processed': self.products_processed,
            'products_failed': self.products_failed,
            'network_requests': self.network_requests,
            'network_failures': self.network_failures,
            'sheets_operations': self.sheets_operations,
            'sheets_failures': self.sheets_failures,
            'success_rate': self.success_rate,
            'network_success_rate': self.network_success_rate,
            'sheets_success_rate': self.sheets_success_rate,
            'error_count': len(self.errors)
        }


class SystemMonitor:
    """Monitors system resources during scraping operations."""
    
    def __init__(self, sample_interval: float = 5.0):
        self.sample_interval = sample_interval
        self.monitoring = False
        self.samples = []
        self._monitor_thread = None
    
    def start_monitoring(self) -> None:
        """Start system monitoring."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.samples = []
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return statistics."""
        self.monitoring = False
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)
        
        return self._calculate_stats()
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.monitoring:
            try:
                sample = {
                    'timestamp': time.time(),
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'memory_used_mb': psutil.virtual_memory().used / (1024 * 1024),
                    'disk_io_read_mb': psutil.disk_io_counters().read_bytes / (1024 * 1024) if psutil.disk_io_counters() else 0,
                    'disk_io_write_mb': psutil.disk_io_counters().write_bytes / (1024 * 1024) if psutil.disk_io_counters() else 0,
                    'network_sent_mb': psutil.net_io_counters().bytes_sent / (1024 * 1024),
                    'network_recv_mb': psutil.net_io_counters().bytes_recv / (1024 * 1024)
                }
                self.samples.append(sample)
                
                time.sleep(self.sample_interval)
            except Exception:
                # Continue monitoring even if individual samples fail
                time.sleep(self.sample_interval)
    
    def _calculate_stats(self) -> Dict[str, Any]:
        """Calculate statistics from collected samples."""
        if not self.samples:
            return {}
        
        # Calculate averages and peaks
        cpu_values = [s['cpu_percent'] for s in self.samples]
        memory_values = [s['memory_percent'] for s in self.samples]
        memory_used_values = [s['memory_used_mb'] for s in self.samples]
        
        # Calculate network and disk I/O deltas
        network_sent_delta = 0
        network_recv_delta = 0
        disk_read_delta = 0
        disk_write_delta = 0
        
        if len(self.samples) > 1:
            network_sent_delta = self.samples[-1]['network_sent_mb'] - self.samples[0]['network_sent_mb']
            network_recv_delta = self.samples[-1]['network_recv_mb'] - self.samples[0]['network_recv_mb']
            disk_read_delta = self.samples[-1]['disk_io_read_mb'] - self.samples[0]['disk_io_read_mb']
            disk_write_delta = self.samples[-1]['disk_io_write_mb'] - self.samples[0]['disk_io_write_mb']
        
        return {
            'monitoring_duration': self.samples[-1]['timestamp'] - self.samples[0]['timestamp'],
            'sample_count': len(self.samples),
            'cpu_avg_percent': sum(cpu_values) / len(cpu_values),
            'cpu_max_percent': max(cpu_values),
            'memory_avg_percent': sum(memory_values) / len(memory_values),
            'memory_max_percent': max(memory_values),
            'memory_avg_used_mb': sum(memory_used_values) / len(memory_used_values),
            'memory_max_used_mb': max(memory_used_values),
            'network_sent_mb': network_sent_delta,
            'network_recv_mb': network_recv_delta,
            'disk_read_mb': disk_read_delta,
            'disk_write_mb': disk_write_delta
        }


class MemoryTracker:
    """Enhanced memory usage tracking and optimization."""
    
    def __init__(self, enable_tracemalloc: bool = True):
        self.enable_tracemalloc = enable_tracemalloc
        self.memory_snapshots = []
        self.peak_memory = 0
        self.baseline_memory = 0
        self._tracking_active = False
        
    def start_tracking(self) -> None:
        """Start memory tracking."""
        if self._tracking_active:
            return
            
        self._tracking_active = True
        
        if self.enable_tracemalloc:
            tracemalloc.start()
        
        # Record baseline memory
        self.baseline_memory = self._get_current_memory()
        self.peak_memory = self.baseline_memory
        
    def stop_tracking(self) -> Dict[str, Any]:
        """Stop memory tracking and return statistics."""
        if not self._tracking_active:
            return {}
            
        self._tracking_active = False
        
        current_memory = self._get_current_memory()
        memory_stats = {
            'baseline_memory_mb': self.baseline_memory,
            'final_memory_mb': current_memory,
            'peak_memory_mb': self.peak_memory,
            'memory_increase_mb': current_memory - self.baseline_memory,
            'peak_increase_mb': self.peak_memory - self.baseline_memory
        }
        
        if self.enable_tracemalloc:
            try:
                snapshot = tracemalloc.take_snapshot()
                top_stats = snapshot.statistics('lineno')[:10]
                
                memory_stats['top_memory_consumers'] = [
                    {
                        'file': stat.traceback.format()[0] if stat.traceback.format() else 'unknown',
                        'size_mb': stat.size / (1024 * 1024),
                        'count': stat.count
                    }
                    for stat in top_stats
                ]
                tracemalloc.stop()
            except Exception:
                # Tracemalloc might fail in some environments
                pass
        
        return memory_stats
    
    def record_snapshot(self, label: str = "") -> None:
        """Record a memory snapshot at a specific point."""
        if not self._tracking_active:
            return
            
        current_memory = self._get_current_memory()
        self.peak_memory = max(self.peak_memory, current_memory)
        
        snapshot = {
            'timestamp': time.time(),
            'label': label,
            'memory_mb': current_memory,
            'memory_increase_mb': current_memory - self.baseline_memory
        }
        self.memory_snapshots.append(snapshot)
    
    def optimize_memory(self) -> Dict[str, Any]:
        """Perform memory optimization and return results."""
        before_memory = self._get_current_memory()
        
        # Force garbage collection
        collected = gc.collect()
        
        after_memory = self._get_current_memory()
        freed_memory = before_memory - after_memory
        
        return {
            'memory_before_mb': before_memory,
            'memory_after_mb': after_memory,
            'memory_freed_mb': freed_memory,
            'objects_collected': collected
        }
    
    def _get_current_memory(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0


class RequestTimer:
    """Enhanced request timing and performance metrics."""
    
    def __init__(self):
        self.request_times = []
        self.active_requests = {}
        
    @contextmanager
    def time_request(self, request_id: str, url: str = ""):
        """Context manager for timing requests."""
        start_time = time.time()
        self.active_requests[request_id] = {
            'start_time': start_time,
            'url': url
        }
        
        try:
            yield
            success = True
            error = None
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            request_data = {
                'request_id': request_id,
                'url': url,
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
                'success': success,
                'error': error
            }
            
            self.request_times.append(request_data)
            self.active_requests.pop(request_id, None)
    
    def get_request_stats(self) -> Dict[str, Any]:
        """Get comprehensive request statistics."""
        if not self.request_times:
            return {}
        
        successful_requests = [r for r in self.request_times if r['success']]
        failed_requests = [r for r in self.request_times if not r['success']]
        
        durations = [r['duration'] for r in successful_requests]
        
        stats = {
            'total_requests': len(self.request_times),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(self.request_times) if self.request_times else 0,
        }
        
        if durations:
            stats.update({
                'avg_response_time': sum(durations) / len(durations),
                'min_response_time': min(durations),
                'max_response_time': max(durations),
                'total_request_time': sum(durations)
            })
            
            # Calculate percentiles
            sorted_durations = sorted(durations)
            stats.update({
                'p50_response_time': self._percentile(sorted_durations, 50),
                'p90_response_time': self._percentile(sorted_durations, 90),
                'p95_response_time': self._percentile(sorted_durations, 95)
            })
        
        return stats
    
    def get_slow_requests(self, threshold: float = 5.0) -> List[Dict[str, Any]]:
        """Get requests that took longer than threshold seconds."""
        return [
            r for r in self.request_times 
            if r['duration'] > threshold
        ]
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of a sorted list."""
        if not data:
            return 0.0
        
        k = (len(data) - 1) * percentile / 100
        f = int(k)
        c = k - f
        
        if f == len(data) - 1:
            return data[f]
        
        return data[f] * (1 - c) + data[f + 1] * c


class BatchProcessor:
    """Batch processing for large datasets to optimize memory usage."""
    
    def __init__(self, batch_size: int = 100, memory_threshold_mb: float = 500.0):
        self.batch_size = batch_size
        self.memory_threshold_mb = memory_threshold_mb
        self.memory_tracker = MemoryTracker()
        
    def process_in_batches(self, items: List[Any], processor_func: Callable, 
                          **processor_kwargs) -> List[Any]:
        """
        Process items in batches to manage memory usage.
        
        Args:
            items: List of items to process
            processor_func: Function to process each batch
            **processor_kwargs: Additional arguments for processor function
            
        Returns:
            List of processed results
        """
        self.memory_tracker.start_tracking()
        results = []
        
        try:
            for i in range(0, len(items), self.batch_size):
                batch = items[i:i + self.batch_size]
                
                # Check memory usage before processing batch
                current_memory = self.memory_tracker._get_current_memory()
                if current_memory > self.memory_threshold_mb:
                    # Optimize memory before continuing
                    optimization_result = self.memory_tracker.optimize_memory()
                    
                # Process batch
                batch_results = processor_func(batch, **processor_kwargs)
                results.extend(batch_results)
                
                # Record memory snapshot after batch
                self.memory_tracker.record_snapshot(f"batch_{i//self.batch_size + 1}")
                
        finally:
            memory_stats = self.memory_tracker.stop_tracking()
            
        return results
    
    def get_optimal_batch_size(self, sample_items: List[Any], 
                              processor_func: Callable, 
                              target_memory_mb: float = 200.0) -> int:
        """
        Determine optimal batch size based on memory usage.
        
        Args:
            sample_items: Sample items to test with
            processor_func: Processing function
            target_memory_mb: Target memory usage per batch
            
        Returns:
            Recommended batch size
        """
        if len(sample_items) < 10:
            return len(sample_items)
        
        # Test with small batch to estimate memory per item
        test_batch_size = min(10, len(sample_items))
        test_batch = sample_items[:test_batch_size]
        
        memory_tracker = MemoryTracker()
        memory_tracker.start_tracking()
        
        try:
            processor_func(test_batch)
            memory_stats = memory_tracker.stop_tracking()
            
            memory_per_item = memory_stats.get('memory_increase_mb', 0) / test_batch_size
            
            if memory_per_item > 0:
                optimal_size = int(target_memory_mb / memory_per_item)
                return max(1, min(optimal_size, 1000))  # Reasonable bounds
            
        except Exception:
            pass
        
        return self.batch_size  # Fallback to default


class PerformanceMonitor:
    """Enhanced performance monitoring class with memory tracking and request timing."""
    
    def __init__(self, enable_memory_tracking: bool = True):
        self.operations = {}
        self.start_times = {}
        self.memory_tracker = MemoryTracker() if enable_memory_tracking else None
        self.request_timer = RequestTimer()
        self.batch_processor = BatchProcessor()
        
    def start_operation(self, operation_name: str) -> None:
        """Start timing an operation with memory tracking."""
        self.start_times[operation_name] = time.time()
        
        if self.memory_tracker:
            self.memory_tracker.record_snapshot(f"start_{operation_name}")
    
    def end_operation(self, operation_name: str, **extra_metrics) -> float:
        """End timing an operation and return duration with memory stats."""
        if operation_name not in self.start_times:
            return 0.0
        
        duration = time.time() - self.start_times[operation_name]
        del self.start_times[operation_name]
        
        # Record memory snapshot
        if self.memory_tracker:
            self.memory_tracker.record_snapshot(f"end_{operation_name}")
        
        # Store operation metrics
        if operation_name not in self.operations:
            self.operations[operation_name] = []
        
        metric_entry = {
            'duration': duration,
            'timestamp': time.time(),
            **extra_metrics
        }
        self.operations[operation_name].append(metric_entry)
        
        return duration
    
    @contextmanager
    def monitor_operation(self, operation_name: str, **extra_metrics):
        """Context manager for monitoring operations."""
        self.start_operation(operation_name)
        try:
            yield
        finally:
            self.end_operation(operation_name, **extra_metrics)
    
    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """Get enhanced statistics for a specific operation."""
        if operation_name not in self.operations:
            return {}
        
        entries = self.operations[operation_name]
        durations = [e['duration'] for e in entries]
        
        stats = {
            'operation': operation_name,
            'total_runs': len(durations),
            'total_duration': sum(durations),
            'average_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'last_run': entries[-1]['timestamp']
        }
        
        # Add percentile calculations
        if len(durations) > 1:
            sorted_durations = sorted(durations)
            stats.update({
                'p50_duration': self._percentile(sorted_durations, 50),
                'p90_duration': self._percentile(sorted_durations, 90),
                'p95_duration': self._percentile(sorted_durations, 95)
            })
        
        return stats
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all operations."""
        return {
            operation: self.get_operation_stats(operation)
            for operation in self.operations.keys()
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        summary = {
            'operations': self.get_all_stats(),
            'request_stats': self.request_timer.get_request_stats(),
            'slow_requests': self.request_timer.get_slow_requests()
        }
        
        if self.memory_tracker:
            summary['memory_snapshots'] = self.memory_tracker.memory_snapshots
        
        return summary
    
    def optimize_performance(self) -> Dict[str, Any]:
        """Perform performance optimization and return results."""
        optimization_results = {}
        
        # Memory optimization
        if self.memory_tracker:
            optimization_results['memory'] = self.memory_tracker.optimize_memory()
        
        # Clear old operation data to free memory
        operations_cleared = 0
        cutoff_time = time.time() - 3600  # Keep last hour of data
        
        for operation_name in list(self.operations.keys()):
            original_count = len(self.operations[operation_name])
            self.operations[operation_name] = [
                entry for entry in self.operations[operation_name]
                if entry['timestamp'] > cutoff_time
            ]
            operations_cleared += original_count - len(self.operations[operation_name])
        
        optimization_results['operations_cleared'] = operations_cleared
        
        return optimization_results
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of a sorted list."""
        if not data:
            return 0.0
        
        k = (len(data) - 1) * percentile / 100
        f = int(k)
        c = k - f
        
        if f == len(data) - 1:
            return data[f]
        
        return data[f] * (1 - c) + data[f + 1] * c


class ScrapingMonitor:
    """Main monitoring class that combines metrics and system monitoring."""
    
    def __init__(self, enable_system_monitoring: bool = True):
        self.enable_system_monitoring = enable_system_monitoring
        self.current_metrics = None
        self.system_monitor = SystemMonitor() if enable_system_monitoring else None
        self.historical_metrics = []
    
    def start_scraping_session(self) -> None:
        """Start a new scraping session."""
        self.current_metrics = ScrapingMetrics(start_time=time.time())
        
        if self.system_monitor:
            self.system_monitor.start_monitoring()
    
    def end_scraping_session(self) -> Dict[str, Any]:
        """End the current scraping session and return complete metrics."""
        if not self.current_metrics:
            return {}
        
        self.current_metrics.end_time = time.time()
        
        # Get system metrics
        system_stats = {}
        if self.system_monitor:
            system_stats = self.system_monitor.stop_monitoring()
        
        # Combine all metrics
        complete_metrics = {
            'scraping_metrics': self.current_metrics.to_dict(),
            'system_metrics': system_stats,
            'session_id': f"scrape_{int(self.current_metrics.start_time)}"
        }
        
        # Store in history
        self.historical_metrics.append(complete_metrics)
        
        # Keep only last 10 sessions
        if len(self.historical_metrics) > 10:
            self.historical_metrics = self.historical_metrics[-10:]
        
        return complete_metrics
    
    def record_page_scraped(self, products_found: int = 0) -> None:
        """Record that a page was scraped."""
        if self.current_metrics:
            self.current_metrics.pages_scraped += 1
            self.current_metrics.products_found += products_found
    
    def record_product_processed(self, success: bool = True) -> None:
        """Record that a product was processed."""
        if self.current_metrics:
            if success:
                self.current_metrics.products_processed += 1
            else:
                self.current_metrics.products_failed += 1
    
    def record_network_request(self, success: bool = True) -> None:
        """Record a network request."""
        if self.current_metrics:
            self.current_metrics.network_requests += 1
            if not success:
                self.current_metrics.network_failures += 1
    
    def record_sheets_operation(self, success: bool = True) -> None:
        """Record a Google Sheets operation."""
        if self.current_metrics:
            self.current_metrics.sheets_operations += 1
            if not success:
                self.current_metrics.sheets_failures += 1
    
    def record_error(self, error: Exception, context: str = "") -> None:
        """Record an error with context."""
        if self.current_metrics:
            error_info = {
                'timestamp': time.time(),
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context
            }
            self.current_metrics.errors.append(error_info)
    
    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """Get current session metrics."""
        if not self.current_metrics:
            return None
        return self.current_metrics.to_dict()
    
    def get_historical_summary(self) -> Dict[str, Any]:
        """Get summary of historical metrics."""
        if not self.historical_metrics:
            return {}
        
        # Calculate averages across sessions
        total_sessions = len(self.historical_metrics)
        
        avg_duration = sum(
            m['scraping_metrics']['duration_seconds'] 
            for m in self.historical_metrics
        ) / total_sessions
        
        avg_products = sum(
            m['scraping_metrics']['products_processed'] 
            for m in self.historical_metrics
        ) / total_sessions
        
        avg_success_rate = sum(
            m['scraping_metrics']['success_rate'] 
            for m in self.historical_metrics
        ) / total_sessions
        
        return {
            'total_sessions': total_sessions,
            'avg_duration_seconds': avg_duration,
            'avg_products_processed': avg_products,
            'avg_success_rate': avg_success_rate,
            'last_session': self.historical_metrics[-1]['scraping_metrics']['start_time'],
            'sessions_last_24h': len([
                m for m in self.historical_metrics
                if datetime.fromisoformat(m['scraping_metrics']['start_time']) > 
                   datetime.now() - timedelta(hours=24)
            ])
        }
    
    def generate_run_summary(self, products_processed: int = 0, 
                           quality_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive summary for a scraping run.
        
        Args:
            products_processed: Number of products processed
            quality_metrics: Data quality metrics if available
            
        Returns:
            Dictionary containing run summary
        """
        current_metrics = self.get_current_metrics()
        
        summary = {
            'run_timestamp': datetime.now().isoformat(),
            'performance_metrics': current_metrics,
            'products_processed': products_processed,
            'system_health': self._assess_system_health()
        }
        
        if quality_metrics:
            summary['quality_metrics'] = quality_metrics
            summary['quality_assessment'] = self._assess_quality_health(quality_metrics)
        
        # Add historical comparison if available
        if len(self.historical_metrics) > 1:
            summary['performance_comparison'] = self._compare_with_previous_runs()
        
        return summary
    
    def _assess_system_health(self) -> Dict[str, Any]:
        """Assess overall system health based on current metrics."""
        current_metrics = self.get_current_metrics()
        
        if not current_metrics:
            return {'status': 'unknown', 'issues': ['No metrics available']}
        
        issues = []
        status = 'healthy'
        
        # Check success rates
        if current_metrics.get('success_rate', 1.0) < 0.9:
            issues.append('Low success rate')
            status = 'warning'
        
        if current_metrics.get('network_success_rate', 1.0) < 0.95:
            issues.append('Network reliability issues')
            status = 'warning'
        
        # Check error count
        error_count = len(current_metrics.get('errors', []))
        if error_count > 10:
            issues.append(f'High error count: {error_count}')
            status = 'critical' if error_count > 50 else 'warning'
        
        # Check duration (if unusually long)
        duration = current_metrics.get('duration_seconds', 0)
        if duration > 1800:  # 30 minutes
            issues.append('Unusually long execution time')
            status = 'warning'
        
        return {
            'status': status,
            'issues': issues,
            'metrics_summary': {
                'duration_minutes': duration / 60,
                'success_rate': current_metrics.get('success_rate', 0),
                'error_count': error_count
            }
        }
    
    def _assess_quality_health(self, quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess data quality health."""
        quality_score = quality_metrics.get('quality_score', 0)
        completeness_rate = quality_metrics.get('completeness_rate', 0)
        validity_rate = quality_metrics.get('validity_rate', 0)
        
        issues = []
        status = 'healthy'
        
        if quality_score < 70:
            issues.append('Poor overall quality score')
            status = 'critical'
        elif quality_score < 85:
            issues.append('Below target quality score')
            status = 'warning'
        
        if completeness_rate < 90:
            issues.append('Low data completeness')
            status = 'warning' if status == 'healthy' else status
        
        if validity_rate < 95:
            issues.append('Data validity issues')
            status = 'warning' if status == 'healthy' else status
        
        return {
            'status': status,
            'issues': issues,
            'scores': {
                'quality_score': quality_score,
                'completeness_rate': completeness_rate,
                'validity_rate': validity_rate
            }
        }
    
    def _compare_with_previous_runs(self) -> Dict[str, Any]:
        """Compare current run with previous runs."""
        if len(self.historical_metrics) < 2:
            return {}
        
        current = self.historical_metrics[-1]['scraping_metrics']
        previous = self.historical_metrics[-2]['scraping_metrics']
        
        comparison = {
            'duration_change': current['duration_seconds'] - previous['duration_seconds'],
            'products_change': current['products_processed'] - previous['products_processed'],
            'success_rate_change': current['success_rate'] - previous['success_rate']
        }
        
        # Add trend assessment
        trends = []
        if comparison['duration_change'] > 60:  # More than 1 minute slower
            trends.append('Performance degradation detected')
        elif comparison['duration_change'] < -60:  # More than 1 minute faster
            trends.append('Performance improvement detected')
        
        if comparison['success_rate_change'] < -0.05:  # 5% drop in success rate
            trends.append('Success rate declining')
        elif comparison['success_rate_change'] > 0.05:  # 5% improvement
            trends.append('Success rate improving')
        
        comparison['trends'] = trends
        
        return comparison