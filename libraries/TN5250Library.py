import subprocess
import time
from robot.api import logger

class TN5250Library:
    """
    Robot Framework library for headless TN5250 testing via tmux.
    Supports SSL connections natively.
    """

    def __init__(self):
        self.session_name = "robot_tn5250_session"

    def start_tn5250_session(self, hostname, ssl=True, devname=None, map=285):
        """
        Starts tn5250 in a background tmux session.
        If ssl is True, connects using 'ssl:hostname'.
        If devname not equal None then use the specifies device name.
        """
        self.stop_tn5250_session() # Cleanup any old sessions
        
        # Construct the command: 'tn5250 ssl:172.16.8.41'
        prefix = "ssl:" if ssl else ""
        
        cmd = f"tn5250 {prefix}{hostname} map={map}"
        if devname is not None:
            cmd += f" env.DEVNAME={devname}"
        
        logger.info(f"Starting session: {cmd}")
        
        # Start headless tmux session (-d) with standard 80x24 screen
        subprocess.run([
            "tmux", "new-session", "-d",
            "-s", self.session_name,
            "-x", "80", "-y", "24",
            cmd
        ], check=True)
        
        time.sleep(3) # Give SSL handshake a moment to finish

    def stop_tn5250_session(self):
        """Kills the tmux session."""
        subprocess.run(
            ["tmux", "kill-session", "-t", self.session_name], 
            stderr=subprocess.DEVNULL
        )

    def send_text(self, text):
        """Types text into the terminal."""
        logger.info(f"Typing: '{text}'")
        subprocess.run(["tmux", "send-keys", "-t", self.session_name, text], check=True)

    def send_special_key(self, key_name):
        """Sends special keys: Enter, Tab, F3, Backspace."""
        logger.info(f"Sending Key: {key_name}")
        subprocess.run(["tmux", "send-keys", "-t", self.session_name, key_name], check=True)
        time.sleep(0.5) # Wait for screen refresh

    def screen_should_contain(self, expected_text, timeout=10):
        """
        Waits for text to appear. Fails if timeout is reached.
        """
        start_time = time.time()
        while time.time() - start_time < int(timeout):
            # Capture current screen content
            result = subprocess.run(
                ["tmux", "capture-pane", "-p", "-t", self.session_name],
                capture_output=True, text=True
            )
            if expected_text in result.stdout:
                logger.info(f"Found text: '{expected_text}'")
                return True
            time.sleep(0.5)
            
        # Log failure
        logger.info("--- SCREEN DUMP (FAILURE) ---")
        logger.info(result.stdout)
        raise AssertionError(f"Timeout: Text '{expected_text}' not found on screen.")