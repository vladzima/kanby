import time
from collections import deque
from enum import Enum


class MessageType(Enum):
    INFO = "info"
    ERROR = "error"
    SUCCESS = "success"
    WARNING = "warning"


class Message:
    def __init__(self, text, message_type=MessageType.INFO, duration=1.5, color_pair=0):
        self.text = text
        self.message_type = message_type
        self.duration = duration
        self.color_pair = color_pair
        self.timestamp = time.time()
        self.displayed = False
    
    def is_expired(self):
        """Check if the message has exceeded its display duration."""
        return time.time() - self.timestamp >= self.duration
    
    def should_display(self):
        """Check if the message should be displayed (not expired and not already cleared)."""
        return not self.is_expired()


class MessageManager:
    def __init__(self):
        self.messages = deque()
        self.current_message = None
        self.last_update = 0
        self.update_interval = 0.05  # Update every 50ms for smooth clearing
    
    def add_message(self, text, message_type=MessageType.INFO, duration=1.5, color_pair=0):
        """Add a new message to the queue."""
        message = Message(text, message_type, duration, color_pair)
        self.messages.append(message)
    
    def add_info(self, text, duration=1.5, color_pair=0):
        """Convenience method for info messages."""
        self.add_message(text, MessageType.INFO, duration, color_pair)
    
    def add_error(self, text, duration=1.5, color_pair=0):
        """Convenience method for error messages."""
        self.add_message(text, MessageType.ERROR, duration, color_pair)
    
    def add_success(self, text, duration=1.0, color_pair=0):
        """Convenience method for success messages."""
        self.add_message(text, MessageType.SUCCESS, duration, color_pair)
    
    def add_warning(self, text, duration=1.5, color_pair=0):
        """Convenience method for warning messages."""
        self.add_message(text, MessageType.WARNING, duration, color_pair)
    
    def get_current_message(self):
        """Get the current message that should be displayed, if any."""
        current_time = time.time()
        
        # Check if we need to update (throttle updates)
        if current_time - self.last_update < self.update_interval:
            return self.current_message
        
        self.last_update = current_time
        
        # Clear expired current message
        if self.current_message and self.current_message.is_expired():
            self.current_message = None
        
        # If no current message, get next from queue
        if not self.current_message and self.messages:
            # Remove expired messages from queue
            while self.messages and self.messages[0].is_expired():
                self.messages.popleft()
            
            # Get next message if available
            if self.messages:
                self.current_message = self.messages.popleft()
        
        return self.current_message
    
    def clear_current(self):
        """Manually clear the current message."""
        self.current_message = None
    
    def clear_all(self):
        """Clear all messages including queued ones."""
        self.messages.clear()
        self.current_message = None
    
    def has_messages(self):
        """Check if there are any messages to display or in queue."""
        return bool(self.current_message or self.messages)
    
    def update_display(self, stdscr):
        """Non-blocking update of message display."""
        try:
            height, width = stdscr.getmaxyx()
            message_row = height - 1
            
            current_msg = self.get_current_message()
            
            if current_msg and current_msg.should_display():
                # Display the message
                text = current_msg.text[:width-1]  # Truncate if too long
                
                # Clear the line first
                stdscr.addstr(message_row, 0, " " * (width - 1))
                
                # Display the message
                stdscr.addstr(message_row, 0, text, current_msg.color_pair)
            else:
                # Clear the message line
                stdscr.addstr(message_row, 0, " " * (width - 1))
            
        except Exception:
            # Ignore curses errors during message display
            pass
    
    def quick_flash(self, stdscr, text, duration=0.3, color_pair=0):
        """Display a very brief flash message (for immediate feedback)."""
        try:
            height, width = stdscr.getmaxyx()
            message_row = height - 1
            
            # Clear and show message
            stdscr.addstr(message_row, 0, " " * (width - 1))
            stdscr.addstr(message_row, 0, text[:width-1], color_pair)
            stdscr.refresh()
            
            # Add to normal message queue for automatic clearing
            self.add_message(text, MessageType.INFO, duration, color_pair)
            
        except Exception:
            pass


# Global message manager instance
message_manager = MessageManager()


def init_message_system():
    """Initialize the message system."""
    return message_manager


def display_message_non_blocking(text, message_type=MessageType.INFO, duration=1.5, color_pair=0):
    """Add a message to be displayed without blocking."""
    message_manager.add_message(text, message_type, duration, color_pair)


def display_info(text, duration=1.5, color_pair=0):
    """Display an info message non-blocking."""
    message_manager.add_info(text, duration, color_pair)


def display_error(text, duration=1.5, color_pair=0):
    """Display an error message non-blocking."""
    message_manager.add_error(text, duration, color_pair)


def display_success(text, duration=1.0, color_pair=0):
    """Display a success message non-blocking."""
    message_manager.add_success(text, duration, color_pair)


def display_warning(text, duration=1.5, color_pair=0):
    """Display a warning message non-blocking."""
    message_manager.add_warning(text, duration, color_pair)


def update_messages(stdscr):
    """Update message display - call this in the main loop."""
    message_manager.update_display(stdscr)


def clear_messages():
    """Clear all messages."""
    message_manager.clear_all()