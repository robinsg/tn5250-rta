import subprocess
import time
import os
import datetime
from robot.api import logger

class TN5250Library:
    """
    Robot Framework library for headless TN5250 testing via tmux.
    Supports SSL connections natively.
    """

    def __init__(self, verbose=False):
        # Robot may pass boolean-like strings; normalize
        try:
            self.verbose = str(verbose).lower() in ("true", "1", "yes", "y")
        except Exception:
            self.verbose = False
        self.session_name = "robot_tn5250_session"

    def set_verbose(self, verbose=True):
        """Keyword to enable/disable verbose console output.

        Usage: `Set TN5250 Verbose    True`
        """
        try:
            self.verbose = str(verbose).lower() in ("true", "1", "yes", "y")
        except Exception:
            self.verbose = False
        logger.info(f"TN5250Library verbose set to {self.verbose}")
        if self.verbose:
            logger.console(f"TN5250Library verbose set to {self.verbose}")

    def _log(self, message):
        logger.info(message)
        if getattr(self, "verbose", False):
            logger.console(message)

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
        
        self._log(f"Starting session: {cmd}")
        
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
        self._log(f"Killing tmux session: {self.session_name}")
        subprocess.run([
            "tmux", "kill-session", "-t", self.session_name
        ], stderr=subprocess.DEVNULL)

    def send_text(self, text):
        """Types text into the terminal."""
        self._log(f"Typing: '{text}'")
        subprocess.run(["tmux", "send-keys", "-t", self.session_name, text], check=True)

    def send_special_key(self, key_name):
        """Sends special keys: Enter, Tab, F3, Backspace."""
        self._log(f"Sending Key: {key_name}")
        subprocess.run(["tmux", "send-keys", "-t", self.session_name, key_name], check=True)
        time.sleep(0.5) # Wait for screen refresh

    def screen_should_contain(self, expected_text, timeout=10):
        """
        Waits for text to appear. Fails if timeout is reached.
        """
        start_time = time.time()
        while time.time() - start_time < int(timeout):
            # Capture current screen content
            result = subprocess.run([
                "tmux", "capture-pane", "-p", "-t", self.session_name
            ], capture_output=True, text=True)
            if expected_text in result.stdout:
                self._log(f"Found text: '{expected_text}'")
                if self.verbose:
                    # Show the matching screen output for debug
                    logger.console("--- SCREEN (MATCH) ---")
                    logger.console(result.stdout)
                return True
            time.sleep(0.5)
            
        # Log failure
        self._log("--- SCREEN DUMP (FAILURE) ---")
        logger.console(result.stdout)
        raise AssertionError(f"Timeout: Text '{expected_text}' not found on screen.")

    def capture_screen(self, filename=None, image=False):
        """
        Captures the current TN5250 screen to a text file under `results/screenshots`.
        If `image` is truthy and ImageMagick `convert` is available, also renders a PNG.
        Returns the path to the text file.
        """
        # Normalize image flag (Robot passes strings sometimes)
        image_flag = False
        try:
            image_flag = str(image).lower() in ("true", "1", "yes", "y")
        except Exception:
            image_flag = False

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = os.path.join("results", "screenshots")
        os.makedirs(out_dir, exist_ok=True)

        base = filename if filename else f"screen_{ts}"
        txt_path = os.path.join(out_dir, base + ".txt")

        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(result.stdout)

        self._log(f"Saved screen text to {txt_path}")

        if image_flag:
            png_path = os.path.join(out_dir, base + ".png")
            try:
                proc = subprocess.run(
                    [
                        "convert",
                        "-background",
                        "black",
                        "-fill",
                        "white",
                        "-font",
                        "DejaVu-Sans-Mono",
                        "-pointsize",
                        "12",
                        "label:@-",
                        png_path,
                    ],
                    input=result.stdout,
                    text=True,
                    capture_output=True,
                )
                if proc.returncode == 0:
                    self._log(f"Saved screen image to {png_path}")
                else:
                    self._log(f"ImageMagick convert failed: {proc.stderr}")
            except FileNotFoundError:
                self._log("ImageMagick `convert` not found; skipping image.")

        return txt_path