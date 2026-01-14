"""Performance monitoring utilities for Tarofai optimization."""
import time
from typing import Optional
from dataclasses import dataclass, field
from contextlib import contextmanager


@dataclass
class TimingResult:
    """Result of a timing measurement."""
    stage: str
    duration: float
    success: bool = True
    details: str = ""


@dataclass
class PerformanceTracker:
    """Track performance across pipeline stages."""
    
    timings: list[TimingResult] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    
    @contextmanager
    def track(self, stage: str):
        """Context manager for timing a stage."""
        start = time.time()
        success = True
        details = ""
        try:
            yield
        except Exception as e:
            success = False
            details = str(e)
            raise
        finally:
            duration = time.time() - start
            self.timings.append(TimingResult(
                stage=stage,
                duration=duration,
                success=success,
                details=details
            ))
            status = "✓" if success else "✗"
            print(f"[PERF] {status} {stage}: {duration:.2f}s")
    
    def log_stage(self, stage: str, duration: float, success: bool = True, details: str = ""):
        """Manually log a timing result."""
        self.timings.append(TimingResult(
            stage=stage,
            duration=duration,
            success=success,
            details=details
        ))
        status = "✓" if success else "✗"
        print(f"[PERF] {status} {stage}: {duration:.2f}s")
    
    def get_total_time(self) -> float:
        """Get total elapsed time since tracker creation."""
        return time.time() - self.start_time
    
    def get_summary(self) -> dict:
        """Get performance summary."""
        return {
            "total_time": self.get_total_time(),
            "stages": [
                {
                    "stage": t.stage,
                    "duration": round(t.duration, 3),
                    "success": t.success
                }
                for t in self.timings
            ],
            "slowest_stage": max(self.timings, key=lambda x: x.duration).stage if self.timings else None,
            "failed_stages": [t.stage for t in self.timings if not t.success]
        }
    
    def print_summary(self):
        """Print formatted performance summary."""
        total = self.get_total_time()
        print("\n" + "=" * 50)
        print(f"[PERF] TOTAL TIME: {total:.2f}s")
        print("-" * 50)
        for t in self.timings:
            pct = (t.duration / total * 100) if total > 0 else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            status = "✓" if t.success else "✗"
            print(f"  {status} {t.stage:20s} {t.duration:6.2f}s ({pct:5.1f}%) {bar}")
        print("=" * 50 + "\n")


# Source performance tracking for adaptive prioritization
class SourcePerformanceTracker:
    """Track performance of individual sources for adaptive prioritization."""
    
    def __init__(self):
        self._source_stats: dict[str, dict] = {}
    
    def record(self, domain: str, success: bool, response_time: float):
        """Record a source request result."""
        if domain not in self._source_stats:
            self._source_stats[domain] = {
                "success_count": 0,
                "fail_count": 0,
                "total_time": 0.0,
                "avg_time": 0.0
            }
        
        stats = self._source_stats[domain]
        if success:
            stats["success_count"] += 1
        else:
            stats["fail_count"] += 1
        
        stats["total_time"] += response_time
        total_requests = stats["success_count"] + stats["fail_count"]
        stats["avg_time"] = stats["total_time"] / total_requests
    
    def get_priority_order(self, domains: list[str]) -> list[str]:
        """Get domains ordered by reliability and speed (best first)."""
        def score(domain: str) -> float:
            if domain not in self._source_stats:
                return 0.5  # Unknown sources get middle priority
            
            stats = self._source_stats[domain]
            total = stats["success_count"] + stats["fail_count"]
            if total == 0:
                return 0.5
            
            success_rate = stats["success_count"] / total
            # Invert avg_time so faster sources get higher score
            speed_score = 1 / (stats["avg_time"] + 0.1)
            
            return success_rate * 0.7 + speed_score * 0.3
        
        return sorted(domains, key=score, reverse=True)


# Global instance for source tracking
source_tracker = SourcePerformanceTracker()
