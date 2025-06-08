import json
import os
import threading
import time
from queue import Queue, Empty
from typing import Dict, Any, Optional, Callable


class SaveRequest:
    def __init__(self, data: Dict[str, Any], callback: Optional[Callable] = None, show_feedback: bool = False):
        self.data = data.copy()  # Make a copy to avoid race conditions
        self.callback = callback
        self.show_feedback = show_feedback
        self.timestamp = time.time()


class AsyncSaveManager:
    def __init__(self, data_file: str = "kanby_data.json"):
        self.data_file = data_file
        self.save_queue = Queue()
        self.is_running = False
        self.save_thread = None
        self.last_save_time = 0
        self.save_in_progress = False
        self.save_counter = 0
        self.failed_saves = 0
        
        # Callbacks for UI feedback
        self.success_callback = None
        self.error_callback = None
        
        self.start()
    
    def start(self):
        """Start the background save thread."""
        if not self.is_running:
            self.is_running = True
            self.save_thread = threading.Thread(target=self._save_worker, daemon=True)
            self.save_thread.start()
    
    def stop(self):
        """Stop the background save thread and process remaining saves."""
        self.is_running = False
        if self.save_thread and self.save_thread.is_alive():
            # Process any remaining saves
            self._process_remaining_saves()
            self.save_thread.join(timeout=2.0)
    
    def set_callbacks(self, success_callback: Optional[Callable] = None, error_callback: Optional[Callable] = None):
        """Set callbacks for save success/error feedback."""
        self.success_callback = success_callback
        self.error_callback = error_callback
    
    def queue_save(self, data: Dict[str, Any], callback: Optional[Callable] = None, show_feedback: bool = False):
        """Queue a save request without blocking."""
        if not self.is_running:
            self.start()
        
        save_request = SaveRequest(data, callback, show_feedback)
        self.save_queue.put(save_request)
    
    def save_now(self, data: Dict[str, Any], timeout: float = 5.0) -> bool:
        """Perform a synchronous save with timeout (for app shutdown)."""
        try:
            return self._save_data_to_file(data, self.data_file)
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Save failed: {str(e)}")
            return False
    
    def _save_worker(self):
        """Background thread worker that processes save requests."""
        while self.is_running:
            try:
                # Get save request with timeout
                save_request = self.save_queue.get(timeout=0.1)
                self._process_save_request(save_request)
                self.save_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                if self.error_callback:
                    self.error_callback(f"Save worker error: {str(e)}")
    
    def _process_remaining_saves(self):
        """Process any remaining saves when shutting down."""
        while not self.save_queue.empty():
            try:
                save_request = self.save_queue.get_nowait()
                self._process_save_request(save_request)
                self.save_queue.task_done()
            except Empty:
                break
            except Exception:
                continue
    
    def _process_save_request(self, save_request: SaveRequest):
        """Process a single save request."""
        self.save_in_progress = True
        
        try:
            success = self._save_data_to_file(save_request.data, self.data_file)
            
            if success:
                self.last_save_time = time.time()
                self.save_counter += 1
                
                if save_request.show_feedback and self.success_callback:
                    self.success_callback("💾 Saved")
                
                if save_request.callback:
                    save_request.callback(True)
            else:
                self.failed_saves += 1
                if self.error_callback:
                    self.error_callback("Save failed")
                
                if save_request.callback:
                    save_request.callback(False)
                    
        except Exception as e:
            self.failed_saves += 1
            if self.error_callback:
                self.error_callback(f"Save error: {str(e)}")
            
            if save_request.callback:
                save_request.callback(False)
        finally:
            self.save_in_progress = False
    
    def _save_data_to_file(self, data: Dict[str, Any], filename: str) -> bool:
        """Safely save data to file with atomic write."""
        temp_filename = filename + ".tmp"
        
        try:
            # Write to temporary file first
            with open(temp_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())  # Ensure data is written to disk
            
            # Atomic move (on most systems)
            if os.path.exists(filename):
                backup_filename = filename + ".bak"
                if os.path.exists(backup_filename):
                    os.remove(backup_filename)
                os.rename(filename, backup_filename)
            
            os.rename(temp_filename, filename)
            
            return True
            
        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                except:
                    pass
            raise e
    
    def get_status(self) -> Dict[str, Any]:
        """Get current save manager status."""
        return {
            "is_running": self.is_running,
            "save_in_progress": self.save_in_progress,
            "queue_size": self.save_queue.qsize(),
            "last_save_time": self.last_save_time,
            "save_counter": self.save_counter,
            "failed_saves": self.failed_saves
        }
    
    def is_busy(self) -> bool:
        """Check if there are pending or in-progress saves."""
        return self.save_in_progress or not self.save_queue.empty()


# Global save manager instance
_save_manager = None


def init_async_save(data_file: str = "kanby_data.json") -> AsyncSaveManager:
    """Initialize the async save manager."""
    global _save_manager
    if _save_manager is None:
        _save_manager = AsyncSaveManager(data_file)
    return _save_manager


def get_save_manager() -> Optional[AsyncSaveManager]:
    """Get the current save manager instance."""
    return _save_manager


def async_save(data: Dict[str, Any], show_feedback: bool = False, callback: Optional[Callable] = None):
    """Queue an async save."""
    if _save_manager:
        _save_manager.queue_save(data, callback, show_feedback)


def sync_save(data: Dict[str, Any], timeout: float = 5.0) -> bool:
    """Perform a synchronous save (for shutdown)."""
    if _save_manager:
        return _save_manager.save_now(data, timeout)
    return False


def shutdown_save_manager():
    """Shutdown the save manager and process remaining saves."""
    global _save_manager
    if _save_manager:
        _save_manager.stop()
        _save_manager = None


def set_save_callbacks(success_callback: Optional[Callable] = None, error_callback: Optional[Callable] = None):
    """Set callbacks for save feedback."""
    if _save_manager:
        _save_manager.set_callbacks(success_callback, error_callback)


def get_save_status() -> Dict[str, Any]:
    """Get current save status."""
    if _save_manager:
        return _save_manager.get_status()
    return {"error": "Save manager not initialized"}


def is_save_busy() -> bool:
    """Check if saves are in progress or pending."""
    if _save_manager:
        return _save_manager.is_busy()
    return False